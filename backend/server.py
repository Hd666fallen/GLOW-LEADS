"""GlowLeads — AI lead generation SaaS for nail technicians.

FastAPI + MongoDB + JWT auth + Gemini Nano Banana AI try-on.
"""
from __future__ import annotations

import asyncio
import base64
import logging
import os
import random
import re
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

import bcrypt
import jwt
from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from dotenv import load_dotenv

from styles_data import STYLES, STYLE_MAP

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("glowleads")

# ---------- Mongo ----------
MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]
mongo_client = AsyncIOMotorClient(MONGO_URL)
db = mongo_client[DB_NAME]

# ---------- Auth ----------
JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
JWT_EXPIRY_HOURS = 24 * 30  # 30 days


def hash_password(raw: str) -> str:
    return bcrypt.hashpw(raw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(raw: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(raw.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def create_token(user_id: str, role: str) -> str:
    payload = {
        "sub": user_id,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing auth token")
    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = await db.users.find_one({"id": payload["sub"]}, {"_id": 0, "password_hash": 0})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


async def require_tech(user: dict = Depends(get_current_user)) -> dict:
    if user.get("role") != "tech":
        raise HTTPException(status_code=403, detail="Nail tech account required")
    return user


async def require_agency(user: dict = Depends(get_current_user)) -> dict:
    if user.get("role") != "agency":
        raise HTTPException(status_code=403, detail="Agency account required")
    return user


# ---------- Pydantic models ----------
class Credentials(BaseModel):
    email: EmailStr
    password: str


class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    business_name: str
    city: str
    phone: Optional[str] = ""


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    business_name: Optional[str] = None
    bio: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    profile_photo: Optional[str] = None


class StylesUpdate(BaseModel):
    enabled_style_ids: list[str]


class DetectIn(BaseModel):
    image_base64: str  # data URL or plain base64


class TryOnIn(BaseModel):
    image_base64: str
    style_id: str
    tech_slug: str


class LeadIn(BaseModel):
    tech_slug: str
    name: str
    phone: Optional[str] = ""
    style_id: str
    preview_image: Optional[str] = None
    detected_style_id: Optional[str] = None


class BookingIn(BaseModel):
    tech_slug: str
    name: str
    phone: str
    style_id: str
    date: str  # ISO date "YYYY-MM-DD"
    time: str  # "14:30"
    preview_image: Optional[str] = None
    lead_id: Optional[str] = None


class AppointmentStatusUpdate(BaseModel):
    status: str  # confirmed / pending / completed / cancelled / no-show


# ---------- Helpers ----------
def slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s or uuid.uuid4().hex[:8]


def clean_user_public(user: dict) -> dict:
    """Strip sensitive fields and return a customer-facing view of a tech."""
    return {
        "id": user["id"],
        "slug": user["slug"],
        "full_name": user["full_name"],
        "business_name": user["business_name"],
        "bio": user.get("bio", ""),
        "city": user.get("city", ""),
        "phone": user.get("phone", ""),
        "profile_photo": user.get("profile_photo", ""),
        "rating": user.get("rating", 4.9),
        "review_count": user.get("review_count", 247),
    }


# ---------- App setup ----------
app = FastAPI(title="GlowLeads API")
api = APIRouter(prefix="/api")


@api.get("/")
async def root():
    return {"message": "GlowLeads API online", "time": datetime.now(timezone.utc).isoformat()}


# ---------- Auth routes ----------
@api.post("/auth/register")
async def register(data: RegisterIn):
    existing = await db.users.find_one({"email": data.email.lower()})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    uid = str(uuid.uuid4())
    base_slug = slugify(data.business_name or data.full_name)
    slug = base_slug
    i = 1
    while await db.users.find_one({"slug": slug}):
        slug = f"{base_slug}-{i}"
        i += 1
    doc = {
        "id": uid,
        "email": data.email.lower(),
        "password_hash": hash_password(data.password),
        "role": "tech",
        "slug": slug,
        "full_name": data.full_name,
        "business_name": data.business_name,
        "city": data.city,
        "phone": data.phone or "",
        "bio": "Certified nail artist. Book your dream nails today ✨",
        "profile_photo": "https://images.unsplash.com/photo-1713552566168-89c00fd622cf?w=400&q=80",
        "enabled_style_ids": [s["id"] for s in STYLES[:30]],
        "portfolio": {},
        "rating": 5.0,
        "review_count": 12,
        "plan": "starter",
        "mrr": 49,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.users.insert_one(doc)
    token = create_token(uid, "tech")
    return {"token": token, "user": {k: v for k, v in doc.items() if k != "password_hash" and k != "_id"}}


@api.post("/auth/login")
async def login(data: Credentials):
    user = await db.users.find_one({"email": data.email.lower()})
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_token(user["id"], user["role"])
    user.pop("_id", None)
    user.pop("password_hash", None)
    return {"token": token, "user": user}


@api.get("/auth/me")
async def me(user: dict = Depends(get_current_user)):
    return user


# ---------- Public funnel routes ----------
@api.get("/styles")
async def list_styles():
    return {"styles": STYLES}


@api.get("/public/tech/{slug}")
async def get_public_tech(slug: str):
    user = await db.users.find_one({"slug": slug, "role": "tech"}, {"_id": 0, "password_hash": 0})
    if not user:
        raise HTTPException(status_code=404, detail="Nail tech not found")
    enabled_ids = set(user.get("enabled_style_ids", []))
    portfolio = user.get("portfolio") or {}
    enabled_styles = []
    for s in STYLES:
        if s["id"] in enabled_ids:
            enriched = {**s}
            if portfolio.get(s["id"]):
                enriched["image"] = portfolio[s["id"]]
            enabled_styles.append(enriched)
    return {"tech": clean_user_public(user), "styles": enabled_styles}


# ---------- AI routes ----------
def _decode_image(image_base64: str) -> str:
    """Strip a data-URL prefix if present and return the raw base64 string."""
    if image_base64.startswith("data:"):
        try:
            return image_base64.split(",", 1)[1]
        except IndexError:
            pass
    return image_base64


@api.post("/ai/detect")
async def ai_detect_style(data: DetectIn):
    """Detect the customer's current nail style from their uploaded hand photo.

    Uses Gemini via emergentintegrations to read the nails. Falls back gracefully
    if the model can't identify a match.
    """
    raw_b64 = _decode_image(data.image_base64)
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent

        api_key = os.environ["EMERGENT_LLM_KEY"]
        chat = LlmChat(
            api_key=api_key,
            session_id=f"detect-{uuid.uuid4()}",
            system_message=(
                "You are a professional nail artist. Given a photo of a hand, "
                "identify the existing nail polish style. Reply ONLY with a short JSON "
                "object like {\"detected\": \"<style keyword>\", \"has_polish\": true/false}. "
                "Use simple keywords like: bare, nude, red, pink, black, french, glitter, chrome, matte, unclear."
            ),
        )
        chat.with_model("gemini", "gemini-3.1-flash-image-preview")
        msg = UserMessage(
            text="What nail polish style is on these nails? Reply with JSON only.",
            file_contents=[ImageContent(raw_b64)],
        )
        text, _images = await asyncio.wait_for(chat.send_message_multimodal_response(msg), timeout=45)
        detected = None
        has_polish = False
        try:
            import json as _json
            cleaned = re.search(r"\{.*\}", text or "", re.DOTALL)
            if cleaned:
                obj = _json.loads(cleaned.group(0))
                detected = (obj.get("detected") or "").lower().strip()
                has_polish = bool(obj.get("has_polish"))
        except Exception:
            detected = None
        # Map keyword to closest style id
        mapping = {
            "red": "classic-red", "pink": "baby-pink", "hot pink": "hot-pink",
            "nude": "nude-milky", "bare": None, "french": "french-classic",
            "black": "black", "glitter": "glitter-ombre", "chrome": "chrome",
            "matte": "matte-gel", "plum": "deep-plum", "brown": "chocolate",
            "white": "white-cream", "blue": "navy-blue",
        }
        style_id = mapping.get(detected) if detected else None
        return {
            "has_polish": has_polish,
            "detected_keyword": detected,
            "detected_style_id": style_id,
            "detected_style_name": STYLE_MAP[style_id]["name"] if style_id and style_id in STYLE_MAP else None,
        }
    except asyncio.TimeoutError:
        logger.warning("AI detect timed out")
        return {"has_polish": False, "detected_keyword": None, "detected_style_id": None, "detected_style_name": None}
    except Exception as e:
        logger.exception("AI detect failed: %s", e)
        return {"has_polish": False, "detected_keyword": None, "detected_style_id": None, "detected_style_name": None}


@api.post("/ai/try-on")
async def ai_try_on(data: TryOnIn):
    """Apply the selected nail style to the user's uploaded hand photo using Gemini Nano Banana."""
    style = STYLE_MAP.get(data.style_id)
    if not style:
        raise HTTPException(status_code=400, detail="Unknown style id")
    raw_b64 = _decode_image(data.image_base64)
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent

        api_key = os.environ["EMERGENT_LLM_KEY"]
        chat = LlmChat(
            api_key=api_key,
            session_id=f"tryon-{uuid.uuid4()}",
            system_message="You are a professional nail artist creating ultra realistic photo edits.",
        )
        chat.with_model("gemini", "gemini-3.1-flash-image-preview").with_params(modalities=["image", "text"])

        prompt = (
            f"Edit this exact photo of a hand. Keep the hand, skin tone, lighting and background identical. "
            f"Only change the fingernails to show this nail style: {style['prompt_hint']}. "
            f"The nails should look like a professional salon manicure, ultra realistic, photographic, "
            f"sharp focus, natural shadows. Do not change anything else about the image."
        )
        msg = UserMessage(text=prompt, file_contents=[ImageContent(raw_b64)])
        text, images = await asyncio.wait_for(chat.send_message_multimodal_response(msg), timeout=90)
        if images:
            img = images[0]
            mime = img.get("mime_type", "image/png")
            data_url = f"data:{mime};base64,{img['data']}"
            return {"preview": data_url, "source": "ai", "style": style}
        logger.warning("AI try-on returned no image; text=%s", (text or "")[:200])
    except asyncio.TimeoutError:
        logger.warning("AI try-on timed out")
    except Exception as e:
        logger.exception("AI try-on failed: %s", e)
    # Fallback: return the style's portfolio/stock image
    return {"preview": style["image"], "source": "fallback", "style": style}


# ---------- Lead & Booking routes ----------
async def _resolve_tech_by_slug(slug: str) -> dict:
    tech = await db.users.find_one({"slug": slug, "role": "tech"}, {"_id": 0, "password_hash": 0})
    if not tech:
        raise HTTPException(status_code=404, detail="Nail tech not found")
    return tech


@api.post("/leads")
async def create_lead(data: LeadIn):
    tech = await _resolve_tech_by_slug(data.tech_slug)
    style = STYLE_MAP.get(data.style_id)
    lead = {
        "id": str(uuid.uuid4()),
        "tech_id": tech["id"],
        "tech_slug": tech["slug"],
        "name": data.name,
        "phone": data.phone or "",
        "style_id": data.style_id,
        "style_name": style["name"] if style else data.style_id,
        "preview_image": data.preview_image or (style["image"] if style else ""),
        "detected_style_id": data.detected_style_id,
        "status": "not_booked",
        "follow_ups_sent": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.leads.insert_one(dict(lead))
    return lead


@api.post("/bookings")
async def create_booking(data: BookingIn):
    tech = await _resolve_tech_by_slug(data.tech_slug)
    style = STYLE_MAP.get(data.style_id)
    if not style:
        raise HTTPException(status_code=400, detail="Unknown style id")
    appt = {
        "id": str(uuid.uuid4()),
        "tech_id": tech["id"],
        "tech_slug": tech["slug"],
        "client_name": data.name,
        "client_phone": data.phone,
        "style_id": data.style_id,
        "style_name": style["name"],
        "style_category": style["category"],
        "preview_image": data.preview_image or style["image"],
        "date": data.date,
        "time": data.time,
        "status": "confirmed",
        "price": style["price_range"]["low"],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.appointments.insert_one(dict(appt))
    # Mark lead as converted if we have its id
    if data.lead_id:
        await db.leads.update_one({"id": data.lead_id}, {"$set": {"status": "converted", "appointment_id": appt["id"]}})
    # Mock SMS log
    await db.sms_logs.insert_one({
        "id": str(uuid.uuid4()),
        "tech_id": tech["id"],
        "to": data.phone,
        "body": f"Booking confirmed with {tech['business_name']} on {data.date} at {data.time} for {style['name']}. See you soon!",
        "type": "booking_confirmation",
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    return {"appointment": appt, "sms_sent": True}


# ---------- Tech dashboard routes ----------
@api.get("/tech/me/profile")
async def tech_profile(user: dict = Depends(require_tech)):
    return clean_user_public(user) | {"email": user["email"], "plan": user.get("plan", "starter")}


@api.put("/tech/me/profile")
async def update_tech_profile(update: ProfileUpdate, user: dict = Depends(require_tech)):
    fields = {k: v for k, v in update.model_dump().items() if v is not None}
    if fields:
        await db.users.update_one({"id": user["id"]}, {"$set": fields})
    fresh = await db.users.find_one({"id": user["id"]}, {"_id": 0, "password_hash": 0})
    return fresh


@api.get("/tech/me/styles")
async def tech_styles(user: dict = Depends(require_tech)):
    enabled = set(user.get("enabled_style_ids", []))
    return {
        "all": STYLES,
        "enabled_ids": list(enabled),
    }


@api.put("/tech/me/styles")
async def update_tech_styles(data: StylesUpdate, user: dict = Depends(require_tech)):
    valid = [sid for sid in data.enabled_style_ids if sid in STYLE_MAP]
    await db.users.update_one({"id": user["id"]}, {"$set": {"enabled_style_ids": valid}})
    return {"enabled_ids": valid}


@api.get("/tech/me/appointments")
async def tech_appointments(user: dict = Depends(require_tech)):
    rows = await db.appointments.find({"tech_id": user["id"]}, {"_id": 0}).sort("date", 1).to_list(500)
    return {"appointments": rows}


@api.put("/tech/me/appointments/{appt_id}")
async def update_appt_status(appt_id: str, data: AppointmentStatusUpdate, user: dict = Depends(require_tech)):
    await db.appointments.update_one(
        {"id": appt_id, "tech_id": user["id"]},
        {"$set": {"status": data.status}},
    )
    appt = await db.appointments.find_one({"id": appt_id, "tech_id": user["id"]}, {"_id": 0})
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appt


@api.get("/tech/me/leads")
async def tech_leads(user: dict = Depends(require_tech)):
    rows = await db.leads.find({"tech_id": user["id"]}, {"_id": 0}).sort("created_at", -1).to_list(500)
    appt_count = await db.appointments.count_documents({"tech_id": user["id"]})
    total_tryons = await db.leads.count_documents({"tech_id": user["id"]}) + appt_count
    booked = appt_count
    conv_pct = round(100.0 * booked / total_tryons, 1) if total_tryons else 0.0
    followups = sum(r.get("follow_ups_sent", 0) for r in rows)
    return {
        "leads": rows,
        "stats": {"total_tryons": total_tryons, "booked": booked, "conversion_pct": conv_pct, "followups_sent": followups},
    }


@api.post("/tech/me/leads/{lead_id}/follow-up")
async def send_followup(lead_id: str, user: dict = Depends(require_tech)):
    lead = await db.leads.find_one({"id": lead_id, "tech_id": user["id"]}, {"_id": 0})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    body = (
        f"Hey {lead['name']}! Still thinking about those {lead['style_name']} nails? "
        f"I have a spot open this week. Want to grab it? -- {user['business_name']}"
    )
    await db.sms_logs.insert_one({
        "id": str(uuid.uuid4()),
        "tech_id": user["id"],
        "to": lead.get("phone", ""),
        "body": body,
        "type": "lead_followup",
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    await db.leads.update_one({"id": lead_id}, {"$inc": {"follow_ups_sent": 1}})
    return {"sent": True, "body": body}


@api.get("/tech/me/stats")
async def tech_stats(user: dict = Depends(require_tech)):
    now = datetime.now(timezone.utc)
    start_week = now - timedelta(days=7)
    start_month = now - timedelta(days=30)
    today_str = now.date().isoformat()
    leads_today = await db.leads.count_documents({
        "tech_id": user["id"],
        "created_at": {"$gte": now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()},
    })
    appts_week = await db.appointments.count_documents({
        "tech_id": user["id"],
        "created_at": {"$gte": start_week.isoformat()},
    })
    appts_month = await db.appointments.find(
        {"tech_id": user["id"], "created_at": {"$gte": start_month.isoformat()}}, {"_id": 0}
    ).to_list(1000)
    revenue_month = sum(a.get("price", 0) for a in appts_month)

    # Activity feed: recent appts & leads
    recent_appts = await db.appointments.find({"tech_id": user["id"]}, {"_id": 0}).sort("created_at", -1).limit(5).to_list(5)
    recent_leads = await db.leads.find({"tech_id": user["id"]}, {"_id": 0}).sort("created_at", -1).limit(5).to_list(5)
    feed = []
    for a in recent_appts:
        feed.append({
            "type": "booking",
            "text": f"{a['client_name']} just booked {a['style_name']} for {a['date']} at {a['time']}",
            "when": a["created_at"],
        })
    for l in recent_leads:
        feed.append({
            "type": "lead",
            "text": f"New lead: {l['name']} tried {l['style_name']}",
            "when": l["created_at"],
        })
    feed.sort(key=lambda x: x["when"], reverse=True)
    return {
        "leads_today": leads_today,
        "appts_this_week": appts_week,
        "revenue_this_month": revenue_month,
        "activity": feed[:8],
        "today": today_str,
    }


# ---------- Agency dashboard routes ----------
@api.get("/agency/overview")
async def agency_overview(_: dict = Depends(require_agency)):
    techs = await db.users.find({"role": "tech"}, {"_id": 0, "password_hash": 0}).to_list(500)
    total_leads = await db.leads.count_documents({})
    total_bookings = await db.appointments.count_documents({})
    mrr = sum(t.get("mrr", 0) for t in techs)
    # Churn risk: pick techs with fewer leads than median
    lead_counts = []
    for t in techs:
        c = await db.leads.count_documents({"tech_id": t["id"]})
        lead_counts.append((t, c))
    lead_counts.sort(key=lambda x: x[1])
    at_risk = [
        {"id": t["id"], "business_name": t["business_name"], "leads": c, "city": t.get("city", "")}
        for t, c in lead_counts[: max(0, len(lead_counts) // 3)] if c < 5
    ]
    # Activity feed
    recent_appts = await db.appointments.find({}, {"_id": 0}).sort("created_at", -1).limit(6).to_list(6)
    recent_leads = await db.leads.find({}, {"_id": 0}).sort("created_at", -1).limit(6).to_list(6)
    tech_name_map = {t["id"]: t["business_name"] for t in techs}
    feed = []
    for a in recent_appts:
        feed.append({
            "type": "booking",
            "text": f"{tech_name_map.get(a['tech_id'], 'A tech')} -- {a['client_name']} booked {a['style_name']}",
            "when": a["created_at"],
        })
    for l in recent_leads:
        feed.append({
            "type": "lead",
            "text": f"{tech_name_map.get(l['tech_id'], 'A tech')} -- {l['name']} tried {l['style_name']}",
            "when": l["created_at"],
        })
    feed.sort(key=lambda x: x["when"], reverse=True)
    return {
        "kpis": {
            "active_clients": len(techs),
            "total_leads": total_leads,
            "total_bookings": total_bookings,
            "mrr": mrr,
        },
        "at_risk": at_risk,
        "activity": feed[:10],
    }


@api.get("/agency/clients")
async def agency_clients(_: dict = Depends(require_agency)):
    techs = await db.users.find({"role": "tech"}, {"_id": 0, "password_hash": 0}).to_list(500)
    rows = []
    for t in techs:
        leads_count = await db.leads.count_documents({"tech_id": t["id"]})
        bookings_count = await db.appointments.count_documents({"tech_id": t["id"]})
        status = "active"
        if leads_count < 3:
            status = "at_risk"
        rows.append({
            "id": t["id"],
            "slug": t["slug"],
            "business_name": t["business_name"],
            "owner_name": t["full_name"],
            "city": t.get("city", ""),
            "plan": t.get("plan", "starter"),
            "leads": leads_count,
            "bookings": bookings_count,
            "mrr": t.get("mrr", 0),
            "status": status,
            "last_active": t.get("created_at", ""),
            "profile_photo": t.get("profile_photo", ""),
        })
    return {"clients": rows}


@api.get("/agency/analytics")
async def agency_analytics(_: dict = Depends(require_agency)):
    techs = await db.users.find({"role": "tech"}, {"_id": 0, "password_hash": 0}).to_list(500)
    # Leads per tech per week (approx) -- using recent buckets
    now = datetime.now(timezone.utc)
    weeks = []
    for w in range(4, -1, -1):
        start = now - timedelta(days=(w + 1) * 7)
        end = now - timedelta(days=w * 7)
        label = f"W-{w}" if w else "This W"
        bucket = {"week": label}
        for t in techs:
            count = await db.leads.count_documents({
                "tech_id": t["id"],
                "created_at": {"$gte": start.isoformat(), "$lt": end.isoformat()},
            })
            bucket[t["business_name"]] = count
        weeks.append(bucket)
    # Conversion per client
    conv = []
    for t in techs:
        leads_c = await db.leads.count_documents({"tech_id": t["id"]})
        appts_c = await db.appointments.count_documents({"tech_id": t["id"]})
        total = leads_c + appts_c
        pct = round(100.0 * appts_c / total, 1) if total else 0.0
        conv.append({"name": t["business_name"], "conversion": pct, "leads": leads_c, "bookings": appts_c})
    # Popular styles
    agg = await db.appointments.aggregate([
        {"$group": {"_id": "$style_name", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 8},
    ]).to_list(20)
    popular = [{"name": r["_id"], "count": r["count"]} for r in agg]
    # Heatmap: day/hour
    appts = await db.appointments.find({}, {"_id": 0, "date": 1, "time": 1}).to_list(2000)
    heat = {}
    for a in appts:
        try:
            d = datetime.fromisoformat(a["date"])
            day = d.strftime("%a")
            hour = int(a["time"].split(":")[0])
            key = f"{day}-{hour}"
            heat[key] = heat.get(key, 0) + 1
        except Exception:
            continue
    heatmap = [{"key": k, "count": v} for k, v in heat.items()]
    # Geo by city
    cities = {}
    for t in techs:
        city = t.get("city", "Unknown")
        c = await db.leads.count_documents({"tech_id": t["id"]})
        cities[city] = cities.get(city, 0) + c
    geo = [{"city": k, "leads": v} for k, v in cities.items()]
    return {
        "leads_weekly": weeks,
        "conversion": conv,
        "popular_styles": popular,
        "heatmap": heatmap,
        "geo": geo,
    }


@api.get("/agency/style-intel")
async def agency_style_intel(_: dict = Depends(require_agency)):
    # Most tried but NOT booked (leads by style)
    lead_agg = await db.leads.aggregate([
        {"$group": {"_id": "$style_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]).to_list(100)
    booked_agg = await db.appointments.aggregate([
        {"$group": {"_id": "$style_id", "count": {"$sum": 1}}},
    ]).to_list(100)
    booked_map = {r["_id"]: r["count"] for r in booked_agg}
    most_tried_not_booked = []
    for r in lead_agg[:10]:
        sid = r["_id"]
        if sid in STYLE_MAP:
            most_tried_not_booked.append({
                "style_id": sid,
                "style_name": STYLE_MAP[sid]["name"],
                "tried": r["count"],
                "booked": booked_map.get(sid, 0),
                "image": STYLE_MAP[sid]["image"],
            })
    # Most detected
    det_agg = await db.leads.aggregate([
        {"$match": {"detected_style_id": {"$ne": None}}},
        {"$group": {"_id": "$detected_style_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ]).to_list(20)
    most_detected = []
    for r in det_agg:
        if r["_id"] in STYLE_MAP:
            most_detected.append({
                "style_id": r["_id"],
                "style_name": STYLE_MAP[r["_id"]]["name"],
                "count": r["count"],
                "image": STYLE_MAP[r["_id"]]["image"],
            })
    # Styles not offered by any client (enabled_style_ids union)
    techs = await db.users.find({"role": "tech"}, {"_id": 0, "enabled_style_ids": 1}).to_list(500)
    offered = set()
    for t in techs:
        offered.update(t.get("enabled_style_ids", []))
    gaps = [
        {"style_id": s["id"], "style_name": s["name"], "category": s["category"], "image": s["image"]}
        for s in STYLES if s["id"] not in offered
    ][:10]
    # Trending this week — most lead activity in past 7 days
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    trending_agg = await db.leads.aggregate([
        {"$match": {"created_at": {"$gte": week_ago}}},
        {"$group": {"_id": "$style_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 6},
    ]).to_list(10)
    trending = []
    for r in trending_agg:
        if r["_id"] in STYLE_MAP:
            trending.append({
                "style_id": r["_id"],
                "style_name": STYLE_MAP[r["_id"]]["name"],
                "count": r["count"],
                "image": STYLE_MAP[r["_id"]]["image"],
            })
    return {
        "most_tried_not_booked": most_tried_not_booked,
        "most_detected": most_detected,
        "market_gaps": gaps,
        "trending": trending,
    }


@api.get("/agency/billing")
async def agency_billing(_: dict = Depends(require_agency)):
    techs = await db.users.find({"role": "tech"}, {"_id": 0, "password_hash": 0}).to_list(500)
    rows = [
        {
            "id": t["id"],
            "business_name": t["business_name"],
            "plan": t.get("plan", "starter"),
            "mrr": t.get("mrr", 49),
            "status": "active",
            "renewal": (datetime.now(timezone.utc) + timedelta(days=30)).date().isoformat(),
        }
        for t in techs
    ]
    mrr = sum(r["mrr"] for r in rows)
    # Last 6 months fake MoM
    now = datetime.now(timezone.utc)
    growth = []
    base = max(mrr - 240, 50)
    for i in range(6, 0, -1):
        month = (now - timedelta(days=30 * i)).strftime("%b")
        growth.append({"month": month, "mrr": base + (6 - i) * 40})
    growth.append({"month": now.strftime("%b"), "mrr": mrr})
    return {"subscriptions": rows, "mrr": mrr, "growth": growth, "failed_payments": []}


# ---------- Seed ----------
SEED_STYLES_FOR_SOPHIE = [
    "classic-gel", "matte-gel", "chrome", "glazed-donut", "cat-eye", "jelly-glass",
    "holographic", "french-classic", "french-colored", "french-ombre", "french-chrome",
    "ombre-classic", "ombre-sunset", "aura-nails", "watercolor", "marble", "floral-art",
    "geometric", "swirl-art", "dots", "butterfly", "celestial", "rhinestone",
    "pearl-accents", "gold-foil", "glitter-ombre", "nude-milky", "classic-red",
    "baby-pink", "hot-pink", "lavender", "black", "coral", "acrylic-full",
    "dip-powder", "polygel", "extensions",
]

SEED_APPOINTMENTS = [
    ("Sarah Chen", "+14155552011", "chrome", 2, "14:00", "confirmed"),
    ("Emma Rodriguez", "+14155552012", "glazed-donut", 3, "10:30", "confirmed"),
    ("Olivia Park", "+14155552013", "french-ombre", 4, "16:15", "confirmed"),
    ("Maya Patel", "+14155552014", "floral-art", 5, "12:00", "pending"),
    ("Chloe Thompson", "+14155552015", "rhinestone", 7, "13:45", "confirmed"),
    ("Zoe Williams", "+14155552016", "aura-nails", -2, "11:00", "completed"),
    ("Isabella Kim", "+14155552017", "swirl-art", -5, "15:30", "completed"),
]

SEED_LEADS = [
    ("Grace Miller", "+14155553001", "matte-gel"),
    ("Lily Davis", "+14155553002", "cat-eye"),
    ("Ava Johnson", "+14155553003", "butterfly"),
    ("Sophia Martinez", "+14155553004", "pearl-accents"),
    ("Mia Anderson", "+14155553005", "chrome"),
    ("Ella Wilson", "+14155553006", "glazed-donut"),
    ("Harper Brown", "+14155553007", "gold-foil"),
    ("Amelia Garcia", "+14155553008", "french-chrome"),
    ("Charlotte Lee", "+14155553009", "ombre-sunset"),
    ("Abigail Taylor", "+14155553010", "holographic"),
]


async def seed_database():
    now = datetime.now(timezone.utc)

    # Agency account
    if not await db.users.find_one({"email": "harry@glowleads.com"}):
        await db.users.insert_one({
            "id": str(uuid.uuid4()),
            "email": "harry@glowleads.com",
            "password_hash": hash_password("agency123"),
            "role": "agency",
            "full_name": "Harry",
            "business_name": "GlowLeads HQ",
            "created_at": now.isoformat(),
        })
        logger.info("Seeded agency account harry@glowleads.com / agency123")

    # Nail tech account: Sophie
    tech = await db.users.find_one({"email": "sophie@glowleads.com"})
    if not tech:
        tech_id = str(uuid.uuid4())
        tech_doc = {
            "id": tech_id,
            "email": "sophie@glowleads.com",
            "password_hash": hash_password("sophie123"),
            "role": "tech",
            "slug": "sophie",
            "full_name": "Sophie Laurent",
            "business_name": "Glow by Sophie",
            "city": "Los Angeles, CA",
            "phone": "+14155550100",
            "bio": "LA-based nail artist specializing in Chrome, Aura and French designs. 8+ years experience.",
            "profile_photo": "https://images.unsplash.com/photo-1713552566168-89c00fd622cf?w=400&q=80",
            "enabled_style_ids": SEED_STYLES_FOR_SOPHIE,
            "portfolio": {},
            "rating": 4.9,
            "review_count": 342,
            "plan": "pro",
            "mrr": 99,
            "created_at": now.isoformat(),
        }
        await db.users.insert_one(tech_doc)
        tech = tech_doc
        logger.info("Seeded tech account sophie@glowleads.com / sophie123 (slug=sophie)")

    # Second tech for agency dashboard variety
    if not await db.users.find_one({"email": "bella@glowleads.com"}):
        await db.users.insert_one({
            "id": str(uuid.uuid4()),
            "email": "bella@glowleads.com",
            "password_hash": hash_password("bella123"),
            "role": "tech",
            "slug": "bella",
            "full_name": "Bella Rivera",
            "business_name": "Bella Nails NYC",
            "city": "Brooklyn, NY",
            "phone": "+12125550111",
            "bio": "Brooklyn's go-to for floral and 3D nail art.",
            "profile_photo": "https://images.unsplash.com/photo-1595475207225-428b62bda831?w=400&q=80",
            "enabled_style_ids": SEED_STYLES_FOR_SOPHIE[:20],
            "portfolio": {},
            "rating": 4.8,
            "review_count": 198,
            "plan": "starter",
            "mrr": 49,
            "created_at": now.isoformat(),
        })
        logger.info("Seeded tech bella@glowleads.com / bella123 (slug=bella)")

    if not await db.users.find_one({"email": "jade@glowleads.com"}):
        await db.users.insert_one({
            "id": str(uuid.uuid4()),
            "email": "jade@glowleads.com",
            "password_hash": hash_password("jade123"),
            "role": "tech",
            "slug": "jade",
            "full_name": "Jade Wilson",
            "business_name": "Jade's Nail Lounge",
            "city": "Miami, FL",
            "phone": "+13055550122",
            "bio": "Miami nail artist -- summer vibes only.",
            "profile_photo": "https://images.unsplash.com/photo-1580618672591-eb180b1a973f?w=400&q=80",
            "enabled_style_ids": SEED_STYLES_FOR_SOPHIE[:15],
            "portfolio": {},
            "rating": 4.7,
            "review_count": 86,
            "plan": "starter",
            "mrr": 49,
            "created_at": now.isoformat(),
        })
        logger.info("Seeded tech jade@glowleads.com / jade123 (slug=jade)")

    # Appointments for Sophie
    if await db.appointments.count_documents({"tech_id": tech["id"]}) == 0:
        for name, phone, sid, day_offset, time_str, status in SEED_APPOINTMENTS:
            style = STYLE_MAP[sid]
            appt_date = (now + timedelta(days=day_offset)).date().isoformat()
            await db.appointments.insert_one({
                "id": str(uuid.uuid4()),
                "tech_id": tech["id"],
                "tech_slug": tech["slug"],
                "client_name": name,
                "client_phone": phone,
                "style_id": sid,
                "style_name": style["name"],
                "style_category": style["category"],
                "preview_image": style["image"],
                "date": appt_date,
                "time": time_str,
                "status": status,
                "price": style["price_range"]["low"],
                "created_at": (now - timedelta(days=random.randint(1, 10))).isoformat(),
            })
        logger.info("Seeded %d appointments for Sophie", len(SEED_APPOINTMENTS))

    # Leads for Sophie
    if await db.leads.count_documents({"tech_id": tech["id"]}) == 0:
        for name, phone, sid in SEED_LEADS:
            style = STYLE_MAP[sid]
            await db.leads.insert_one({
                "id": str(uuid.uuid4()),
                "tech_id": tech["id"],
                "tech_slug": tech["slug"],
                "name": name,
                "phone": phone,
                "style_id": sid,
                "style_name": style["name"],
                "preview_image": style["image"],
                "detected_style_id": random.choice(["classic-red", "nude-milky", "french-classic", None]),
                "status": "not_booked",
                "follow_ups_sent": 0,
                "created_at": (now - timedelta(days=random.randint(0, 14))).isoformat(),
            })
        logger.info("Seeded %d leads for Sophie", len(SEED_LEADS))


@app.on_event("startup")
async def _startup():
    try:
        await seed_database()
    except Exception as e:
        logger.exception("Seed failed: %s", e)


@app.on_event("shutdown")
async def _shutdown():
    mongo_client.close()


# Register router + CORS
app.include_router(api)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)
