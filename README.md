<img align="center" alt="Coding" width="1440" src="https://i.imgur.com/2ZhZyzX.png">

<h1 align="left">Hi 👋, I'm Cheswick</h1>
<h3 align="left">A keyboard and monitor enthusiast</h3>

<img align="right" alt="Coding" width="400" src="https://i.imgur.com/QiSCzPb.jpg">


- 🌱 I’m currently learning **Ansible & Playwright**

- 📫 How to reach me **cheswick@ultrawidemasterrace.net**

<h3 align="left">Connect with me:</h3>
<p align="left">
<a href="https://www.youtube.com/c/ultrawidemasterrace" target="blank"><img align="center" src="https://raw.githubusercontent.com/rahuldkjain/github-profile-readme-generator/master/src/images/icons/Social/youtube.svg" alt="ultrawidemasterrace" height="30" width="40" /></a>
<a href="https://discord.gg/cheswick#0001" target="blank"><img align="center" src="https://raw.githubusercontent.com/rahuldkjain/github-profile-readme-generator/master/src/images/icons/Social/discord.svg" alt="cheswick#0001" height="30" width="40" /></a>
</p>

<h3 align="left">Languages and Tools:</h3>
<p align="left"> <a href="https://www.gnu.org/software/bash/" target="_blank" rel="noreferrer"> <img src="https://www.vectorlogo.zone/logos/gnu_bash/gnu_bash-icon.svg" alt="bash" width="40" height="40"/> </a> <a href="https://www.w3schools.com/cs/" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/csharp/csharp-original.svg" alt="csharp" width="40" height="40"/> </a> <a href="https://www.docker.com/" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/docker/docker-original-wordmark.svg" alt="docker" width="40" height="40"/> </a> <a href="https://www.photoshop.com/en" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/photoshop/photoshop-line.svg" alt="photoshop" width="40" height="40"/> </a> </p>




## WoWProgress Scraper

This repository now contains `wowprogress_scraper.py`, a Playwright-based tool
that collects the active roster of a World of Warcraft guild from
[wowprogress.com](https://www.wowprogress.com/) and extracts the social media
handles (Battle.net, Discord, etc.) listed on each member profile.

```bash
pip install -r requirements.txt
playwright install chromium
python wowprogress_scraper.py --region eu --realm draenor --guild Method --stealth \
    --output method_roster.json
```

> **Hint:** When running inside a headless environment (like a Linux server)
you may need to prefix the command with `xvfb-run -a` or disable `--headless`
to let Playwright negotiate Cloudflare challenges more reliably.
