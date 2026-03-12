# PokerGuys 🃏

Texas Hold'em poker session tracker & finance manager.

[![Deploy with Vercel](https://vercel.com/button)](https://poker-guys.vercel.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

### Core Features
- **Session Recording**: Track buy-ins, final stacks, and number of hands for each player
- **Balance Validation**: Auto-check if table is balanced (net zero sum)
- **Player Stats**: Lifetime P&L tracking per player with filtering
- **Multi-session History**: View and manage past sessions

### Community (Cloud Sync)
- **Create/Join Community**: Start a new poker group or join existing one with 6-char code
- **Shared Data**: All community members see the same sessions
- **Player Leaderboard**: See who's winning the most across all sessions

### UI/UX
- **Binance-inspired Theme**: Professional dark/light mode
- **Phone View Mode**: Optimized layout for mobile
- **Responsive Design**: Works on desktop and mobile

### Statistics Dashboard
- Total sessions, buy-ins, and net P&L
- Longest winning streak per player
- Highest loss in single session
- Average P&L per session
- Cumulative P&L chart over time
- Player performance comparison

## Live Demo

🌐 **Production**: [https://poker-guys.vercel.app](https://poker-guys.vercel.app)

> **Note**: Vercel has limited support for Streamlit apps. For best experience, run locally.

## Quick Start (Local)

```bash
# Clone the repo
git clone https://github.com/OceanCD/PokerGuys.git
cd PokerGuys

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run main.py
```

## Tech Stack

- **Frontend**: Streamlit (Python)
- **Database**: SQLite (local) + Supabase (community sync)
- **Charts**: Plotly
- **Deployment**: Vercel

## Community

A **Community** is your poker group — friends, regular players, or club members who play together.

### How to Use:
1. **Create a Community**: One person creates a community and gets a 6-character code
2. **Share the Code**: Share the code with your poker friends
3. **Join**: Others enter the code to join and see shared session data
4. **Track Together**: All members can record and view sessions

### Community Code (Demo)
- Code: `DHILLL`
- Join to see sample sessions!

## Project Structure

```
PokerGuys/
├── main.py              # Main Streamlit app
├── requirements.txt     # Python dependencies
├── pokerguys.db        # Local SQLite database
├── supabase/           # Supabase schema for community
└── README.md          # This file
```

## Roadmap

- [ ] PDF export (Premium)
- [ ] Import from poker sites
- [ ] ML win probability predictor
- [ ] iOS/Android mobile app

## License

MIT License - feel free to use and modify!
