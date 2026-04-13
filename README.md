# dashboard.charisrv.fyi

Personal homepage dashboard built with Python (Flask) and HTMX.
Self-hosted on Proxmox LXC, served via Cloudflare Tunnel.

## Widgets

| Widget | Source | Auth |
|---|---|---|
| Bitcoin / USD | CoinGecko API | None |
| BRL/USD · BRL/GBP | frankfurter.app | None |
| Hacker News Top 5 | HN Firebase API | None |
| Weather — Fortaleza / Maracanaú | Open-Meteo | None |
| GitHub activity | GitHub Events API | None |
| Football (Flamengo · Man Utd · BVB) | Free API Live Football Data | RapidAPI key |
| Proxmox connectivity | Internal HTTP check | — |

## Stack

- **Backend**: Python 3 / Flask 3
- **Frontend**: Jinja2 + HTMX (no JavaScript framework)
- **Cache**: cachetools (TTL per widget)
- **Infra**: Proxmox LXC (Debian 12) + systemd + Cloudflare Tunnel

## Setup

```bash
git clone https://github.com/renaldofreire/dashboard.git
cd dashboard
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Set environment variable:

```bash
export FOOTBALL_API_KEY=your_key_here
```

Run:

```bash
python run.py
```

## Deploy (LXC)

```bash
cd /opt/dashboard && git pull && systemctl restart dashboard
```

## Progress

- [x] Project structure
- [x] Bitcoin / USD widget
- [x] BRL exchange rates widget
- [x] Hacker News widget
- [ ] Weather widget (Fortaleza / Maracanaú toggle)
- [ ] GitHub activity widget
- [ ] Football widget (Flamengo · Man Utd · BVB)
- [ ] Proxmox connectivity check
