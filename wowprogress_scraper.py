#!/usr/bin/env python3
"""Utilities for scraping guild member social tags from wowprogress.com.

The script relies on Playwright to drive Chromium so that the Cloudflare
challenge that protects the public pages can be solved in a regular browser
context. The scraper collects the active roster of a guild and then visits
the profile page for each character to extract social media handles.

Example usage::

    python wowprogress_scraper.py --region eu --realm draenor --guild Method \
        --max-members 10 --output members.json

Running the script for the first time requires that the Playwright browsers
are installed::

    playwright install chromium
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from contextlib import contextmanager
from typing import Dict, Iterator, List, Optional, Tuple
from urllib.parse import quote_plus, urljoin

from playwright.sync_api import Browser, BrowserContext, Page, TimeoutError, sync_playwright

try:
    from playwright_stealth import Stealth
except ImportError:  # pragma: no cover - optional dependency
    Stealth = None  # type: ignore


CLOUDFLARE_TITLES = {
    "attention required! | cloudflare",
    "just a moment...",
    "sorry, you have been blocked",
}

SOCIAL_PATTERNS: Dict[str, re.Pattern[str]] = {
    "battle_net": re.compile(r"Battle\.net\s*[:：-]\s*([^\n]+)", re.IGNORECASE),
    "discord": re.compile(r"Discord\s*[:：-]\s*([^\n]+)", re.IGNORECASE),
    "twitter": re.compile(r"Twitter\s*[:：-]\s*([^\n]+)", re.IGNORECASE),
    "twitch": re.compile(r"Twitch\s*[:：-]\s*([^\n]+)", re.IGNORECASE),
    "youtube": re.compile(r"YouTube\s*[:：-]\s*([^\n]+)", re.IGNORECASE),
}


@dataclass
class MemberProfile:
    """Structured information for a single guild member."""

    name: str
    rank: Optional[str]
    role: Optional[str]
    item_level: Optional[str]
    profile_url: str
    social_tags: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        payload = asdict(self)
        return payload


def build_guild_url(region: str, realm: str, guild: str) -> str:
    slug_realm = quote_plus(realm.strip())
    slug_guild = quote_plus(guild.strip())
    return f"https://www.wowprogress.com/guild/{region.strip().lower()}/{slug_realm}/{slug_guild}"


@contextmanager
def configure_browser(
    headless: bool, user_agent: Optional[str], use_stealth: bool
) -> Iterator[Tuple[Browser, BrowserContext]]:
    """Yield a configured Playwright browser and context respecting stealth options."""

    if use_stealth:
        if Stealth is None:
            raise RuntimeError(
                "playwright-stealth is required when --stealth is enabled. "
                "Install it with `pip install playwright-stealth`."
            )
        stealth = Stealth()
        playwright_manager = stealth.use_sync(sync_playwright())
    else:
        stealth = None
        playwright_manager = sync_playwright()

    with playwright_manager as playwright:  # type: ignore[misc]
        browser_args = [
            "--ignore-certificate-errors",
            "--disable-blink-features=AutomationControlled",
        ]
        browser_kwargs = {
            "headless": headless,
            "args": browser_args,
            "chromium_sandbox": False,
        }
        browser: Browser = playwright.chromium.launch(**browser_kwargs)
        context_kwargs = {
            "ignore_https_errors": True,
            "java_script_enabled": True,
            "viewport": {"width": 1365, "height": 768},
            "locale": "en-US",
        }
        if user_agent:
            context_kwargs["user_agent"] = user_agent

        context: BrowserContext = browser.new_context(**context_kwargs)
        try:
            yield browser, context
        finally:
            context.close()
            browser.close()


def ensure_not_blocked(page: Page) -> None:
    title = (page.title() or "").strip().lower()
    if title in CLOUDFLARE_TITLES:
        raise RuntimeError(
            "Cloudflare blocked the request. Try enabling stealth mode, running in "
            "headed mode with xvfb, or solving the challenge in a persistent profile."
        )
    body_text = page.locator("body").inner_text().lower()
    if "cloudflare" in body_text and ("verify you are human" in body_text or "blocked" in body_text):
        raise RuntimeError(
            "Cloudflare challenge detected. Manual intervention may be required before scraping can continue."
        )


def extract_row_data(row: Page) -> Optional[MemberProfile]:
    """Convert a roster row element into a :class:`MemberProfile`."""

    cells = row.locator("td")
    if cells.count() < 2:
        return None

    rank = cells.nth(0).inner_text().strip() or None
    char_cell = cells.nth(1)
    name_anchor = char_cell.locator("a").first
    if name_anchor.count() == 0:
        return None
    name = name_anchor.inner_text().strip()
    href = name_anchor.get_attribute("href") or ""
    profile_url = urljoin("https://www.wowprogress.com/", href)

    role = None
    role_badge = char_cell.locator("span[class*='spec'], span[class*='role']").first
    if role_badge and role_badge.count() > 0:
        role = role_badge.inner_text().strip() or None

    item_level = None
    if cells.count() >= 4:
        ilvl_text = cells.nth(3).inner_text().strip()
        item_level = ilvl_text or None

    classes = (row.get_attribute("class") or "").lower()
    text = row.inner_text().lower()
    if "inactive" in classes or "inactive" in text:
        return None

    return MemberProfile(
        name=name,
        rank=rank,
        role=role,
        item_level=item_level,
        profile_url=profile_url,
    )


def scrape_roster(page: Page, max_members: Optional[int] = None) -> List[MemberProfile]:
    table_locator = page.locator("table:has(th:has-text('Character'))")
    table_locator.wait_for(timeout=15000)
    rows = table_locator.locator("tbody tr")
    members: List[MemberProfile] = []
    for idx in range(rows.count()):
        row = rows.nth(idx)
        member = extract_row_data(row)
        if not member:
            continue
        members.append(member)
        if max_members and len(members) >= max_members:
            break
    return members


def scrape_social_tags(page: Page) -> Dict[str, str]:
    ensure_not_blocked(page)
    body_text = page.locator("body").inner_text()
    tags: Dict[str, str] = {}
    for key, pattern in SOCIAL_PATTERNS.items():
        match = pattern.search(body_text)
        if not match:
            continue
        value = match.group(1).strip()
        value = re.sub(r"[\s\u00a0]+", " ", value)
        tags[key] = value
    return tags


def visit_member_profiles(context: BrowserContext, members: List[MemberProfile], delay: float, jitter: float) -> None:
    profile_page = context.new_page()
    try:
        for member in members:
            profile_page.goto(member.profile_url, wait_until="domcontentloaded", timeout=30000)
            ensure_not_blocked(profile_page)
            member.social_tags = scrape_social_tags(profile_page)
            sleep_for = delay + random.uniform(-jitter, jitter)
            if sleep_for > 0:
                time.sleep(sleep_for)
    finally:
        profile_page.close()


def save_output(members: List[MemberProfile], output: Optional[Path]) -> None:
    payload = [member.to_dict() for member in members]
    serialized = json.dumps(payload, indent=2, ensure_ascii=False)
    if output:
        output.write_text(serialized, encoding="utf-8")
    else:
        print(serialized)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--region", required=True, help="Region of the guild, e.g. eu, us, kr")
    parser.add_argument("--realm", required=True, help="Realm (server) name")
    parser.add_argument("--guild", required=True, help="Guild name")
    parser.add_argument("--headless", action="store_true", default=False, help="Run the browser in headless mode")
    parser.add_argument("--user-agent", help="Override the browser user agent")
    parser.add_argument("--stealth", action="store_true", help="Enable playwright-stealth mitigations")
    parser.add_argument("--max-members", type=int, help="Limit the number of members to fetch for testing")
    parser.add_argument("--delay", type=float, default=2.0, help="Base delay between profile visits (seconds)")
    parser.add_argument(
        "--jitter",
        type=float,
        default=0.75,
        help="Random jitter added/subtracted to the base delay to mimic human behaviour",
    )
    parser.add_argument("--output", type=Path, help="Optional output JSON file")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    guild_url = build_guild_url(args.region, args.realm, args.guild)

    try:
        with configure_browser(
            headless=args.headless, user_agent=args.user_agent, use_stealth=args.stealth
        ) as (_, context):
            page = context.new_page()
            page.goto(guild_url, wait_until="domcontentloaded", timeout=30000)
            ensure_not_blocked(page)
            members = scrape_roster(page, max_members=args.max_members)
            if not members:
                raise RuntimeError("No active members were discovered. Check the guild URL or login requirements.")
            visit_member_profiles(context, members, delay=args.delay, jitter=args.jitter)
            save_output(members, args.output)
    except TimeoutError as exc:
        print(f"Timed out while loading pages: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
