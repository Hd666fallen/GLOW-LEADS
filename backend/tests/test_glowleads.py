"""GlowLeads backend API tests."""
import base64
import os
import time
import uuid

import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://glowleads-demo.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"

# Tiny 1x1 PNG
TINY_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAAWgmWQ0AAAAASUVORK5CYII="
)


@pytest.fixture(scope="session")
def session():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="session")
def tech_token(session):
    r = session.post(f"{API}/auth/login", json={"email": "sophie@glowleads.com", "password": "sophie123"})
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["user"]["role"] == "tech"
    return data["token"]


@pytest.fixture(scope="session")
def agency_token(session):
    r = session.post(f"{API}/auth/login", json={"email": "harry@glowleads.com", "password": "agency123"})
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["user"]["role"] == "agency"
    return data["token"]


# ---------- Auth ----------
class TestAuth:
    def test_root(self, session):
        r = session.get(f"{API}/")
        assert r.status_code == 200
        assert "GlowLeads" in r.json()["message"]

    def test_login_tech(self, session):
        r = session.post(f"{API}/auth/login", json={"email": "sophie@glowleads.com", "password": "sophie123"})
        assert r.status_code == 200
        d = r.json()
        assert "token" in d and len(d["token"]) > 10
        assert d["user"]["role"] == "tech"
        assert d["user"]["slug"] == "sophie"
        assert "password_hash" not in d["user"]

    def test_login_agency(self, session):
        r = session.post(f"{API}/auth/login", json={"email": "harry@glowleads.com", "password": "agency123"})
        assert r.status_code == 200
        assert r.json()["user"]["role"] == "agency"

    def test_login_bad(self, session):
        r = session.post(f"{API}/auth/login", json={"email": "sophie@glowleads.com", "password": "WRONG"})
        assert r.status_code == 401

    def test_register_creates_tech(self, session):
        unique = uuid.uuid4().hex[:8]
        payload = {
            "email": f"TEST_{unique}@example.com",
            "password": "testpass123",
            "full_name": f"Test User {unique}",
            "business_name": f"TEST Salon {unique}",
            "city": "Austin, TX",
            "phone": "+15125550000",
        }
        r = session.post(f"{API}/auth/register", json=payload)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["user"]["role"] == "tech"
        assert d["user"]["slug"]  # auto slug
        assert "_id" not in d["user"]


# ---------- Public funnel ----------
class TestPublic:
    def test_styles_list(self, session):
        r = session.get(f"{API}/styles")
        assert r.status_code == 200
        styles = r.json()["styles"]
        assert len(styles) == 60, f"expected 60 styles, got {len(styles)}"
        cats = {s["category"] for s in styles}
        assert len(cats) == 7, f"expected 7 categories, got {len(cats)}"

    def test_public_tech_sophie(self, session):
        r = session.get(f"{API}/public/tech/sophie")
        assert r.status_code == 200
        d = r.json()
        assert d["tech"]["slug"] == "sophie"
        assert "password_hash" not in d["tech"]
        assert len(d["styles"]) == 37, f"expected 37 enabled styles, got {len(d['styles'])}"

    def test_public_tech_404(self, session):
        r = session.get(f"{API}/public/tech/nonexistent_xyz")
        assert r.status_code == 404


# ---------- AI ----------
class TestAI:
    def test_detect_no_500(self, session):
        r = session.post(f"{API}/ai/detect", json={"image_base64": TINY_PNG_B64}, timeout=120)
        assert r.status_code == 200, f"detect must not 500: {r.status_code} {r.text[:200]}"
        d = r.json()
        # Either has detected fields or all None
        assert "detected_style_id" in d
        assert "has_polish" in d

    def test_tryon_no_500(self, session):
        r = session.post(
            f"{API}/ai/try-on",
            json={"image_base64": TINY_PNG_B64, "style_id": "chrome", "tech_slug": "sophie"},
            timeout=180,
        )
        assert r.status_code == 200, f"try-on must not 500: {r.status_code} {r.text[:200]}"
        d = r.json()
        assert "preview" in d and d["preview"]
        assert d["source"] in ("ai", "fallback")
        assert d["style"]["id"] == "chrome"

    def test_tryon_bad_style(self, session):
        r = session.post(
            f"{API}/ai/try-on",
            json={"image_base64": TINY_PNG_B64, "style_id": "nope-xyz", "tech_slug": "sophie"},
        )
        assert r.status_code == 400


# ---------- Lead + Booking ----------
class TestLeadBooking:
    def test_create_lead_and_booking(self, session):
        lead_payload = {
            "tech_slug": "sophie",
            "name": "TEST_Lead",
            "phone": "+15555550100",
            "style_id": "chrome",
            "preview_image": "",
            "detected_style_id": "classic-red",
        }
        r = session.post(f"{API}/leads", json=lead_payload)
        assert r.status_code == 200, r.text
        lead = r.json()
        assert lead["status"] == "not_booked"
        assert lead["style_name"]
        lead_id = lead["id"]

        book_payload = {
            "tech_slug": "sophie",
            "name": "TEST_Lead",
            "phone": "+15555550100",
            "style_id": "chrome",
            "date": "2026-12-01",
            "time": "14:30",
            "lead_id": lead_id,
        }
        r2 = session.post(f"{API}/bookings", json=book_payload)
        assert r2.status_code == 200, r2.text
        d = r2.json()
        assert d["sms_sent"] is True
        assert d["appointment"]["status"] == "confirmed"
        assert d["appointment"]["date"] == "2026-12-01"


# ---------- Tech dashboard ----------
class TestTech:
    def auth(self, token):
        return {"Authorization": f"Bearer {token}"}

    def test_stats(self, session, tech_token):
        r = session.get(f"{API}/tech/me/stats", headers=self.auth(tech_token))
        assert r.status_code == 200
        d = r.json()
        for k in ("leads_today", "appts_this_week", "revenue_this_month", "activity"):
            assert k in d

    def test_appointments_list(self, session, tech_token):
        r = session.get(f"{API}/tech/me/appointments", headers=self.auth(tech_token))
        assert r.status_code == 200
        rows = r.json()["appointments"]
        assert len(rows) >= 7

    def test_leads_list(self, session, tech_token):
        r = session.get(f"{API}/tech/me/leads", headers=self.auth(tech_token))
        assert r.status_code == 200
        d = r.json()
        assert len(d["leads"]) >= 10
        assert "stats" in d

    def test_styles_list(self, session, tech_token):
        r = session.get(f"{API}/tech/me/styles", headers=self.auth(tech_token))
        assert r.status_code == 200
        d = r.json()
        assert len(d["all"]) == 60
        assert len(d["enabled_ids"]) == 37

    def test_update_appt_status(self, session, tech_token):
        r = session.get(f"{API}/tech/me/appointments", headers=self.auth(tech_token))
        appt = r.json()["appointments"][0]
        r2 = session.put(
            f"{API}/tech/me/appointments/{appt['id']}",
            json={"status": "completed"},
            headers=self.auth(tech_token),
        )
        assert r2.status_code == 200
        assert r2.json()["status"] == "completed"

    def test_update_styles(self, session, tech_token):
        new_ids = ["chrome", "matte-gel", "classic-red"]
        r = session.put(
            f"{API}/tech/me/styles",
            json={"enabled_style_ids": new_ids},
            headers=self.auth(tech_token),
        )
        assert r.status_code == 200
        assert set(r.json()["enabled_ids"]) == set(new_ids)
        # restore
        from styles_data import STYLES  # type: ignore  # noqa
        # Just restore to a sensible default — the seed list
        seed_list = [
            "classic-gel", "matte-gel", "chrome", "glazed-donut", "cat-eye", "jelly-glass",
            "holographic", "french-classic", "french-colored", "french-ombre", "french-chrome",
            "ombre-classic", "ombre-sunset", "aura-nails", "watercolor", "marble", "floral-art",
            "geometric", "swirl-art", "dots", "butterfly", "celestial", "rhinestone",
            "pearl-accents", "gold-foil", "glitter-ombre", "nude-milky", "classic-red",
            "baby-pink", "hot-pink", "lavender", "black", "coral", "acrylic-full",
            "dip-powder", "polygel", "extensions",
        ]
        session.put(
            f"{API}/tech/me/styles",
            json={"enabled_style_ids": seed_list},
            headers=self.auth(tech_token),
        )

    def test_followup(self, session, tech_token):
        r = session.get(f"{API}/tech/me/leads", headers=self.auth(tech_token))
        leads = r.json()["leads"]
        assert leads
        lead = leads[0]
        before = lead.get("follow_ups_sent", 0)
        r2 = session.post(
            f"{API}/tech/me/leads/{lead['id']}/follow-up", headers=self.auth(tech_token)
        )
        assert r2.status_code == 200
        assert r2.json()["sent"] is True
        # verify increment
        r3 = session.get(f"{API}/tech/me/leads", headers=self.auth(tech_token))
        updated = next(l for l in r3.json()["leads"] if l["id"] == lead["id"])
        assert updated["follow_ups_sent"] == before + 1

    def test_tech_endpoint_rejects_agency(self, session, agency_token):
        r = session.get(f"{API}/tech/me/stats", headers=self.auth(agency_token))
        assert r.status_code == 403


# ---------- Agency ----------
class TestAgency:
    def auth(self, token):
        return {"Authorization": f"Bearer {token}"}

    def test_overview(self, session, agency_token):
        r = session.get(f"{API}/agency/overview", headers=self.auth(agency_token))
        assert r.status_code == 200
        d = r.json()
        for k in ("kpis", "at_risk", "activity"):
            assert k in d
        assert d["kpis"]["active_clients"] >= 3

    def test_clients(self, session, agency_token):
        r = session.get(f"{API}/agency/clients", headers=self.auth(agency_token))
        assert r.status_code == 200
        clients = r.json()["clients"]
        assert len(clients) >= 3

    def test_analytics(self, session, agency_token):
        r = session.get(f"{API}/agency/analytics", headers=self.auth(agency_token))
        assert r.status_code == 200
        d = r.json()
        for k in ("leads_weekly", "conversion", "popular_styles", "heatmap", "geo"):
            assert k in d

    def test_style_intel(self, session, agency_token):
        r = session.get(f"{API}/agency/style-intel", headers=self.auth(agency_token))
        assert r.status_code == 200
        d = r.json()
        for k in ("most_tried_not_booked", "most_detected", "market_gaps", "trending"):
            assert k in d

    def test_billing(self, session, agency_token):
        r = session.get(f"{API}/agency/billing", headers=self.auth(agency_token))
        assert r.status_code == 200
        d = r.json()
        assert "subscriptions" in d and "mrr" in d and "growth" in d

    def test_agency_endpoint_rejects_tech(self, session, tech_token):
        r = session.get(f"{API}/agency/overview", headers=self.auth(tech_token))
        assert r.status_code == 403

    def test_missing_token(self, session):
        r = session.get(f"{API}/agency/overview")
        assert r.status_code == 401
