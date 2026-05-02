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

## What's Been Implemented (2026-02)
### Backend
- JWT login/register (`/api/auth/*`) with `verifyAuth`-safe token check
- Public funnel: `/api/public/tech/{slug}`, `/api/styles`, `/api/ai/detect`, `/api/ai/try-on`, `/api/leads`, `/api/bookings`
- **Bookings now trigger 3 automation SMS logs** (instant confirmation + 24h reminder + 1h reminder) deterministically
- Tech dashboard: profile, styles, appointments, leads (with hot/warm/cold temp), stats (activity feed w/ automation icons), follow-up, automations get/put, winback section
- Agency dashboard: overview, clients, analytics, style-intel (drop-off %, walking_in_with, market_gaps), billing
- Seeds 1 agency + 5 techs (Sophie/Bella/Jade/Luxe MTL/Nailed It YYC — all Canadian) + 30 leads + 10 appts + pre-computed automation SMS logs
- Startup purges any TEST_ data

### Frontend
- Landing page with pulse-cta animation (box-shadow only, no layout jitter) + amber scarcity line
- Full 7-step customer funnel with StyleImage fallback helper → 60 unique style images
- Tech dashboard with bottom nav + loading states on Appts/Leads
- Settings: 5 tabs (Page / Styles / Hours / **Automations** / Account)
- Styles tab: search + 8 category filters + price field + photo upload button + 60 toggles
- **Automation Center**: 7 togglable SMS automations with weekly stats card
- Leads tab: Hot 🔥 / Warm 💛 / Cold 🧊 badges + separate "Win-back" section
- Agency dashboard: sidebar + verifyAuth on mount (direct-URL nav works); Style Intel with drop-off %, competitor walking-in % bars, market gaps with requested counts

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
