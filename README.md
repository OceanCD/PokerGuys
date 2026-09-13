# PokerGuys

PokerGuys is a bilingual poker session ledger for a private group of friends. It records buy-ins and final stacks, checks that the table balances to zero, saves session history, and turns the shared ledger into player and group statistics.

## Current product

- **Live session:** add players, track multiple buy-ins, enter final stacks, and validate the table balance.
- **Reliable on mobile:** an in-progress table is restored after a refresh for up to 24 hours.
- **History:** review and edit completed sessions, with amounts viewable in chips or HKD.
- **Stats:** cumulative and monthly P&L, player records, streaks, ROI, table-size impact, and head-to-head results in either unit.
- **Groups:** join a shared Supabase community using a six-character code.
- **Bilingual:** English and Traditional Chinese UI.
- **iPhone-ready:** installable PWA plus a Capacitor configuration for a native iOS build.

PokerGuys uses the group conversion rate **5 chips = HK$1**. Historical sessions without unit metadata are treated as chip-denominated; newer HKD-denominated sessions carry their unit and conversion rate inside the session player data.

The production web app is deployed at [poker-guys.vercel.app](https://poker-guys.vercel.app).

## Run locally

The current production client is the static `index.html` app. No Python packages are needed to work on the UI:

```bash
python3 -m http.server 4173
```

Then open `http://localhost:4173`.

The older Streamlit prototype remains in `main.py` as a reference implementation, but it is not the primary web client.

## Build the iOS web bundle

```bash
npm install
npm run build
```

The command copies the shared web client into `dist/`, which Capacitor uses for the iOS app. See [IOS.md](./IOS.md) for Home Screen, Xcode, TestFlight, and App Store instructions.

## Project structure

```text
PokerGuys/
├── index.html                 # Web app markup, state, and calculations
├── styles.css                # Responsive application UI
├── manifest.webmanifest      # Home Screen / PWA metadata
├── sw.js                     # Offline application shell
├── assets/                   # Shared icons
├── capacitor.config.json     # Native iOS wrapper configuration
├── scripts/build-web.mjs     # Builds Capacitor's dist directory
├── supabase/                 # Database schemas and legacy client helper
├── main.py                   # Original Streamlit prototype
└── IOS.md                    # iPhone and App Store workflow
```

## Data and security note

The current `schema-simple.sql` intentionally gives public clients broad table access and treats the community code as a password. That is acceptable only for an early prototype with non-sensitive test data. Before a public or App Store release, use Supabase Auth and membership-aware Row Level Security so one group cannot enumerate or modify another group's data.

## License

MIT
