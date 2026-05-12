# GlowLeads — Product Requirements Document

## Original Problem Statement
Full-stack AI-powered lead generation SaaS platform for nail technicians with 3 separate interfaces:
1. **Customer Funnel** — Public 7-step AI try-on booking journey (hero → upload → AI detection → style select → AI try-on → booking → confirmation).
2. **Nail Tech Dashboard** — Mobile-first Instagram-simple dashboard (Home / Appointments / Leads / Settings).
3. **Agency Dashboard** — Desktop dark SaaS admin (Overview / Clients / Analytics / Style Intelligence / Billing).

## Architecture
- **Backend:** FastAPI (single `server.py`) + MongoDB (Motor) + JWT auth (bcrypt)
- **Frontend:** React 19 + Tailwind + Shadcn UI + Recharts + React Router
- **AI:** Gemini Nano Banana via `emergentintegrations` (EMERGENT_LLM_KEY) — real image editing & analysis, with graceful fallback to stock image on failure
- **Mocked:** Twilio SMS (logged to `sms_logs`), Stripe, Google Calendar

## User Personas
- **Customer** — potential nail client trying on styles before booking
- **Nail Tech** — individual nail artist (Sophie / Bella / Jade) managing bookings
- **Agency Owner** — Harry, running GlowLeads as a multi-tenant SaaS

## Core Requirements (Static)
- 60-style master library across 7 categories (Finishes, French, Ombre, Nail Art, Embellishments, Colors, Specialty)
- AI current-style detection + AI try-on on user's uploaded hand photo
- JWT auth with email/password; role-based (tech vs agency)
- Swipe-style appointment status updates
- Auto-lead capture when user reaches try-on step but doesn't book

## Iteration 3 — Funnel rebuilt as Upload → Shape → Design → Colour → AI → Book
- New `/app/backend/funnel_data.py`: 6 SHAPES (with detected-shape highlighting), 7 DESIGN_GROUPS (50 designs total with badges Most Popular/Trending/Classic/Fan Fave), 9 COLOR_GROUPS (200 colors with hex + name + brand)
- New endpoints: `GET /api/funnel/config`, `POST /api/ai/detect-shape`
- AI try-on now accepts `design_id` (preferred) or `style_id` (legacy) + `shape_id` + `color_hex`/`color_name` — all optional except design/style
- Bookings + leads accept design_id + shape_id + color details (price taken from design's price_range)
- Customer funnel completely rewritten: persistent hand photo across session, bottom-sheet "change shape/design/colour" flows with confirm dialogs, instant color preview on hand photo
- Step 4 colour picker has 9 horizontal-scroll color rows (one per family) with sticky bottom bar showing selected name + brand
- Booking form pre-filled with chosen shape + design + colour as a chip
- Fixed booking 500 when only design_id provided (was using `style['name']` — now uses computed `label`)

## What's Been Implemented (2026-02)
### Backend
- JWT login/register (`/api/auth/*`) with `verifyAuth`-safe token check
- Public funnel: `/api/public/tech/{slug}`, `/api/styles`, `/api/ai/detect`, `/api/ai/try-on`, `/api/leads`, `/api/bookings`
- **Bookings now trigger 3 automation SMS logs** (instant confirmation + 24h reminder + 1h reminder) deterministically
- Tech dashboard: profile, styles, appointments, leads (with hot/warm/cold temp), stats (activity feed w/ automation icons), follow-up, automations get/put, winback section
- Agency dashboard: overview, clients, analytics, style-intel (drop-off %, walking_in_with, market_gaps), billing
- Seeds 1 agency + 5 techs (Sophie/Bella/Jade/Luxe MTL/Nailed It YYC — all Canadian) + 30 leads + 10 appts + pre-computed automation SMS logs
- Startup purges any TEST_ data
- **Iteration 4 (Feb 2026):** Replaced 3 broken Unsplash IDs (squoval shape, _MATTE, _GLITTER) with verified-200 URLs so every shape/design card renders — no blank cards.
- **Iteration 5 (Feb 2026):**
  - `POST /api/tech/me/style-photo` (multipart) + `DELETE /api/tech/me/style-photo/{id}` — tech-uploaded style photos saved to `/app/backend/uploads/{slug}/{id}.{ext}` and served via mounted `/api/uploads` static route. URLs persisted on `users.style_photos`.
  - `GET /api/funnel/config?tech_slug=X` — overrides design.image with tech-uploaded photos (matched by design_id OR case-insensitive style name) and tags `custom_by_tech: true`.
  - `LeadIn` accepts `finger_customizations` for per-finger picks.

### Frontend
- Landing page with pulse-cta animation (box-shadow only, no layout jitter) + amber scarcity line
- Full 7-step customer funnel with StyleImage fallback helper → 60 unique style images
- Tech dashboard with bottom nav + loading states on Appts/Leads
- Settings: 5 tabs (Page / Styles / Hours / **Automations** / Account)
- Styles tab: search + 8 category filters + price field + photo upload button + 60 toggles
- **Automation Center**: 7 togglable SMS automations with weekly stats card
- Leads tab: Hot 🔥 / Warm 💛 / Cold 🧊 badges + separate "Win-back" section
- Agency dashboard: sidebar + verifyAuth on mount (direct-URL nav works); Style Intel with drop-off %, competitor walking-in % bars, market gaps with requested counts
- **Iteration 4 (Feb 2026):** Shape & Design grids enforced to strict compact layout — `grid-cols-2 md:grid-cols-3 gap-3`, fixed card height `h-[200px]`, image occupies `h-[65%]`, text section `h-[35%]` with truncated title + price/description. No blank cards, Instagram-style nail menu.
- **Iteration 5 (Feb 2026) — separation of concerns into 3 distinct pages:**
  - **Page 1 — Landing (`/`):** New 3-line headline "She saw it. / She tried it on. / *She booked it. 💅*" (last line italic pink Playfair). New subheadline. CTA renamed to "See a live demo →". Demo credentials removed from public view. Added **pricing section** (Starter $49 / Pro $99 / Agency $299) with feature lists. Replaced 3 generic feature cards with **AI Try-On / Smart Automations / Lead Intelligence**.
  - **Page 2 — Customer funnel (`/try/:slug`):** Header now shows `tech.business_name ✨` (e.g. "Glow by Sophie ✨"). Zero GlowLeads pricing/demo-login references inside the funnel. Funnel is **now 6 numbered steps** (Upload → Shape → Design → Colour → **Per-finger Customizer (NEW)** → Result), plus the booking sheet.
  - **Page 3 — Tech dashboard (`/tech` Home tab):** Prominent gradient pink-bordered **funnel-link card** moved directly under the stats row, containing the full URL, copy button, **QR code** (150×150 from api.qrserver.com) and a "Preview my funnel" button that opens `/try/<slug>` in a new tab.
- **Iteration 5 — Styles tab photo upload:** Each style row now has a working "Upload photo" file picker → POST multipart to `/api/tech/me/style-photo`. Thumbnail updates immediately, a red **X** button reverts to the default stock photo, and changes persist after refresh (fetched from `/tech/me/styles` with `style_photos`). Uploaded photos automatically appear in the customer funnel design cards (matched by id or name) with a small pink **"Her work ✨"** badge.
- **Iteration 5 — Per-finger customizer (Step 5):** New step initialized with all 10 fingers (`l-thumb`…`r-pinky`) matching the user's global shape/design/colour. Left/Right hand toggle, 48×64 finger preview row (rounded top, pink border + gold glow when active with `translateY(-5px)`), "Apply to all fingers" button, three-section editor (shape 3-col grid, design 3-col grid with category tabs, full color palette), 34×46 summary strip at bottom for both hands, sticky **"Generate my look ✨"** CTA + "Skip — same look for all" link. State updates use immutable spread per finger; other fingers are never reset.

## Bug fixes in this iteration
- Fixed POST /api/bookings to actually persist all 3 SMS types (was only inserting booking_confirmation)
- Fixed 60-style image variety: new StyleImage helper + curated unique Unsplash URLs + onError fallback
- Fixed missing StyleImage import in CustomerFunnel.jsx (caused blank Step 4)
- Fixed agency direct-URL session persistence via verifyAuth
- Fixed pulse animation causing unclickable CTA (transform:scale → box-shadow-only pulse)
- Replaced all TEST_ seed data with realistic Canadian names + Mia Anderson

## Test Credentials
- **Agency:** harry@glowleads.com / agency123
- **Tech (demo):** sophie@glowleads.com / sophie123 (funnel: `/try/sophie`)
- **Tech:** bella@glowleads.com / bella123 · jade@glowleads.com / jade123

## Prioritized Backlog
### P1 — polish & real integrations
- Real Twilio SMS integration (confirm, 24h + 1h reminders, no-show rebook)
- Stripe billing (real subscriptions + failed-payment retry)
- Google Calendar connect toggle → real OAuth
- Onboarding wizard (agency → "Add new client" flow to auto-generate page + send welcome)
- Per-tech portfolio photo uploads (object storage) so they can replace stock images per style

### P2 — advanced features
- Geographic heatmap (Mapbox/Leaflet) on Analytics page
- "Add Your Own Style" custom style creator
- Share-to-Instagram story generator with watermark
- Mobile web push notifications for new leads
- Deposit collection at booking via Stripe

### P3 — scale & ops
- Split server.py into routers (auth, public, ai, tech, agency)
- Aggregate-pipeline refactor for Analytics leads_weekly
- Refresh tokens + shorter JWT expiry
- Admin audit log
