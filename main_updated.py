#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚡ HPVIRUS SELF — سلف‌بات سروش‌پلاس — نسخه ارتقایافته v2.0.0
============================================================

این فایل نسخهٔ کامل، اصلاح‌شده و ارتقایافتهٔ سلف‌بات سروش‌پلاس است.

پیش‌نیازها
----------
- Python 3.9 یا جدیدتر (روی 3.12 تست شده)
- کتابخانهٔ splusthon (همان محیطی که قبلاً سلف با آن اجرا می‌شده)
- هیچ وابستگی جدیدی لازم نیست؛ همهٔ قابلیت‌های جدید فقط با کتابخانهٔ استاندارد پایتون کار می‌کنند.

اجرا
----
    python main_updated.py

دستورها
-------
    داخل سروش پیام /help بفرست.

ساختار فایل
-----------
    بخش ۱  : ورودی‌ها، ثابت‌ها، لاگ، ظاهر ترمینال، تاریخ شمسی
    بخش ۲  : ذخیره‌سازی (اتمیک)، ابزارهای عمومی، آمار، ماشین‌حساب، سرگرمی، فونت
    بخش ۳  : پروفایل/ساعت، مدیریت تسک‌ها و یادآوری‌ها، توابع سروش
    بخش ۴  : سیستم دستورها (رجیستری) و پیاده‌سازی همهٔ دستورها
    بخش ۵  : هندلر پیام‌ها، خوش‌آمد/خداحافظ، main و نقطهٔ ورود
"""

from __future__ import annotations

import asyncio
import ast
import json
import logging
import math
import operator
import os
import random
import re
import secrets
import string
import sys
import time
from datetime import date, datetime, timedelta
from logging.handlers import RotatingFileHandler
from typing import Any, Callable, Dict, List, Optional, Tuple

# ─────────────────────────────────────────────────────────────────────────────
# بخش ۱-۱: ورودی کتابخانهٔ splusthon (محافظت‌شده)
# ---------------------------------------------------------------------------
# اگر splusthon نصب نباشد، برنامه به‌جای خطای ImportError با پیام فارسیِ
# خوانا خارج می‌شود و ماژول همچنان برای تست قابل import است.
# ─────────────────────────────────────────────────────────────────────────────

try:
    from splusthon import SoroushClient, events
    from splusthon.sessions import StringSession
    from splusthon.tl.functions.account import UpdateProfileRequest
    from splusthon.tl.functions.photos import GetUserPhotosRequest
    from splusthon.tl.functions.users import GetFullUserRequest
    from splusthon.tl.functions.upload import GetFileRequest
    from splusthon.tl.types import InputPhotoFileLocation

    HAS_SPLUSTHON = True
except Exception:  # pragma: no cover - فقط وقتی splusthon در دسترس نیست
    HAS_SPLUSTHON = False
    SoroushClient = None  # type: ignore[assignment]
    events = None  # type: ignore[assignment]
    StringSession = None  # type: ignore[assignment]
    UpdateProfileRequest = None  # type: ignore[assignment]
    GetUserPhotosRequest = None  # type: ignore[assignment]
    GetFullUserRequest = None  # type: ignore[assignment]
    GetFileRequest = None  # type: ignore[assignment]
    InputPhotoFileLocation = None  # type: ignore[assignment]

# ─────────────────────────────────────────────────────────────────────────────
# بخش ۱-۲: ثابت‌ها
# ─────────────────────────────────────────────────────────────────────────────

__version__ = "2.0.0"
VERSION = __version__
BRAND = "HPVIRUS SELF"
CREATOR = "@HPVIRUS"

SESSION_FILE = "session.txt"
DATA_FILE = "self_data.json"
LOG_FILE = "self_bot.log"
START_TIME = datetime.now()

# سقف‌های ایمن (برای جلوگیری از فلود و فشار روی سرور)
MAX_DELETE_PER_OP = 5000        # بیشینهٔ پیام در هر عملیات پاک‌سازی
MAX_PURGE = 1000                # سقف /purge در هر اجرا
MAX_SCAN_MESSAGES = 5000        # سقف اسکن پیام در top/cleanuser
MAX_TOP_LIMIT = 50              # سقف /top
MAX_SPAM_COUNT = 500            # سقف تعداد تکرار هر عملیات spam/rep
MAX_SHOMARESH = 100             # سقف /shomaresh (مثل قبل)
MAX_REMINDER_SECONDS = 30 * 86400   # سقف زمان‌بندی یک یادآوری
MIN_SDEL_SECONDS = 3
MAX_SDEL_SECONDS = 86400
STATS_HISTORY_KEEP_DAYS = 60    # نگهداری تاریخچهٔ آمار (روز)

CLOCK_FONTS: Dict[int, str] = {
    1: "%H:%M",
    2: "⌚ %H:%M",
    3: "⏰ %H:%M",
    4: "【%H:%M】",
    5: "『%H:%M』",
    6: "〔%H:%M〕",
    7: "「%H:%M」",
    8: "• %H:%M •",
    9: "┃ %H:%M ┃",
    10: "◈ %H:%M ◈",
    # فونت‌های جدید (۱۱ تا ۱۶) — اضافه‌شده در نسخهٔ ۲
    11: "✦ %H:%M ✦",
    12: "⟨ %H:%M ⟩",
    13: "★ %H:%M ★",
    14: "⊹ %H:%M ⊹",
    15: "〖 %H:%M 〗",
    16: "⌈ %H:%M ⌉",
}

STAT_KEYS: Tuple[str, ...] = (
    "messages_processed",
    "replies_sent",
    "deleted_messages",
    "kicks",
    "bans",
    "mutes",
    "invites_success",
    "invites_failed",
    "invites_skipped",
)

DEFAULT_DATA: Dict[str, Any] = {
    "auto_reply": False,
    "auto_message": "الان در دسترس نیستم، بعداً جواب می‌دم.",
    # کلیدهای جدید نسخهٔ ۲ — مقادیر پیش‌فرض دقیقاً رفتار نسخهٔ قبل را حفظ می‌کنند
    "auto_reply_bots": True,       # قبلاً به همه (حتی ربات‌ها) جواب می‌داد
    "auto_reply_groups": True,     # قبلاً در گروه‌ها هم جواب می‌داد
    "auto_reply_cooldown": 0,      # 0 = بدون محدودیت (رفتار قبلی)
    "notes": [],
    "display_name": "",
    "name_clock": False,
    "clock_position": "lastname",
    "clock_font": 1,
    "spam_slots": [""] * 8,
    "rep_slots": [""] * 8,
    "triggers": [],
    "welcome_enabled": False,
    "welcome_message": "خوش اومدی {name} 👋",
    "goodbye_enabled": False,
    "goodbye_message": "خداحافظ {name} 👋",
    "stats": {},
    "invite_state": None,
    "reminders": [],               # یادآوری‌های ماندگار (جدید)
    "version": VERSION,
}

# ─────────────────────────────────────────────────────────────────────────────
# بخش ۱-۳: سیستم لاگ (جایگزین سکوت مطلق؛ خطاها هم در ترمینال هم در فایل)
# ─────────────────────────────────────────────────────────────────────────────

log = logging.getLogger("self")
log.addHandler(logging.NullHandler())


class ColorFormatter(logging.Formatter):
    """فرمت رنگی برای ترمینال؛ در فایل بدون رنگ نوشته می‌شود."""

    COLORS = {
        "DEBUG": "\033[90m",
        "INFO": "\033[96m",
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "CRITICAL": "\033[1;91m",
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        colored = record.levelname
        if self.COLORS.get(record.levelname) and sys.stdout.isatty():
            colored = f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"
        clone = logging.makeLogRecord(record.__dict__)
        clone.levelname = colored
        return super(ColorFormatter, self).format(clone)


def setup_logging() -> logging.Logger:
    """راه‌اندازی لاگ کنسول + فایل چرخشی (یک‌بار)."""
    if any(not isinstance(h, logging.NullHandler) for h in log.handlers):
        return log

    log.setLevel(logging.INFO)
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(ColorFormatter("%(asctime)s │ %(levelname)s │ %(message)s", "%H:%M:%S"))
    log.addHandler(console)

    try:
        file_handler = RotatingFileHandler(
            LOG_FILE, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
        )
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s │ %(levelname)s │ %(message)s")
        )
        log.addHandler(file_handler)
    except OSError as exc:
        log.warning("فایل لاگ ساخته نشد: %s", exc)

    log.propagate = False
    return log


# ─────────────────────────────────────────────────────────────────────────────
# بخش ۱-۴: ظاهر ترمینال (بنر شروع) و ظاهر پیام‌ها (کارت‌ساز)
# ─────────────────────────────────────────────────────────────────────────────

if os.name == "nt":  # فعال‌سازی رنگ ANSI در ویندوز
    os.system("")

_A = "\033[1;96m"   # آبی روشن بولد
_B = "\033[1;95m"   # صورتی بولد
_C = "\033[1;93m"   # زرد بولد
_R = "\033[0m"


def term_banner() -> None:
    """بنر شروع زیبا در ترمینال."""
    print(f"""{_C}╔══════════════════════════════════════════════╗
║          {_A}⚡ H P V I R U S  S E L F ⚡{_C}          ║
║        {_B}Soroush Plus Self-Bot · v{VERSION}{_C}         ║
╚══════════════════════════════════════════════╝{_R}""")
    print(f"{_A}  👑 سازنده: {CREATOR}{_R}")
    print(f"{_B}  📦 نسخه: {VERSION}   🕐 شروع: {START_TIME:%Y/%m/%d - %H:%M:%S}{_R}")
    print(f"{_C}  {'─' * 46}{_R}")


def card_title(icon: str, title: str) -> str:
    """تیتر کارت پیام: ━━━ ⏰ عنوان ━━━"""
    return f"━━━━ {icon} {title} ━━━"


def brand_footer() -> str:
    """پانویس برند برای کارت‌های بزرگ."""
    return f"┈┈┈┈┈┈ ⚡ {BRAND} ┈┈┈┈┈┈"


# ─────────────────────────────────────────────────────────────────────────────
# بخش ۱-۵: تاریخ شمسی (بدون هیچ وابستگی بیرونی) و رقم فارسی
# ─────────────────────────────────────────────────────────────────────────────

_FA_DIGITS_TRANS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
_FA_DIGITS_REVERSE = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")

JALALI_MONTHS = [
    "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند",
]
WEEKDAYS_FA = [
    "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه", "شنبه", "یکشنبه",
]


def to_persian_digits(value: str) -> str:
    """تبدیل ارقام لاتین به فارسی: 1404 → ۱۴۰۴"""
    return str(value).translate(_FA_DIGITS_TRANS)


def from_persian_digits(value: str) -> str:
    """تبدیل ارقام فارسی/عربی به لاتین (برای ورودی دستورها)."""
    return str(value).translate(_FA_DIGITS_REVERSE)


def gregorian_to_jalali(gy: int, gm: int, gd: int) -> Tuple[int, int, int]:
    """تبدیل تاریخ میلادی به شمسی (الگوریتم استاندارد جلالی)."""
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    gy2 = gy - 1600
    gm2 = gm - 1
    gd2 = gd - 1

    g_day_no = 365 * gy2 + (gy2 + 3) // 4 - (gy2 + 99) // 100 + (gy2 + 399) // 400
    g_day_no += g_d_m[gm2]
    if gm2 > 1 and ((gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0)):
        g_day_no += 1
    g_day_no += gd2

    j_day_no = g_day_no - 79
    j_np = j_day_no // 12053
    j_day_no %= 12053
    jy = 979 + 33 * j_np + 4 * (j_day_no // 1461)
    j_day_no %= 1461

    if j_day_no >= 366:
        jy += (j_day_no - 1) // 365
        j_day_no = (j_day_no - 1) % 365

    if j_day_no < 186:
        jm = 1 + j_day_no // 31
        jd = 1 + j_day_no % 31
    else:
        jm = 7 + (j_day_no - 186) // 30
        jd = 1 + (j_day_no - 186) % 30

    return jy, jm, jd


def jalali_today_text(with_time: bool = False) -> str:
    """متن تاریخ امروز به شمسی، مثال: پنجشنبه ۱۵ آبان ۱۴۰۴"""
    now = datetime.now()
    jy, jm, jd = gregorian_to_jalali(now.year, now.month, now.day)
    weekday = WEEKDAYS_FA[now.weekday()]
    text = f"{weekday} {to_persian_digits(jd)} {JALALI_MONTHS[jm - 1]} {to_persian_digits(jy)}"
    if with_time:
        text += f" — ساعت {to_persian_digits(now.strftime('%H:%M:%S'))}"
    return text


# ═════════════════════════════════════════════════════════════════════════════
# بخش ۲: ذخیره‌سازی، ابزارهای عمومی، آمار، ماشین‌حساب، سرگرمی، فونت
# ═════════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────────────
# بخش ۲-۱: وضعیت سراسری
# ─────────────────────────────────────────────────────────────────────────────

data: Optional[Dict[str, Any]] = None
scheduled_tasks = set()
operation_tasks: Dict[str, set] = {
    "spam": set(),
    "rep": set(),
    "shomaresh": set(),
    "moderation": set(),
    "invite": set(),
}
name_clock_task: Optional[asyncio.Task] = None

# برای ذخیرهٔ بهینه: به‌جای نوشتن دیسک روی «هر» پیام، تغییرات صف می‌شوند
_DIRTY = {"flag": False}
_last_auto_reply: Dict[str, float] = {}   # cooldown پاسخگوی خودکار per chat


def mark_dirty() -> None:
    """علامت‌گذاری اینکه داده تغییر کرده (نوشتن به‌صورت صفحه‌بندی‌شده انجام می‌شود)."""
    _DIRTY["flag"] = True


def flush_if_dirty(force: bool = False) -> None:
    """اگر تغییر صف‌شده وجود دارد، همین حالا روی دیسک بنویس."""
    if data is not None and (_DIRTY["flag"] or force):
        try:
            save_data(data)
        except OSError as exc:
            log.error("ذخیرهٔ داده ناموفق بود: %s", exc)
        _DIRTY["flag"] = False


# ─────────────────────────────────────────────────────────────────────────────
# بخش ۲-۲: ذخیره‌سازی اتمیک + بازیابی با پشتیبان‌گیری از فایل خراب
# ─────────────────────────────────────────────────────────────────────────────

def _deep_default(value: Any) -> Any:
    return json.loads(json.dumps(value))


def load_data() -> Dict[str, Any]:
    """خواندن self_data.json + ادغام کلیدهای جدید + پشتیبان از فایل خراب."""
    global data

    if not os.path.exists(DATA_FILE):
        fresh = _deep_default(DEFAULT_DATA)
        save_data(fresh)
        data = fresh
        return fresh

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            loaded = json.load(file)
        if not isinstance(loaded, dict):
            raise ValueError("ساختار داده باید dict باشد")
    except (json.JSONDecodeError, ValueError, OSError) as exc:
        # قبلاً فایل خراب بی‌صدا دور ریخته می‌شد و اطلاعاتها از بین می‌رفت؛
        # حالا از فایل خراب پشتیبان گرفته می‌شود.
        backup = f"{DATA_FILE}.corrupt-{datetime.now():%Y%m%d-%H%M%S}"
        try:
            os.replace(DATA_FILE, backup)
            log.error("فایل داده خراب بود؛ پشتیبان گرفته شد: %s (%s)", backup, exc)
        except OSError:
            log.error("فایل داده خراب بود و پشتیبان‌گیری هم ناموفق بود: %s", exc)
        fresh = _deep_default(DEFAULT_DATA)
        save_data(fresh)
        data = fresh
        return fresh

    # ادغام کلیدهای پیش‌فرض (نسخه‌های جدید بدون از دست رفتن دادهٔ قدیمی)
    for key, value in DEFAULT_DATA.items():
        if key not in loaded:
            loaded[key] = _deep_default(value)

    # نرمال‌سازی مقادیر حساس
    loaded["spam_slots"] = (loaded.get("spam_slots") or [""] * 8)[:8]
    loaded["rep_slots"] = (loaded.get("rep_slots") or [""] * 8)[:8]
    loaded["spam_slots"] += [""] * (8 - len(loaded["spam_slots"]))
    loaded["rep_slots"] += [""] * (8 - len(loaded["rep_slots"]))
    loaded["triggers"] = loaded.get("triggers") or []
    loaded["notes"] = loaded.get("notes") or []
    loaded["stats"] = loaded.get("stats") or {}
    loaded["reminders"] = loaded.get("reminders") or []
    if not isinstance(loaded["reminders"], list):
        loaded["reminders"] = []
    loaded["invite_state"] = loaded.get("invite_state") or None

    data = loaded
    return loaded


def save_data(value: Dict[str, Any]) -> None:
    """ذخیرهٔ اتمیک: اول در فایل موقت، بعد جایگزینی — دیگر هیچ‌وقت نصفه‌نیمه نمی‌ماند."""
    tmp_path = f"{DATA_FILE}.tmp"
    payload = json.dumps(value, ensure_ascii=False, indent=2)
    with open(tmp_path, "w", encoding="utf-8") as file:
        file.write(payload)
        file.flush()
        os.fsync(file.fileno())
    os.replace(tmp_path, DATA_FILE)


def load_session() -> str:
    if not os.path.exists(SESSION_FILE):
        return ""

    try:
        with open(SESSION_FILE, "r", encoding="utf-8") as file:
            return file.read().strip()
    except OSError:
        return ""


def save_session(session: str) -> None:
    """ذخیرهٔ session + محدودکردن دسترسی فایل به کاربر فعلی (امنیت)."""
    with open(SESSION_FILE, "w", encoding="utf-8") as file:
        file.write(session)
    try:
        os.chmod(SESSION_FILE, 0o600)
    except OSError:
        pass


# ─────────────────────────────────────────────────────────────────────────────
# بخش ۲-۳: ابزارهای عمومی
# ─────────────────────────────────────────────────────────────────────────────

def format_uptime() -> str:
    seconds = int((datetime.now() - START_TIME).total_seconds())
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    return " ".join(parts)


def clock_text() -> str:
    font = CLOCK_FONTS.get(int(data.get("clock_font", 1)), CLOCK_FONTS[1])
    return datetime.now().strftime(font)


def get_slot(slots: List[str], number: int) -> Optional[str]:
    if not 1 <= number <= 8:
        return None
    return slots[number - 1]


def split_slot_messages(text: str) -> List[str]:
    """اسلات را با جداکنندهٔ | به چند پیام مرتب تبدیل می‌کند."""
    return [item.strip() for item in text.split("|") if item.strip()]


def parse_duration(value: str) -> Optional[int]:
    """زمان‌های انعطاف‌پذیر: 53، 53s، 53m، 2h، 1d → ثانیه (اعداد فارسی هم قبول است)."""
    value = from_persian_digits(str(value)).strip().lower()
    if not value:
        return None

    if re.fullmatch(r"\d+(?:\.\d+)?", value):
        return int(float(value))

    aliases = {
        "s": 1, "sec": 1, "secs": 1, "second": 1, "seconds": 1,
        "m": 60, "min": 60, "mins": 60, "minute": 60, "minutes": 60,
        "h": 3600, "hr": 3600, "hrs": 3600, "hour": 3600, "hours": 3600,
        "d": 86400, "day": 86400, "days": 86400,
    }
    match = re.fullmatch(r"(\d+(?:\.\d+)?)([a-zA-Z]+)", value)
    if not match:
        return None

    multiplier = aliases.get(match.group(2))
    if multiplier is None:
        return None

    return int(float(match.group(1)) * multiplier)


def format_duration(seconds: int) -> str:
    seconds = int(seconds)
    if seconds % 86400 == 0:
        return f"{seconds // 86400}d"
    if seconds % 3600 == 0:
        return f"{seconds // 3600}h"
    if seconds % 60 == 0:
        return f"{seconds // 60}m"
    return f"{seconds}s"


def display_name(user: Any) -> str:
    return " ".join(
        x for x in (getattr(user, "first_name", None), getattr(user, "last_name", None))
        if x
    ) or f"ID:{getattr(user, 'id', '?')}"


def safe_member_name(user: Any) -> str:
    """فقط نام نمایشی برای خروجی‌های اعضا (بدون ID و یوزرنیم)."""
    name = " ".join(
        x for x in (
            getattr(user, "first_name", None),
            getattr(user, "last_name", None),
        )
        if x
    ).strip()
    return name or "بدون نام"


def render_template(template: str, name: str, username: Optional[str] = None,
                    chat_title: Optional[str] = None) -> str:
    """جایگذاری متغیرهای پیام: {name} {username} {chat}"""
    out = str(template).replace("{name}", name)
    if username:
        out = out.replace("{username}", f"@{username}")
    else:
        out = out.replace("@{username}", "").replace("{username}", "")
    out = out.replace("{chat}", chat_title or "")
    return out


# ─────────────────────────────────────────────────────────────────────────────
# بخش ۲-۴: آمار
# ─────────────────────────────────────────────────────────────────────────────

def chat_stat(chat_id: Any) -> Dict[str, Any]:
    assert data is not None
    key = str(chat_id)
    stats_map = data.setdefault("stats", {})
    if key not in stats_map or not isinstance(stats_map.get(key), dict):
        stats_map[key] = {name: 0 for name in STAT_KEYS}
        stats_map[key]["history"] = {}

    stats = stats_map[key]
    for name in STAT_KEYS:
        if name not in stats:
            stats[name] = 0
    if not isinstance(stats.get("history"), dict):
        stats["history"] = {}

    return stats


def add_stat(chat_id: Any, key: str, amount: int = 1) -> None:
    stats = chat_stat(chat_id)
    stats[key] = stats.get(key, 0) + amount

    day = datetime.now().strftime("%Y-%m-%d")
    history = stats.setdefault("history", {})
    daily = history.setdefault(day, {})
    daily[key] = daily.get(key, 0) + amount


def stats_period(chat_id: Any, days: int) -> Dict[str, int]:
    stats = chat_stat(chat_id)
    history = stats.get("history", {})
    total: Dict[str, int] = {}
    today = datetime.now().date()

    for index in range(days):
        key = (today - timedelta(days=index)).strftime("%Y-%m-%d")
        daily = history.get(key, {})
        for stat_name, value in daily.items():
            total[stat_name] = total.get(stat_name, 0) + int(value or 0)

    return total


def prune_stats_history(keep_days: int = STATS_HISTORY_KEEP_DAYS) -> int:
    """حذف تاریخچهٔ آمار قدیمی‌تر از keep_days روز (نگهداری مرتب)."""
    if data is None:
        return 0
    cutoff = (datetime.now().date() - timedelta(days=keep_days)).strftime("%Y-%m-%d")
    removed = 0
    for stats in data.get("stats", {}).values():
        history = stats.get("history")
        if not isinstance(history, dict):
            continue
        for day in list(history.keys()):
            if str(day) < cutoff:
                history.pop(day, None)
                removed += 1
    return removed


# ─────────────────────────────────────────────────────────────────────────────
# بخش ۲-۵: ماشین‌حساب امن (بدون eval — تحلیل AST با لیست سفید)
# ─────────────────────────────────────────────────────────────────────────────

_CALC_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_CALC_FUNCS = {
    "sqrt": math.sqrt,
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "pow": pow,
    "fact": math.factorial,
    "faktor": math.factorial,
}
_CALC_CONSTS = {
    "pi": math.pi,
    "e": math.e,
}


def _calc_node(node: ast.AST) -> Any:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return node.value
        raise ValueError("فقط عدد مجاز است")

    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _CALC_BINOPS:
            raise ValueError("عملگر مجاز نیست")
        left = _calc_node(node.left)
        right = _calc_node(node.right)
        if op_type is ast.Pow and (abs(right) > 1000 or abs(left) > 10 ** 100):
            raise ValueError("عدد بیش از حد بزرگ است")
        result = _CALC_BINOPS[op_type](left, right)
        if isinstance(result, complex):
            raise ValueError("نتیجه عدد مختلط شد")
        if isinstance(result, (int, float)) and abs(result) > 10 ** 1000:
            raise ValueError("نتیجه بیش از حد بزرگ است")
        return result

    if isinstance(node, ast.UnaryOp):
        value = _calc_node(node.operand)
        if isinstance(node.op, ast.USub):
            return -value
        if isinstance(node.op, ast.UAdd):
            return +value
        raise ValueError("عملگر مجاز نیست")

    if isinstance(node, ast.Name):
        if node.id in _CALC_CONSTS:
            return _CALC_CONSTS[node.id]
        raise ValueError(f"نام ناشناخته: {node.id}")

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name) or node.func.id not in _CALC_FUNCS:
            raise ValueError("تابع مجاز نیست")
        if node.keywords:
            raise ValueError("آرگومان نام‌دار مجاز نیست")
        args = [_calc_node(arg) for arg in node.args]
        return _CALC_FUNCS[node.func.id](*args)

    raise ValueError("عبارت مجاز نیست")


def safe_calc(expression: str) -> Any:
    """محاسبهٔ امن عبارت ریاضی؛ اعداد فارسی و ×÷− هم پشتیبانی می‌شود."""
    expr = from_persian_digits(expression.strip())
    expr = (expr.replace("×", "*").replace("÷", "/")
                .replace("−", "-").replace("،", ","))
    if not expr:
        raise ValueError("عبارت خالی است")

    tree = ast.parse(expr, mode="eval")
    return _calc_node(tree.body)


# ─────────────────────────────────────────────────────────────────────────────
# بخش ۲-۶: سرگرمی و ابزار کوچک (تاس، سکه، تصادفی، رمز عبور)
# ─────────────────────────────────────────────────────────────────────────────

def gen_password(length: int = 16) -> str:
    """تولید رمز امن با تضمین حضور حرف کوچک/بزرگ/رقم/نماد."""
    if not 8 <= length <= 64:
        raise ValueError("طول رمز باید بین ۸ تا ۶۴ باشد")
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+?"
    while True:
        password = "".join(secrets.choice(alphabet) for _ in range(length))
        if (
            any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and any(c.isdigit() for c in password)
            and any(c in "!@#$%^&*()-_=+?" for c in password)
        ):
            return password


# ─────────────────────────────────────────────────────────────────────────────
# بخش ۲-۷: فونت‌های فنسی (یونیکد) برای زیباسازی متن
# ─────────────────────────────────────────────────────────────────────────────

def _map_alpha(text: str, up_base: int, low_base: int, digit_base: Optional[int] = None,
               upper_exc: Optional[Dict[str, str]] = None,
               lower_exc: Optional[Dict[str, str]] = None,
               digit_exc: Optional[Dict[str, str]] = None) -> str:
    upper_exc = upper_exc or {}
    lower_exc = lower_exc or {}
    digit_exc = digit_exc or {}
    out: List[str] = []
    for ch in text:
        if ch in upper_exc:
            out.append(upper_exc[ch])
        elif ch in lower_exc:
            out.append(lower_exc[ch])
        elif ch in digit_exc:
            out.append(digit_exc[ch])
        elif "A" <= ch <= "Z":
            out.append(chr(up_base + ord(ch) - 65))
        elif "a" <= ch <= "z":
            out.append(chr(low_base + ord(ch) - 97))
        elif digit_base is not None and "0" <= ch <= "9":
            out.append(chr(digit_base + ord(ch) - 48))
        else:
            out.append(ch)
    return "".join(out)


_SCRIPT_UPPER = {c: v for c, v in zip("BEFGHILMR", "ℬℰℱℋℐℒℳℛ")}
_SCRIPT_LOWER = {c: v for c, v in zip("egoo", "ℯℊℴℴ")}
_FRAKTUR_UPPER = {c: v for c, v in zip("CHIRZ", "ℭℌℑℜℨ")}
_DOUBLE_UPPER = {c: v for c, v in zip("CHNPQRZ", "ℂℍℕℙℚℝℤ")}
_CIRCLED_DIGITS = {"0": "⓪", **{chr(48 + d): chr(0x2460 + d - 1) for d in range(1, 10)}}
_SQUARE_UPPER_BASE = 0x1F130
_NEG_CIRCLED_BASE = 0x1F150

# (نام، تابع تبدیل)
FANCY_FONTS: List[Tuple[str, Callable[[str], str]]] = [
    ("Bold", lambda t: _map_alpha(t, 0x1D400, 0x1D41A, 0x1D7CE)),
    ("Italic", lambda t: _map_alpha(t, 0x1D434, 0x1D44E, None, lower_exc={"h": "ℎ"})),
    ("Bold Italic", lambda t: _map_alpha(t, 0x1D468, 0x1D482, 0x1D7CE)),
    ("Script", lambda t: _map_alpha(t, 0x1D49C, 0x1D4B6, None, _SCRIPT_UPPER, _SCRIPT_LOWER)),
    ("Fraktur", lambda t: _map_alpha(t, 0x1D504, 0x1D51E, None, _FRAKTUR_UPPER)),
    ("Double", lambda t: _map_alpha(t, 0x1D538, 0x1D552, 0x1D7D8, _DOUBLE_UPPER)),
    ("Mono", lambda t: _map_alpha(t, 0x1D670, 0x1D68A, 0x1D7F6)),
    ("Circled", lambda t: _map_alpha(t, 0x24B6, 0x24D0, None, digit_exc=_CIRCLED_DIGITS)),
    ("Squared", lambda t: _map_alpha(t, _SQUARE_UPPER_BASE, _SQUARE_UPPER_BASE, None)),
    ("Negative", lambda t: _map_alpha(t, _NEG_CIRCLED_BASE, _NEG_CIRCLED_BASE, None)),
    ("Small Caps", lambda t: t.translate(str.maketrans(
        "abcdefghijklmnopqrstuvwxyz",
        "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ",
    ))),
]


def fancy_text(text: str, style: int) -> str:
    """تبدیل متن به یکی از فونت‌های فنسی (اندیس از ۱)."""
    if not 1 <= style <= len(FANCY_FONTS):
        raise ValueError(f"سبک باید بین ۱ تا {len(FANCY_FONTS)} باشد")
    return FANCY_FONTS[style - 1][1](text)


# ═════════════════════════════════════════════════════════════════════════════
# بخش ۳: پروفایل/ساعت، مدیریت تسک‌ها، یادآوری ماندگار، توابع سروش
# ═════════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────────────
# بخش ۳-۱: پروفایل و ساعت نام
# ─────────────────────────────────────────────────────────────────────────────

async def update_profile(client: Any, **kwargs: Any) -> bool:
    if UpdateProfileRequest is None:
        return False
    try:
        await client(UpdateProfileRequest(**kwargs))
        return True
    except Exception as exc:
        log.warning("بروزرسانی پروفایل ناموفق بود: %s: %s", type(exc).__name__, exc)
        return False


async def update_clock_profile(client: Any) -> bool:
    base_name = str(data.get("display_name", "")).strip()
    if not base_name:
        return False

    value = clock_text()

    if data.get("clock_position") == "bio":
        return await update_profile(client, first_name=base_name, about=value)

    return await update_profile(client, first_name=base_name, last_name=value)


async def update_name(client: Any, name: str) -> bool:
    name = name.strip()
    if not name:
        return False
    return await update_profile(client, first_name=name)


# خطای گذرا (شبکه و …) نباید ساعت را کامل خاموش کند؛ چند بار تلاش می‌کنیم.
CLOCK_MAX_CONSECUTIVE_FAILURES = 5


async def name_clock_loop(client: Any) -> None:
    global name_clock_task

    failures = 0
    try:
        while data.get("name_clock"):
            if not str(data.get("display_name", "")).strip():
                data["name_clock"] = False
                save_data(data)
                break

            if not await update_clock_profile(client):
                failures += 1
                if failures >= CLOCK_MAX_CONSECUTIVE_FAILURES:
                    log.error("ساعت نام بعد از %d تلاش ناموفق خاموش شد", failures)
                    data["name_clock"] = False
                    save_data(data)
                    break
                await asyncio.sleep(2 * failures)   # backoff کوتاه، بدون حلقهٔ بی‌نهایت
                continue

            failures = 0
            now = datetime.now()
            await asyncio.sleep(max(1, 60 - now.second))
    except asyncio.CancelledError:
        pass
    finally:
        name_clock_task = None


async def start_name_clock(client: Any) -> None:
    global name_clock_task

    if name_clock_task and not name_clock_task.done():
        return

    if not str(data.get("display_name", "")).strip():
        return

    data["name_clock"] = True
    save_data(data)
    name_clock_task = asyncio.create_task(name_clock_loop(client))


async def stop_name_clock(client: Any) -> None:
    global name_clock_task

    data["name_clock"] = False
    save_data(data)

    if name_clock_task and not name_clock_task.done():
        name_clock_task.cancel()
        try:
            await name_clock_task
        except asyncio.CancelledError:
            pass

    name_clock_task = None

    if str(data.get("display_name", "")).strip():
        if data.get("clock_position") == "bio":
            await update_profile(client, first_name=data["display_name"], about="")
        else:
            await update_profile(client, first_name=data["display_name"], last_name="")


# ─────────────────────────────────────────────────────────────────────────────
# بخش ۳-۲: مدیریت تسک‌ها
# ─────────────────────────────────────────────────────────────────────────────

def add_task(group: set, task: asyncio.Task) -> None:
    group.add(task)
    task.add_done_callback(group.discard)


def active_tasks_count() -> int:
    return sum(len(group) for group in operation_tasks.values()) + len(scheduled_tasks)


async def send_later(event: Any, delay: int, text: str) -> None:
    try:
        await asyncio.sleep(delay)
        await event.respond(text)
    except asyncio.CancelledError:
        pass
    except Exception as exc:
        log.error("ارسال زمان‌بندی‌شده ناموفق بود: %s: %s", type(exc).__name__, exc)
    finally:
        task = asyncio.current_task()
        if task:
            scheduled_tasks.discard(task)


async def repeated_send(event: Any, messages: List[str], count: int, delay: int,
                        group: set) -> None:
    try:
        for index in range(count):
            if index:
                await asyncio.sleep(delay)
            await event.respond(messages[index % len(messages)])
    except asyncio.CancelledError:
        pass
    except Exception as exc:
        log.error("ارسال تکراری متوقف شد: %s: %s", type(exc).__name__, exc)
    finally:
        task = asyncio.current_task()
        if task:
            group.discard(task)


async def repeated_reply(event: Any, messages: List[str], count: int, delay: int) -> None:
    if not event.is_reply:
        return

    target = await event.get_reply_message()
    if not target:
        return

    try:
        for index in range(count):
            if index:
                await asyncio.sleep(delay)
            await target.reply(messages[index % len(messages)])
    except asyncio.CancelledError:
        pass
    except Exception as exc:
        log.error("ریپلای تکراری متوقف شد: %s: %s", type(exc).__name__, exc)
    finally:
        task = asyncio.current_task()
        if task:
            operation_tasks["rep"].discard(task)


async def count_numbers(event: Any, count: int) -> None:
    try:
        for number in range(1, count + 1):
            await event.respond(str(number))
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass
    except Exception as exc:
        log.error("شمارش متوقف شد: %s: %s", type(exc).__name__, exc)
    finally:
        task = asyncio.current_task()
        if task:
            operation_tasks["shomaresh"].discard(task)


# ─────────────────────────────────────────────────────────────────────────────
# بخش ۳-۳: یادآوری ماندگار (بعد از ری‌استارت هم زنده می‌ماند)
# ─────────────────────────────────────────────────────────────────────────────

def add_reminder(chat_id: Any, text: str, due_ts: float) -> int:
    """افزودن یادآوری ماندگار؛ اندیس آن (برای /reminddel) برگردانده می‌شود."""
    assert data is not None
    entry = {
        "id": time.time_ns(),
        "chat_id": str(chat_id),
        "text": text,
        "due_ts": float(due_ts),
        "created": datetime.now().isoformat(timespec="seconds"),
    }
    data.setdefault("reminders", []).append(entry)
    save_data(data)
    return len(data["reminders"]) - 1


def remove_reminder(index: int) -> Optional[Dict[str, Any]]:
    assert data is not None
    reminders = data.get("reminders") or []
    if not 0 <= index < len(reminders):
        return None
    item = reminders.pop(index)
    save_data(data)
    return item


async def _reminder_fire(client: Any, chat_id: str, text: str, late: bool = False) -> None:
    send = getattr(client, "send_message", None)
    if not callable(send):
        log.warning("client.send_message در این نسخهٔ splusthon موجود نیست؛ یادآوری ارسال نشد")
        return
    prefix = "⏰ یادآوری (با تأخیر)" if late else "⏰ یادآوری"
    await send(int(chat_id), f"{prefix}\n\n{text}")


async def _reminder_run(client: Any, entry: Dict[str, Any]) -> None:
    remaining = entry["due_ts"] - time.time()
    try:
        if remaining > 0:
            await asyncio.sleep(remaining)
        await _reminder_fire(client, entry["chat_id"], entry["text"], late=remaining < -5)
    except asyncio.CancelledError:
        return
    except Exception as exc:
        log.error("یادآوری اجرا نشد: %s: %s", type(exc).__name__, exc)
    finally:
        assert data is not None
        try:
            data.setdefault("reminders", []).remove(entry)
        except ValueError:
            pass
        save_data(data)
        task = asyncio.current_task()
        if task:
            scheduled_tasks.discard(task)


def spawn_reminder(client: Any, entry: Dict[str, Any]) -> asyncio.Task:
    task = asyncio.create_task(_reminder_run(client, entry))
    scheduled_tasks.add(task)
    task.add_done_callback(scheduled_tasks.discard)
    return task


def restore_reminders(client: Any) -> int:
    """بازیابی یادآوری‌های معلق بعد از ری‌استارت (یادآوری‌های گذشته فوراً ارسال می‌شوند)."""
    assert data is not None
    restored = 0
    now = time.time()
    for entry in list(data.get("reminders") or []):
        try:
            if float(entry.get("due_ts", 0)) <= now:
                # دیرهنگام: فوراً بفرست و از لیست پاک کن
                asyncio.get_event_loop().create_task(
                    _send_late_and_clean(client, entry)
                )
            else:
                spawn_reminder(client, entry)
            restored += 1
        except Exception as exc:
            log.warning("بازیابی یک یادآوری ناموفق بود: %s", exc)
    return restored


async def _send_late_and_clean(client: Any, entry: Dict[str, Any]) -> None:
    try:
        await _reminder_fire(client, entry.get("chat_id", "0"), entry.get("text", ""), late=True)
    except Exception as exc:
        log.warning("ارسال یادآوری دیرهنگام ناموفق بود: %s", exc)
    finally:
        assert data is not None
        try:
            data.setdefault("reminders", []).remove(entry)
        except ValueError:
            pass
        save_data(data)


# ─────────────────────────────────────────────────────────────────────────────
# بخش ۳-۴: ابزارهای سروش — اعضا، مدیران، تصویر
# ─────────────────────────────────────────────────────────────────────────────

async def collect_group_members(client: Any, chat_ref: Any,
                                require_group: bool = True) -> Dict[str, Any]:
    """جمع‌آوری اعضا فقط از روی پاسخ GetParticipants.

    نکته: بعضی نسخه‌های SPlusthon هنگام resolve کامل entity خطای KeyError
    می‌دهند؛ عمداً فقط از get_input_entity استفاده می‌کنیم.
    """
    from splusthon.tl.functions.channels import GetParticipantsRequest
    from splusthon.tl.types import ChannelParticipantsRecent

    try:
        channel = await client.get_input_entity(chat_ref)
    except Exception as exc:
        return {"status": "error", "error": f"{type(exc).__name__}: {exc}"}

    users_by_id: Dict[Any, Any] = {}
    participants_by_id: Dict[Any, Any] = {}
    offset = 0
    pages = 0

    while True:
        try:
            result = await client(
                GetParticipantsRequest(
                    channel=channel,
                    filter=ChannelParticipantsRecent(),
                    offset=offset,
                    limit=200,
                    hash=0,
                )
            )
        except Exception as exc:
            return {"status": "error", "error": f"{type(exc).__name__}: {exc}"}

        pages += 1
        users = list(getattr(result, "users", None) or [])
        participants = list(getattr(result, "participants", None) or [])

        # هرچه سرور داد کپی می‌کنیم؛ هرگز فرض نمی‌کنیم هر participant
        # در همین پاسخ یک User هم داشته باشد.
        for user in users:
            uid = getattr(user, "id", None)
            if uid is not None:
                users_by_id[uid] = user

        for participant in participants:
            uid = getattr(participant, "user_id", None)
            if uid is not None:
                participants_by_id[uid] = participant

        batch_count = max(len(users), len(participants))
        if batch_count == 0 or batch_count < 200:
            break
        offset += batch_count

    return {
        "status": "ok",
        "channel": channel,
        "users": users_by_id,
        "participants": participants_by_id,
        "pages": pages,
    }


def member_role(participant: Any) -> str:
    name = participant.__class__.__name__.lower() if participant else ""
    if "creator" in name:
        return "creator"
    if "admin" in name:
        return "admin"
    return "member"


def member_is_online(user: Any) -> bool:
    status = getattr(user, "status", None)
    return bool(
        status and status.__class__.__name__.lower() == "userstatusonline"
    )


def member_is_bot(user: Any) -> bool:
    return bool(getattr(user, "bot", False))


def render_members_page(users: Dict[Any, Any], participants: Dict[Any, Any],
                        page: int, per_page: int = 30) -> Tuple[str, int]:
    # فقط نام نمایش داده می‌شود؛ بدون ID و یوزرنیم تا خروجی به‌عنوان
    # لیست منشن/تگ مستقیم قابل استفاده نباشد.
    ordered = sorted(
        users.values(),
        key=lambda user: (
            str(getattr(user, "first_name", "") or "").lower(),
            int(getattr(user, "id", 0) or 0),
        ),
    )

    total_pages = max(1, (len(ordered) + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    items = ordered[start:start + per_page]

    lines = [
        card_title("👥", f"اعضای گپ | صفحه {to_persian_digits(page)}/{to_persian_digits(total_pages)}"),
        f"📦 تعداد نمایش: {to_persian_digits(len(items))} از {to_persian_digits(len(ordered))}",
        "",
    ]

    for index, user in enumerate(items, start + 1):
        uid = getattr(user, "id", None)
        name = display_name(user)
        participant = participants.get(uid)
        role = member_role(participant)
        role_text = {"creator": "👑", "admin": "🛡️", "member": "👤"}.get(role, "👤")
        lines.append(f"{to_persian_digits(index)}. {role_text} {name}")

    return "\n".join(lines), total_pages


async def get_members_summary(event: Any, client: Any, page: int = 1) -> Dict[str, Any]:
    result = await collect_group_members(client, event.chat_id)
    if result.get("status") != "ok":
        return result

    users = result["users"]
    participants = result["participants"]

    # ممکن است برای بعضی participantها آبجکت User در پاسخ نباشد؛
    # نقش‌ها فقط از متادیتای participants شمرده می‌شود.
    admins = sum(1 for item in participants.values() if member_role(item) in {"admin", "creator"})
    creators = sum(1 for item in participants.values() if member_role(item) == "creator")
    bots = sum(1 for user in users.values() if member_is_bot(user))
    online = sum(1 for user in users.values() if member_is_online(user))

    page_text, total_pages = render_members_page(users, participants, page)

    summary = (
        card_title("📊", "خلاصه اعضای گپ") + "\n\n"
        f"👥 کل اعضا: {to_persian_digits(len(users))}\n"
        f"🛡️ مدیران: {to_persian_digits(admins)}\n"
        f"👑 سازنده: {to_persian_digits(creators)}\n"
        f"🤖 ربات‌ها: {to_persian_digits(bots)}\n"
        f"🟢 آنلاین: {to_persian_digits(online)}\n"
        f"📄 صفحات: {to_persian_digits(total_pages)}\n\n"
        f"{page_text}\n\n{brand_footer()}"
    )

    return {
        "status": "ok",
        "text": summary,
        "count": len(users),
        "admins": admins,
        "creators": creators,
        "bots": bots,
        "online": online,
        "pages": total_pages,
    }


async def get_chat_info(event: Any, client: Any) -> str:
    chat = await event.get_chat()
    title = getattr(chat, "title", None) or getattr(chat, "first_name", None) or "بدون عنوان"
    username = getattr(chat, "username", None)
    kind = chat.__class__.__name__
    username_text = f"@{username}" if username else "ندارد"
    return (
        card_title("🔎", "اطلاعات گپ") + "\n\n"
        f"📛 نام: {title}\n"
        f"🆔 ID: {getattr(chat, 'id', event.chat_id)}\n"
        f"🏷 یوزرنیم: {username_text}\n"
        f"🧩 نوع: {kind}\n"
        f"👑 سازنده: {'بله' if getattr(chat, 'creator', False) else 'خیر'}\n\n"
        f"{brand_footer()}"
    )


async def download_profile_photo(client: Any, input_user: Any, output_path: str) -> Optional[str]:
    exported_sender = None

    try:
        photos_result = await client(
            GetUserPhotosRequest(user_id=input_user, offset=0, max_id=0, limit=1)
        )

        photos = getattr(photos_result, "photos", None)
        if not photos:
            return None

        photo = photos[0]
        sizes = getattr(photo, "sizes", None)
        if not sizes:
            return None

        valid_sizes = [
            item for item in sizes
            if getattr(item, "w", None) and getattr(item, "h", None)
        ]
        if not valid_sizes:
            return None

        largest = max(valid_sizes, key=lambda item: getattr(item, "w", 0) * getattr(item, "h", 0))

        location = InputPhotoFileLocation(
            id=photo.id,
            access_hash=photo.access_hash,
            file_reference=photo.file_reference,
            thumb_size=getattr(largest, "type", ""),
        )

        photo_dc = getattr(photo, "dc_id", None)
        session_dc = getattr(client.session, "dc_id", None)
        borrow = getattr(client, "_borrow_exported_sender", None)
        giveback = getattr(client, "_return_exported_sender", None)

        if photo_dc and session_dc and photo_dc != session_dc and callable(borrow):
            exported_sender = await borrow(photo_dc)

        chunk_size = 64 * 1024
        offset = 0

        with open(output_path, "wb") as file:
            while True:
                result = await client(
                    GetFileRequest(location=location, offset=offset, limit=chunk_size)
                )

                chunk = getattr(result, "bytes", None)
                if not chunk:
                    break

                file.write(chunk)
                offset += len(chunk)

                if len(chunk) < chunk_size:
                    break

        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            return None

        return output_path

    except Exception as exc:
        log.warning("دانلود عکس پروفایل ناموفق بود: %s: %s", type(exc).__name__, exc)
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
            except OSError:
                pass
        return None
    finally:
        if exported_sender and callable(giveback):
            try:
                await giveback(exported_sender)
            except Exception:
                pass


async def get_user_info(client: Any, user: Any) -> Tuple[str, Optional[str]]:
    """کارت اطلاعات کاربر + مسیر عکس پروفایل (در صورت وجود).

    رفع باگ: در نسخهٔ قبل سه خط ID/Bio/وضعیت دو بار تکرار می‌شد.
    """
    try:
        input_user = await client.get_input_entity(user)
        full = await client(GetFullUserRequest(input_user))

        first_name = getattr(user, "first_name", None)
        last_name = getattr(user, "last_name", None)
        name = " ".join(x for x in (first_name, last_name) if x) or "بدون نام"

        username = getattr(user, "username", None)
        user_id = getattr(user, "id", None)
        bio = getattr(full, "about", None) or "ندارد"

        status = getattr(user, "status", None)
        status_map = {
            "UserStatusOnline": "آنلاین",
            "UserStatusOffline": "آفلاین",
            "UserStatusRecently": "اخیراً آنلاین",
            "UserStatusLastWeek": "این هفته آنلاین",
            "UserStatusLastMonth": "این ماه آنلاین",
        }
        status_text = status_map.get(
            status.__class__.__name__, "در دسترس نیست"
        ) if status else "در دسترس نیست"

        flags = {
            "Premium": getattr(user, "premium", False),
            "Bot": getattr(user, "bot", False),
            "Verified": getattr(user, "verified", False),
            "Scam": getattr(user, "scam", False),
            "Fake": getattr(user, "fake", False),
            "Restricted": getattr(user, "restricted", False),
            "Deleted": getattr(user, "deleted", False),
        }

        usernames = [
            f"@{value}"
            for item in (getattr(user, "usernames", None) or [])
            if (value := getattr(item, "username", None))
        ]

        user_type = getattr(user, "user_type", None)
        user_type_name = user_type.__class__.__name__ if user_type else "در دسترس نیست"

        emoji_status = "دارد" if getattr(user, "emoji_status", None) else "ندارد"
        has_photo = bool(getattr(user, "photo", None))
        username_text = f"@{username}" if username else "ندارد"

        info = (
            card_title("👤", "اطلاعات کاربر") + "\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"📛 نام: {name}\n"
            f"🔗 یوزرنیم: {username_text}\n"
            f"🆔 ID: {user_id}\n"
            f"📝 Bio: {bio}\n"
            f"🟢 وضعیت: {status_text}\n\n"
            "── ویژگی‌ها ──\n"
        )

        for key, value in flags.items():
            info += f"• {key}: {'بله' if value else 'خیر'}\n"

        info += (
            f"👤 یوزرنیم‌های اضافی: {', '.join(usernames) if usernames else 'ندارد'}\n"
            f"🧩 نوع کاربر: {user_type_name}\n"
            f"✨ Emoji Status: {emoji_status}\n"
            f"📷 عکس پروفایل: {'دارد' if has_photo else 'ندارد'}\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"{brand_footer()}"
        )

        photo_path = None
        if has_photo and user_id:
            photo_path = f"profile_{user_id}.jpg"
            if not await download_profile_photo(client, input_user, photo_path):
                photo_path = None

        return info, photo_path

    except Exception as error:
        log.warning("دریافت اطلاعات کاربر ناموفق بود: %s", error)
        return f"❌ خطا در دریافت اطلاعات کاربر.\n\n{error}", None


async def get_top_members(event: Any, client: Any, limit: int = 10,
                          message_limit: int = 1000) -> Dict[str, Any]:
    """فعال‌ترین اعضا در تاریخچهٔ اخیر پیام‌ها."""
    if limit <= 0:
        limit = 10
    limit = min(limit, MAX_TOP_LIMIT)
    message_limit = max(100, min(message_limit, MAX_SCAN_MESSAGES))

    counts: Dict[Any, int] = {}
    users: Dict[Any, Any] = {}

    try:
        messages = await client.get_messages(event.chat_id, limit=message_limit)
    except Exception as exc:
        return {"status": "error", "error": f"{type(exc).__name__}: {exc}"}

    for message in messages:
        sender_id = getattr(message, "sender_id", None)
        if not sender_id:
            continue
        counts[sender_id] = counts.get(sender_id, 0) + 1

        sender = getattr(message, "sender", None)
        if sender is not None:
            users[sender_id] = sender

    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]

    rows = []
    for index, (user_id, count) in enumerate(ranked, 1):
        user = users.get(user_id)
        if user is None:
            try:
                user = await client.get_entity(user_id)
                users[user_id] = user
            except Exception:
                user = None
        name = display_name(user) if user is not None else f"کاربر {user_id}"
        rows.append((index, name, count))

    return {
        "status": "ok",
        "rows": rows,
        "scanned": len(messages),
        "active_users": len(counts),
    }


async def get_channel_admins(event: Any, client: Any) -> Any:
    """لیست مدیرهای کانال/سوپرگروپ."""
    from splusthon.tl.functions.channels import GetParticipantsRequest
    from splusthon.tl.types import ChannelParticipantsAdmins

    chat = await event.get_chat()
    if not (getattr(chat, "megagroup", False) or getattr(chat, "gigagroup", False)):
        return "unsupported_chat"

    channel = await client.get_input_entity(event.chat_id)
    offset = 0
    admins: List[Any] = []

    while True:
        result = await client(
            GetParticipantsRequest(
                channel=channel,
                filter=ChannelParticipantsAdmins(),
                offset=offset,
                limit=200,
                hash=0,
            )
        )
        users = list(getattr(result, "users", None) or [])
        participants = list(getattr(result, "participants", None) or [])

        # بعضی پاسخ‌ها participant بدون آبجکت User برمی‌گردانند؛
        # هرگز مستقیم ایندکس نمی‌کنیم و فقط چیزهای قابل‌حل را برمی‌داریم.
        if users:
            admins.extend(users)
        else:
            for participant in participants:
                uid = getattr(participant, "user_id", None)
                if not uid:
                    continue
                try:
                    user = await client.get_entity(uid)
                    if user is not None:
                        admins.append(user)
                except Exception:
                    continue

        if len(users) < 200 and len(participants) < 200:
            break
        offset += max(len(users), len(participants))

    unique: Dict[Any, Any] = {}
    for user in admins:
        uid = getattr(user, "id", None)
        if uid:
            unique[uid] = user
    return list(unique.values())


# ─────────────────────────────────────────────────────────────────────────────
# بخش ۳-۵: پاک‌سازی، مدیریت اعضا، سنجاق
# ─────────────────────────────────────────────────────────────────────────────

async def delete_own_messages(event: Any, client: Any, count: int) -> int:
    """حذف تا count پیام اخیر خودِ این اکانت در این گپ."""
    messages = await client.get_messages(event.chat_id, limit=max(count + 20, count))
    own_ids = [
        message.id
        for message in messages
        if getattr(message, "out", False)
    ][:count]

    if not own_ids:
        return 0

    await client.delete_messages(event.chat_id, own_ids, revoke=True)
    return len(own_ids)


def _chat_is_group(chat: Any) -> bool:
    return bool(
        getattr(chat, "megagroup", False)
        or getattr(chat, "gigagroup", False)
        or chat.__class__.__name__.lower() in {"chat", "channel"}
    )


def _can_delete_messages(chat: Any) -> bool:
    admin_rights = getattr(chat, "admin_rights", None)
    return bool(
        getattr(chat, "creator", False)
        or getattr(admin_rights, "delete_messages", False)
        or getattr(admin_rights, "delete_message", False)
    )


def _can_kick_members(chat: Any) -> bool:
    admin_rights = getattr(chat, "admin_rights", None)
    return bool(
        getattr(chat, "creator", False)
        or getattr(admin_rights, "ban_users", False)
        or getattr(admin_rights, "ban_user", False)
    )


async def delete_group_messages(event: Any, client: Any, count: int) -> Any:
    """حذف پیام‌های اخیر گروه در صورت داشتن مجوز حذف."""
    chat = await event.get_chat()

    if not _chat_is_group(chat):
        return "not_group"

    if not _can_delete_messages(chat):
        return "no_permission"

    messages = await client.get_messages(event.chat_id, limit=count)
    message_ids = [
        message.id
        for message in messages
        if getattr(message, "id", None)
    ]

    if not message_ids:
        return 0

    await client.delete_messages(event.chat_id, message_ids, revoke=True)
    return len(message_ids)


async def purge_messages(event: Any, client: Any, since_id: int) -> int:
    """حذف همهٔ پیام‌ها از since_id تا جدیدترین (سقف MAX_PURGE)."""
    newest = await client.get_messages(event.chat_id, limit=1)
    if not newest:
        return 0

    last = getattr(newest[0], "id", None)
    if not last or last < since_id:
        return 0

    collected: List[int] = []
    upper = last
    while upper >= since_id and len(collected) < MAX_PURGE:
        batch = await client.get_messages(event.chat_id, limit=200, max_id=upper + 1)
        if not batch:
            break
        batch_ids = [
            getattr(m, "id", None)
            for m in batch
            if getattr(m, "id", None) is not None and since_id <= getattr(m, "id") <= upper
        ]
        collected.extend(batch_ids)
        lower = min(getattr(m, "id", 0) or 0 for m in batch)
        if lower <= 0 or lower <= since_id:
            break
        upper = lower - 1

    ids = sorted(set(collected))[:MAX_PURGE]
    if not ids:
        return 0

    deleted = 0
    for start in range(0, len(ids), 100):
        chunk = ids[start:start + 100]
        await client.delete_messages(event.chat_id, chunk, revoke=True)
        deleted += len(chunk)
    return deleted


async def clean_messages(event: Any, client: Any, mode: str, count: int,
                         user_id: Any = None) -> Dict[str, Any]:
    can, status = await is_group_admin(event)
    if status == "not_group":
        return {"status": "not_group"}
    if not can:
        return {"status": "no_permission"}

    scan_limit = max(count, 1) if mode != "user" else min(max(count * 20, 200), MAX_SCAN_MESSAGES)
    messages = await client.get_messages(event.chat_id, limit=scan_limit)
    selected = []
    url_re = re.compile(r"(?:https?://|www\.|t\.me/|@\w+)", re.I)
    for message in messages:
        mid = getattr(message, "id", None)
        if not mid:
            continue
        if mode == "links":
            body = getattr(message, "raw_text", None) or getattr(message, "message", None) or ""
            if url_re.search(body):
                selected.append(mid)
        elif mode == "media":
            if getattr(message, "media", None):
                selected.append(mid)
        elif mode == "user":
            if getattr(message, "sender_id", None) == user_id:
                selected.append(mid)
        if len(selected) >= count:
            break

    if not selected:
        return {"status": "empty", "count": 0}

    await client.delete_messages(event.chat_id, selected, revoke=True)
    add_stat(event.chat_id, "deleted_messages", len(selected))
    save_data(data)
    return {"status": "ok", "count": len(selected)}


async def is_group_admin(event: Any) -> Tuple[bool, Optional[str]]:
    """آیا اکانت فعلی در این گپ مجوز مدیریت اعضا دارد؟"""
    chat = await event.get_chat()
    if not _chat_is_group(chat):
        return False, "not_group"
    return _can_kick_members(chat), None


async def get_replied_user(event: Any) -> Tuple[Any, Any]:
    if not event.is_reply:
        return None, "no_reply"
    reply = await event.get_reply_message()
    if not reply:
        return None, "no_reply"
    user_id = getattr(reply, "sender_id", None)
    if not user_id:
        return None, "no_user"
    return await event.client.get_input_entity(user_id), user_id


async def target_is_admin(event: Any, client: Any, user_id: Any) -> bool:
    """هدف سازنده/مدیر است؟"""
    try:
        from splusthon.tl.functions.channels import GetParticipantRequest
        participant = await client(
            GetParticipantRequest(
                channel=await client.get_input_entity(event.chat_id),
                participant=user_id,
            )
        )
        row = getattr(participant, "participant", None)
        name = row.__class__.__name__.lower() if row else ""
        return "admin" in name or "creator" in name
    except Exception:
        return False


async def moderate_member(event: Any, client: Any, action: str,
                          target_user: Any = None) -> Dict[str, Any]:
    """بن/آنبن/میوت/آنمیوت عضو.

    target_user=None → روی فرستندهٔ پیامِ ریپلای‌شده عمل می‌کند (رفتار اصلی).
    target_user=شناسه/انتیتی → روی همان کاربر (برای زمان‌سنجِ رفع خودکار).
    """
    can_kick, status = await is_group_admin(event)
    if status == "not_group":
        return {"status": "not_group"}
    if not can_kick:
        return {"status": "no_permission"}

    if target_user is None:
        user_entity, user_id_or_status = await get_replied_user(event)
        if user_entity is None:
            return {"status": user_id_or_status}
        user_id = user_id_or_status
    else:
        user_id = getattr(target_user, "id", target_user)
        try:
            user_entity = await client.get_input_entity(target_user)
        except Exception as exc:
            log.warning("حل کاربر هدف ناموفق بود: %s", exc)
            return {"status": "resolve_failed"}

    me = await client.get_me()
    if getattr(me, "id", None) == user_id:
        return {"status": "self"}

    if await target_is_admin(event, client, user_id):
        return {"status": "target_admin"}

    chat = await event.get_chat()
    if not (getattr(chat, "megagroup", False) or getattr(chat, "gigagroup", False)):
        return {"status": "unsupported_chat"}

    from splusthon.tl.functions.channels import EditBannedRequest
    from splusthon.tl.types import ChatBannedRights

    if action == "ban":
        rights = ChatBannedRights(
            until_date=None,
            view_messages=True,
            send_messages=True,
            send_media=True,
            send_stickers=True,
            send_gifs=True,
            send_games=True,
            send_inline=True,
            embed_links=True,
            send_polls=True,
            change_info=True,
            invite_users=True,
            pin_messages=True,
            manage_topics=True,
        )
    elif action == "mute":
        rights = ChatBannedRights(
            until_date=None,
            view_messages=False,
            send_messages=True,
            send_media=True,
            send_stickers=True,
            send_gifs=True,
            send_games=True,
            send_inline=True,
            embed_links=True,
            send_polls=True,
            send_photos=True,
            send_videos=True,
            send_roundvideos=True,
            send_audios=True,
            send_voices=True,
            send_docs=True,
            send_plain=True,
        )
    else:
        # unban / unmute → همهٔ محدودیت‌ها برداشته می‌شود
        rights = ChatBannedRights(
            until_date=None,
            view_messages=False,
            send_messages=False,
            send_media=False,
            send_stickers=False,
            send_gifs=False,
            send_games=False,
            send_inline=False,
            embed_links=False,
            send_polls=False,
            change_info=False,
            invite_users=False,
            pin_messages=False,
            manage_topics=False,
            send_photos=False,
            send_videos=False,
            send_roundvideos=False,
            send_audios=False,
            send_voices=False,
            send_docs=False,
            send_plain=False,
        )

    await client(
        EditBannedRequest(
            channel=await client.get_input_entity(event.chat_id),
            participant=user_entity,
            banned_rights=rights,
        )
    )
    return {"status": "ok"}


# نام قدیمی برای سازگاری داخلی
async def change_member_moderation(event: Any, client: Any, action: str) -> Dict[str, Any]:
    return await moderate_member(event, client, action)


async def schedule_unmoderate(event: Any, client: Any, user_id: Any,
                              action: str, seconds: int) -> None:
    """رفع خودکار بن/میوت بعد از مدت مشخص.

    رفع باگ نسخهٔ قبل: برای میوتِ موقت اشتباهاً «unban» صدا زده می‌شد و
    میوت هرگز برداشته نمی‌شد؛ حالا اکشن معکوسِ درست اعمال می‌شود.
    """
    inverse = {"mute": "unmute", "ban": "unban"}.get(action)
    if inverse is None:
        return
    try:
        await asyncio.sleep(seconds)
        result = await moderate_member(event, client, inverse, target_user=user_id)
        if result.get("status") == "ok":
            log.info("رفع خودکار %s برای کاربر %s انجام شد", action, user_id)
        else:
            log.warning(
                "رفع خودکار %s برای %s انجام نشد: %s", action, user_id, result.get("status")
            )
    except asyncio.CancelledError:
        pass
    except Exception as exc:
        log.error("رفع خودکار خطا داد: %s: %s", type(exc).__name__, exc)
    finally:
        task = asyncio.current_task()
        if task:
            operation_tasks["moderation"].discard(task)


async def kick_replied_member(event: Any, client: Any) -> Any:
    """اخراج عضوی که روی پیامش ریپلای شده."""
    can_kick, status = await is_group_admin(event)
    if status == "not_group":
        return "not_group"
    if not can_kick:
        return "no_permission"

    reply = await event.get_reply_message()
    if reply is None:
        return "no_reply"

    user_id = getattr(reply, "sender_id", None)
    if not user_id:
        return "no_user"

    me = await client.get_me()
    if getattr(me, "id", None) == user_id:
        return "self"

    try:
        await client.kick_participant(event.chat_id, user_id)
        return 1
    except AttributeError:
        await client.edit_permissions(
            event.chat_id,
            user_id,
            view_messages=False,
            send_messages=False,
        )
        return 1


async def kick_all_members(event: Any, client: Any) -> Dict[str, Any]:
    """حذف اعضای عادی از کانال/سوپرگروپ سروش‌پلاس."""
    can_kick, status = await is_group_admin(event)
    if status == "not_group":
        return {"status": "not_group"}
    if not can_kick:
        return {"status": "no_permission"}

    chat = await event.get_chat()
    if not (getattr(chat, "megagroup", False) or getattr(chat, "gigagroup", False)):
        return {"status": "unsupported_chat"}

    try:
        from splusthon.tl.functions.channels import (
            GetParticipantsRequest,
            EditBannedRequest,
        )
        from splusthon.tl.types import (
            ChannelParticipantsRecent,
            ChannelParticipantsSearch,
            ChatBannedRights,
        )
    except ImportError as exc:
        return {"status": "unsupported_api", "error": str(exc)}

    channel = await client.get_input_entity(event.chat_id)
    me = await client.get_me()
    my_id = getattr(me, "id", None)

    # در نسخهٔ قبل فقط ChannelParticipantsSearch("") استفاده می‌شد؛
    # ChannelParticipantsRecent هم فیلتر استاندارد لیست اعضاست.
    filters = [ChannelParticipantsRecent(), ChannelParticipantsSearch("")]

    users_by_id: Dict[Any, Any] = {}
    participant_ids: set = set()
    admin_ids: set = set()
    pages = 0

    for participant_filter in filters:
        offset = 0
        while True:
            result = await client(
                GetParticipantsRequest(
                    channel=channel,
                    filter=participant_filter,
                    offset=offset,
                    limit=200,
                    hash=0,
                )
            )
            pages += 1
            users = list(getattr(result, "users", None) or [])
            participants = list(getattr(result, "participants", None) or [])

            for user in users:
                uid = getattr(user, "id", None)
                if uid:
                    users_by_id[uid] = user
                    participant_ids.add(uid)

            for participant in participants:
                uid = getattr(participant, "user_id", None)
                if not uid:
                    continue
                participant_ids.add(uid)
                kind = participant.__class__.__name__.lower()
                if "admin" in kind or "creator" in kind:
                    admin_ids.add(uid)

            batch_count = len(users) or len(participants)
            if batch_count == 0 or batch_count < 200:
                break
            offset += batch_count

        # وقتی Recent اعضای واقعی برگرداند، نیازی به فیلتر جایگزین نیست.
        if participant_ids:
            break

    removed = 0
    skipped_admins = 0
    failed = 0

    # اول بن (=حذف از گروه)، بعد آنبن تا بتواند دوباره عضو شود.
    ban_rights = ChatBannedRights(
        until_date=None,
        view_messages=True,
        send_messages=True,
        send_media=True,
        send_stickers=True,
        send_gifs=True,
        send_games=True,
        send_inline=True,
        embed_links=True,
    )
    unban_rights = ChatBannedRights(until_date=None)

    for uid in sorted(participant_ids):
        if not uid or uid == my_id:
            continue
        if uid in admin_ids:
            skipped_admins += 1
            continue

        try:
            entity = users_by_id.get(uid)
            participant = await client.get_input_entity(entity if entity is not None else uid)

            await client(
                EditBannedRequest(
                    channel=channel,
                    participant=participant,
                    banned_rights=ban_rights,
                )
            )
            await client(
                EditBannedRequest(
                    channel=channel,
                    participant=participant,
                    banned_rights=unban_rights,
                )
            )
            removed += 1
        except Exception:
            failed += 1

    return {
        "status": "ok",
        "removed": removed,
        "skipped_admins": skipped_admins,
        "failed": failed,
        "found": len(participant_ids),
        "pages": pages,
    }


async def pin_replied_message(event: Any, client: Any, unpin: bool = False) -> str:
    """سنجاق یا برداشتن سنجاق پیام ریپلای‌شده."""
    chat = await event.get_chat()
    admin_rights = getattr(chat, "admin_rights", None)
    can_pin = bool(
        getattr(chat, "creator", False)
        or getattr(admin_rights, "pin_messages", False)
    )
    if not can_pin:
        return "no_permission"
    if not event.is_reply:
        return "no_reply"

    reply = await event.get_reply_message()
    if not reply or not getattr(reply, "id", None):
        return "no_message"

    from splusthon.tl.functions.messages import UpdatePinnedMessageRequest
    await client(
        UpdatePinnedMessageRequest(
            peer=event.chat_id,
            id=reply.id,
            silent=False,
            unpin=unpin,
            pm_oneside=False,
        )
    )
    return "ok"


async def resolve_chat_entity(client: Any, chat_value: Any) -> Optional[Any]:
    """حل شناسهٔ عددی/یوزرنیم گپ، شامل IDهای کش‌شده در دیالوگ‌ها."""
    value = str(chat_value).strip()
    if not value:
        return None

    try:
        if re.fullmatch(r"-?\d+", value):
            return await client.get_input_entity(int(value))
        return await client.get_input_entity(value)
    except Exception:
        pass

    try:
        dialogs = await client.get_dialogs(limit=None)
        wanted_id = int(value) if re.fullmatch(r"-?\d+", value) else None
        wanted_username = value.lstrip("@").lower()

        for dialog in dialogs:
            entity = getattr(dialog, "entity", None)
            if entity is None:
                continue

            if wanted_id is not None and getattr(entity, "id", None) == wanted_id:
                return await client.get_input_entity(entity)

            username = getattr(entity, "username", None)
            if username and username.lower() == wanted_username:
                return await client.get_input_entity(entity)
    except Exception:
        return None

    return None


# ─────────────────────────────────────────────────────────────────────────────
# بخش ۳-۶: InviteAll (دعوت گروهی با ذخیرهٔ وضعیت و ادامه از محل قطع)
# ─────────────────────────────────────────────────────────────────────────────

async def invite_all_members(event: Any, client: Any, target_chat: Any) -> Dict[str, Any]:
    """
    مبدا = گپی که /inviteall در آن اجرا می‌شود.
    مقصد = CHAT_ID داده‌شده در دستور.

    چک مدیر بودن روی گپ مبدا انجام نمی‌شود؛ سمت مقصد سرور اجازه را
    تعیین می‌کند (رفتار اصلی حفظ شده است).
    """
    source_chat = event.chat_id

    source = await collect_group_members(client, source_chat, require_group=True)
    if source.get("status") != "ok":
        return source

    target_channel = await resolve_chat_entity(client, target_chat)
    if target_channel is None:
        return {"status": "target_not_found"}

    try:
        from splusthon.tl.functions.channels import (
            GetParticipantsRequest,
            InviteToChannelRequest,
        )
        from splusthon.tl.types import ChannelParticipantsRecent
    except ImportError as exc:
        return {"status": "unsupported_api", "error": str(exc)}

    # اعضای فعلی مقصد برای جلوگیری از دعوت تکراری
    target_ids: set = set()
    try:
        offset = 0
        while True:
            result = await client(
                GetParticipantsRequest(
                    channel=target_channel,
                    filter=ChannelParticipantsRecent(),
                    offset=offset,
                    limit=200,
                    hash=0,
                )
            )

            users = list(getattr(result, "users", None) or [])
            participants = list(getattr(result, "participants", None) or [])

            for user in users:
                uid = getattr(user, "id", None)
                if uid is not None:
                    target_ids.add(uid)

            for participant in participants:
                uid = getattr(participant, "user_id", None)
                if uid is not None:
                    target_ids.add(uid)

            batch_count = max(len(users), len(participants))
            if batch_count == 0 or batch_count < 200:
                break
            offset += batch_count

    except Exception:
        # اگر خواندن اعضای مقصد ممکن نبود، کل عملیات را قطع نکن؛
        # سرور تک‌تک دعوت‌ها را اعتبارسنجی می‌کند.
        target_ids = set()

    me = await client.get_me()
    my_id = getattr(me, "id", None)

    source_users = source.get("users", {})
    user_ids = sorted(source_users.keys())
    pending = [
        uid for uid in user_ids
        if uid != my_id and uid not in target_ids
    ]

    already_member = len(user_ids) - len(pending)
    if my_id in user_ids:
        already_member -= 1
    already_member = max(already_member, 0)

    state = {
        "source_chat": str(source_chat),
        "target_chat": str(target_chat),
        "user_ids": pending,
        "index": 0,
        "found": len(user_ids),
        "already_member": already_member,
        "invited": 0,
        "failed": 0,
        "flood_waits": 0,
        "started_at": datetime.now().isoformat(timespec="seconds"),
        "running": True,
    }

    data["invite_state"] = state
    save_data(data)

    return await run_invite_job(event, client, target_channel)


async def run_invite_job(event: Any, client: Any, target_channel: Any) -> Dict[str, Any]:
    """پردازش وضعیت ماندگار دعوت؛ بعد از قطعی قابل ادامه است."""
    state = data.get("invite_state")
    if not state:
        return {"status": "no_job"}

    from splusthon.tl.functions.channels import InviteToChannelRequest

    total = len(state.get("user_ids", []))
    job_task = asyncio.current_task()
    if job_task:
        add_task(operation_tasks["invite"], job_task)

    status_message = None
    try:
        try:
            status_message = await event.respond(
                "🚀 InviteAll شروع شد...\n\n"
                f"👥 آماده پردازش: {to_persian_digits(total)}\n"
                f"✅ موفق: {to_persian_digits(state.get('invited', 0))}\n"
                f"⚠️ ناموفق: {to_persian_digits(state.get('failed', 0))}"
            )
        except Exception:
            status_message = None

        last_update = time.monotonic()

        while state.get("index", 0) < total:
            index = state["index"]
            uid = state["user_ids"][index]

            try:
                user = await client.get_entity(uid)
                input_user = await client.get_input_entity(user)

                await client(
                    InviteToChannelRequest(channel=target_channel, users=[input_user])
                )
                state["invited"] = state.get("invited", 0) + 1

            except Exception as exc:
                error_name = exc.__class__.__name__.lower()
                error_text = str(exc).lower()

                if "floodwait" in error_name:
                    state["flood_waits"] = state.get("flood_waits", 0) + 1
                    wait_seconds = max(int(getattr(exc, "seconds", 10) or 10), 1)
                    await asyncio.sleep(wait_seconds)

                    try:
                        user = await client.get_entity(uid)
                        input_user = await client.get_input_entity(user)
                        await client(
                            InviteToChannelRequest(channel=target_channel, users=[input_user])
                        )
                        state["invited"] = state.get("invited", 0) + 1
                    except Exception:
                        state["failed"] = state.get("failed", 0) + 1

                elif (
                    "already" in error_name
                    or "already" in error_text
                    or ("participant" in error_text and "exist" in error_text)
                ):
                    state["already_member"] = state.get("already_member", 0) + 1
                else:
                    state["failed"] = state.get("failed", 0) + 1
                    log.info("دعوت کاربر %s ناموفق بود: %s", uid, exc)

            state["index"] = index + 1

            # ذخیرهٔ پیشرفت تا ری‌استارت بتواند از همین‌جا ادامه دهد
            data["invite_state"] = state
            save_data(data)

            now = time.monotonic()
            if status_message is not None and (now - last_update >= 5 or state["index"] == total):
                done = state["index"]
                percent = (done / total * 100) if total else 100
                try:
                    await status_message.edit(
                        "🚀 InviteAll در حال اجرا\n\n"
                        f"📦 پیشرفت: {done}/{total} ({percent:.1f}%)\n"
                        f"✅ دعوت موفق: {state.get('invited', 0)}\n"
                        f"⏭️ از قبل عضو: {state.get('already_member', 0)}\n"
                        f"⚠️ ناموفق: {state.get('failed', 0)}\n"
                        f"⏳ FloodWait: {state.get('flood_waits', 0)}"
                    )
                except Exception:
                    pass
                last_update = now

        state["running"] = False
        data["invite_state"] = state

        add_stat(event.chat_id, "invites_success", state.get("invited", 0))
        add_stat(event.chat_id, "invites_failed", state.get("failed", 0))
        add_stat(event.chat_id, "invites_skipped", state.get("already_member", 0))
        save_data(data)

        result = {"status": "ok", **state}

        if status_message is not None:
            try:
                await status_message.edit(
                    "✅ InviteAll تمام شد.\n\n"
                    f"👥 کل اعضای مبدا: {state.get('found', 0)}\n"
                    f"➕ دعوت موفق: {state.get('invited', 0)}\n"
                    f"⏭️ از قبل عضو: {state.get('already_member', 0)}\n"
                    f"⚠️ ناموفق: {state.get('failed', 0)}\n"
                    f"⏳ FloodWait: {state.get('flood_waits', 0)}"
                )
            except Exception:
                pass

        return result

    except asyncio.CancelledError:
        state["running"] = False
        data["invite_state"] = state
        save_data(data)
        raise
    except Exception as exc:
        state["running"] = False
        state["last_error"] = f"{type(exc).__name__}: {exc}"
        data["invite_state"] = state
        save_data(data)
        return {"status": "error", **state}


async def resume_invite_job(event: Any, client: Any) -> Dict[str, Any]:
    state = data.get("invite_state")
    if not state:
        return {"status": "no_job"}

    if state.get("index", 0) >= len(state.get("user_ids", [])):
        return {"status": "complete", **state}

    target_channel = await resolve_chat_entity(client, state.get("target_chat", ""))
    if target_channel is None:
        return {"status": "target_not_found"}

    state["running"] = True
    data["invite_state"] = state
    save_data(data)

    return await run_invite_job(event, client, target_channel)


# ─────────────────────────────────────────────────────────────────────────────
# بخش ۳-۷: سلامت سلف
# ─────────────────────────────────────────────────────────────────────────────

async def get_self_health(event: Any, client: Any) -> str:
    """بررسی فایل‌های محلی و سلامت اتصال SPlusthon."""
    checks = []

    data_ok = isinstance(data, dict)
    checks.append(("Data", data_ok))

    session_ok = bool(load_session())
    checks.append(("Session", session_ok))

    data_file_ok = os.path.exists(DATA_FILE)
    checks.append(("Data file", data_file_ok))

    started = time.perf_counter()
    connection_ok = False
    connection_ms = None
    account_name = None

    try:
        me = await client.get_me()
        connection_ms = (time.perf_counter() - started) * 1000
        connection_ok = me is not None
        if me is not None:
            account_name = safe_member_name(me)
    except Exception:
        connection_ok = False

    checks.append(("Connection", connection_ok))

    overall_ok = all(ok for _, ok in checks)

    lines = [
        card_title("🩺", f"سلامت سلف · v{VERSION}"),
        "",
        f"{'🟢' if overall_ok else '🟡'} وضعیت کلی: {'OK' if overall_ok else 'CHECK'}",
        f"{'🟢' if data_ok else '🔴'} Data: {'OK' if data_ok else 'ERROR'}",
        f"{'🟢' if session_ok else '🔴'} Session: {'OK' if session_ok else 'ERROR'}",
        f"{'🟢' if data_file_ok else '🔴'} Data File: {'OK' if data_file_ok else 'ERROR'}",
        f"{'🟢' if connection_ok else '🔴'} Connection: {'OK' if connection_ok else 'ERROR'}",
    ]

    if connection_ms is not None:
        lines.append(f"⚡ Ping: {connection_ms:.0f} ms")
    if account_name:
        lines.append(f"👤 Account: {account_name}")

    lines.extend([
        f"⏱ Uptime: {format_uptime()}",
        f"📦 Active tasks: {active_tasks_count()}",
        f"🕐 Started: {START_TIME:%Y/%m/%d - %H:%M:%S}",
        "",
        brand_footer(),
    ])

    return "\n".join(lines)


# ═════════════════════════════════════════════════════════════════════════════
# بخش ۴: سیستم دستورها — رجیستری، هندلرها، dispatcher و راهنما
# ═════════════════════════════════════════════════════════════════════════════

CATS: List[Tuple[str, str]] = [
    ("profile", "👤 پروفایل"),
    ("slots", "💬 اسلات چندپیامی"),
    ("automation", "🤖 اتوماسیون"),
    ("moderation", "🛡️ مدیریت"),
    ("cleanup", "🧹 پاک‌سازی"),
    ("tools", "🔎 ابزار"),
    ("schedule", "⏱ زمان‌بندی"),
    ("notes", "📝 یادداشت"),
    ("status", "📊 وضعیت و آمار"),
    ("stop", "🛑 توقف"),
    ("system", "⚙️ سیستم"),
]

COMMANDS: Dict[str, Dict[str, Any]] = {}


def command(*names: str, cat: str, usage: str, desc: str) -> Callable:
    """رجیستری دستورها: هر هندلر با متادیتا ثبت می‌شود و /help خودکار می‌سازد."""
    def deco(fn: Callable) -> Callable:
        for name in names:
            COMMANDS[name] = {
                "fn": fn,
                "cat": cat,
                "usage": usage,
                "desc": desc,
                "primary": names[0],
            }
        return fn
    return deco


async def _respond(event: Any, text: str) -> None:
    try:
        await event.respond(text)
    except Exception as exc:
        log.error("ارسال پاسخ ناموفق بود: %s: %s", type(exc).__name__, exc)


# ─────────────────────────────────────────────────────────────────────────────
# بخش ۴-۱: راهنما
# ─────────────────────────────────────────────────────────────────────────────

def help_text() -> str:
    lines = [
        "╭───── ✦ 🤖 HPVIRUS SELF ✦ ─────╮",
        f"│  👑 {CREATOR}   •   📦 v{VERSION}      │",
        "╰────────────────────────────────╯",
        "",
    ]
    for cat_key, cat_title in CATS:
        entries = [
            spec for name, spec in COMMANDS.items()
            if spec["cat"] == cat_key and name == spec["primary"]
        ]
        if not entries:
            continue
        lines.append(f"━━ {cat_title} ━━")
        for spec in entries:
            lines.append(f"{spec['usage']} · {spec['desc']}")
        lines.append("")
    lines.append("⚙️ زمان: 53s | 53m | 2h | 1d — اعداد فارسی هم OK")
    lines.append("ℹ️ توضیح هر دستور: /help دستور (مثال: /help spam)")
    lines.append(brand_footer())
    return "\n".join(lines)


def help_for(command_name: str) -> str:
    spec = COMMANDS.get(command_name)
    if spec is None:
        return ""
    aliases = [n for n, s in COMMANDS.items() if s["primary"] == command_name and n != command_name]
    lines = [
        card_title("📖", f"راهنمای {command_name}"),
        "",
        f"📌 کاربرد: {spec['usage']}",
        f"💬 توضیح: {spec['desc']}",
        f"🗂 دسته: {dict(CATS).get(spec['cat'], spec['cat'])}",
    ]
    if aliases:
        lines.append(f"🔀 نام‌های دیگر: {' '.join(aliases)}")
    lines.append("")
    lines.append(brand_footer())
    return "\n".join(lines)


@command("/help", "/start", cat="system", usage="/help [دستور]",
         desc="راهنمای کامل سلف")
async def cmd_help(event: Any, client: Any, parts: List[str], text: str) -> None:
    if len(parts) >= 2:
        target = parts[1].lower().lstrip("/")
        detail = help_for("/" + target)
        if detail:
            await _respond(event, detail)
            return
        await _respond(event, f"ℹ️ دستور «{target}» پیدا نشد.\n\n{help_text()}")
        return
    await _respond(event, help_text())


@command("/start", cat="system", usage="/start", desc="کارت خوش‌آمد و شروع سریع")
async def cmd_start(event: Any, client: Any, parts: List[str], text: str) -> None:
    await _respond(event, "\n".join([
        "╭───── ✦ 🤖 HPVIRUS SELF ✦ ─────╮",
        f"│  👑 {CREATOR}   •   📦 v{VERSION}      │",
        "╰────────────────────────────────╯",
        "",
        "سلام 👋 سلف آماده است!",
        "📝 لیست کامل دستورها: /help",
        "🩺 وضعیت سلامت: /health",
        "",
        brand_footer(),
    ]))


# ─────────────────────────────────────────────────────────────────────────────
# بخش ۴-۲: پروفایل
# ─────────────────────────────────────────────────────────────────────────────

@command("/name", cat="profile", usage="/name متن", desc="تغییر نام اکانت")
async def cmd_name(event: Any, client: Any, parts: List[str], text: str) -> None:
    if len(parts) < 2:
        await _respond(event, "استفاده: /name نام")
        return

    name = text[len("/name"):].strip()
    if not name:
        await _respond(event, "⛔ اسم خالی است.")
        return

    data["display_name"] = name
    save_data(data)

    if data.get("name_clock"):
        success = await update_clock_profile(client)
    else:
        success = await update_name(client, name)

    await _respond(event, "✅ اسم تغییر کرد." if success else "❌ تغییر اسم ناموفق بود.")


async def _clock_set(event: Any, client: Any, parts: List[str], mode: str) -> None:
    if mode == "on":
        if not str(data.get("display_name", "")).strip():
            await _respond(event, "⛔ اول /name نام را اجرا کن.")
            return
        data["name_clock"] = True
        save_data(data)
        await start_name_clock(client)
        await _respond(event, "⏰ ساعت فعال شد.")
    elif mode == "off":
        await stop_name_clock(client)
        await _respond(event, "⏰ ساعت خاموش شد.")
    else:
        await _respond(event, "فقط on یا off.")


@command("/clock", cat="profile", usage="/clock on|off",
         desc="ساعت زنده در نام یا بیو")
async def cmd_clock(event: Any, client: Any, parts: List[str], text: str) -> None:
    if len(parts) < 2:
        await _respond(event, "/clock on\n/clock off")
        return
    await _clock_set(event, client, parts, parts[1].lower())


@command("/time", cat="tools", usage="/time [on|off]",
         desc="نمایش زمان الان (یا تنظیم ساعت پروفایل)")
async def cmd_time(event: Any, client: Any, parts: List[str], text: str) -> None:
    if len(parts) >= 2 and parts[1].lower() in {"on", "off"}:
        await _clock_set(event, client, parts, parts[1].lower())
        return

    now = datetime.now()
    await _respond(event, "\n".join([
        card_title("🕐", "زمان الان"),
        "",
        f"⏰ ساعت: {to_persian_digits(now.strftime('%H:%M:%S'))}",
        f"📅 شمسی: {jalali_today_text()}",
        f"🗓 میلادی: {to_persian_digits(now.strftime('%Y/%m/%d'))} — {now.strftime('%A')}",
        f"⏱ Uptime: {format_uptime()}",
        "",
        brand_footer(),
    ]))


@command("/jdate", cat="tools", usage="/jdate", desc="تاریخ امروز به شمسی")
async def cmd_jdate(event: Any, client: Any, parts: List[str], text: str) -> None:
    await _respond(event, "\n".join([
        card_title("📅", "تاریخ شمسی"),
        "",
        f"🗓 {jalali_today_text(with_time=True)}",
        "",
        brand_footer(),
    ]))


@command("/clockpos", cat="profile", usage="/clockpos lastname|bio",
         desc="محل قرارگیری ساعت")
async def cmd_clockpos(event: Any, client: Any, parts: List[str], text: str) -> None:
    if len(parts) < 2 or parts[1].lower() not in {"lastname", "bio"}:
        await _respond(event, "/clockpos lastname\n/clockpos bio")
        return

    data["clock_position"] = parts[1].lower()
    save_data(data)

    if data.get("name_clock"):
        await update_clock_profile(client)

    await _respond(event, f"✅ محل ساعت: {data['clock_position']}")


@command("/clockfont", cat="profile", usage="/clockfont [1-16]",
         desc="انتخاب فونت ساعت")
async def cmd_clockfont(event: Any, client: Any, parts: List[str], text: str) -> None:
    if len(parts) < 2:
        await _respond(event, "استفاده: /clockfont [1-16]")
        return

    try:
        font = int(from_persian_digits(parts[1]))
    except ValueError:
        await _respond(event, "⛔ شماره فونت باید عدد باشد.")
        return

    if font not in CLOCK_FONTS:
        await _respond(event, "⛔ فونت باید بین 1 تا 16 باشد.")
        return

    data["clock_font"] = font
    save_data(data)

    if data.get("name_clock"):
        await update_clock_profile(client)

    await _respond(event, f"✅ فونت ساعت روی {font} تنظیم شد.")


@command("/clockfonts", cat="profile", usage="/clockfonts",
         desc="نمایش همهٔ فونت‌های ساعت")
async def cmd_clockfonts(event: Any, client: Any, parts: List[str], text: str) -> None:
    await _respond(event,
                   "⏰ فونت‌های ساعت:\n\n" + "\n".join(
                       f"{number}. {datetime.now().strftime(fmt)}"
                       for number, fmt in CLOCK_FONTS.items()
                   ))


@command("/me", cat="profile", usage="/me", desc="اطلاعات اکانت خودت")
async def cmd_me(event: Any, client: Any, parts: List[str], text: str) -> None:
    try:
        me = await client.get_me()
        if me is None:
            await _respond(event, "❌ دریافت اطلاعات اکانت ناموفق بود.")
            return
        info, _photo = await get_user_info(client, me)
        await _respond(event, info)
    except Exception as exc:
        await _respond(event, f"❌ دریافت اطلاعات اکانت ناموفق بود.\n{type(exc).__name__}: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# بخش ۴-۳: اسلات‌ها و عملیات تکراری
# ─────────────────────────────────────────────────────────────────────────────

async def _handle_set_slot(event: Any, client: Any, parts: List[str], text: str,
                           kind: str, slot: int) -> None:
    if not 1 <= slot <= 8:
        await _respond(event, "⛔ اسلات باید 1 تا 8 باشد.")
        return

    label = "Spam" if kind == "spam" else "Reply"
    message = text[len(parts[0]):].strip()
    if not message:
        await _respond(event, f"استفاده: /set{kind.lower()}{slot} پیام اول | پیام دوم | پیام سوم")
        return

    messages = split_slot_messages(message)
    if not messages:
        await _respond(event, "⛔ حداقل یک پیام معتبر وارد کن.")
        return

    key = "spam_slots" if kind == "spam" else "rep_slots"
    data[key][slot - 1] = " | ".join(messages)
    save_data(data)
    await _respond(event, f"✅ {label} slot {slot} ذخیره شد.\n💬 تعداد پیام‌ها: {len(messages)}")


@command("/spam", cat="slots", usage="/spam تعداد زمان اسلات",
         desc="ارسال تکراری پیام‌های اسلات")
async def cmd_spam(event: Any, client: Any, parts: List[str], text: str) -> None:
    if len(parts) < 3:
        await _respond(event, "استفاده: /spam [تعداد] [زمان] [اسلات 1-8]")
        return

    if len(parts) < 4:
        await _respond(event,
                       "❌ فرمت اشتباه است.\nاستفاده: /spam تعداد زمان اسلات\n"
                       "مثال: /spam 5 53s 1\n"
                       "مثال اسلات: /setspam1 سلام | خوبی؟ | چه خبر؟")
        return

    try:
        count = int(from_persian_digits(parts[1]))
        slot = int(from_persian_digits(parts[3]))
    except ValueError:
        await _respond(event, "❌ تعداد و اسلات باید عدد باشند و زمان مثل 53s، 53m یا 2h باشد.")
        return

    delay = parse_duration(parts[2])
    # رفع باگ: در نسخهٔ قبل زمان نامعتبر اینجا چک نمی‌شد و تسک بی‌صدا می‌مرد.
    if delay is None:
        await _respond(event, "❌ زمان معتبر نیست. مثال: 53s، 53m، 2h یا 1d")
        return

    if count <= 0:
        await _respond(event, "❌ تعداد باید بیشتر از صفر باشد.")
        return

    if count > MAX_SPAM_COUNT:
        await _respond(event, f"⛔ سقف هر عملیات {MAX_SPAM_COUNT} بار است (محافظت از اکانت).")
        return

    if not 1 <= slot <= 8:
        await _respond(event, "❌ اسلات باید بین 1 تا 8 باشد.")
        return

    message = get_slot(data["spam_slots"], slot)
    if not message:
        await _respond(event, f"⛔ Spam slot {slot} خالی است.")
        return

    messages = split_slot_messages(message)
    if not messages:
        await _respond(event, f"⛔ Spam slot {slot} پیام معتبری ندارد.")
        return

    task = asyncio.create_task(
        repeated_send(event, messages, count, delay, operation_tasks["spam"])
    )
    add_task(operation_tasks["spam"], task)
    await _respond(event, f"🚀 عملیات ارسال شروع شد: {count} بار")


@command("/rep", cat="slots", usage="/rep تعداد زمان اسلات",
         desc="ریپلای تکراری روی پیام هدف")
async def cmd_rep(event: Any, client: Any, parts: List[str], text: str) -> None:
    if len(parts) < 3:
        await _respond(event, "استفاده: /rep [تعداد] [زمان] [اسلات 1-8]")
        return

    if not event.is_reply:
        await _respond(event, "⛔ این دستور باید روی یک پیام Reply شود.")
        return

    if len(parts) < 4:
        await _respond(event, "❌ فرمت اشتباه است.\nاستفاده: /rep تعداد زمان اسلات\nمثال: /rep 5 53s 1")
        return

    try:
        count = int(from_persian_digits(parts[1]))
        slot = int(from_persian_digits(parts[3]))
    except ValueError:
        await _respond(event, "❌ تعداد و اسلات باید عدد باشند و زمان مثل 53s، 53m یا 2h باشد.")
        return

    delay = parse_duration(parts[2])
    if delay is None:
        await _respond(event, "❌ زمان نامعتبر است. مثال: 53s، 53m، 2h یا 1d")
        return

    if count <= 0:
        await _respond(event, "❌ تعداد باید بیشتر از صفر باشد.")
        return

    if count > MAX_SPAM_COUNT:
        await _respond(event, f"⛔ سقف هر عملیات {MAX_SPAM_COUNT} بار است (محافظت از اکانت).")
        return

    if not 1 <= slot <= 8:
        await _respond(event, "❌ اسلات باید بین 1 تا 8 باشد.")
        return

    message = get_slot(data["rep_slots"], slot)
    if not message:
        await _respond(event, f"⛔ Reply slot {slot} خالی است.")
        return

    messages = split_slot_messages(message)
    if not messages:
        await _respond(event, f"⛔ Reply slot {slot} پیام معتبری ندارد.")
        return

    task = asyncio.create_task(repeated_reply(event, messages, count, delay))
    add_task(operation_tasks["rep"], task)
    # مثل قبل: بدون پیام تأیید و حذف خودِ دستور
    await delete_own_messages(event, client, 1)


@command("/shomaresh", cat="slots", usage="/shomaresh تعداد",
         desc="شمارش عددی ۱ تا N")
async def cmd_shomaresh(event: Any, client: Any, parts: List[str], text: str) -> None:
    if len(parts) < 2:
        await _respond(event, "استفاده: /shomaresh تعداد")
        return

    try:
        count = int(from_persian_digits(parts[1]))
    except ValueError:
        await _respond(event, "⛔ تعداد باید عدد باشد.")
        return

    if not 1 <= count <= MAX_SHOMARESH:
        await _respond(event, f"⛔ تعداد باید بین 1 تا {MAX_SHOMARESH} باشد.")
        return

    task = asyncio.create_task(count_numbers(event, count))
    add_task(operation_tasks["shomaresh"], task)
    await _respond(event, "🔢 شمارش شروع شد.")


# ─────────────────────────────────────────────────────────────────────────────
# بخش ۴-۴: اتوماسیون (پاسخگوی خودکار، تریگر، خوش‌آمد/خداحافظ)
# ─────────────────────────────────────────────────────────────────────────────

@command("/auto", "/autoresponder", cat="automation", usage="/auto on|off",
         desc="روشن/خاموش کردن پاسخگوی خودکار")
async def cmd_auto(event: Any, client: Any, parts: List[str], text: str) -> None:
    if len(parts) < 2:
        await _respond(event, f"{parts[0]} on\n{parts[0]} off")
        return

    mode = parts[1].lower()
    if mode not in {"on", "off"}:
        await _respond(event, "فقط on یا off.")
        return

    data["auto_reply"] = mode == "on"
    save_data(data)
    await _respond(event, f"🤖 Auto Reply {'فعال' if mode == 'on' else 'خاموش'} شد.")


@command("/setauto", "/setautomsg", cat="automation", usage="/setauto متن",
         desc="متن پاسخگوی خودکار")
async def cmd_setauto(event: Any, client: Any, parts: List[str], text: str) -> None:
    message = text[len(parts[0]):].strip()
    if not message:
        await _respond(event, "⛔ متن خالی است.")
        return

    data["auto_message"] = message
    save_data(data)
    await _respond(event, "✅ متن پاسخگو ذخیره شد.")


@command("/autobots", cat="automation", usage="/autobots on|off",
         desc="پاسخ خودکار به ربات‌ها (پیش‌فرض: روشن مثل قبل)")
async def cmd_autobots(event: Any, client: Any, parts: List[str], text: str) -> None:
    if len(parts) < 2 or parts[1].lower() not in {"on", "off"}:
        await _respond(event, "/autobots on\n/autobots off")
        return
    data["auto_reply_bots"] = parts[1].lower() == "on"
    save_data(data)
    await _respond(event, f"🛡 پاسخ به ربات‌ها: {'روشن' if data['auto_reply_bots'] else 'خاموش'}")


@command("/autogroups", cat="automation", usage="/autogroups on|off",
         desc="پاسخ خودکار در گروه‌ها (پیش‌فرض: روشن مثل قبل)")
async def cmd_autogroups(event: Any, client: Any, parts: List[str], text: str) -> None:
    if len(parts) < 2 or parts[1].lower() not in {"on", "off"}:
        await _respond(event, "/autogroups on\n/autogroups off")
        return
    data["auto_reply_groups"] = parts[1].lower() == "on"
    save_data(data)
    await _respond(event, f"👥 پاسخ در گروه‌ها: {'روشن' if data['auto_reply_groups'] else 'خاموش'}")


@command("/setcooldown", cat="automation", usage="/setcooldown ثانیه",
         desc="حداقل فاصلهٔ پاسخ خودکار به هر گپ (0 = بی‌نهایت مثل قبل)")
async def cmd_setcooldown(event: Any, client: Any, parts: List[str], text: str) -> None:
    if len(parts) < 2:
        await _respond(event, "استفاده: /setcooldown 30   (0 = خاموش)")
        return
    try:
        seconds = int(from_persian_digits(parts[1]))
    except ValueError:
        await _respond(event, "❌ عدد ثانیه معتبر نیست.")
        return
    if not 0 <= seconds <= 86400:
        await _respond(event, "⛔ مقدار باید بین 0 تا 86400 باشد.")
        return
    data["auto_reply_cooldown"] = seconds
    save_data(data)
    state = f"{seconds} ثانیه" if seconds else "خاموش (مثل قبل)"
    await _respond(event, f"⏳ فاصلهٔ پاسخ خودکار: {state}")


@command("/trigger", cat="automation", usage="/trigger add کلمه | پاسخ",
         desc="مدیریت تریگرهای پاسخ خودکار")
async def cmd_trigger(event: Any, client: Any, parts: List[str], text: str) -> None:
    if len(parts) < 2:
        await _respond(event, "استفاده:\n/trigger add کلمه | پاسخ\n/trigger list\n/trigger del شماره")
        return
    action = parts[1].lower()
    if action == "add":
        raw = text[len("/trigger add"):].strip()
        bits = [x.strip() for x in raw.split("|", 1)]
        if len(bits) != 2 or not bits[0] or not bits[1]:
            await _respond(event, "❌ فرمت: /trigger add کلمه | پاسخ")
            return
        data["triggers"].append({"trigger": bits[0].lower(), "response": bits[1]})
        save_data(data)
        await _respond(event, "✅ Trigger ذخیره شد.")
        return
    if action == "list":
        if not data["triggers"]:
            await _respond(event, "ℹ️ Triggerی ثبت نشده.")
            return
        await _respond(event, "🤖 Triggerها\n\n" + "\n".join(
            f"{i}. {item['trigger']} → {item['response']}"
            for i, item in enumerate(data["triggers"], 1)
        ))
        return
    if action == "del":
        try:
            index = int(from_persian_digits(parts[2])) - 1
            item = data["triggers"].pop(index)
        except (ValueError, IndexError):
            await _respond(event, "❌ شماره Trigger نامعتبر است.")
            return
        save_data(data)
        await _respond(event, f"🗑 حذف شد: {item['trigger']}")
        return
    await _respond(event, "❌ دستور Trigger نامعتبر است.")


@command("/welcome", cat="automation", usage="/welcome on|off",
         desc="خوش‌آمدگویی به عضو جدید")
async def cmd_welcome(event: Any, client: Any, parts: List[str], text: str) -> None:
    if len(parts) < 2:
        await _respond(event, f"{parts[0]} on\n{parts[0]} off")
        return
    mode = parts[1].lower()
    if mode not in {"on", "off"}:
        await _respond(event, "فقط on یا off.")
        return
    data["welcome_enabled"] = mode == "on"
    save_data(data)
    await _respond(event, f"✅ Welcome {'فعال' if data['welcome_enabled'] else 'خاموش'} شد.")


@command("/setwelcome", cat="automation", usage="/setwelcome متن",
         desc="متن خوش‌آمد ({name} {username} {chat})")
async def cmd_setwelcome(event: Any, client: Any, parts: List[str], text: str) -> None:
    message = text[len(parts[0]):].strip()
    if not message:
        await _respond(event, "❌ متن خالی است.")
        return
    data["welcome_message"] = message
    save_data(data)
    await _respond(event, "✅ پیام ذخیره شد.")


@command("/goodbye", cat="automation", usage="/goodbye on|off",
         desc="پیام خداحافظی برای عضو خارج‌شده")
async def cmd_goodbye(event: Any, client: Any, parts: List[str], text: str) -> None:
    if len(parts) < 2:
        await _respond(event, f"{parts[0]} on\n{parts[0]} off")
        return
    mode = parts[1].lower()
    if mode not in {"on", "off"}:
        await _respond(event, "فقط on یا off.")
        return
    data["goodbye_enabled"] = mode == "on"
    save_data(data)
    await _respond(event, f"✅ Goodbye {'فعال' if data['goodbye_enabled'] else 'خاموش'} شد.")


@command("/setgoodbye", cat="automation", usage="/setgoodbye متن",
         desc="متن خداحافظی ({name} {username} {chat})")
async def cmd_setgoodbye(event: Any, client: Any, parts: List[str], text: str) -> None:
    message = text[len(parts[0]):].strip()
    if not message:
        await _respond(event, "❌ متن خالی است.")
        return
    data["goodbye_message"] = message
    save_data(data)
    await _respond(event, "✅ پیام ذخیره شد.")


# ─────────────────────────────────────────────────────────────────────────────
# بخش ۴-۵: مدیریت گروه
# ─────────────────────────────────────────────────────────────────────────────

@command("/adminlist", cat="moderation", usage="/adminlist",
         desc="لیست مدیران گپ")
async def cmd_adminlist(event: Any, client: Any, parts: List[str], text: str) -> None:
    try:
        admins = await get_channel_admins(event, client)
        if admins == "unsupported_chat":
            await _respond(event, "⛔ این دستور فقط داخل گپ/سوپرگروپ قابل استفاده است.")
            return
        if not admins:
            await _respond(event, "ℹ️ لیست مدیرها خالی است یا قابل دریافت نیست.")
            return
        lines = ["🛡️ مدیران گپ\n"]
        for index, user in enumerate(admins, 1):
            name = safe_member_name(user)
            username = getattr(user, "username", None)
            suffix = f" • @{username}" if username else ""
            lines.append(f"{index}. {name}{suffix} • ID: {getattr(user, 'id', '-')}")
        await _respond(event, "\n".join(lines))
    except Exception as exc:
        await _respond(event, f"❌ دریافت مدیرها ناموفق بود.\n{exc}")


@command("/members", cat="moderation", usage="/members [صفحه]",
         desc="لیست اعضای گپ با صفحه‌بندی")
async def cmd_members(event: Any, client: Any, parts: List[str], text: str) -> None:
    try:
        page = 1
        if len(parts) >= 2:
            page = int(from_persian_digits(parts[1]))
            if page <= 0:
                raise ValueError

        result = await get_members_summary(event, client, page)

        if result.get("status") == "unsupported_chat":
            await _respond(event, "⛔ این دستور فقط داخل گپ/سوپرگروپ قابل استفاده است.")
        elif result.get("status") == "ok":
            await _respond(event, result["text"])
        else:
            await _respond(event, f"❌ دریافت اعضا ناموفق بود.\n{result}")
    except ValueError:
        await _respond(event, "❌ شماره صفحه باید عدد مثبت باشد.")
    except Exception as exc:
        await _respond(event,
                       "❌ دریافت لیست اعضا ناموفق بود.\n"
                       f"نوع خطا: {type(exc).__name__}\n"
                       f"جزئیات: {exc}")


@command("/top", cat="moderation", usage="/top [تعداد]",
         desc="فعال‌ترین اعضای گپ")
async def cmd_top(event: Any, client: Any, parts: List[str], text: str) -> None:
    try:
        limit = 10
        if len(parts) >= 2:
            limit = int(from_persian_digits(parts[1]))
        if not 1 <= limit <= MAX_TOP_LIMIT:
            raise ValueError
    except ValueError:
        await _respond(event, f"❌ تعداد باید بین 1 تا {MAX_TOP_LIMIT} باشد.")
        return

    try:
        result = await get_top_members(event, client, limit=limit)
        if result.get("status") != "ok":
            await _respond(event,
                           "❌ دریافت Top ناموفق بود.\n"
                           f"{result.get('error', 'unknown error')}")
            return

        rows = result.get("rows", [])
        if not rows:
            await _respond(event, "ℹ️ در پیام‌های اخیر فعالیتی پیدا نشد.")
            return

        lines = [
            card_title("🏆", "فعال‌ترین اعضا"),
            "",
            f"📨 بررسی پیام‌ها: {to_persian_digits(result.get('scanned', 0))}",
            f"👥 کاربران فعال: {to_persian_digits(result.get('active_users', 0))}",
            "",
        ]

        medals = {1: "🥇", 2: "🥈", 3: "🥉"}
        for index, name, count in rows:
            medal = medals.get(index, f"{to_persian_digits(index)}.")
            lines.append(f"{medal} {name} — {to_persian_digits(count)} پیام")

        lines.extend(["", brand_footer()])
        await _respond(event, "\n".join(lines))
    except Exception as exc:
        await _respond(event, f"❌ دریافت Top ناموفق بود.\n{type(exc).__name__}: {exc}")


@command("/kick", cat="moderation", usage="/kick ← Reply",
         desc="اخراج عضو هدف")
async def cmd_kick(event: Any, client: Any, parts: List[str], text: str) -> None:
    try:
        result = await kick_replied_member(event, client)
        if result == "not_group":
            await _respond(event, "⛔ این دستور فقط داخل گپ/گروه قابل استفاده است.")
        elif result == "no_permission":
            await _respond(event, "⛔ دسترسی اخراج عضو نداری.")
        elif result == "no_reply":
            await _respond(event, "↩️ برای اخراج یک نفر، روی پیام خودش Reply کن و بعد /kick بزن.")
        elif result == "self":
            await _respond(event, "⛔ نمی‌توانی خودت را با این دستور اخراج کنی.")
        elif result == "no_user":
            await _respond(event, "❌ کاربر پیام پیدا نشد.")
        else:
            add_stat(event.chat_id, "kicks")
            save_data(data)
            await _respond(event, "✅ عضو از گپ حذف شد.")
    except Exception as exc:
        await _respond(event, f"❌ اخراج عضو انجام نشد.\n{exc}")


@command("/kickall", cat="moderation", usage="/kickall تایید",
         desc="اخراج همهٔ اعضای عادی (نیاز به تایید)")
async def cmd_kickall(event: Any, client: Any, parts: List[str], text: str) -> None:
    if len(parts) != 2 or parts[1] != "تایید":
        await _respond(event,
                       "⚠️ این دستور اعضای عادی گپ را اخراج می‌کند.\n\n"
                       "برای اجرای آن دقیقاً بنویس:\n"
                       "/kickall تایید")
        return

    try:
        result = await kick_all_members(event, client)
        status = result.get("status") if isinstance(result, dict) else None

        if status == "not_group":
            await _respond(event, "⛔ این دستور فقط داخل گپ/سوپرگروپ قابل استفاده است.")
        elif status == "no_permission":
            await _respond(event, "⛔ دسترسی اخراج اعضا نداری.")
        elif status == "unsupported_chat":
            await _respond(event, "⛔ این نوع Channel برای اخراج اعضا توسط این دستور پشتیبانی نمی‌شود.")
        elif status == "unsupported_api":
            await _respond(event,
                           "❌ API لازم در نسخه فعلی SPlusthon موجود نیست.\n\n"
                           f"جزئیات: {result.get('error', 'unknown')}")
        elif status == "ok":
            add_stat(event.chat_id, "kicks", result["removed"])
            save_data(data)
            await _respond(event,
                           "✅ عملیات اخراج انجام شد.\n\n"
                           f"👤 حذف‌شده: {result['removed']}\n"
                           f"🛡️ مدیران/حساب‌های محافظت‌شده: {result['skipped_admins']}\n"
                           f"⚠️ ناموفق: {result['failed']}\n"
                           f"🔎 اعضای پیدا‌شده: {result['found']}")
        else:
            await _respond(event, "❌ نتیجه نامشخص از عملیات اخراج دریافت شد.")
    except Exception as exc:
        await _respond(event, f"❌ عملیات حذف اعضا کامل نشد.\n{type(exc).__name__}: {exc}")


MOD_LABELS = {
    "ban": "مسدود",
    "unban": "رفع مسدودی",
    "mute": "ساکت",
    "unmute": "رفع سکوت",
}


@command("/ban", "/unban", "/mute", "/unmute", cat="moderation",
         usage="/ban [زمان] ← Reply", desc="بن/آنبن/میوت/آنمیوت عضو هدف")
async def cmd_moderate(event: Any, client: Any, parts: List[str], text: str) -> None:
    command = parts[0].lower()
    action = command[1:]
    duration = None
    if command in {"/ban", "/mute"} and len(parts) >= 2:
        duration = parse_duration(parts[1])
        if duration is None:
            await _respond(event, "❌ زمان معتبر نیست. مثال: 10s، 5m، 2h، 1d")
            return

    try:
        result = await moderate_member(event, client, action)
        status = result.get("status") if isinstance(result, dict) else None
        if status == "not_group":
            await _respond(event, "⛔ این دستور فقط داخل گپ/گروه قابل استفاده است.")
        elif status == "no_permission":
            await _respond(event, "⛔ دسترسی مدیریت اعضا نداری.")
        elif status == "no_reply":
            await _respond(event, "↩️ روی پیام عضو Reply کن و بعد دستور را بزن.")
        elif status == "no_user":
            await _respond(event, "❌ کاربر پیام پیدا نشد.")
        elif status == "self":
            await _respond(event, "⛔ نمی‌توانی خودت را مدیریت کنی.")
        elif status == "target_admin":
            await _respond(event, "🛡️ مدیرها با این دستور دستکاری نمی‌شوند.")
        elif status == "unsupported_chat":
            await _respond(event, "⛔ این نوع چت برای این عملیات پشتیبانی نمی‌شود.")
        else:
            if action == "ban":
                add_stat(event.chat_id, "bans")
            elif action == "mute":
                add_stat(event.chat_id, "mutes")
            save_data(data)
            if duration and event.is_reply:
                reply = await event.get_reply_message()
                target_id = getattr(reply, "sender_id", None) if reply else None
                if target_id:
                    task = asyncio.create_task(
                        schedule_unmoderate(event, client, target_id, action, duration)
                    )
                    add_task(operation_tasks["moderation"], task)
            extra = f" تا {format_duration(duration)}" if duration else ""
            await _respond(event, f"✅ عضو {MOD_LABELS[action]} شد{extra}.")
    except Exception as exc:
        await _respond(event, f"❌ عملیات {MOD_LABELS[action]} انجام نشد.\n{exc}")


@command("/pin", "/unpin", cat="moderation", usage="/pin ← Reply",
         desc="سنجاق/برداشتن سنجاق پیام")
async def cmd_pin(event: Any, client: Any, parts: List[str], text: str) -> None:
    unpin = parts[0].lower() == "/unpin"
    try:
        result = await pin_replied_message(event, client, unpin=unpin)
        if result == "no_permission":
            await _respond(event, "⛔ دسترسی سنجاق کردن پیام را نداری.")
        elif result == "no_reply":
            await _respond(event, "↩️ روی پیامی که می‌خواهی سنجاق/برداری Reply کن.")
        elif result == "no_message":
            await _respond(event, "❌ پیام پیدا نشد.")
        else:
            await _respond(event, "✅ پیام از سنجاق خارج شد." if unpin else "📌 پیام سنجاق شد.")
    except Exception as exc:
        label = "برداشتن سنجاق" if unpin else "سنجاق"
        await _respond(event, f"❌ عملیات {label} ناموفق بود.\n{exc}")


@command("/purge", cat="cleanup", usage="/purge ← Reply",
         desc="حذف همهٔ پیام‌ها از پیام هدف تا الان")
async def cmd_purge(event: Any, client: Any, parts: List[str], text: str) -> None:
    chat = await event.get_chat()
    if not _chat_is_group(chat):
        await _respond(event, "⛔ این دستور فقط داخل گپ/گروه قابل استفاده است.")
        return
    if not _can_delete_messages(chat):
        await _respond(event, "⛔ دسترسی حذف پیام نداری.")
        return
    if not event.is_reply:
        await _respond(event, "↩️ روی اولین پیامی که می‌خواهی از آنجا پاک شود Reply کن.")
        return

    reply = await event.get_reply_message()
    reply_id = getattr(reply, "id", None) if reply else None
    if not reply_id:
        await _respond(event, "❌ پیام هدف پیدا نشد.")
        return

    status_msg = await event.respond("🧹 در حال پاک‌سازی...")
    try:
        deleted = await purge_messages(event, client, reply_id)
    except Exception as exc:
        log.exception("purge ناموفق بود")
        deleted = -1
        error_text = f"{type(exc).__name__}: {exc}"

    try:
        if deleted == 0:
            await status_msg.edit("ℹ️ پیامی برای حذف پیدا نشد.")
        elif deleted > 0:
            add_stat(event.chat_id, "deleted_messages", deleted)
            save_data(data)
            await status_msg.edit(f"✅ {deleted} پیام حذف شد (سقف {MAX_PURGE}).")
        else:
            await status_msg.edit(f"❌ پاک‌سازی ناموفق بود.\n{error_text}")
    except Exception:
        pass


@command("/inviteall", cat="moderation", usage="/inviteall CHAT_ID تایید",
         desc="دعوت اعضای این گپ به گپ مقصد")
async def cmd_inviteall(event: Any, client: Any, parts: List[str], text: str) -> None:
    if len(parts) < 3 or parts[2].lower() not in {"تایید", "confirm"}:
        await _respond(event,
                       "⚠️ دعوت گروهی نیاز به تأیید دارد.\n\n"
                       "گپ فعلی = مبدا\n"
                       "CHAT_ID = مقصد\n\n"
                       "استفاده:\n"
                       "/inviteall CHAT_ID تایید\n\n"
                       "مثال:\n"
                       "/inviteall -1000024339727 تایید")
        return

    state = data.get("invite_state")

    # جلوگیری از دو عملیات هم‌زمان
    if state and state.get("running"):
        await _respond(event,
                       "⏳ یک عملیات InviteAll همین الان در حال اجراست.\n"
                       "/inviteprogress")
        return

    target_chat = parts[1]

    # ادامهٔ عملیات قبلی
    if (
        state
        and state.get("index", 0) < len(state.get("user_ids", []))
        and str(state.get("target_chat")) == str(target_chat)
    ):
        try:
            task = asyncio.create_task(resume_invite_job(event, client))
            add_task(operation_tasks["invite"], task)
            await _respond(event, "♻️ عملیات قبلی پیدا شد؛ ادامه از آخرین نقطه شروع می‌شود.")
        except Exception as exc:
            await _respond(event, f"❌ ادامه عملیات ناموفق بود.\n{type(exc).__name__}: {exc}")
        return

    # شروع عملیات جدید
    try:
        result = await invite_all_members(event, client, target_chat)
        status = result.get("status")

        if status == "target_not_found":
            await _respond(event, "❌ گپ مقصد پیدا نشد یا این session به آن دسترسی ندارد.")
        elif status == "unsupported_api":
            await _respond(event, f"❌ API لازم موجود نیست.\n{result.get('error', 'unknown')}")
        elif status == "ok":
            if result.get("invited", 0) == 0 and result.get("failed", 0) == 0:
                await _respond(event, "ℹ️ کار جدیدی برای دعوت باقی نمانده بود.")
        elif status == "error":
            await _respond(event,
                           "❌ InviteAll با خطا روبه‌رو شد؛ پیشرفت ذخیره شده است.\n\n"
                           f"{result.get('last_error', 'unknown')}\n"
                           "برای ادامه دوباره همان /inviteall را بزن.")
        else:
            await _respond(event, f"❌ دریافت اعضای گپ مبدا ناموفق بود.\n\n{result}")
    except Exception as exc:
        await _respond(event, f"❌ اجرای InviteAll ناموفق بود.\n{type(exc).__name__}: {exc}")


@command("/inviteprogress", cat="moderation", usage="/inviteprogress",
         desc="وضعیت عملیات InviteAll")
async def cmd_inviteprogress(event: Any, client: Any, parts: List[str], text: str) -> None:
    state = data.get("invite_state")
    if not state:
        await _respond(event, "ℹ️ عملیات InviteAll فعالی ثبت نشده است.")
        return

    total = len(state.get("user_ids", []))
    done = state.get("index", 0)
    percent = (done / total * 100) if total else 100
    await _respond(event,
                   "📊 وضعیت InviteAll\n\n"
                   f"📦 پیشرفت: {done}/{total} ({percent:.1f}%)\n"
                   f"✅ موفق: {state.get('invited', 0)}\n"
                   f"⏭️ از قبل عضو: {state.get('already_member', 0)}\n"
                   f"⚠️ ناموفق: {state.get('failed', 0)}\n"
                   f"⏳ FloodWait: {state.get('flood_waits', 0)}\n"
                   f"📍 مقصد: {state.get('target_chat', '-')}\n"
                   f"🔄 وضعیت: {'در حال اجرا' if state.get('running') else 'متوقف/پایان یافته'}")


# ─────────────────────────────────────────────────────────────────────────────
# بخش ۴-۶: پاک‌سازی
# ─────────────────────────────────────────────────────────────────────────────

@command("/delme", cat="cleanup", usage="/delme تعداد",
         desc="حذف پیام‌های خودت در گپ")
async def cmd_delme(event: Any, client: Any, parts: List[str], text: str) -> None:
    if len(parts) != 2:
        await _respond(event, "❌ فرمت اشتباه است.\n\nاستفاده:\n/delme تعداد\n\nمثال:\n/delme 20")
        return

    try:
        count = int(from_persian_digits(parts[1]))
    except ValueError:
        await _respond(event, "❌ تعداد باید یک عدد صحیح باشد.")
        return

    if count <= 0:
        await _respond(event, "❌ تعداد باید بیشتر از صفر باشد.")
        return

    try:
        deleted_count = await delete_own_messages(event, client, count)
        add_stat(event.chat_id, "deleted_messages", deleted_count)
        save_data(data)
        if deleted_count == 0:
            await _respond(event, "ℹ️ پیام خروجی‌ای برای حذف پیدا نشد.")
    except Exception as exc:
        await _respond(event, f"❌ حذف پیام‌ها انجام نشد:\n{exc}")


@command("/delgroup", cat="cleanup", usage="/delgroup تعداد",
         desc="حذف پیام‌های اخیر گروه (نیاز به مجوز حذف)")
async def cmd_delgroup(event: Any, client: Any, parts: List[str], text: str) -> None:
    if len(parts) != 2:
        await _respond(event, "❌ فرمت اشتباه است.\n\nاستفاده:\n/delgroup تعداد\n\nمثال:\n/delgroup 20")
        return

    try:
        count = int(from_persian_digits(parts[1]))
    except ValueError:
        await _respond(event, "❌ تعداد باید یک عدد صحیح باشد.")
        return

    if count <= 0:
        await _respond(event, "❌ تعداد باید بیشتر از صفر باشد.")
        return

    try:
        deleted_count = await delete_group_messages(event, client, count)

        if deleted_count == "not_group":
            await _respond(event, "⛔ این دستور فقط داخل گپ/گروه قابل استفاده است.")
        elif deleted_count == "no_permission":
            await _respond(event,
                           "⛔ دسترسی حذف پیام نداری.\n"
                           "فقط مدیر/سازنده‌ای که مجوز حذف پیام دارد می‌تواند از این دستور استفاده کند.")
        elif deleted_count == 0:
            await _respond(event, "ℹ️ پیامی برای حذف پیدا نشد.")
    except Exception as exc:
        await _respond(event,
                       "❌ حذف پیام‌های گروه انجام نشد.\n"
                       "ممکن است دسترسی حذف پیام نداشته باشی یا گروه اجازه این عملیات را ندهد.\n\n"
                       f"جزئیات: {exc}")


@command("/cleanlinks", "/cleanmedia", "/cleanuser", cat="cleanup",
         usage="/cleanlinks تعداد", desc="پاک‌سازی لینک/رسانه/پیام کاربر")
async def cmd_clean(event: Any, client: Any, parts: List[str], text: str) -> None:
    command = parts[0].lower()

    if command == "/cleanuser":
        # دو حالت: /cleanuser تعداد (با Reply) یا /cleanuser USER_ID تعداد
        if len(parts) == 3:
            try:
                user_id = int(from_persian_digits(parts[1]))
                count = int(from_persian_digits(parts[2]))
            except ValueError:
                await _respond(event, "❌ شناسه کاربر و تعداد باید عدد صحیح باشند.\nمثال: /cleanuser 123456789 20")
                return
            if user_id <= 0:
                await _respond(event, "❌ شناسه کاربر معتبر نیست.")
                return
        elif len(parts) == 2:
            try:
                count = int(from_persian_digits(parts[1]))
            except ValueError:
                await _respond(event, "❌ تعداد باید عدد باشد.")
                return
            if not event.is_reply:
                await _respond(event, "استفاده: /cleanuser تعداد (با Reply) یا /cleanuser USER_ID تعداد")
                return
            reply = await event.get_reply_message()
            user_id = getattr(reply, "sender_id", None) if reply else None
            if not user_id:
                await _respond(event, "❌ کاربر پیدا نشد.")
                return
        else:
            await _respond(event, "استفاده: /cleanuser تعداد (با Reply) یا /cleanuser USER_ID تعداد\nمثال: /cleanuser 123456789 20")
            return
        mode = "user"
    else:
        if len(parts) != 2:
            await _respond(event, f"استفاده: {command} تعداد")
            return
        try:
            count = int(from_persian_digits(parts[1]))
        except ValueError:
            await _respond(event, "❌ تعداد باید عدد باشد.")
            return
        mode = "links" if command == "/cleanlinks" else "media"
        user_id = None

    if count <= 0:
        await _respond(event, "❌ تعداد باید بیشتر از صفر باشد.")
        return

    try:
        result = await clean_messages(event, client, mode, count, user_id)
        if result["status"] == "not_group":
            await _respond(event, "⛔ فقط داخل گپ قابل استفاده است.")
        elif result["status"] == "no_permission":
            await _respond(event, "⛔ دسترسی حذف پیام نداری.")
        elif result["status"] == "empty":
            await _respond(event, "ℹ️ از پیام‌های بررسی‌شده، موردی برای حذف پیدا نشد.")
        else:
            await _respond(event, f"✅ {result['count']} پیام حذف شد.")
    except Exception as exc:
        await _respond(event, f"❌ پاک‌سازی ناموفق بود.\n{exc}")


# ─────────────────────────────────────────────────────────────────────────────
# بخش ۴-۷: ابزار (آیدی، اطلاعات، ماشین‌حساب، فونت، سرگرمی، فوروارد)
# ─────────────────────────────────────────────────────────────────────────────

@command("/id", "/chatid", cat="tools", usage="/id ← Reply",
         desc="شناسه کاربر/گپ")
async def cmd_id(event: Any, client: Any, parts: List[str], text: str) -> None:
    if event.is_reply:
        reply = await event.get_reply_message()
        user_id = getattr(reply, "sender_id", None) if reply else None
        if user_id:
            sender = getattr(reply, "sender", None)
            name = display_name(sender) if sender else ""
            lines = [card_title("🆔", "شناسه‌ها"), ""]
            if name:
                lines.append(f"👤 کاربر: {name}")
            lines.append(f"🆔 User ID: {user_id}")
            lines.append(f"💬 Chat ID: {event.chat_id}")
            await _respond(event, "\n".join(lines))
            return
    await _respond(event, f"🆔 Chat ID: {event.chat_id}")


@command("/chatinfo", cat="tools", usage="/chatinfo", desc="اطلاعات گپ فعلی")
async def cmd_chatinfo(event: Any, client: Any, parts: List[str], text: str) -> None:
    try:
        await _respond(event, await get_chat_info(event, client))
    except Exception as exc:
        await _respond(event, f"❌ دریافت اطلاعات گپ ناموفق بود.\n{exc}")


@command("/info", cat="tools", usage="/info ← Reply", desc="اطلاعات کامل کاربر + عکس")
async def cmd_info(event: Any, client: Any, parts: List[str], text: str) -> None:
    if not event.is_reply:
        await _respond(event, "❌ روی پیام کاربر Reply کن و /info بفرست.")
        return

    reply = await event.get_reply_message()
    sender = await reply.get_sender() if reply else None
    if not sender:
        await _respond(event, "❌ کاربر پیدا نشد.")
        return

    info, photo = await get_user_info(client, sender)
    await _respond(event, info)

    if photo:
        try:
            await client.send_file(event.chat_id, photo, caption="🖼 عکس پروفایل")
        finally:
            try:
                os.remove(photo)
            except OSError:
                pass


@command("/calc", cat="tools", usage="/calc عبارت",
         desc="ماشین‌حساب امن (sqrt, pow, fact, pi, e — اعداد فارسی OK)")
async def cmd_calc(event: Any, client: Any, parts: List[str], text: str) -> None:
    expression = text[len(parts[0]):].strip()
    if not expression:
        await _respond(event, "استفاده: /calc (2+3)*4\nمثال: /calc sqrt(144) × ۲")
        return
    try:
        result = safe_calc(expression)
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        await _respond(event, "\n".join([
            card_title("🧮", "ماشین‌حساب"),
            "",
            f"📥 عبارت: {expression}",
            f"📤 نتیجه: {result}",
        ]))
    except ZeroDivisionError:
        await _respond(event, "❌ تقسیم بر صفر مجاز نیست.")
    except Exception as exc:
        await _respond(event, f"❌ عبارت معتبر نیست.\n{exc}")


@command("/fonts", cat="tools", usage="/fonts", desc="لیست فونت‌های فنسی")
async def cmd_fonts(event: Any, client: Any, parts: List[str], text: str) -> None:
    lines = [card_title("🔤", "فونت‌های فنسی"), ""]
    for index, (name, transform) in enumerate(FANCY_FONTS, 1):
        lines.append(f"{to_persian_digits(index)}. {name}: {transform('Abc 123')}")
    lines.extend(["", "استفاده: /font شماره متن", "", brand_footer()])
    await _respond(event, "\n".join(lines))


@command("/font", cat="tools", usage="/font شماره متن",
         desc="تبدیل متن به فونت فنسی")
async def cmd_font(event: Any, client: Any, parts: List[str], text: str) -> None:
    if len(parts) < 3:
        await _respond(event, "استفاده: /font شماره متن\nلیست: /fonts")
        return
    try:
        style = int(from_persian_digits(parts[1]))
    except ValueError:
        await _respond(event, "❌ شماره فونت باید عدد باشد.")
        return
    message = text[len(parts[0]) + 1 + len(parts[1]):].strip()
    if not message:
        await _respond(event, "⛔ متن خالی است.")
        return
    try:
        converted = fancy_text(message, style)
    except ValueError as exc:
        await _respond(event, f"❌ {exc}")
        return
    await _respond(event, converted)


@command("/password", "/pass", cat="tools", usage="/password [طول 8-64]",
         desc="تولید رمز عبور امن")
async def cmd_password(event: Any, client: Any, parts: List[str], text: str) -> None:
    length = 16
    if len(parts) >= 2:
        try:
            length = int(from_persian_digits(parts[1]))
        except ValueError:
            await _respond(event, "❌ طول باید عدد باشد.")
            return
    try:
        password = gen_password(length)
    except ValueError as exc:
        await _respond(event, f"❌ {exc}")
        return
    await _respond(event, "\n".join([
        card_title("🔐", "رمز عبور امن"),
        "",
        f"🔑 {password}",
        "",
        "⚠️ این پیام را بعد از کپی کردن حذف کن (/sdel کمک می‌کند).",
    ]))


@command("/coin", cat="tools", usage="/coin", desc="شیر یا خط")
async def cmd_coin(event: Any, client: Any, parts: List[str], text: str) -> None:
    side = random.choice(["🪙 رو (Heads)", "🪙 خط (Tails)"])
    await _respond(event, f"🎲 نتیجه: {side}")


@command("/dice", cat="tools", usage="/dice [تعداد وجه]",
         desc="انداختن تاس")
async def cmd_dice(event: Any, client: Any, parts: List[str], text: str) -> None:
    sides = 6
    if len(parts) >= 2:
        try:
            sides = int(from_persian_digits(parts[1]))
        except ValueError:
            await _respond(event, "❌ تعداد وجه باید عدد باشد.")
            return
    if not 2 <= sides <= 1000:
        await _respond(event, "⛔ تعداد وجه باید بین ۲ تا ۱۰۰۰ باشد.")
        return
    value = random.randint(1, sides)
    await _respond(event, f"🎲 تاس {sides} وجهی: {to_persian_digits(value)}")


@command("/random", cat="tools", usage="/random عدد1 عدد2",
         desc="عدد تصادفی بین دو عدد")
async def cmd_random(event: Any, client: Any, parts: List[str], text: str) -> None:
    if len(parts) < 3:
        await _respond(event, "استفاده: /random 1 100")
        return
    try:
        a = int(from_persian_digits(parts[1]))
        b = int(from_persian_digits(parts[2]))
    except ValueError:
        await _respond(event, "❌ دو عدد معتبر بده.")
        return
    value = random.randint(min(a, b), max(a, b))
    await _respond(event, f"🎯 عدد تصادفی بین {min(a, b)} و {max(a, b)}: {to_persian_digits(value)}")


@command("/pick", cat="tools", usage="/pick گزینه1 | گزینه2 | ...",
         desc="انتخاب تصادفی یک گزینه")
async def cmd_pick(event: Any, client: Any, parts: List[str], text: str) -> None:
    options = [opt.strip() for opt in text[len(parts[0]):].split("|") if opt.strip()]
    if len(options) < 2:
        await _respond(event, "استفاده: /pick گزینه1 | گزینه2 | گزینه3")
        return
    choice = random.choice(options)
    await _respond(event, f"🎯 از بین {len(options)} گزینه انتخاب شد:\n👉 {choice}")


@command("/save", cat="tools", usage="/save ← Reply",
         desc="فوروارد پیام به پیام‌های ذخیره‌شده")
async def cmd_save(event: Any, client: Any, parts: List[str], text: str) -> None:
    if not event.is_reply:
        await _respond(event, "↩️ روی پیامی که می‌خواهی ذخیره کنی Reply کن.")
        return
    reply = await event.get_reply_message()
    if not reply:
        await _respond(event, "❌ پیام پیدا نشد.")
        return
    forward = getattr(client, "forward_messages", None)
    if not callable(forward):
        await _respond(event, "❌ این نسخهٔ SPlusthon از forward پشتیبانی نمی‌کند.")
        return
    try:
        try:
            await forward("me", reply.id, event.chat_id)
        except TypeError:
            await forward("me", reply)
        await _respond(event, "💾 در پیام‌های ذخیره‌شده ذخیره شد.")
    except Exception as exc:
        await _respond(event, f"❌ ذخیره ناموفق بود.\n{type(exc).__name__}: {exc}")


@command("/forward", cat="tools", usage="/forward CHAT_ID ← Reply",
         desc="فوروارد پیام به گپ دیگر")
async def cmd_forward(event: Any, client: Any, parts: List[str], text: str) -> None:
    if len(parts) < 2:
        await _respond(event, "استفاده: /forward CHAT_ID (با Reply)")
        return
    if not event.is_reply:
        await _respond(event, "↩️ روی پیامی که می‌خواهی فوروارد کنی Reply کن.")
        return
    target = await resolve_chat_entity(client, parts[1])
    if target is None:
        await _respond(event, "❌ گپ مقصد پیدا نشد.")
        return
    reply = await event.get_reply_message()
    if not reply:
        await _respond(event, "❌ پیام پیدا نشد.")
        return
    forward = getattr(client, "forward_messages", None)
    if not callable(forward):
        await _respond(event, "❌ این نسخهٔ SPlusthon از forward پشتیبانی نمی‌کند.")
        return
    try:
        try:
            await forward(target, reply.id, event.chat_id)
        except TypeError:
            await forward(target, reply)
        await _respond(event, "📤 فوروارد شد.")
    except Exception as exc:
        await _respond(event, f"❌ فوروارد ناموفق بود.\n{type(exc).__name__}: {exc}")


@command("/copy", cat="tools", usage="/copy ← Reply",
         desc="کپی متن پیام هدف به‌عنوان پیام خودت")
async def cmd_copy(event: Any, client: Any, parts: List[str], text: str) -> None:
    if not event.is_reply:
        await _respond(event, "↩️ روی پیامی که می‌خواهی کپی کنی Reply کن.")
        return
    reply = await event.get_reply_message()
    body = (getattr(reply, "raw_text", None) or getattr(reply, "message", None) or "") if reply else ""
    if not body.strip():
        await _respond(event, "ℹ️ این پیام متن متنی ندارد (فقط متن کپی می‌شود).")
        return
    await _respond(event, body)


# ─────────────────────────────────────────────────────────────────────────────
# بخش ۴-۸: زمان‌بندی و یادآوری ماندگار
# ─────────────────────────────────────────────────────────────────────────────

@command("/schedule", "/remind", cat="schedule", usage="/remind 10m متن",
         desc="یادآوری/پیام زمان‌بندی‌شده (ماندگار)")
async def cmd_schedule(event: Any, client: Any, parts: List[str], text: str) -> None:
    if len(parts) < 3:
        await _respond(event, f"استفاده: {parts[0]} 10m متن")
        return
    delay = parse_duration(parts[1])
    if delay is None:
        try:
            delay = int(from_persian_digits(parts[1]))
        except ValueError:
            delay = None
    if delay is None or delay < 0:
        await _respond(event, "⛔ زمان نامعتبر است. مثال: 30s یا 10m یا 2h")
        return
    if delay > MAX_REMINDER_SECONDS:
        await _respond(event, "⛔ حداکثر زمان‌بندی 30 روز است.")
        return
    message = text[len(parts[0]) + 1 + len(parts[1]):].strip()
    if not message:
        await _respond(event, "⛔ متن خالی است.")
        return
    prefix = "⏰ یادآوری" if parts[0].lower() == "/remind" else "⏰ پیام زمان‌بندی‌شده"

    # ماندگار: بعد از ری‌استارت هم اجرا می‌شود
    index = add_reminder(event.chat_id, f"{prefix}\n\n{message}", time.time() + delay)
    entry = data["reminders"][index]
    spawn_reminder(client, entry)
    await _respond(event,
                   f"✅ زمان‌بندی شد: {format_duration(delay)}\n"
                   "💾 ماندگار است — با ری‌استارت هم از دست نمی‌رود.")


@command("/reminders", cat="schedule", usage="/reminders",
         desc="لیست یادآوری‌های معلق")
async def cmd_reminders(event: Any, client: Any, parts: List[str], text: str) -> None:
    entries = data.get("reminders") or []
    if not entries:
        await _respond(event, "⏰ یادآوری فعالی نداری.")
        return

    lines = [card_title("⏰", f"یادآوری‌های معلق ({len(entries)})"), ""]
    now = time.time()
    for index, entry in enumerate(entries, 1):
        remaining = int(float(entry.get("due_ts", 0)) - now)
        remaining_text = format_duration(max(remaining, 0)) if remaining > 0 else "همین حالا"
        preview = str(entry.get("text", "")).splitlines()
        title = preview[-1][:40] if preview else ""
        lines.append(f"{index}. ⏳ {remaining_text} — {title}")
    lines.extend(["", "حذف: /reminddel شماره", "", brand_footer()])
    await _respond(event, "\n".join(lines))


@command("/reminddel", cat="schedule", usage="/reminddel شماره",
         desc="حذف یک یادآوری معلق")
async def cmd_reminddel(event: Any, client: Any, parts: List[str], text: str) -> None:
    if len(parts) < 2:
        await _respond(event, "استفاده: /reminddel شماره\nلیست: /reminders")
        return
    try:
        index = int(from_persian_digits(parts[1])) - 1
    except ValueError:
        await _respond(event, "❌ شماره باید عدد باشد.")
        return
    item = remove_reminder(index)
    if item is None:
        await _respond(event, "❌ شماره یادآوری نامعتبر است.")
        return
    title = str(item.get("text", "")).splitlines()[-1][:40] if item.get("text") else ""
    await _respond(event, f"🗑 یادآوری حذف شد: {title}")


@command("/sdel", cat="schedule", usage="/sdel ثانیه متن",
         desc="ارسال پیام با حذف خودکار بعد از N ثانیه")
async def cmd_sdel(event: Any, client: Any, parts: List[str], text: str) -> None:
    if len(parts) < 3:
        await _respond(event, "استفاده: /sdel 60 متن")
        return
    try:
        delay = int(from_persian_digits(parts[1]))
    except ValueError:
        await _respond(event, "❌ ثانیه باید عدد باشد.")
        return
    if not MIN_SDEL_SECONDS <= delay <= MAX_SDEL_SECONDS:
        await _respond(event, f"⛔ ثانیه باید بین {MIN_SDEL_SECONDS} تا {MAX_SDEL_SECONDS} باشد.")
        return
    message = text[len(parts[0]) + 1 + len(parts[1]):].strip()
    if not message:
        await _respond(event, "⛔ متن خالی است.")
        return

    sent = await event.respond(message)

    async def _auto_delete() -> None:
        try:
            await asyncio.sleep(delay)
            delete = getattr(sent, "delete", None)
            if callable(delete):
                await delete()
        except asyncio.CancelledError:
            pass
        except Exception as exc:
            log.warning("حذف خودکار پیام ناموفق بود: %s", exc)

    asyncio.create_task(_auto_delete())


# ─────────────────────────────────────────────────────────────────────────────
# بخش ۴-۹: یادداشت
# ─────────────────────────────────────────────────────────────────────────────

@command("/note", cat="notes", usage="/note add متن", desc="مدیریت یادداشت‌ها")
async def cmd_note(event: Any, client: Any, parts: List[str], text: str) -> None:
    if len(parts) < 2:
        await _respond(event, "/note add متن\n/note list\n/note del شماره")
        return

    action = parts[1].lower()

    if action == "add":
        note = text[len("/note add"):].strip()
        if not note:
            await _respond(event, "⛔ متن یادداشت خالی است.")
            return
        data["notes"].append(note)
        save_data(data)
        await _respond(event, f"📝 یادداشت ذخیره شد ({to_persian_digits(len(data['notes']))} عدد).")
        return

    if action == "list":
        if not data["notes"]:
            await _respond(event, "📝 یادداشتی وجود ندارد.")
            return
        await _respond(event,
                       "📝 Notes\n\n" + "\n".join(
                           f"{to_persian_digits(index)}. {note}"
                           for index, note in enumerate(data["notes"], 1)
                       ))
        return

    if action == "del":
        try:
            number = int(from_persian_digits(parts[2]))
            deleted = data["notes"].pop(number - 1)
        except (ValueError, IndexError):
            await _respond(event, "⛔ شماره یادداشت نامعتبر است.")
            return
        save_data(data)
        await _respond(event, f"🗑 حذف شد:\n{deleted}")
        return

    await _respond(event, "⛔ دستور note نامعتبر است.")


# ─────────────────────────────────────────────────────────────────────────────
# بخش ۴-۱۰: وضعیت و آمار
# ─────────────────────────────────────────────────────────────────────────────

@command("/ping", cat="status", usage="/ping", desc="تست پاسخ‌دهی")
async def cmd_ping(event: Any, client: Any, parts: List[str], text: str) -> None:
    start = time.perf_counter()
    message = await event.respond("🏓 در حال بررسی...")
    elapsed = (time.perf_counter() - start) * 1000
    try:
        await message.edit(f"🏓 Pong!\n⚡ {elapsed:.0f} ms\n📦 v{VERSION}")
    except Exception:
        pass


@command("/uptime", cat="status", usage="/uptime", desc="مدت زمان روشن بودن سلف")
async def cmd_uptime(event: Any, client: Any, parts: List[str], text: str) -> None:
    await _respond(event, f"⏱ Uptime: {format_uptime()}\n🕐 Started: {START_TIME:%Y/%m/%d - %H:%M:%S}")


@command("/status", cat="status", usage="/status", desc="وضعیت کلی سلف")
async def cmd_status(event: Any, client: Any, parts: List[str], text: str) -> None:
    await _respond(event, "\n".join([
        card_title("⚡", "وضعیت سلف"),
        "",
        "🟢 Online",
        f"👤 {data.get('display_name') or 'Not Set'}",
        f"⏰ Clock: {'ON' if data.get('name_clock') else 'OFF'}",
        f"🤖 Auto Reply: {'ON' if data.get('auto_reply') else 'OFF'}",
        f"🛡 Auto for Bots: {'ON' if data.get('auto_reply_bots', True) else 'OFF'}",
        f"👥 Auto in Groups: {'ON' if data.get('auto_reply_groups', True) else 'OFF'}",
        f"⏳ Cooldown: {data.get('auto_reply_cooldown', 0)}s",
        f"📝 Notes: {len(data.get('notes', []))}",
        f"🧲 Triggers: {len(data.get('triggers', []))}",
        f"⏱ Uptime: {format_uptime()}",
        f"📦 Tasks: {active_tasks_count()}",
        f"💾 Version: v{VERSION}",
        "",
        brand_footer(),
    ]))


@command("/amar", cat="status", usage="/amar", desc="آمار سلف")
async def cmd_amar(event: Any, client: Any, parts: List[str], text: str) -> None:
    await _respond(event, "\n".join([
        card_title("📊", "آمار سلف"),
        "",
        f"⏱ Uptime: {format_uptime()}",
        f"⏰ Clock: {'ON' if data.get('name_clock') else 'OFF'}",
        f"🤖 Auto Reply: {'ON' if data.get('auto_reply') else 'OFF'}",
        f"📝 Notes: {len(data.get('notes', []))}",
        f"📦 Spam slots: {sum(bool(x) for x in data.get('spam_slots', []))}/8",
        f"💬 Reply slots: {sum(bool(x) for x in data.get('rep_slots', []))}/8",
        f"⏰ Reminders: {len(data.get('reminders', []))}",
        f"🕐 Started: {START_TIME:%Y/%m/%d - %H:%M:%S}",
        "",
        brand_footer(),
    ]))


@command("/stats", cat="status", usage="/stats", desc="آمار پیشرفته این گپ")
async def cmd_stats(event: Any, client: Any, parts: List[str], text: str) -> None:
    stats = chat_stat(event.chat_id)
    today = stats_period(event.chat_id, 1)
    week = stats_period(event.chat_id, 7)

    def _line(icon: str, label: str, key: str) -> str:
        return f"{icon} {label}: {stats.get(key, 0)}"

    def _short(key: str) -> str:
        return (f"{today.get(key, 0)}" if False else
                f"{today.get(key, 0)} / {week.get(key, 0)}")

    await _respond(event, "\n".join([
        card_title("📊", "آمار پیشرفته این گپ"),
        "",
        "━━━━ همه زمان‌ها ━━━━",
        _line("💬", "پردازش پیام", "messages_processed"),
        _line("🤖", "پاسخ", "replies_sent"),
        _line("🗑", "حذف پیام", "deleted_messages"),
        _line("👢", "اخراج", "kicks"),
        _line("🚫", "بن", "bans"),
        _line("🔇", "میوت", "mutes"),
        _line("➕", "دعوت موفق", "invites_success"),
        _line("⚠️", "دعوت ناموفق", "invites_failed"),
        _line("⏭️", "از قبل عضو", "invites_skipped"),
        "",
        "━━━━ امروز / ۷ روز ━━━━",
        f"💬 پیام: {_short('messages_processed')}",
        f"🤖 پاسخ: {_short('replies_sent')}",
        f"👢 اخراج: {_short('kicks')}",
        f"🚫 بن: {_short('bans')}",
        f"🔇 میوت: {_short('mutes')}",
        f"➕ دعوت: {_short('invites_success')}",
        "",
        "ℹ️ ریست آمار: /statsreset تایید",
        brand_footer(),
    ]))


@command("/statsreset", cat="status", usage="/statsreset تایید",
         desc="ریست آمار این گپ")
async def cmd_statsreset(event: Any, client: Any, parts: List[str], text: str) -> None:
    if len(parts) < 2 or parts[1] != "تایید":
        await _respond(event, "⚠️ برای ریست آمار این گپ دقیقاً بنویس:\n/statsreset تایید")
        return
    data.setdefault("stats", {}).pop(str(event.chat_id), None)
    save_data(data)
    await _respond(event, "♻️ آمار این گپ ریست شد.")


@command("/health", cat="status", usage="/health", desc="بررسی سلامت سلف")
async def cmd_health(event: Any, client: Any, parts: List[str], text: str) -> None:
    try:
        await _respond(event, await get_self_health(event, client))
    except Exception as exc:
        await _respond(event, f"❌ Health Check ناموفق بود.\n{type(exc).__name__}: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# بخش ۴-۱۱: توقف عملیات
# ─────────────────────────────────────────────────────────────────────────────

def _cancel_group(group: set) -> int:
    count = 0
    for task in list(group):
        if not task.done():
            task.cancel()
            count += 1
    return count


@command("/stopspam", cat="stop", usage="/stopspam", desc="توقف عملیات Spam")
async def cmd_stopspam(event: Any, client: Any, parts: List[str], text: str) -> None:
    _cancel_group(operation_tasks["spam"])
    await _respond(event, "🛑 Spam متوقف شد.")


@command("/stoprep", cat="stop", usage="/stoprep", desc="توقف عملیات Reply")
async def cmd_stoprep(event: Any, client: Any, parts: List[str], text: str) -> None:
    _cancel_group(operation_tasks["rep"])
    await _respond(event, "🛑 Reply متوقف شد.")


@command("/stopshomaresh", cat="stop", usage="/stopshomaresh",
         desc="توقف عملیات شمارش")
async def cmd_stopshomaresh(event: Any, client: Any, parts: List[str], text: str) -> None:
    _cancel_group(operation_tasks["shomaresh"])
    await _respond(event, "🛑 شمارش متوقف شد.")


@command("/stop", cat="stop", usage="/stop", desc="توقف همهٔ عملیات فعال")
async def cmd_stop(event: Any, client: Any, parts: List[str], text: str) -> None:
    stopped = 0
    for group_name in ("spam", "rep", "shomaresh", "moderation", "invite"):
        stopped += _cancel_group(operation_tasks[group_name])
    stopped += _cancel_group(scheduled_tasks)

    cleared_reminders = 0
    if data.get("reminders"):
        cleared_reminders = len(data["reminders"])
        data["reminders"] = []
        save_data(data)

    message = "🛑 تمام عملیات فعال متوقف شدند."
    if cleared_reminders:
        message += f"\n⏰ {cleared_reminders} یادآوری معلق هم پاک شد."
    await _respond(event, message)


# ─────────────────────────────────────────────────────────────────────────────
# بخش ۴-۱۲: سیستم (تنظیمات، ریست)
# ─────────────────────────────────────────────────────────────────────────────

def settings_text() -> str:
    cooldown = data.get("auto_reply_cooldown", 0)
    return "\n".join([
        card_title("⚙️", "تنظیمات سلف"),
        "",
        f"🤖 پاسخگوی خودکار: {'روشن' if data.get('auto_reply') else 'خاموش'}",
        f"💬 متن پاسخ: {data.get('auto_message', '')}",
        f"⏳ فاصلهٔ پاسخ (cooldown): {cooldown if cooldown else 'خاموش'}",
        f"🛡 پاسخ به ربات‌ها: {'روشن' if data.get('auto_reply_bots', True) else 'خاموش'}",
        f"👥 پاسخ در گروه‌ها: {'روشن' if data.get('auto_reply_groups', True) else 'خاموش'}",
        f"⏰ ساعت نام: {'روشن' if data.get('name_clock') else 'خاموش'}"
        f" (فونت {data.get('clock_font', 1)} — محل: {data.get('clock_position', 'lastname')})",
        f"📛 نام ذخیره‌شده: {data.get('display_name') or 'ثبت نشده'}",
        f"👋 خوش‌آمد: {'روشن' if data.get('welcome_enabled') else 'خاموش'}",
        f"🙏 خداحافظ: {'روشن' if data.get('goodbye_enabled') else 'خاموش'}",
        f"🧲 تریگرها: {len(data.get('triggers', []))}",
        f"📝 یادداشت‌ها: {len(data.get('notes', []))}",
        f"⏰ یادآوری‌های معلق: {len(data.get('reminders', []))}",
        f"📦 نسخه: v{VERSION}",
        "",
        brand_footer(),
    ])


@command("/settings", cat="system", usage="/settings", desc="نمایش همهٔ تنظیمات")
async def cmd_settings(event: Any, client: Any, parts: List[str], text: str) -> None:
    await _respond(event, settings_text())


@command("/resetdata", cat="system", usage="/resetdata تایید",
         desc="بازگشت همهٔ تنظیمات به حالت اولیه")
async def cmd_resetdata(event: Any, client: Any, parts: List[str], text: str) -> None:
    if len(parts) < 2 or parts[1] != "تایید":
        await _respond(event,
                       "⚠️ این دستور همهٔ تنظیمات، تریگرها، یادداشت‌ها و آمار را پاک می‌کند.\n\n"
                       "برای اجرا دقیقاً بنویس:\n/resetdata تایید")
        return

    global data
    # پشتیبان قبل از ریست
    try:
        backup = f"{DATA_FILE}.backup-{datetime.now():%Y%m%d-%H%M%S}"
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as src, open(backup, "w", encoding="utf-8") as dst:
                dst.write(src.read())
    except OSError as exc:
        log.warning("پشتیبان‌گیری قبل از ریست ناموفق بود: %s", exc)

    data = json.loads(json.dumps(DEFAULT_DATA))
    save_data(data)
    await _respond(event, "♻️ همهٔ تنظیمات به حالت اولیه برگشت.\n📁 پشتیبان تنظیمات قبلی ذخیره شد.")


# ─────────────────────────────────────────────────────────────────────────────
# بخش ۴-۱۳: dispatcher اصلی دستورها
# ─────────────────────────────────────────────────────────────────────────────

async def command_handler(event: Any, client: Any) -> None:
    text = (event.raw_text or "").strip()
    if not text.startswith("/"):
        return

    parts = text.split(maxsplit=3)
    command_name = parts[0].lower()

    # دستورهای اسلات داینامیک: /setspam1..8 و /setrep1..8
    match = re.fullmatch(r"/setspam(\d+)", command_name)
    if match:
        await _handle_set_slot(event, client, parts, text, "spam", int(match.group(1)))
        return
    match = re.fullmatch(r"/setrep(\d+)", command_name)
    if match:
        await _handle_set_slot(event, client, parts, text, "rep", int(match.group(1)))
        return

    spec = COMMANDS.get(command_name)
    if spec is None:
        # دستور ناشناخته — مثل قبل بی‌صدا نادیده گرفته می‌شود
        return

    try:
        await spec["fn"](event, client, parts, text)
    except Exception as exc:
        log.exception("خطا در اجرای دستور %s", command_name)
        try:
            await event.respond(
                f"❌ خطای غیرمنتظره در اجرای {command_name}\n"
                f"{type(exc).__name__}: {exc}"
            )
        except Exception:
            pass


# ═════════════════════════════════════════════════════════════════════════════
# بخش ۵: هندلر پیام‌ها، خوش‌آمد/خداحافظ، main و نقطهٔ ورود
# ═════════════════════════════════════════════════════════════════════════════

def _event_is_group(event: Any) -> bool:
    checker = getattr(event, "is_group", None)
    try:
        if callable(checker):
            return bool(checker())
        return bool(checker)
    except Exception:
        return False


async def message_handler(event: Any, client: Any = None) -> None:
    """پاسخگوی خودکار + تریگرها برای پیام‌های ورودی."""
    if getattr(event, "out", False):
        return

    text = (event.raw_text or "").strip()
    if not text or text.startswith("/"):
        return

    add_stat(event.chat_id, "messages_processed")
    mark_dirty()

    lower_text = text.lower()
    for item in data.get("triggers", []):
        trigger = str(item.get("trigger", "")).strip().lower()
        if trigger and trigger in lower_text:
            try:
                await event.reply(item.get("response", ""))
                add_stat(event.chat_id, "replies_sent")
                mark_dirty()
            except Exception as exc:
                log.warning("ارسال پاسخ تریگر ناموفق بود: %s", exc)
            return

    if not data.get("auto_reply"):
        return

    # فیلترهای جدید (پیش‌فرض‌ها دقیقاً رفتار نسخهٔ قبل را حفظ می‌کنند)
    if not data.get("auto_reply_groups", True) and _event_is_group(event):
        return

    if not data.get("auto_reply_bots", True):
        sender = getattr(event, "sender", None)
        if sender is None:
            getter = getattr(event, "get_sender", None)
            if callable(getter):
                try:
                    sender = await getter()
                except Exception:
                    sender = None
        if sender is not None and getattr(sender, "bot", False):
            return

    cooldown = int(data.get("auto_reply_cooldown", 0) or 0)
    if cooldown > 0:
        key = str(event.chat_id)
        now = time.monotonic()
        last = _last_auto_reply.get(key, 0.0)
        if now - last < cooldown:
            return
        _last_auto_reply[key] = now

    try:
        await event.reply(data.get("auto_message", ""))
        add_stat(event.chat_id, "replies_sent")
        mark_dirty()
    except Exception as exc:
        log.warning("ارسال پاسخ خودکار ناموفق بود: %s", exc)


def get_action_user(event: Any) -> Any:
    for attr in ("user", "user_joined", "user_left"):
        value = getattr(event, attr, None)
        if value is not None and not isinstance(value, bool):
            return value
    return None


async def action_handler(event: Any, client: Any) -> None:
    user = get_action_user(event)
    if not user:
        reply = getattr(event, "action_message", None)
        user = getattr(reply, "sender", None) if reply else None
    if not user:
        return

    name = display_name(user)
    username = getattr(user, "username", None)
    chat_title = None
    try:
        chat = await event.get_chat()
        chat_title = getattr(chat, "title", None) or getattr(chat, "first_name", None)
    except Exception:
        chat_title = None

    if getattr(event, "user_joined", False) and data.get("welcome_enabled"):
        try:
            await event.respond(render_template(
                data["welcome_message"], name, username, chat_title
            ))
        except Exception as exc:
            log.warning("ارسال خوش‌آمد ناموفق بود: %s", exc)
    elif getattr(event, "user_left", False) and data.get("goodbye_enabled"):
        try:
            await event.respond(render_template(
                data["goodbye_message"], name, username, chat_title
            ))
        except Exception as exc:
            log.warning("ارسال خداحافظ ناموفق بود: %s", exc)


# ─────────────────────────────────────────────────────────────────────────────
# بخش ۵-۲: تسک‌های پس‌زمینه (ذخیرهٔ صفحه‌بندی‌شده + نظافت آمار)
# ─────────────────────────────────────────────────────────────────────────────

async def periodic_maintenance() -> None:
    """هر ۵ ثانیه: نوشتن تغییرات صف‌شده. هر شب: پاک‌سازی تاریخچهٔ آمار."""
    last_prune = datetime.now()
    try:
        while True:
            await asyncio.sleep(5)
            flush_if_dirty()

            if (datetime.now() - last_prune).total_seconds() >= 86400:
                removed = prune_stats_history()
                if removed:
                    log.info("تاریخچهٔ آمار قدیمی پاک شد: %d روز", removed)
                    flush_if_dirty(force=True)
                last_prune = datetime.now()
    except asyncio.CancelledError:
        pass


# ─────────────────────────────────────────────────────────────────────────────
# بخش ۵-۳: main
# ─────────────────────────────────────────────────────────────────────────────

async def main() -> None:
    global data

    setup_logging()
    term_banner()

    data = load_data()
    log.info("داده بارگذاری شد — نسخه v%s", VERSION)

    session = load_session()
    client = SoroushClient(StringSession(session) if session else StringSession())

    @client.on(events.NewMessage(outgoing=True))
    async def outgoing_handler(event):
        await command_handler(event, client)

    @client.on(events.NewMessage(incoming=True))
    async def incoming_handler(event):
        await message_handler(event)

    if hasattr(events, "ChatAction"):
        @client.on(events.ChatAction)
        async def action_event_handler(event):
            await action_handler(event, client)

    await client.start()

    try:
        session = client.session.save()
        if session:
            save_session(session)
    except Exception as exc:
        log.warning("ذخیره session ناموفق بود: %s", exc)

    # یادآوری‌های ماندگار بعد از ری‌استارت برمی‌گردند
    try:
        restored = restore_reminders(client)
        if restored:
            log.info("تعداد %d یادآوری معلق بازیابی شد", restored)
    except Exception as exc:
        log.warning("بازیابی یادآوری‌ها ناموفق بود: %s", exc)

    maintenance_task = asyncio.create_task(periodic_maintenance())

    if data.get("name_clock") and data.get("display_name"):
        await start_name_clock(client)

    log.info("⚡ %s آماده است — برای راهنما /help را بفرست", BRAND)

    try:
        await client.run_until_disconnected()
    finally:
        maintenance_task.cancel()
        flush_if_dirty(force=True)
        log.info("سلف خاموش شد؛ داده‌ها ذخیره شدند.")


if __name__ == "__main__":
    if not HAS_SPLUSTHON:
        print("❌ کتابخانهٔ splusthon نصب نیست یا پیدا نشد.")
        print("   همان محیطی که قبلاً سلف را اجرا می‌کرد را استفاده کن،")
        print("   یا کتابخانه را طبق راهنمای ارائه‌دهنده نصب کن.")
        sys.exit(1)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 خداحافظ!")
