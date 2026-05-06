"""Backend tests for the rebuilt GlowLeads funnel (Upload→Shape→Design→Colour→AI→Book)."""
import os
import base64
import io
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://glowleads-demo.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"

# Tiny 1x1 PNG (valid)
TINY_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII="
)


@pytest.fixture(scope="module")
def session():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


# ----- /api/funnel/config -----
class TestFunnelConfig:
    def test_config_structure(self, session):
        r = session.get(f"{API}/funnel/config", timeout=15)
        assert r.status_code == 200
        d = r.json()
        assert "shapes" in d and "design_groups" in d and "color_groups" in d

    def test_shapes_count_and_fields(self, session):
        d = session.get(f"{API}/funnel/config", timeout=15).json()
        shapes = d["shapes"]
        assert len(shapes) == 6
        ids = {s["id"] for s in shapes}
        assert ids == {"round", "square", "coffin", "almond", "stiletto", "squoval"}
        for s in shapes:
            assert s["label"] and s["description"] and s["image"].startswith("http")

    def test_design_groups_total(self, session):
        d = session.get(f"{API}/funnel/config", timeout=15).json()
        groups = d["design_groups"]
        assert len(groups) == 7
        expected_ids = {"popular", "french", "ombre", "chrome", "nail-art", "embellishments", "specialty"}
        assert {g["id"] for g in groups} == expected_ids
        total = sum(len(g["designs"]) for g in groups)
        assert 40 <= total <= 60, f"Expected ~50 designs, got {total}"
        for g in groups:
            for ds in g["designs"]:
                assert ds["id"] and ds["label"]
                assert "low" in ds["price_range"] and "high" in ds["price_range"]
                assert ds["image"].startswith("http")

    def test_color_groups_total(self, session):
        d = session.get(f"{API}/funnel/config", timeout=15).json()
        cgs = d["color_groups"]
        assert len(cgs) == 9
        expected = {"nudes", "pinks", "reds", "oranges", "purples", "blues", "greens", "darks", "trendy"}
        assert {g["id"] for g in cgs} == expected
        total = sum(len(g["colors"]) for g in cgs)
        assert 150 <= total <= 250, f"Expected ~200 colors, got {total}"
        for g in cgs:
            for c in g["colors"]:
                assert c["hex"].startswith("#") and c["name"] and c["brand"]


# ----- /api/ai/detect-shape -----
class TestDetectShape:
    def test_detect_shape_with_tiny_image_returns_200(self, session):
        r = session.post(f"{API}/ai/detect-shape", json={"image_base64": TINY_PNG_B64}, timeout=60)
        assert r.status_code == 200
        d = r.json()
        assert "shape_id" in d and "shape_label" in d and "length" in d

    def test_detect_shape_with_garbage_returns_200(self, session):
        r = session.post(f"{API}/ai/detect-shape", json={"image_base64": "not-real-base64!!!"}, timeout=60)
        assert r.status_code == 200
        d = r.json()
        assert d["shape_id"] is None or d["shape_id"] in {"round","square","coffin","almond","stiletto","squoval"}


# ----- /api/ai/try-on -----
class TestTryOn:
    def test_try_on_with_design_id(self, session):
        payload = {
            "image_base64": TINY_PNG_B64,
            "tech_slug": "sophie",
            "design_id": "chrome",
            "shape_id": "almond",
            "color_hex": "#FF1493",
            "color_name": "Hot Pink",
        }
        r = session.post(f"{API}/ai/try-on", json=payload, timeout=120)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["source"] in ("ai", "fallback")
        assert d.get("preview")

    def test_try_on_legacy_style_id(self, session):
        payload = {
            "image_base64": TINY_PNG_B64,
            "tech_slug": "sophie",
            "style_id": "classic-red",
        }
        r = session.post(f"{API}/ai/try-on", json=payload, timeout=120)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["source"] in ("ai", "fallback")

    def test_try_on_missing_id_returns_400(self, session):
        payload = {"image_base64": TINY_PNG_B64, "tech_slug": "sophie"}
        r = session.post(f"{API}/ai/try-on", json=payload, timeout=30)
        assert r.status_code == 400


# ----- /api/leads with design_id -----
class TestLeads:
    def test_create_lead_with_design_and_color(self, session):
        payload = {
            "tech_slug": "sophie",
            "name": "TEST_FunnelLead",
            "phone": "+15551110000",
            "design_id": "chrome",
            "shape_id": "almond",
            "color_hex": "#FF1493",
            "color_name": "Hot Pink",
        }
        r = session.post(f"{API}/leads", json=payload, timeout=15)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["name"] == "TEST_FunnelLead"
        assert "id" in d


# ----- /api/bookings with design_id and color -----
class TestBookings:
    def test_create_booking_with_design_color(self, session):
        payload = {
            "tech_slug": "sophie",
            "name": "TEST_FunnelBooking",
            "phone": "+15551110001",
            "email": "test_funnel@example.com",
            "design_id": "chrome-mirror",
            "shape_id": "almond",
            "date": "2026-02-15",
            "time": "14:00",
            "color_hex": "#FFD700",
            "color_name": "Gold",
            "color_brand": "OPI Gold",
            "notes": "TEST booking notes",
        }
        r = session.post(f"{API}/bookings", json=payload, timeout=15)
        assert r.status_code == 200, r.text
        d = r.json()
        appt = d["appointment"]
        assert appt["client_name"] == "TEST_FunnelBooking"
        assert appt["design_id"] == "chrome-mirror"
        assert appt["shape_id"] == "almond"
        assert appt["color_hex"] == "#FFD700"
        assert appt["color_name"] == "Gold"
        assert appt["color_brand"] == "OPI Gold"
        # 3 SMS logs (instant + 24h + 1h)
        assert d["automations_scheduled"] == 3

    def test_booking_missing_id_returns_400(self, session):
        payload = {
            "tech_slug": "sophie",
            "name": "TEST_NoDesign",
            "phone": "+15551110002",
            "date": "2026-02-15",
            "time": "14:00",
        }
        r = session.post(f"{API}/bookings", json=payload, timeout=15)
        assert r.status_code == 400


# ----- Quick regression: login still works -----
class TestRegression:
    def test_sophie_login(self, session):
        r = session.post(f"{API}/auth/login", json={"email": "sophie@glowleads.com", "password": "sophie123"}, timeout=15)
        assert r.status_code == 200
        assert r.json()["user"]["role"] == "tech"

    def test_harry_login(self, session):
        r = session.post(f"{API}/auth/login", json={"email": "harry@glowleads.com", "password": "agency123"}, timeout=15)
        assert r.status_code == 200
        assert r.json()["user"]["role"] == "agency"
