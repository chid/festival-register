# Festival Calendar — Improvement Roadmap & Execution Plan

A structured roadmap for subsequent improvements to the **Festival Calendar** ([https://chid.github.io/festival-register/](https://chid.github.io/festival-register/)).

---

## 🏁 Completed Milestones

- [x] **Core macOS Sequoia iCal Web App**: 4 views (Agenda/List, Month Grid, 12-Month Year Overview, Tabular Data Grid), 89 verified festivals in NSW/VIC/ACT, regional circuit filters, price tier filters, genre chips, and RFC 5545 single-event export.
- [x] **Mobile Responsive Upgrade (iOS HIG 390px)**: Pinned frosted-glass bottom tab bar (`Agenda`, `Month`, `Year`, `Filters`, `.ics`), off-canvas slide-out filter drawer with backdrop blur, mobile card stacking, and Apple Calendar-style month cell micro-dots with day drilldowns.
- [x] **Option A — Live `webcal://` Feeds & 1-Click Subscriptions**:
  - Python feed generator (`site/build_feeds.py`) producing 5 live RFC 5545 feeds:
    - `festivals-all.ics` (89 events)
    - `festivals-sydney.ics` (52 events)
    - `festivals-melbourne.ics` (26 events)
    - `festivals-canberra.ics` (11 events)
    - `festivals-free.ics` (47 events)
  - Feeds configured with `REFRESH-INTERVAL;VALUE=DURATION:P1D` and `TRANSP:TRANSPARENT`.
  - Native 1-click **Apple Calendar** (`webcal://`), **Google Calendar** (render CID), and clipboard copy sheet.
- [x] **Option B — Native Dark Mode & Progressive Web App (PWA)**:
  - 3-way appearance toggle (`Auto` / `Dark` / `Light`) with `localStorage` persistence and `prefers-color-scheme` synchronization.
  - Apple Dark Appearance palette (`#1C1C1E` canvas, `#242426` cards, `#2C2C2E` containers, `#38383A` hairlines, and high-contrast electric city accents).
  - Web App Manifest (`manifest.json`) with `black-translucent` status bar for standalone iOS Home Screen installation.
  - Custom Apple Calendar-style icons (`make_icons.py`: `apple-touch-icon.png`, `icon-192.png`, `icon-512.png`, `favicon.svg`).
  - Offline Service Worker (`sw.js`) pre-caching app shell, data JSON, and calendar feeds.

---

## 🚀 Subsequent Improvements (Backlog & Execution Specifications)

### Phase 1: Core Calendar & Visualization Enhancements

#### 1. Multi-Day Horizontal Event Spanning on Month Grid (Option C)
- **Goal**: Full visual parity with desktop Apple Calendar and Google Calendar for multi-day festivals.
- **Problem**: Currently, a multi-day festival (e.g. *Vivid Sydney*, 23 May – 15 Jun) appears as individual repeated badge boxes in every single day cell.
- **Specification**:
  - Group month days into weekly rows (7 columns: Mon–Sun).
  - For each week row, calculate festival segments that run across that week.
  - Render a continuous horizontal banner block spanning from `start_col` to `end_col`.
  - Stack up to 3 parallel multi-day bars vertically; if more than 3 festivals overlap, render a `+N more` link that opens a popover listing all festivals running on that date.
  - Single-day festivals appear as smaller badges or colored dot indicators beneath spanning bars.

#### 2. "Happening Now / Next 5 Up" Highlight Strip (Option D)
- **Goal**: Immediate answers to *"What's on right now or this weekend?"*
- **Specification**:
  - Add a collapsible ribbon above the main calendar canvas.
  - Calculate the 5 nearest upcoming/active festivals relative to today's date (`new Date()`).
  - Render horizontal cards showing:
    - Status badge: *"Happening Now"*, *"Starts Tomorrow"*, *"This Weekend"*, or *"In X days"*.
    - Festival name, city pill, and date range.
    - Quick "Official Website" and "Add to .ics" buttons.
  - Allows users scanning on mobile to find immediate weekend plans without navigating month grids.

#### 3. "Color By" Dimension Switcher
- **Goal**: Allow users to visualize festivals by different dimensions.
- **Specification**:
  - Add a switch in the sidebar: **Color by: [ City | Price Tier | Category ]**.
  - **City mode (default)**: Sydney Blue (`#007AFF`), Melbourne Purple (`#AF52DE`), Canberra Green (`#34C759`).
  - **Price Tier mode**:
    - Free ($0): Emerald Green (`#34C759`)
    - Low (<$30): Teal / Cyan (`#30B0C7`)
    - Mid ($30–$100): Royal Blue (`#007AFF`)
    - Premium (>$100): Vivid Amber (`#FF9500`)
  - **Category mode**: Music (Rose), Film (Violet), Comedy (Orange), Food (Yellow), Arts (Indigo), Cultural (Cyan), Sport (Green).

---

### Phase 2: Micro-Planning Views & Native Modals

#### 4. Dedicated Week & Day Views
- **Goal**: High-resolution hourly and multi-day planning for festival weekends.
- **Specification**:
  - Add **Week** and **Day** buttons to the top toolbar segmented switch and mobile tab bar.
  - **Week View**:
    - 7-column grid showing current week (Mon–Sun).
    - Dedicated "All-Day" header row displaying continuous festival banners.
    - Hourly time grid below (9:00 AM to 11:00 PM) displaying morning, afternoon, and evening festival highlights.
  - **Day View**: Single day inspection showing active festival stages, venues, and typical opening hours.

#### 5. Interactive Regional Map View
- **Goal**: Spatial discovery of festival locations across Greater Sydney, Melbourne, and Canberra.
- **Specification**:
  - Integrate a lightweight Leaflet or MapLibre instance with Apple Maps-inspired vector styling.
  - Plot venues with color-coded markers (Sydney CBD, Parramatta, Western Sydney, Southbank Melbourne, Lake Burley Griffin).
  - Clicking a marker opens the festival's iCal inspection popover.
  - Filter markers dynamically based on the active sidebar filters (city, tier, date range).

#### 6. In-App "Submit a Festival" Modal
- **Goal**: Enable community contributions without requiring users to navigate to GitHub Issues.
- **Specification**:
  - Replace the external GitHub link with a modal dialog containing:
    - Festival Name (text input)
    - City (Sydney, Melbourne, Canberra, or Other)
    - Category & Price Tier (select dropdowns)
    - Typical Month & Confirmed Dates (date pickers)
    - Venue & Official URL
    - Past Editions reference URL
  - Outputs:
    - Direct pre-filled GitHub Issue link via URL query parameters for GitHub users.
    - "Copy JSON Entry" button for direct pull request submission.
    - `mailto:` fallback for non-technical users.

---

### Phase 3: Automation & Regional Expansion

#### 7. Automated Date & URL Freshness Workflow (GitHub Actions)
- **Goal**: Keep all 89+ festival links and upcoming edition dates fresh without manual auditing.
- **Specification**:
  - Create `.github/workflows/verify-festivals.yml`:
    - Scheduled weekly cron (`0 2 * * 1`).
    - HTTP HEAD/GET health check for all official websites (`url`) and past edition sources.
    - Flags broken links (HTTP 404, 500, SSL expirations) in `link_status.json`.
    - Automatically regenerates `.ics` feeds (`python3 site/build_feeds.py`).
    - Commits and pushes any date updates to `main`.

#### 8. Circuit Expansion: Brisbane (QLD) & Adelaide (SA)
- **Goal**: Expand from Southeast Australia to cover the complete Australian cultural festival circuit.
- **Target Additions**:
  - **Brisbane & Gold Coast**: Brisbane Festival, Valley Fiesta, BLEACH* Festival, Woodford Folk Festival, Bluesfest Byron Bay.
  - **Adelaide**: Adelaide Fringe (world's 2nd largest fringe festival), Adelaide Festival, WOMADelaide, OzAsia Festival, Tasting Australia.
  - Update dataset schema to support QLD and SA regional tags and calendar feeds (`festivals-brisbane.ics`, `festivals-adelaide.ics`).

---

## 🛠️ Implementation Priority Matrix

| Feature | Effort | Impact | Recommended Order |
| :--- | :---: | :---: | :---: |
| **Option C: Multi-day Spanning Bars** | Medium | High | **1st** |
| **Option D: "Happening Now" Strip** | Low | High | **2nd** |
| **"Color By" Dimension Switcher** | Low | Medium | **3rd** |
| **Week View & Day View** | Medium | Medium | **4th** |
| **In-App Submit Festival Modal** | Low | Medium | **5th** |
| **Automated GitHub Action Cron** | Medium | High | **6th** |
| **Interactive Regional Map View** | High | Medium | **7th** |
| **Brisbane & Adelaide Expansion** | High | High | **8th** |

---

*Last Updated: 2026-10-13 — Sydney, Australia*
