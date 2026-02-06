# ⚔️ WoWProgress Scraper

### Scrape guild rosters and member social tags from WoWProgress — with Cloudflare bypass via Playwright.

[![GitHub Stars](https://img.shields.io/github/stars/CheswickDEV/WoWProgress-Scraper?color=00d4ff&labelColor=16161f)](https://github.com/CheswickDEV/WoWProgress-Scraper)
[![Last Commit](https://img.shields.io/github/last-commit/CheswickDEV/WoWProgress-Scraper?color=a855f7&labelColor=16161f)](https://github.com/CheswickDEV/WoWProgress-Scraper/commits/main)
![Version](https://img.shields.io/badge/version-1.0-00d4ff?labelColor=16161f)
![Status](https://img.shields.io/badge/status-Active-00d4ff?labelColor=16161f)
![License](https://img.shields.io/badge/license-MIT-a855f7?labelColor=16161f)
![Python](https://img.shields.io/badge/Python-3.10+-a855f7?logo=python&logoColor=white&labelColor=16161f)

---

## 💡 What It Does

WoWProgress protects its pages with Cloudflare challenges, making traditional HTTP-based scraping impossible. This tool uses **Playwright** to drive a real Chromium browser, solve the challenge automatically, and then:

1. Navigate to any guild's roster page
2. Extract active members with name, rank, role, and item level
3. Visit each member's profile to collect social media handles (Battle.net, Discord, Twitter, Twitch, YouTube)
4. Output everything as structured JSON

Built for guild leaders, community managers, and recruitment officers who need roster data that WoWProgress doesn't expose via an API.

---

## ⚡ Features

- **🛡️ Cloudflare Bypass** — Uses a real browser context with configurable user agent and optional [playwright-stealth](https://pypi.org/project/playwright-stealth/) to bypass Cloudflare's bot detection.

- **📋 Full Roster Extraction** — Parses the guild member table including character name, rank, role (spec), item level, and profile URL. Inactive members are automatically filtered out.

- **🔗 Social Tag Collection** — Visits each member's profile page and extracts Battle.net, Discord, Twitter, Twitch, and YouTube handles via regex pattern matching.

- **⏱️ Rate Limiting** — Configurable delay and random jitter between profile visits to avoid triggering rate limits or bans.

- **📄 JSON Output** — Clean, structured output to stdout or file — ready for further processing or import into spreadsheets and databases.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Chromium browser (installed via Playwright)

### Installation

```bash
# 1. Clone
git clone https://github.com/CheswickDEV/WoWProgress-Scraper.git
cd WoWProgress-Scraper

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install Playwright browsers
playwright install chromium
```

---

## 📖 Usage

```bash
# Basic usage — scrape a guild roster + social tags
python wowprogress_scraper.py \
  --region eu \
  --realm draenor \
  --guild Method \
  --output members.json

# Quick test with limited members
python wowprogress_scraper.py \
  --region eu \
  --realm draenor \
  --guild Method \
  --max-members 5

# Stealth mode + headless for automation
python wowprogress_scraper.py \
  --region us \
  --realm illidan \
  --guild "Liquid" \
  --headless \
  --stealth \
  --output liquid.json
```

### CLI Parameters

| Parameter | Required | Default | Description |
|:----------|:--------:|:-------:|:------------|
| `--region` | ✅ | — | Region of the guild (`eu`, `us`, `kr`, etc.) |
| `--realm` | ✅ | — | Realm (server) name |
| `--guild` | ✅ | — | Guild name |
| `--output` | ❌ | stdout | Output JSON file path |
| `--max-members` | ❌ | all | Limit number of members (useful for testing) |
| `--headless` | ❌ | `false` | Run browser without visible window |
| `--stealth` | ❌ | `false` | Enable playwright-stealth mitigations |
| `--user-agent` | ❌ | default | Override browser user agent string |
| `--delay` | ❌ | `2.0` | Base delay between profile visits (seconds) |
| `--jitter` | ❌ | `0.75` | Random jitter ± added to delay |

### Output Format

```json
[
  {
    "name": "Charactername",
    "rank": "1",
    "role": null,
    "item_level": "639",
    "profile_url": "https://www.wowprogress.com/character/eu/draenor/Charactername",
    "social_tags": {
      "discord": "user#1234",
      "twitch": "streamername",
      "twitter": "@handle"
    }
  }
]
```

---

## ⚠️ Disclaimer

This tool is for **personal use and research purposes only**. Respect WoWProgress's terms of service. Use reasonable delays between requests and avoid hammering their servers. The Cloudflare bypass operates within a standard browser context — no CAPTCHA solving or token forgery is involved.

---

## 🛠️ Tech Stack

![Python](https://img.shields.io/badge/Python-16161f?logo=python&logoColor=00d4ff)
![Playwright](https://img.shields.io/badge/Playwright-16161f?logo=playwright&logoColor=00d4ff)

```
WoWProgress-Scraper/
├── wowprogress_scraper.py   # Main scraper script
├── requirements.txt         # Python dependencies
└── README.md
```

**Dependencies:**
- `playwright` ≥ 1.55.0
- `playwright-stealth` ≥ 2.0.0 (optional, for `--stealth` mode)

---

## 📝 Changelog

### v1.0 (current)
- 🚀 Initial release
- ✨ Guild roster extraction with Cloudflare bypass
- ✨ Social tag collection (Battle.net, Discord, Twitter, Twitch, YouTube)
- ✨ Configurable rate limiting with jitter
- ✨ JSON output to file or stdout
- ✨ Optional stealth mode via playwright-stealth

---

## 📄 License

[MIT](LICENSE) — do what you want, just give credit.

---

<p align="center">
  <a href="https://cheswick.dev">
    <img src="https://img.shields.io/badge/CHESWICK.DEV-00d4ff?logo=firefox&logoColor=0a0a0f&labelColor=a855f7" alt="cheswick.dev" />
  </a>
</p>

<p align="center">
  Made with 🖤 by <a href="https://cheswick.dev">cheswick.dev</a>
</p>
