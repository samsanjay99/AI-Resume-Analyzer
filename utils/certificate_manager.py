"""
Certificate Manager
Handles video progress tracking, completion validation, and certificate generation.
"""
import os
import uuid
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io
from config.database import get_database_connection


# ── Database Setup ────────────────────────────────────────────────────────────

_tables_ready = False

def setup_certificate_tables():
    """Create video_progress and certificates tables if they don't exist. Runs once per process."""
    global _tables_ready
    if _tables_ready:
        return
    try:
        with get_database_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS video_progress (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    video_id TEXT NOT NULL,
                    watch_time INTEGER DEFAULT 0,
                    completion_status BOOLEAN DEFAULT FALSE,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, video_id)
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS certificates (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    skill_name TEXT NOT NULL,
                    video_id TEXT NOT NULL,
                    certificate_id TEXT UNIQUE NOT NULL,
                    date_generated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    file_path TEXT,
                    UNIQUE(user_id, video_id)
                )
            """)
            conn.commit()
        _tables_ready = True
    except Exception as e:
        print(f"Certificate table setup error: {e}")


# ── Progress Tracking ─────────────────────────────────────────────────────────

def save_progress(user_id: int, video_id: str, watch_time: int, completed: bool):
    """Upsert watch progress for a user+video."""
    try:
        with get_database_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO video_progress (user_id, video_id, watch_time, completion_status, last_updated)
                VALUES (%s, %s, %s, %s, NOW())
                ON CONFLICT (user_id, video_id)
                DO UPDATE SET
                    watch_time = GREATEST(video_progress.watch_time, EXCLUDED.watch_time),
                    completion_status = video_progress.completion_status OR EXCLUDED.completion_status,
                    last_updated = NOW()
            """, (user_id, video_id, watch_time, completed))
            conn.commit()
            return True
    except Exception as e:
        print(f"Save progress error: {e}")
        return False


def get_progress(user_id: int, video_id: str) -> dict:
    """Get watch progress for a user+video."""
    try:
        with get_database_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT watch_time, completion_status
                FROM video_progress
                WHERE user_id=%s AND video_id=%s
            """, (user_id, video_id))
            row = cur.fetchone()
            if row:
                return {"watch_time": row[0], "completed": row[1]}
    except Exception as e:
        print(f"Get progress error: {e}")
    return {"watch_time": 0, "completed": False}


def is_completed(user_id: int, video_id: str) -> bool:
    return get_progress(user_id, video_id)["completed"]


def get_all_completed_video_ids(user_id: int) -> set:
    """Return a set of all video_ids the user has completed — single DB call."""
    try:
        with get_database_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT video_id FROM video_progress WHERE user_id=%s AND completion_status=TRUE",
                (user_id,)
            )
            return {row[0] for row in cur.fetchall()}
    except Exception:
        return set()


# ── Certificate Generation ────────────────────────────────────────────────────

def _load_font(filename: str, size: int) -> ImageFont.FreeTypeFont:
    """Load a font from assets/fonts/, fall back to system fonts, then default."""
    candidates = [
        os.path.join("assets", "fonts", filename),
        # System fallbacks
        f"C:/Windows/Fonts/{filename}",
        f"/usr/share/fonts/truetype/{filename}",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    # Last resort — PIL default (no size control)
    return ImageFont.load_default()


def _center_text(draw: ImageDraw.Draw, text: str, font, y: int, color, W: int,
                 max_width: int = None, min_size: int = 20):
    """Draw center-aligned text. Shrinks font if text exceeds max_width."""
    if max_width and hasattr(font, 'path'):
        size = font.size
        while size > min_size:
            bbox = draw.textbbox((0, 0), text, font=font)
            if (bbox[2] - bbox[0]) <= max_width:
                break
            size -= 2
            try:
                font = ImageFont.truetype(font.path, size)
            except Exception:
                break

    bbox = draw.textbbox((0, 0), text, font=font)
    tw   = bbox[2] - bbox[0]
    x    = (W - tw) / 2
    draw.text((x, y), text, font=font, fill=color)
    return font


def generate_certificate(user_name: str, skill_name: str, user_id: int, video_id: str) -> dict:
    """
    Generate a certificate PNG + PDF using Pillow with custom fonts.
    Returns dict with keys: certificate_id, png_bytes, pdf_bytes, date, already_existed
    """
    existing = get_certificate(user_id, video_id)
    if existing:
        return {**existing, "already_existed": True}

    cert_id  = "SRAI-" + str(uuid.uuid4())[:8].upper()
    date_str = datetime.now().strftime("%B %d, %Y")

    template_path = os.path.join("assets", "certificate_template.png")
    if not os.path.exists(template_path):
        raise FileNotFoundError("certificate_template.png not found in assets/")

    img  = Image.open(template_path).convert("RGBA")
    W, H = img.size
    draw = ImageDraw.Draw(img)

    # ── Fonts ─────────────────────────────────────────────────────────────────
    font_name   = _load_font("GreatVibes.ttf",      90)
    font_course = _load_font("PlayfairDisplay.ttf",  38)
    font_small  = _load_font("Lato-Regular.ttf",     23)

    # ── User name (centered, y=390, UPPERCASE) ───────────────────────────────
    _center_text(draw, user_name.upper(), font_name, 390,
                 "#0b2c4d", W, max_width=int(W * 0.65))

    # ── Course name (centered, y=550, UPPERCASE) ──────────────────────────────
    _center_text(draw, skill_name.upper(), font_course, 550,
                 "#0b2c4d", W, max_width=int(W * 0.70))

    # ── Date (573, 793) ───────────────────────────────────────────────────────
    draw.text((573, 793), date_str, font=font_small, fill="#0b2c4d")

    # ── Certificate ID (914, 793) ─────────────────────────────────────────────
    draw.text((914, 793), cert_id, font=font_small, fill="#0b2c4d")

    # ── Export ────────────────────────────────────────────────────────────────
    rgb_img = img.convert("RGB")

    png_buf = io.BytesIO()
    rgb_img.save(png_buf, format="PNG")
    png_bytes = png_buf.getvalue()

    pdf_buf = io.BytesIO()
    rgb_img.save(pdf_buf, format="PDF", resolution=150)
    pdf_bytes = pdf_buf.getvalue()

    os.makedirs("certificates", exist_ok=True)
    file_path = f"certificates/{user_id}_{cert_id}.png"
    rgb_img.save(file_path)

    try:
        with get_database_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO certificates (user_id, skill_name, video_id, certificate_id, date_generated, file_path)
                VALUES (%s, %s, %s, %s, NOW(), %s)
                ON CONFLICT (user_id, video_id) DO NOTHING
            """, (user_id, skill_name, video_id, cert_id, file_path))
            conn.commit()
    except Exception as e:
        print(f"Certificate DB save error: {e}")

    return {
        "certificate_id": cert_id,
        "png_bytes": png_bytes,
        "pdf_bytes": pdf_bytes,
        "date": date_str,
        "already_existed": False,
    }


def get_certificate(user_id: int, video_id: str) -> dict | None:
    """Return existing certificate data if already generated."""
    try:
        with get_database_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT certificate_id, skill_name, date_generated, file_path
                FROM certificates
                WHERE user_id=%s AND video_id=%s
            """, (user_id, video_id))
            row = cur.fetchone()
            if row:
                cert_id, skill, date_gen, file_path = row
                png_bytes, pdf_bytes = None, None
                if file_path and os.path.exists(file_path):
                    with open(file_path, "rb") as f:
                        png_bytes = f.read()
                    buf = io.BytesIO()
                    Image.open(file_path).convert("RGB").save(buf, format="PDF", resolution=150)
                    pdf_bytes = buf.getvalue()
                return {
                    "certificate_id": cert_id,
                    "skill_name": skill,
                    "date": date_gen.strftime("%B %d, %Y") if date_gen else "",
                    "png_bytes": png_bytes,
                    "pdf_bytes": pdf_bytes,
                }
    except Exception as e:
        print(f"Get certificate error: {e}")
    return None


def _delete_certificate(user_id: int, video_id: str):
    """Delete a certificate record so it can be regenerated."""
    try:
        with get_database_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "DELETE FROM certificates WHERE user_id=%s AND video_id=%s",
                (user_id, video_id)
            )
            conn.commit()
    except Exception as e:
        print(f"Delete certificate error: {e}")


def get_user_certificates(user_id: int) -> list:
    """Return all certificates for a user."""
    try:
        with get_database_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT certificate_id, skill_name, date_generated
                FROM certificates WHERE user_id=%s
                ORDER BY date_generated DESC
            """, (user_id,))
            rows = cur.fetchall()
            return [{"certificate_id": r[0], "skill_name": r[1], "date": r[2]} for r in rows]
    except Exception as e:
        print(f"Get user certificates error: {e}")
    return []
