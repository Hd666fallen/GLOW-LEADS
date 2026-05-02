"""GlowLeads iteration 2 tests — bug fixes + automation features."""
import os
import time
import uuid

import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL").rstrip("/")
API = f"{BASE_URL}/api"


@pytest.fixture(scope="session")
def session():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="session")
def tech_token(session):
    r = session.post(f"{API}/auth/login", json={"email": "sophie@glowleads.com", "password": "sophie123"})
    assert r.status_code == 200, r.text
    return r.json()["token"]


@pytest.fixture(scope="session")
def agency_token(session):
    r = session.post(f"{API}/auth/login", json={"email": "harry@glowleads.com", "password": "agency123"})
    assert r.status_code == 200, r.text
    return r.json()["token"]


def auth_h(t):
    return {"Authorization": f"Bearer {t}"}


# ---------- BUG FIX 3: No TEST_ data leftover; Mia Anderson present ----------
class TestNoTestData:
    def test_no_test_lead_in_leads(self, session, tech_token):
        r = session.get(f"{API}/tech/me/leads", headers=auth_h(tech_token))
        assert r.status_code == 200
        leads = r.json()["leads"]
        bad = [l for l in leads if l.get("name", "").startswith("TEST_")]
        assert not bad, f"Found TEST_ leads: {[l['name'] for l in bad]}"

    def test_no_test_in_appointments(self, session, tech_token):
        r = session.get(f"{API}/tech/me/appointments", headers=auth_h(tech_token))
        assert r.status_code == 200
        rows = r.json()["appointments"]
        bad = [a for a in rows if a.get("client_name", "").startswith("TEST_")]
        assert not bad, f"Found TEST_ appointments: {[a['client_name'] for a in bad]}"

    def test_mia_anderson_present(self, session, tech_token):
        r = session.get(f"{API}/tech/me/appointments", headers=auth_h(tech_token))
        appts = r.json()["appointments"]
        r2 = session.get(f"{API}/tech/me/leads", headers=auth_h(tech_token))
        leads = r2.json()["leads"]
        names = {a.get("client_name", "") for a in appts} | {l.get("name", "") for l in leads}
        assert "Mia Anderson" in names, f"Mia Anderson not found. Names: {sorted(names)[:20]}"


# ---------- DATA: Canadian cities ----------
class TestCanadianCities:
    def test_sophie_calgary(self, session):
        r = session.get(f"{API}/public/tech/sophie")
        assert r.status_code == 200
        assert r.json()["tech"]["city"] == "Calgary, AB"

    def test_agency_clients_canadian(self, session, agency_token):
        r = session.get(f"{API}/agency/clients", headers=auth_h(agency_token))
        assert r.status_code == 200
        clients = r.json()["clients"]
        assert len(clients) >= 5, f"expected 5 techs, got {len(clients)}"
        # Check Bella in Toronto, Jade in Vancouver
        by_slug = {c.get("slug") or c.get("business_slug") or c.get("name", "").lower(): c for c in clients}
        cities = [c.get("city", "") for c in clients]
        assert any("Toronto" in c for c in cities), f"No Toronto tech in {cities}"
        assert any("Vancouver" in c for c in cities), f"No Vancouver tech in {cities}"
        assert any("Calgary" in c for c in cities), f"No Calgary tech in {cities}"
        # All Canadian provinces (AB / BC / ON / QC / etc)
        ca_indicators = ("AB", "BC", "ON", "QC", "MB", "SK", "NS", "NB")
        for c in cities:
            assert any(ind in c for ind in ca_indicators), f"Non-Canadian city: {c}"


# ---------- AUTOMATION: GET/PUT /tech/me/automations ----------
class TestAutomations:
    REQUIRED_KEYS = {
        "instant_booking", "reminder_24h", "reminder_1h",
        "review_request", "noshow_recovery", "lead_sequence", "winback",
    }

    def test_get_automations(self, session, tech_token):
        r = session.get(f"{API}/tech/me/automations", headers=auth_h(tech_token))
        assert r.status_code == 200, r.text
        d = r.json()
        assert "settings" in d, d
        for k in self.REQUIRED_KEYS:
            assert k in d["settings"], f"missing {k}"
            assert isinstance(d["settings"][k], bool)
        assert "stats" in d
        for k in ("sms_this_week", "followups_this_week", "reviews_this_week"):
            assert k in d["stats"]
            assert isinstance(d["stats"][k], int)

    def test_put_automations_persists(self, session, tech_token):
        # GET current
        r = session.get(f"{API}/tech/me/automations", headers=auth_h(tech_token))
        original = r.json()["settings"]
        # toggle review_request
        new_val = not original["review_request"]
        new_settings = dict(original)
        new_settings["review_request"] = new_val
        r2 = session.put(
            f"{API}/tech/me/automations",
            json=new_settings,
            headers=auth_h(tech_token),
        )
        assert r2.status_code == 200, r2.text
        # GET again to verify persisted
        r3 = session.get(f"{API}/tech/me/automations", headers=auth_h(tech_token))
        assert r3.json()["settings"]["review_request"] == new_val
        # restore
        session.put(f"{API}/tech/me/automations", json=original, headers=auth_h(tech_token))


# ---------- AUTOMATION: POST /bookings creates 3 sms logs ----------
class TestBookingSmsLogs:
    def test_booking_creates_multiple_sms(self, session, tech_token):
        # Use a non TEST_ name to remain after seed purges, but with unique phone to avoid collision
        unique = uuid.uuid4().hex[:6]
        # Create lead first
        lead = session.post(f"{API}/leads", json={
            "tech_slug": "sophie",
            "name": f"Auto Sms {unique}",
            "phone": f"+1555550{unique[:4]}",
            "style_id": "chrome",
        }).json()
        # Book
        r = session.post(f"{API}/bookings", json={
            "tech_slug": "sophie",
            "name": f"Auto Sms {unique}",
            "phone": f"+1555550{unique[:4]}",
            "style_id": "chrome",
            "date": "2026-12-15",
            "time": "11:00",
            "lead_id": lead["id"],
        })
        assert r.status_code == 200, r.text
        appt = r.json()["appointment"]
        # Wait briefly for any async tasks
        time.sleep(0.5)
        # Check sms logs for that appt
        r2 = session.get(
            f"{API}/tech/me/appointments/{appt['id']}/sms",
            headers=auth_h(tech_token),
        )
        assert r2.status_code == 200, r2.text
        sms = r2.json()["sms"]
        types = {s.get("type") for s in sms}
        assert len(sms) >= 3, f"expected >=3 sms logs, got {len(sms)}: types={types}"
        for required in ("booking_confirmation", "reminder_24h", "reminder_1h"):
            assert required in types, f"missing {required} in {types}"
        # Cleanup: delete appt + lead so we don't leave stale future-date data
        # (server has no delete endpoints; leave it — non TEST prefix)


# ---------- AUTOMATION: stats activity feed icons + types ----------
class TestActivityFeed:
    def test_activity_has_icons_and_mixed_types(self, session, tech_token):
        r = session.get(f"{API}/tech/me/stats", headers=auth_h(tech_token))
        assert r.status_code == 200
        d = r.json()
        feed = d.get("activity", [])
        assert len(feed) > 0
        for item in feed:
            assert "icon" in item, f"missing icon: {item}"
            assert "text" in item, f"missing text: {item}"
            assert "when" in item, f"missing when: {item}"
            assert item["icon"], "icon should be non-empty"
        # mixed types (booking + automation types)
        types = {item.get("type") for item in feed}
        assert len(types) >= 2, f"expected >=2 distinct types, got {types}"


# ---------- AUTOMATION: leads have temperature + winback ----------
class TestLeadTemperature:
    def test_leads_have_temperature(self, session, tech_token):
        r = session.get(f"{API}/tech/me/leads", headers=auth_h(tech_token))
        assert r.status_code == 200
        d = r.json()
        leads = d["leads"]
        assert len(leads) > 0
        valid = {"hot", "warm", "cold"}
        for l in leads:
            assert l.get("temperature") in valid, f"bad temperature on {l.get('name')}: {l.get('temperature')}"
        # Should distribute across at least 2 temperatures
        temps = {l["temperature"] for l in leads}
        assert len(temps) >= 2, f"all leads same temperature: {temps}"

    def test_winback_array_present(self, session, tech_token):
        r = session.get(f"{API}/tech/me/leads", headers=auth_h(tech_token))
        d = r.json()
        assert "winback" in d, d.keys()
        assert isinstance(d["winback"], list)


# ---------- AUTH session persistence (BUG FIX 1) — verify token endpoint ----------
class TestAuthSession:
    def test_verify_token_for_agency(self, session, agency_token):
        # Most apps have a /api/auth/me or similar — check what server has
        for path in ("/auth/me", "/me"):
            r = session.get(f"{API}{path}", headers=auth_h(agency_token))
            if r.status_code == 200:
                return
        # If neither, ensure agency endpoint accepts the token (used by frontend on remount)
        r = session.get(f"{API}/agency/overview", headers=auth_h(agency_token))
        assert r.status_code == 200

    def test_verify_token_for_tech(self, session, tech_token):
        for path in ("/auth/me", "/me"):
            r = session.get(f"{API}{path}", headers=auth_h(tech_token))
            if r.status_code == 200:
                return
        r = session.get(f"{API}/tech/me/stats", headers=auth_h(tech_token))
        assert r.status_code == 200


# ---------- Style intel data (Drop-off etc) ----------
class TestStyleIntelDetail:
    EXPECTED_STYLES = {"Chrome", "Glazed Donut", "Cat Eye", "3D Nail Art"}

    def test_dropoff_has_expected_styles(self, session, agency_token):
        r = session.get(f"{API}/agency/style-intel", headers=auth_h(agency_token))
        assert r.status_code == 200
        d = r.json()
        rows = d.get("most_tried_not_booked") or d.get("drop_off") or []
        names = {row.get("name") or row.get("style_name") for row in rows}
        # At least 2 of the expected
        overlap = names & self.EXPECTED_STYLES
        assert len(overlap) >= 2, f"expected >=2 of {self.EXPECTED_STYLES}, got {names}"
