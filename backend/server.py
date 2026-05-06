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
from funnel_data import SHAPES, SHAPE_MAP, DESIGN_GROUPS, DESIGN_MAP, COLOR_GROUPS

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
    tech_slug: str
    style_id: Optional[str] = None
    design_id: Optional[str] = None
    shape_id: Optional[str] = None
    color_hex: Optional[str] = None
    color_name: Optional[str] = None


class LeadIn(BaseModel):
    tech_slug: str
    name: str
    phone: Optional[str] = ""
    style_id: Optional[str] = None
    design_id: Optional[str] = None
    shape_id: Optional[str] = None
    preview_image: Optional[str] = None
    detected_style_id: Optional[str] = None
    color_hex: Optional[str] = None
    color_name: Optional[str] = None


class BookingIn(BaseModel):
    tech_slug: str
    name: str
    phone: str
    email: Optional[str] = ""
    style_id: Optional[str] = None
    design_id: Optional[str] = None
    shape_id: Optional[str] = None
    date: str
    time: str
    preview_image: Optional[str] = None
    lead_id: Optional[str] = None
    color_hex: Optional[str] = None
    color_name: Optional[str] = None
    color_brand: Optional[str] = None
    notes: Optional[str] = ""


class ShapeDetectIn(BaseModel):
    image_base64: str


class AppointmentStatusUpdate(BaseModel):
    status: str  # confirmed / pending / completed / cancelled / no-show


class AutomationSettings(BaseModel):
    instant_booking: bool = True
    reminder_24h: bool = True
    reminder_1h: bool = True
    review_request: bool = True
    noshow_recovery: bool = True
    lead_sequence: bool = True
    winback: bool = True


# ---------- Helpers ----------
def default_automation_settings() -> dict:
    return {
        "instant_booking": True,
        "reminder_24h": True,
        "reminder_1h": True,
        "review_request": True,
        "noshow_recovery": True,
        "lead_sequence": True,
        "winback": True,
    }


def lead_temperature(created_at_iso: str) -> str:
    """Return 'hot' / 'warm' / 'cold' based on days since lead creation."""
    try:
        created = datetime.fromisoformat(created_at_iso)
    except Exception:
        return "warm"
    delta = datetime.now(timezone.utc) - created
    hours = delta.total_seconds() / 3600
    if hours <= 24:
        return "hot"
    if hours <= 72:
        return "warm"
    return "cold"


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
        "style_prices": {},
        "rating": 5.0,
        "review_count": 12,
        "plan": "starter",
        "mrr": 49,
        "automation_settings": default_automation_settings(),
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


@api.get("/funnel/config")
async def funnel_config():
    """Shapes + design groups + color groups for the new funnel flow."""
    return {
        "shapes": SHAPES,
        "design_groups": DESIGN_GROUPS,
        "color_groups": COLOR_GROUPS,
    }


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
    """Apply the selected nail design (or legacy style) to the user's hand photo using Gemini Nano Banana."""
    # Resolve the visual style description from either design_id (new) or style_id (legacy)
    design = DESIGN_MAP.get(data.design_id) if data.design_id else None
    style = STYLE_MAP.get(data.style_id) if data.style_id else None
    shape = SHAPE_MAP.get(data.shape_id) if data.shape_id else None

    if not design and not style:
        raise HTTPException(status_code=400, detail="design_id or style_id is required")

    fallback_image = (design or style)["image"] if (design or style) else None
    style_name = (design or style)["label" if design else "name"]
    style_hint = (style.get("prompt_hint") if style else None) or design["label"].lower()

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

        shape_text = f"{shape['label'].lower()} shaped" if shape else ""
        color_text = ""
        if data.color_hex:
            color_text = f" using the colour {data.color_name or data.color_hex} (hex {data.color_hex})"
        prompt = (
            f"Edit this exact photo of a hand. Keep the hand, skin tone, lighting and background identical. "
            f"Only change the fingernails to show {shape_text} nails in {style_name} style ({style_hint}){color_text}. "
            f"Photorealistic, professional nail salon quality, sharp focus, natural shadows. "
            f"Same hand preserved, high quality. Do not change anything else about the image."
        )
        msg = UserMessage(text=prompt, file_contents=[ImageContent(raw_b64)])
        text, images = await asyncio.wait_for(chat.send_message_multimodal_response(msg), timeout=90)
        if images:
            img = images[0]
            mime = img.get("mime_type", "image/png")
            data_url = f"data:{mime};base64,{img['data']}"
            return {"preview": data_url, "source": "ai", "design": design, "style": style, "shape": shape}
        logger.warning("AI try-on returned no image; text=%s", (text or "")[:200])
    except asyncio.TimeoutError:
        logger.warning("AI try-on timed out")
    except Exception as e:
        logger.exception("AI try-on failed: %s", e)
    return {"preview": fallback_image, "source": "fallback", "design": design, "style": style, "shape": shape}


@api.post("/ai/detect-shape")
async def ai_detect_shape(data: ShapeDetectIn):
    """Detect the customer's current nail shape + length from their hand photo."""
    raw_b64 = _decode_image(data.image_base64)
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage, ImageContent

        api_key = os.environ["EMERGENT_LLM_KEY"]
        chat = LlmChat(
            api_key=api_key,
            session_id=f"shape-{uuid.uuid4()}",
            system_message=(
                "You are a professional nail artist. Identify the nail shape and length from the photo. "
                "Reply ONLY with JSON like {\"shape\": \"<round|square|coffin|almond|stiletto|squoval>\", "
                "\"length\": \"<short|medium|long>\"}. If you can't tell, use \"unknown\" for either."
            ),
        )
        chat.with_model("gemini", "gemini-3.1-flash-image-preview")
        msg = UserMessage(
            text="Identify the nail shape and length. Reply with JSON only.",
            file_contents=[ImageContent(raw_b64)],
        )
        text, _ = await asyncio.wait_for(chat.send_message_multimodal_response(msg), timeout=45)
        shape_id = None
        length = "medium"
        try:
            import json as _json
            m = re.search(r"\{.*\}", text or "", re.DOTALL)
            if m:
                obj = _json.loads(m.group(0))
                cand = (obj.get("shape") or "").lower().strip()
                if cand in SHAPE_MAP:
                    shape_id = cand
                length = (obj.get("length") or "medium").lower().strip() or "medium"
        except Exception:
            pass
        return {
            "shape_id": shape_id,
            "shape_label": SHAPE_MAP[shape_id]["label"] if shape_id else None,
            "length": length,
        }
    except asyncio.TimeoutError:
        return {"shape_id": None, "shape_label": None, "length": "medium"}
    except Exception as e:
        logger.exception("Shape detect failed: %s", e)
        return {"shape_id": None, "shape_label": None, "length": "medium"}


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
    design = DESIGN_MAP.get(data.design_id) if data.design_id else None
    style = STYLE_MAP.get(data.style_id) if data.style_id else None
    if not design and not style:
        raise HTTPException(status_code=400, detail="design_id or style_id is required")
    label = design["label"] if design else style["name"]
    category = design["group_label"] if design else style.get("category", "")
    price = (design["price_range"]["low"] if design else style["price_range"]["low"])
    image = data.preview_image or (design["image"] if design else style["image"])
    appt = {
        "id": str(uuid.uuid4()),
        "tech_id": tech["id"],
        "tech_slug": tech["slug"],
        "client_name": data.name,
        "client_phone": data.phone,
        "client_email": data.email or "",
        "style_id": data.style_id or data.design_id,
        "design_id": data.design_id,
        "shape_id": data.shape_id,
        "style_name": label,
        "style_category": category,
        "preview_image": image,
        "color_hex": data.color_hex,
        "color_name": data.color_name,
        "color_brand": data.color_brand,
        "notes": data.notes or "",
        "date": data.date,
        "time": data.time,
        "status": "confirmed",
        "price": price,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.appointments.insert_one(dict(appt))
    # Mark lead as converted if we have its id
    if data.lead_id:
        await db.leads.update_one({"id": data.lead_id}, {"$set": {"status": "converted", "appointment_id": appt["id"]}})

    # Schedule full automation sequence based on tech's automation_settings
    automations = tech.get("automation_settings") or default_automation_settings()
    now_utc = datetime.now(timezone.utc)
    try:
        appt_dt = datetime.fromisoformat(f"{data.date}T{data.time}:00+00:00")
    except Exception:
        appt_dt = now_utc + timedelta(days=1)

    sms_to_log = []
    if automations.get("instant_booking", True):
        sms_to_log.append({
            "type": "booking_confirmation",
            "body": (
                f"Hey {data.name}! You're booked with {tech['business_name']} for "
                f"{label} nails on {data.date} at {data.time}. Can't wait to see you!"
            ),
            "created_at": now_utc.isoformat(),
            "scheduled_for": now_utc.isoformat(),
            "delivered": True,
        })
    if automations.get("reminder_24h", True):
        when = appt_dt - timedelta(hours=24)
        sms_to_log.append({
            "type": "reminder_24h",
            "body": (
                f"Hey {data.name}, just a reminder -- you're booked with {tech['business_name']} "
                f"tomorrow at {data.time} for {label} nails. Need to reschedule? Reply RESCHEDULE"
            ),
            "created_at": when.isoformat(),
            "scheduled_for": when.isoformat(),
            "delivered": when <= now_utc,
        })
    if automations.get("reminder_1h", True):
        when = appt_dt - timedelta(hours=1)
        sms_to_log.append({
            "type": "reminder_1h",
            "body": (
                f"See you in 1 hour {data.name}! {tech['business_name']} is ready for your "
                f"{label} nails."
            ),
            "created_at": when.isoformat(),
            "scheduled_for": when.isoformat(),
            "delivered": when <= now_utc,
        })
    for s in sms_to_log:
        await db.sms_logs.insert_one({
            "id": str(uuid.uuid4()),
            "tech_id": tech["id"],
            "appointment_id": appt["id"],
            "client_name": data.name,
            "to": data.phone,
            **s,
        })
    return {"appointment": appt, "sms_sent": True, "automations_scheduled": len(sms_to_log)}


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
    for r in rows:
        r["temperature"] = lead_temperature(r.get("created_at", ""))
    appt_count = await db.appointments.count_documents({"tech_id": user["id"]})
    total_tryons = await db.leads.count_documents({"tech_id": user["id"]}) + appt_count
    booked = appt_count
    conv_pct = round(100.0 * booked / total_tryons, 1) if total_tryons else 0.0
    followups = sum(r.get("follow_ups_sent", 0) for r in rows)
    # Win-back: leads last seen 30+ days ago with no booking
    cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    winback = [r for r in rows if r.get("created_at", "") <= cutoff and r.get("status") != "converted"]
    return {
        "leads": rows,
        "winback": winback,
        "stats": {"total_tryons": total_tryons, "booked": booked, "conversion_pct": conv_pct, "followups_sent": followups},
    }


@api.get("/tech/me/automations")
async def get_automations(user: dict = Depends(require_tech)):
    settings = user.get("automation_settings") or default_automation_settings()
    # Weekly stats for the automation center
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    sms_this_week = await db.sms_logs.count_documents({"tech_id": user["id"], "created_at": {"$gte": week_ago}})
    followups = await db.sms_logs.count_documents({"tech_id": user["id"], "type": {"$in": ["lead_day0", "lead_day2", "lead_day5", "lead_followup"]}, "created_at": {"$gte": week_ago}})
    reviews = await db.sms_logs.count_documents({"tech_id": user["id"], "type": "review_request", "created_at": {"$gte": week_ago}})
    return {"settings": settings, "stats": {"sms_this_week": sms_this_week, "followups_this_week": followups, "reviews_this_week": reviews}}


@api.put("/tech/me/automations")
async def update_automations(settings: AutomationSettings, user: dict = Depends(require_tech)):
    await db.users.update_one({"id": user["id"]}, {"$set": {"automation_settings": settings.model_dump()}})
    return {"settings": settings.model_dump()}


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

    # Activity feed: pull from sms_logs (automations) + recent appts + leads
    ACTIVITY_ICONS = {
        "booking_confirmation": "🎉",
        "reminder_24h": "📅",
        "reminder_1h": "⏰",
        "review_request": "⭐",
        "noshow_recovery": "😔",
        "lead_day0": "💬",
        "lead_day2": "💬",
        "lead_day5": "💬",
        "lead_followup": "💬",
        "winback": "💌",
    }
    ACTIVITY_LABELS = {
        "booking_confirmation": "Booking confirmation sent to",
        "reminder_24h": "24h reminder sent to",
        "reminder_1h": "1h reminder sent to",
        "review_request": "Review request sent to",
        "noshow_recovery": "No-show recovery SMS to",
        "lead_day0": "Follow-up Day 0 sent to",
        "lead_day2": "Follow-up Day 2 sent to",
        "lead_day5": "Follow-up Day 5 sent to",
        "lead_followup": "Follow-up sent to",
        "winback": "Win-back sent to",
    }
    recent_sms = await db.sms_logs.find(
        {"tech_id": user["id"], "delivered": True},
        {"_id": 0},
    ).sort("created_at", -1).limit(30).to_list(30)
    recent_appts = await db.appointments.find({"tech_id": user["id"]}, {"_id": 0}).sort("created_at", -1).limit(10).to_list(10)
    recent_leads = await db.leads.find({"tech_id": user["id"]}, {"_id": 0}).sort("created_at", -1).limit(10).to_list(10)
    feed = []
    for sms in recent_sms:
        t = sms.get("type", "lead_followup")
        name = sms.get("client_name") or "a client"
        if t == "booking_confirmation":
            continue  # will be rendered from appointment below with style context
        feed.append({
            "type": t,
            "icon": ACTIVITY_ICONS.get(t, "✨"),
            "text": f"{ACTIVITY_LABELS.get(t, 'Message sent to')} {name}",
            "when": sms.get("created_at"),
        })
    for a in recent_appts:
        feed.append({
            "type": "booking",
            "icon": "🎉",
            "text": f"{a['client_name']} just booked {a['style_name']} for {a['date']} at {a['time']}",
            "when": a["created_at"],
        })
    for l in recent_leads:
        feed.append({
            "type": "lead",
            "icon": "👀",
            "text": f"New lead: {l['name']} tried {l['style_name']}",
            "when": l["created_at"],
        })
    feed.sort(key=lambda x: x.get("when") or "", reverse=True)

    # Automation weekly stats
    week_ago_iso = start_week.isoformat()
    sms_this_week = await db.sms_logs.count_documents({"tech_id": user["id"], "created_at": {"$gte": week_ago_iso}})
    return {
        "leads_today": leads_today,
        "appts_this_week": appts_week,
        "revenue_this_month": revenue_month,
        "activity": feed[:12],
        "automation_stats": {"sms_this_week": sms_this_week},
        "today": today_str,
    }


@api.get("/tech/me/appointments/{appt_id}/sms")
async def tech_appt_sms(appt_id: str, user: dict = Depends(require_tech)):
    logs = await db.sms_logs.find(
        {"tech_id": user["id"], "appointment_id": appt_id},
        {"_id": 0},
    ).sort("created_at", 1).to_list(20)
    return {"sms": logs}


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
    # Most tried but NOT booked — include drop-off %
    most_tried_not_booked = []
    for r in lead_agg[:10]:
        sid = r["_id"]
        if sid in STYLE_MAP:
            tried = r["count"]
            booked = booked_map.get(sid, 0)
            total = tried + booked
            dropoff = round(100.0 * tried / total, 0) if total else 0
            most_tried_not_booked.append({
                "style_id": sid,
                "style_name": STYLE_MAP[sid]["name"],
                "tried": tried,
                "booked": booked,
                "dropoff_pct": dropoff,
                "image": STYLE_MAP[sid]["image"],
            })
    # Competitor intel: "what clients are walking in WITH" — from detected_style_id
    total_leads = await db.leads.count_documents({})
    no_polish = await db.leads.count_documents({"detected_style_id": None})
    det_counts = await db.leads.aggregate([
        {"$match": {"detected_style_id": {"$ne": None}}},
        {"$group": {"_id": "$detected_style_id", "count": {"$sum": 1}}},
    ]).to_list(50)
    # Map to categories for competitor intel
    category_map = {
        "Plain / No polish": no_polish,
        "Basic gel solid color": 0,
        "French tip": 0,
        "Acrylic": 0,
        "Other": 0,
    }
    for r in det_counts:
        sid = r["_id"]
        if sid not in STYLE_MAP:
            category_map["Other"] += r["count"]; continue
        style = STYLE_MAP[sid]
        if "french" in sid:
            category_map["French tip"] += r["count"]
        elif "acrylic" in sid or "polygel" in sid or "extensions" in sid:
            category_map["Acrylic"] += r["count"]
        elif style["category"] == "COLORS" or sid in {"classic-gel", "matte-gel", "nude-milky"}:
            category_map["Basic gel solid color"] += r["count"]
        else:
            category_map["Other"] += r["count"]
    walking_in_with = []
    total_for_pct = max(total_leads, 1)
    for label, count in category_map.items():
        walking_in_with.append({
            "label": label,
            "count": count,
            "pct": round(100.0 * count / total_for_pct, 0),
        })
    walking_in_with.sort(key=lambda x: x["pct"], reverse=True)

    # Also keep old most_detected shape for backwards compat
    most_detected = []
    for r in det_counts:
        if r["_id"] in STYLE_MAP:
            most_detected.append({
                "style_id": r["_id"],
                "style_name": STYLE_MAP[r["_id"]]["name"],
                "count": r["count"],
                "image": STYLE_MAP[r["_id"]]["image"],
            })
    most_detected.sort(key=lambda x: x["count"], reverse=True)
    most_detected = most_detected[:10]

    # Styles not offered by any client — with requested counts
    techs = await db.users.find({"role": "tech"}, {"_id": 0, "enabled_style_ids": 1}).to_list(500)
    offered = set()
    tech_offer_counts = {}
    for t in techs:
        for sid in t.get("enabled_style_ids", []):
            offered.add(sid)
            tech_offer_counts[sid] = tech_offer_counts.get(sid, 0) + 1
    # For each style, count how many techs offer it and how often it was "requested" (lead volume)
    req_agg = await db.leads.aggregate([
        {"$group": {"_id": "$style_id", "count": {"$sum": 1}}},
    ]).to_list(200)
    req_map = {r["_id"]: r["count"] for r in req_agg}
    gaps = []
    for s in STYLES:
        offer_count = tech_offer_counts.get(s["id"], 0)
        requested = req_map.get(s["id"], 0)
        if offer_count <= 1 and requested >= 1:
            gaps.append({
                "style_id": s["id"],
                "style_name": s["name"],
                "category": s["category"],
                "image": s["image"],
                "requested": requested,
                "tech_count": offer_count,
            })
    gaps.sort(key=lambda x: (-x["requested"], x["tech_count"]))
    gaps = gaps[:10]

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
        "walking_in_with": walking_in_with,
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

# Realistic mix of Canadian-sounding names for appointments (relative dates from today)
SEED_APPOINTMENTS = [
    ("Sarah Chen", "+14035551101", "chrome", 2, "14:00", "confirmed"),
    ("Emma Rodriguez", "+14035551102", "glazed-donut", 3, "10:30", "confirmed"),
    ("Olivia Park", "+14035551103", "french-ombre", 4, "16:15", "confirmed"),
    ("Mia Anderson", "+14035551104", "floral-art", 5, "12:00", "pending"),
    ("Chloe Thompson", "+14035551105", "rhinestone", 7, "13:45", "confirmed"),
    ("Zoe Williams", "+14035551106", "aura-nails", -2, "11:00", "completed"),
    ("Priya Sharma", "+14035551107", "swirl-art", -5, "15:30", "completed"),
    ("Noor El-Sayed", "+14035551108", "classic-red", -8, "12:30", "completed"),
    ("Amelie Tremblay", "+14035551109", "cat-eye", -12, "10:00", "completed"),
]

# Leads for Sophie — include realistic detected_style distribution for Style Intel competitor data
SEED_LEADS_SOPHIE = [
    ("Grace Miller", "+14035552001", "matte-gel", 0, None),
    ("Lily Davis", "+14035552002", "cat-eye", 1, "nude-milky"),
    ("Ava Johnson", "+14035552003", "butterfly", 1, None),
    ("Sophia Martinez", "+14035552004", "pearl-accents", 2, "classic-gel"),
    ("Mia Anderson", "+14035552005", "chrome", 2, None),
    ("Ella Wilson", "+14035552006", "glazed-donut", 3, "french-classic"),
    ("Harper Brown", "+14035552007", "gold-foil", 4, "classic-gel"),
    ("Amelia Garcia", "+14035552008", "french-chrome", 5, "acrylic-full"),
    ("Charlotte Lee", "+14035552009", "ombre-sunset", 6, "nude-milky"),
    ("Abigail Taylor", "+14035552010", "holographic", 7, None),
    ("Yuki Tanaka", "+14035552011", "chrome", 8, "classic-gel"),
    ("Rachel Goldberg", "+14035552012", "chrome", 9, "nude-milky"),
    ("Fatima Ahmed", "+14035552013", "cat-eye", 10, None),
    ("Hannah Cooper", "+14035552014", "glazed-donut", 12, "french-classic"),
    ("Zara Khan", "+14035552015", "cat-eye", 14, "nude-milky"),
    ("Nadia Patel", "+14035552016", "3d-art", 20, None),
    ("Evelyn Dubois", "+14035552017", "3d-art", 25, "classic-gel"),
    ("Scarlett Reid", "+14035552018", "velvet-suede", 30, None),
    ("Tessa MacDonald", "+14035552019", "chrome", 32, "nude-milky"),
    ("Leah Romano", "+14035552020", "aura-nails", 45, "classic-gel"),
]

SEED_LEADS_BELLA = [
    ("Elena Rossi", "+16475551101", "floral-art", 1, None),
    ("Maya Singh", "+16475551102", "3d-art", 2, "nude-milky"),
    ("Jasmine Wong", "+16475551103", "chrome", 3, "classic-gel"),
    ("Talia Bernard", "+16475551104", "glazed-donut", 5, "french-classic"),
    ("Sienna Okafor", "+16475551105", "butterfly", 8, None),
    ("Ines Moreau", "+16475551106", "pearl-accents", 12, "classic-gel"),
]

SEED_LEADS_JADE = [
    ("Ariana Cohen", "+16045551101", "aura-nails", 1, None),
    ("Chiara Ferri", "+16045551102", "velvet-suede", 4, "nude-milky"),
    ("Linh Nguyen", "+16045551103", "cat-eye", 6, None),
    ("Sarah Campbell", "+16045551104", "ombre-sunset", 9, "classic-gel"),
    ("Riley O'Brien", "+16045551105", "chrome", 14, "french-classic"),
]

SEED_LEADS_LUXE = [
    ("Josephine Leclerc", "+15145551101", "chrome", 2, None),
    ("Camille Dubois", "+15145551102", "glazed-donut", 4, "classic-gel"),
    ("Margot Beauchamp", "+15145551103", "french-chrome", 7, "nude-milky"),
    ("Elodie Gagnon", "+15145551104", "cat-eye", 10, None),
    ("Anaïs Bélanger", "+15145551105", "3d-art", 15, "classic-gel"),
]

SEED_LEADS_NAILEDIT = [
    ("Brooke Sinclair", "+14165551101", "glazed-donut", 3, "french-classic"),
    ("Danielle Kaur", "+14165551102", "holographic", 6, None),
    ("Paige Henderson", "+14165551103", "chrome", 11, "classic-gel"),
    ("Sloane Richardson", "+14165551104", "french-ombre", 17, "nude-milky"),
]


def _seed_tech_doc(email, password, slug, full_name, business, city, phone,
                   bio, photo, enabled, rating, reviews, plan, mrr, now):
    return {
        "id": str(uuid.uuid4()),
        "email": email,
        "password_hash": hash_password(password),
        "role": "tech",
        "slug": slug,
        "full_name": full_name,
        "business_name": business,
        "city": city,
        "phone": phone,
        "bio": bio,
        "profile_photo": photo,
        "enabled_style_ids": enabled,
        "portfolio": {},
        "style_prices": {},
        "rating": rating,
        "review_count": reviews,
        "plan": plan,
        "mrr": mrr,
        "automation_settings": default_automation_settings(),
        "created_at": now.isoformat(),
    }


async def _seed_leads_for(tech, leads_list, now):
    if await db.leads.count_documents({"tech_id": tech["id"]}) > 0:
        return
    for name, phone, sid, days_ago, detected in leads_list:
        style = STYLE_MAP.get(sid)
        if not style:
            continue
        created_at = (now - timedelta(days=days_ago, hours=random.randint(0, 23))).isoformat()
        await db.leads.insert_one({
            "id": str(uuid.uuid4()),
            "tech_id": tech["id"],
            "tech_slug": tech["slug"],
            "name": name,
            "phone": phone,
            "style_id": sid,
            "style_name": style["name"],
            "preview_image": style["image"],
            "detected_style_id": detected,
            "status": "not_booked",
            "follow_ups_sent": 0,
            "created_at": created_at,
        })


async def _seed_automation_sms_for(tech, now):
    """Pre-populate a handful of automation SMS logs so the activity feed feels alive."""
    if await db.sms_logs.count_documents({"tech_id": tech["id"]}) > 0:
        return
    # Look at this tech's leads & appts to create realistic auto-sent messages
    leads = await db.leads.find({"tech_id": tech["id"]}, {"_id": 0}).to_list(100)
    appts = await db.appointments.find({"tech_id": tech["id"]}, {"_id": 0}).to_list(100)
    entries = []
    for l in leads:
        try:
            created = datetime.fromisoformat(l["created_at"])
        except Exception:
            continue
        hours_ago = (now - created).total_seconds() / 3600
        # Day 0 follow-up (1h after try-on)
        if hours_ago >= 1:
            entries.append({
                "type": "lead_day0",
                "client_name": l["name"],
                "body": f"Hey {l['name']}! You tried {l['style_name']} nails on GlowLeads. {tech['business_name']} has a spot open this week -- want to grab it?",
                "created_at": (created + timedelta(hours=1)).isoformat(),
                "delivered": True,
                "lead_id": l["id"],
            })
        # Day 2
        if hours_ago >= 48:
            entries.append({
                "type": "lead_day2",
                "client_name": l["name"],
                "body": f"Still thinking about those {l['style_name']} nails? Here's a peek at what they'd look like on you. Book here.",
                "created_at": (created + timedelta(days=2)).isoformat(),
                "delivered": True,
                "lead_id": l["id"],
            })
        # Day 5
        if hours_ago >= 120:
            entries.append({
                "type": "lead_day5",
                "client_name": l["name"],
                "body": f"Last chance! {tech['business_name']}'s spots are filling up fast. Claim your {l['style_name']} appointment before it's gone.",
                "created_at": (created + timedelta(days=5)).isoformat(),
                "delivered": True,
                "lead_id": l["id"],
            })
        # 30-day win-back
        if hours_ago >= 24 * 30:
            entries.append({
                "type": "winback",
                "client_name": l["name"],
                "body": f"Hey {l['name']}! It's been a while -- we miss you. Come back and try our new look. Book here.",
                "created_at": (created + timedelta(days=30)).isoformat(),
                "delivered": True,
                "lead_id": l["id"],
            })
    for a in appts:
        try:
            appt_dt = datetime.fromisoformat(f"{a['date']}T{a['time']}:00+00:00")
        except Exception:
            continue
        created_at = a.get("created_at", now.isoformat())
        entries.append({
            "type": "booking_confirmation",
            "client_name": a["client_name"],
            "body": f"Hey {a['client_name']}! You're booked with {tech['business_name']} for {a['style_name']} nails on {a['date']} at {a['time']}.",
            "created_at": created_at,
            "appointment_id": a["id"],
            "delivered": True,
        })
        # 24h reminder
        when = appt_dt - timedelta(hours=24)
        entries.append({
            "type": "reminder_24h",
            "client_name": a["client_name"],
            "body": f"Hey {a['client_name']}, you're booked with {tech['business_name']} tomorrow at {a['time']} for {a['style_name']} nails.",
            "created_at": when.isoformat(),
            "appointment_id": a["id"],
            "delivered": when <= now,
        })
        # 1h reminder
        when = appt_dt - timedelta(hours=1)
        entries.append({
            "type": "reminder_1h",
            "client_name": a["client_name"],
            "body": f"See you in 1 hour {a['client_name']}! {tech['business_name']} is ready for your {a['style_name']} nails.",
            "created_at": when.isoformat(),
            "appointment_id": a["id"],
            "delivered": when <= now,
        })
        # Review request (2h after completed)
        if a.get("status") == "completed":
            when = appt_dt + timedelta(hours=2)
            entries.append({
                "type": "review_request",
                "client_name": a["client_name"],
                "body": f"Thanks for coming in {a['client_name']}! Hope you love your {a['style_name']} nails. Leave a quick review.",
                "created_at": when.isoformat(),
                "appointment_id": a["id"],
                "delivered": when <= now,
            })
    for e in entries:
        await db.sms_logs.insert_one({
            "id": str(uuid.uuid4()),
            "tech_id": tech["id"],
            "to": "",
            **e,
        })


async def seed_database():
    now = datetime.now(timezone.utc)

    # Clean up stale TEST_ data from any previous testing runs
    await db.leads.delete_many({"name": {"$regex": "^TEST_", "$options": "i"}})
    await db.appointments.delete_many({"client_name": {"$regex": "^TEST_", "$options": "i"}})
    await db.users.delete_many({"email": {"$regex": "^TEST_", "$options": "i"}})

    # Ensure automation_settings + Canadian cities on existing tech docs (one-time migration)
    async for t in db.users.find({"role": "tech"}):
        updates = {}
        if "automation_settings" not in t:
            updates["automation_settings"] = default_automation_settings()
        if "style_prices" not in t:
            updates["style_prices"] = {}
        # Reset to Canadian cities + bios
        if t.get("email") == "sophie@glowleads.com":
            if t.get("city") != "Calgary, AB":
                updates["city"] = "Calgary, AB"
            if "LA-based" in (t.get("bio") or "") or "Los Angeles" in (t.get("bio") or ""):
                updates["bio"] = "Calgary nail artist specializing in Chrome, Aura and French designs. 8+ years experience."
        if t.get("email") == "bella@glowleads.com" and "Brooklyn" in (t.get("city") or ""):
            updates["city"] = "Toronto, ON"
            updates["business_name"] = "Bella Nails Toronto"
        if t.get("email") == "jade@glowleads.com" and "Miami" in (t.get("city") or ""):
            updates["city"] = "Vancouver, BC"
            updates["business_name"] = "Jade's Nail Lounge"
        if updates:
            await db.users.update_one({"id": t["id"]}, {"$set": updates})

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

    # Sophie — primary demo tech (Calgary)
    sophie = await db.users.find_one({"email": "sophie@glowleads.com"})
    if not sophie:
        sophie = _seed_tech_doc(
            "sophie@glowleads.com", "sophie123", "sophie",
            "Sophie Laurent", "Glow by Sophie", "Calgary, AB", "+14035550100",
            "Calgary nail artist specializing in Chrome, Aura and French designs. 8+ years experience.",
            "https://images.unsplash.com/photo-1713552566168-89c00fd622cf?w=400&q=80",
            SEED_STYLES_FOR_SOPHIE, 4.9, 342, "pro", 99, now,
        )
        await db.users.insert_one(sophie)
        logger.info("Seeded tech sophie@glowleads.com / sophie123")

    bella = await db.users.find_one({"email": "bella@glowleads.com"})
    if not bella:
        bella = _seed_tech_doc(
            "bella@glowleads.com", "bella123", "bella",
            "Bella Rivera", "Bella Nails Toronto", "Toronto, ON", "+14165550111",
            "Toronto's go-to for floral and 3D nail art.",
            "https://images.unsplash.com/photo-1595475207225-428b62bda831?w=400&q=80",
            SEED_STYLES_FOR_SOPHIE[:20], 4.8, 198, "starter", 49, now,
        )
        await db.users.insert_one(bella)
        logger.info("Seeded tech bella@glowleads.com / bella123")

    jade = await db.users.find_one({"email": "jade@glowleads.com"})
    if not jade:
        jade = _seed_tech_doc(
            "jade@glowleads.com", "jade123", "jade",
            "Jade Wilson", "Jade's Nail Lounge", "Vancouver, BC", "+16045550122",
            "Vancouver nail artist -- west coast vibes only.",
            "https://images.unsplash.com/photo-1580618672591-eb180b1a973f?w=400&q=80",
            SEED_STYLES_FOR_SOPHIE[:15], 4.7, 86, "starter", 49, now,
        )
        await db.users.insert_one(jade)
        logger.info("Seeded tech jade@glowleads.com / jade123")

    luxe = await db.users.find_one({"email": "luxe@glowleads.com"})
    if not luxe:
        luxe = _seed_tech_doc(
            "luxe@glowleads.com", "luxe123", "luxe-mtl",
            "Camille Tremblay", "Luxe Nails MTL", "Montreal, QC", "+15145550133",
            "Salon de manucure haut de gamme à Montréal.",
            "https://images.unsplash.com/photo-1632345031435-8727f6897d53?w=400&q=80",
            SEED_STYLES_FOR_SOPHIE[:25], 4.9, 156, "pro", 99, now,
        )
        await db.users.insert_one(luxe)
        logger.info("Seeded tech luxe@glowleads.com / luxe123")

    nailedit = await db.users.find_one({"email": "nailedit@glowleads.com"})
    if not nailedit:
        nailedit = _seed_tech_doc(
            "nailedit@glowleads.com", "nailedit123", "nailed-it-yyc",
            "Taylor Reid", "Nailed It YYC", "Calgary, AB", "+14035550144",
            "Calgary's trendiest nail studio for Y2K and chrome looks.",
            "https://images.unsplash.com/photo-1601612628452-9e99ced43524?w=400&q=80",
            SEED_STYLES_FOR_SOPHIE[:18], 4.6, 74, "starter", 49, now,
        )
        await db.users.insert_one(nailedit)
        logger.info("Seeded tech nailedit@glowleads.com / nailedit123")

    # Appointments for Sophie (relative to today)
    sophie = await db.users.find_one({"email": "sophie@glowleads.com"})
    if await db.appointments.count_documents({"tech_id": sophie["id"]}) == 0:
        for name, phone, sid, day_offset, time_str, status in SEED_APPOINTMENTS:
            style = STYLE_MAP[sid]
            appt_date = (now + timedelta(days=day_offset)).date().isoformat()
            created_offset = abs(day_offset) + random.randint(1, 6)
            await db.appointments.insert_one({
                "id": str(uuid.uuid4()),
                "tech_id": sophie["id"],
                "tech_slug": sophie["slug"],
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
                "created_at": (now - timedelta(days=created_offset)).isoformat(),
            })
        logger.info("Seeded %d appointments for Sophie", len(SEED_APPOINTMENTS))

    # Add a few appointments for other techs so analytics has signal
    for tech, count in [(bella, 4), (jade, 3), (luxe, 5), (nailedit, 2)]:
        tech = await db.users.find_one({"id": tech["id"]})  # refresh
        if await db.appointments.count_documents({"tech_id": tech["id"]}) > 0:
            continue
        sids = tech.get("enabled_style_ids", [])[:8]
        for i in range(count):
            sid = random.choice(sids) if sids else "classic-gel"
            style = STYLE_MAP[sid]
            day_offset = random.choice([-10, -6, -3, 1, 4, 8])
            appt_date = (now + timedelta(days=day_offset)).date().isoformat()
            await db.appointments.insert_one({
                "id": str(uuid.uuid4()),
                "tech_id": tech["id"],
                "tech_slug": tech["slug"],
                "client_name": random.choice([
                    "Jordan Lee", "Sam Patel", "Riley Chen", "Quinn Tran",
                    "Avery Johnson", "Morgan Singh", "Kai Nakamura", "Sky Evans",
                ]),
                "client_phone": "+1" + "".join([str(random.randint(0, 9)) for _ in range(10)]),
                "style_id": sid,
                "style_name": style["name"],
                "style_category": style["category"],
                "preview_image": style["image"],
                "date": appt_date,
                "time": f"{random.randint(9, 17)}:00",
                "status": "completed" if day_offset < 0 else "confirmed",
                "price": style["price_range"]["low"],
                "created_at": (now - timedelta(days=abs(day_offset) + random.randint(1, 5))).isoformat(),
            })

    # Leads (re-fetch techs)
    sophie = await db.users.find_one({"email": "sophie@glowleads.com"})
    bella = await db.users.find_one({"email": "bella@glowleads.com"})
    jade = await db.users.find_one({"email": "jade@glowleads.com"})
    luxe = await db.users.find_one({"email": "luxe@glowleads.com"})
    nailedit = await db.users.find_one({"email": "nailedit@glowleads.com"})
    await _seed_leads_for(sophie, SEED_LEADS_SOPHIE, now)
    await _seed_leads_for(bella, SEED_LEADS_BELLA, now)
    await _seed_leads_for(jade, SEED_LEADS_JADE, now)
    await _seed_leads_for(luxe, SEED_LEADS_LUXE, now)
    await _seed_leads_for(nailedit, SEED_LEADS_NAILEDIT, now)

    # Pre-populated automation SMS logs for realism
    for t in [sophie, bella, jade, luxe, nailedit]:
        if t:
            await _seed_automation_sms_for(t, now)


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
