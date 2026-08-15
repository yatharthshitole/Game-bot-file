#!/usr/bin/env python3
# ╔══════════════════════════════════════════════════════════╗
# ║        Life RPG Bot  —  Developed By Yatharth 🫶         ║
# ║    Economy · PvP · Social · Store · Pets · Premium       ║
# ╚══════════════════════════════════════════════════════════╝

import asyncio, base64, json, logging, random, time, zlib
from datetime import date
from typing import Optional, Dict, Any, List

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand,
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, ChatMemberHandler,
)
from telegram.constants import ParseMode, ChatMemberStatus

# ══════════════════════ CONFIG ══════════════════════════════
BOT_TOKEN      = "8067862143:AAG65taUVNOUB_5z5osB5lg4i7ZkdSx2Eks"
OWNER_ID       = 7289793022
LOG_CHANNEL_ID = -1003712840424
GIF_CHANNEL_ID = -1003712840424   # channel where you post GIFs
BOT_NAME       = "Life RPG"
BOT_USERNAME   = "darkmafiaabot"   # without @
DEV_USERNAME   = "yatharth_78"
CHANNEL        = "rawdrops1"
# ════════════════════════════════════════════════════════════

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
#  GIF MESSAGE IDs FROM YOUR GIF CHANNEL
#  How: Post GIF in channel → copy link → t.me/channel/42 → put "42"
# ─────────────────────────────────────────────────────────────
GIFS: Dict[str, str] = {
    # Social
    "kiss":         "127",
    "hug":          "128",
    "slap":         "129",
    # Combat
    "kill_success": "156",
    "kill_fail":    "152",
    # Rob
    "rob_success":  "137",
    "rob_fail":     "139",
    # Rob fail types
    "police":       "131",   # caught by police
    "beaten":       "136",   # beaten while robbing
    # Bet
    "bet_win":      "158",
    "bet_lose":     "132",
}

# ─────────────────────────────────────────────────────────────
#  STORE CATALOGUE
# ─────────────────────────────────────────────────────────────
STORE: Dict[str, Any] = {
    # Food split into 3 sub-categories via "sub" field
    "food": {
        # 🥦 Veg & Fruits
        "tomato":     {"emoji":"🍅","price":50,  "health":15,"sub":"veg"},
        "apple":      {"emoji":"🍎","price":60,  "health":15,"sub":"veg"},
        "watermelon": {"emoji":"🍉","price":80,  "health":18,"sub":"veg"},
        "grapes":     {"emoji":"🍇","price":70,  "health":16,"sub":"veg"},
        "salad":      {"emoji":"🥗","price":90,  "health":18,"sub":"veg"},
        "orange":     {"emoji":"🍊","price":65,  "health":16,"sub":"veg"},
        # 🍔 Fast Food
        "burger":     {"emoji":"🍔","price":120, "health":20,"sub":"fast"},
        "pizza":      {"emoji":"🍕","price":130, "health":22,"sub":"fast"},
        "hotdog":     {"emoji":"🌭","price":80,  "health":14,"sub":"fast"},
        "fries":      {"emoji":"🍟","price":70,  "health":12,"sub":"fast"},
        "sandwich":   {"emoji":"🥪","price":100, "health":17,"sub":"fast"},
        "taco":       {"emoji":"🌮","price":110, "health":18,"sub":"fast"},
        # 🍱 Meals
        "chicken":    {"emoji":"🍗","price":170, "health":28,"sub":"meal"},
        "sushi":      {"emoji":"🍣","price":220, "health":32,"sub":"meal"},
        "biryani":    {"emoji":"🍛","price":180, "health":30,"sub":"meal"},
        "ramen":      {"emoji":"🍜","price":160, "health":26,"sub":"meal"},
        "steak":      {"emoji":"🥩","price":250, "health":35,"sub":"meal"},
        "curry":      {"emoji":"🍲","price":150, "health":25,"sub":"meal"},
    },
    "weapons": {
        "knife":   {"emoji":"🔪","price":500,  "kill_chance":0.35,"ammo":5},
        "pistol":  {"emoji":"🔫","price":1500, "kill_chance":0.60,"ammo":5},
        "shotgun": {"emoji":"💥","price":2500, "kill_chance":0.70,"ammo":5},
        "ak47":    {"emoji":"🪖","price":4000, "kill_chance":0.85,"ammo":5},
        "sniper":  {"emoji":"🎯","price":6000, "kill_chance":0.92,"ammo":5},
    },
    "pets": {
        "dog":    {"emoji":"🐕","price":2000, "bonus":"Rob +15%"},
        "cat":    {"emoji":"🐈","price":2000, "bonus":"Game luck +15%"},
        "monkey": {"emoji":"🐒","price":2000, "bonus":"Random bonus"},
        "rabbit": {"emoji":"🐇","price":2500, "bonus":"Cooldown −10%"},
        "parrot": {"emoji":"🦜","price":3000, "bonus":"Spy intel"},
        "fox":    {"emoji":"🦊","price":3500, "bonus":"Rob +20%"},
        "bear":   {"emoji":"🐻","price":5000, "bonus":"Defense +25%"},
        "tiger":  {"emoji":"🐯","price":8000, "bonus":"Kill +10%"},
        "dragon": {"emoji":"🐉","price":15000,"bonus":"All bonuses"},
    },
    "cosmetics": {
        "rose":       {"emoji":"🌹","price":200, "slot":"flower"},
        "tulip":      {"emoji":"🌷","price":200, "slot":"flower"},
        "sunflower":  {"emoji":"🌻","price":200, "slot":"flower"},
        "carrot":     {"emoji":"🥕","price":150, "slot":"vegetable"},
        "corn":       {"emoji":"🌽","price":150, "slot":"vegetable"},
        "broccoli":   {"emoji":"🥦","price":150, "slot":"vegetable"},
        "red_theme":  {"emoji":"🔴","price":500, "slot":"theme"},
        "blue_theme": {"emoji":"💙","price":500, "slot":"theme"},
        "gold_theme": {"emoji":"✨","price":1000,"slot":"theme"},
    },
    "petfood": {
        "petfood": {"emoji":"🦴","price":100,"hunger":30},
    },
}

FOOD_SUBS = {
    "veg":  {"label":"🥦 Veg & Fruits",  "cb":"food_veg"},
    "fast": {"label":"🍔 Fast Food",      "cb":"food_fast"},
    "meal": {"label":"🍱 Meals",          "cb":"food_meal"},
}

# ─────────────────────────────────────────────────────────────
#  COOLDOWNS  (seconds)
# ─────────────────────────────────────────────────────────────
CD_KILL  = 3
CD_ROB   = 3
CD_BET   = 3

# ─────────────────────────────────────────────────────────────
#  THEME STYLES
# ─────────────────────────────────────────────────────────────
THEMES = {
    "gold_theme":  {"top":"✨","badge":"👑","tag":"PREMIUM","div":"─────────────────────"},
    "blue_theme":  {"top":"💙","badge":"💠","tag":"ELITE",  "div":"─────────────────────"},
    "red_theme":   {"top":"🔴","badge":"🔥","tag":"WARRIOR","div":"─────────────────────"},
    "default":     {"top":"",  "badge":"👤","tag":"",       "div":"─────────────────────"},
}

def get_theme(user: dict) -> dict:
    th = user.get("cos_equipped", {}).get("theme")
    return THEMES.get(th, THEMES["default"]) if th else THEMES["default"]

def hp_bar(hp: int) -> str:
    filled = round(hp / 10)
    return "█" * filled + "░" * (10 - filled)

def fmt(n: int) -> str:
    return f"₹{n:,}"

# ─────────────────────────────────────────────────────────────
#  DATA LAYER
# ─────────────────────────────────────────────────────────────
_cache: Dict[str, Any] = {}
_pin_id: Optional[int] = None


def _compress(data: dict) -> str:
    raw = json.dumps(data, separators=(",", ":"))
    return base64.b64encode(zlib.compress(raw.encode(), level=9)).decode()


def _decompress(text: str) -> dict:
    try:
        return json.loads(zlib.decompress(base64.b64decode(text.strip())))
    except Exception:
        return {}


def _default_user(name: str) -> dict:
    return {
        "name":       name,
        "wallet":     1000,
        "bank":       0,
        "health":     100,
        "weapon":     None,
        "pet_equipped": None,
        "cos_equipped": {"flower": None, "vegetable": None, "theme": None},
        "inventory":  {"food": {}, "petfood": 0, "pets": [], "cosmetics": []},
        "relationship": None,
        "kills_today": 0,
        "robs_today":  0,
        "last_kill":   0.0,
        "last_rob":    0.0,
        "last_bet":    0.0,
        "mg_last":     {},
        "bounty":      0,
        "banned":      False,
        "spam_times":  [],
        "spam_blocked":0.0,
        "protection":  0.0,
        "day":         str(date.today()),
    }


def _default_data() -> dict:
    return {"users": {}, "groups": [], "maintenance": False}


async def load_data(app) -> None:
    global _cache, _pin_id
    try:
        chat = await app.bot.get_chat(LOG_CHANNEL_ID)
        if chat.pinned_message:
            _pin_id = chat.pinned_message.message_id
            txt = chat.pinned_message.text or ""
            if txt.startswith("LRPG:"):
                loaded = _decompress(txt[5:])
                if loaded:
                    _cache = loaded
                    logger.info("Data loaded.")
                    return
    except Exception as e:
        logger.error(f"load_data: {e}")
    _cache = _default_data()


async def save_data(app) -> None:
    global _pin_id
    txt = "LRPG:" + _compress(_cache)
    try:
        if _pin_id:
            try:
                await app.bot.edit_message_text(
                    chat_id=LOG_CHANNEL_ID, message_id=_pin_id, text=txt
                )
                return
            except Exception:
                pass
        msg = await app.bot.send_message(LOG_CHANNEL_ID, txt)
        await app.bot.pin_chat_message(
            LOG_CHANNEL_ID, msg.message_id, disable_notification=True
        )
        _pin_id = msg.message_id
    except Exception as e:
        logger.error(f"save_data: {e}")


# ─────────────────────────────────────────────────────────────
#  USER HELPERS
# ─────────────────────────────────────────────────────────────
def get_user(uid: str) -> Optional[dict]:
    return _cache.get("users", {}).get(uid)


def ensure_user(uid: str, name: str) -> dict:
    users = _cache.setdefault("users", {})
    if uid not in users:
        users[uid] = _default_user(name)
    u = users[uid]
    # migrations
    if "pet" in u:
        u.setdefault("pet_equipped", u.pop("pet"))
    if "cosmetics" in u and isinstance(u.get("cosmetics"), dict) and "flowers" in u.get("cosmetics", {}):
        old = u.pop("cosmetics")
        fl  = old.get("flowers", [])
        vg  = old.get("vegetables", [])
        th  = old.get("theme")
        u["cos_equipped"] = {
            "flower":    fl[0] if fl else None,
            "vegetable": vg[0] if vg else None,
            "theme":     th,
        }
    u.setdefault("cos_equipped", {"flower": None, "vegetable": None, "theme": None})
    u.setdefault("pet_equipped", None)
    if not isinstance(u.get("inventory"), dict) or "food" not in u.get("inventory", {}):
        old = u.get("inventory", {})
        ni: Dict[str, Any] = {"food": {}, "petfood": 0, "pets": [], "cosmetics": []}
        if isinstance(old, dict):
            for k, v in old.items():
                if k in STORE["food"]:  ni["food"][k] = v
                elif k == "petfood":    ni["petfood"] = v
        u["inventory"] = ni
    u.setdefault("last_bet", 0.0)
    return u


def daily_reset(u: dict) -> None:
    today = str(date.today())
    if u.get("day") != today:
        u["day"] = today
        u["kills_today"] = 0
        u["robs_today"]  = 0
        u["mg_last"]     = {}


async def dm(bot, uid: int, text: str) -> None:
    try:
        await bot.send_message(uid, text, parse_mode=ParseMode.HTML)
    except Exception:
        pass


def reply_target(update: Update) -> Optional[tuple]:
    if (
        update.message
        and update.message.reply_to_message
        and update.message.reply_to_message.from_user
    ):
        u = update.message.reply_to_message.from_user
        return str(u.id), u.first_name
    return None


async def send_gif(bot, chat_id: int, key: str, caption: str) -> bool:
    """Try to send a GIF from channel. Returns True on success."""
    mid = GIFS.get(key, "").strip()
    if not mid:
        return False
    try:
        await bot.copy_message(
            chat_id=chat_id,
            from_chat_id=GIF_CHANNEL_ID,
            message_id=int(mid),
            caption=caption,
            parse_mode=ParseMode.HTML,
        )
        return True
    except Exception:
        return False


# ─────────────────────────────────────────────────────────────
#  GUARD
# ─────────────────────────────────────────────────────────────
async def guard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if not update.effective_user or not update.message:
        return True
    uid = str(update.effective_user.id)
    if _cache.get("maintenance") and update.effective_user.id != OWNER_ID:
        await update.message.reply_text("🔧 Maintenance mode — try later.")
        return True
    u = get_user(uid)
    if u and u.get("banned"):
        await update.message.reply_text("🚫 You are banned.")
        return True
    if u:
        now = time.time()
        if u.get("spam_blocked", 0) > now:
            await update.message.reply_text(
                f"⛔ Blocked for spam. Wait {int(u['spam_blocked']-now)}s."
            )
            return True
        recent = [t for t in u.get("spam_times", []) if now - t < 10]
        recent.append(now)
        u["spam_times"] = recent[-20:]
        if len(recent) >= 7:
            u["spam_blocked"] = now + 120
            u["spam_times"]   = []
            await update.message.reply_text("⚠️ Spam detected! Blocked 2 min.")
            return True
    return False


# ─────────────────────────────────────────────────────────────
#  BOTTOM BUTTONS (shared)
# ─────────────────────────────────────────────────────────────
def bottom_kb() -> List[List[InlineKeyboardButton]]:
    return [[
        InlineKeyboardButton("👨‍💻 Developer", url=f"https://t.me/{DEV_USERNAME}"),
        InlineKeyboardButton("📢 Channel",    url=f"https://t.me/{CHANNEL}"),
    ]]


# ─────────────────────────────────────────────────────────────
#  /start
# ─────────────────────────────────────────────────────────────
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    u   = update.effective_user
    uid = str(u.id)
    ensure_user(uid, u.first_name)
    if update.effective_chat.type in ("group", "supergroup"):
        gid    = str(update.effective_chat.id)
        groups = _cache.setdefault("groups", [])
        if gid not in groups:
            groups.append(gid)
    await save_data(context.application)
    if update.effective_chat.type != "private":
        await update.message.reply_text(
            f"⚔️ <b>Welcome, {u.first_name}!</b>\n"
            "Use /help to see all commands.",
            parse_mode=ParseMode.HTML,
        )
        return
    kb = [
        [InlineKeyboardButton(
            "➕ Add to Group",
            url=f"https://t.me/{context.bot.username}?startgroup=true",
        )],
        [
            InlineKeyboardButton("📜 Rules", callback_data="info_rules"),
            InlineKeyboardButton("❓ Help",  callback_data="info_help"),
        ],
    ] + bottom_kb()
    await update.message.reply_text(
        f"<b>⚔️ {BOT_NAME}</b>\n"
        "──────────────────────\n\n"
        f"👋 Hey <b>{u.first_name}</b>, welcome!\n\n"
        "<b>Build your life from zero.</b>\n"
        "💰 Earn  ·  🔫 Fight  ·  🐾 Pets\n"
        "📈 Trade  ·  🏆 Dominate\n\n"
        "<i>Add me to a group to start playing!</i>",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode=ParseMode.HTML,
    )


async def cb_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    await q.answer()
    back = [[InlineKeyboardButton("⬅️ Back", callback_data="info_back")]]

    if q.data == "info_rules":
        text = (
            "<b>📜 Game Rules</b>\n"
            "──────────────────────\n\n"
            "<b>⚔️ Combat</b>\n"
            "  • Weapon required to kill\n"
            "  • Dead (HP=0) players are safe\n"
            "  • Kill limit: 10/day · CD: 3s\n\n"
            "<b>🕵️ Robbery</b>\n"
            "  • Only wallet can be robbed\n"
            "  • Bank is 100% safe\n"
            "  • Rob limit: 12/day · CD: 3s\n\n"
            "<b>🛡️ Protection</b>\n"
            "  • Hospital → 2 min shield\n"
            "  • Dead players can't be robbed\n\n"
            "<b>🐾 Pets</b>\n"
            "  • Hunger drops every 2h\n"
            "  • Hunger = 0 → pet runs away!\n\n"
            "<b>⚠️ Anti-Spam</b>\n"
            "  • 7 cmds/10s → 2 min block\n\n"
            "<i>Abuse / exploits = permanent ban</i>"
        )
    elif q.data == "info_help":
        text = (
            "<b>❓ Help Center</b>\n"
            "──────────────────────\n\n"
            "<b>💰 Economy</b>\n"
            "  /bal  /deposit  /withdraw  /pay\n\n"
            "<b>❤️ Health</b>\n"
            "  /eat  /hospital  /medi\n\n"
            "<b>⚔️ Combat</b>\n"
            "  /kill  /rob  /bounty\n\n"
            "<b>🛒 Store & Items</b>\n"
            "  /store  /inv  /sell\n\n"
            "<b>🎲 Games</b>\n"
            "  /dice  /football  /dart  /bowling\n"
            "  /bet &lt;amount&gt;\n\n"
            "<b>🐾 Pet</b>  /feedpet\n\n"
            "<b>💞 Social</b>\n"
            "  /profile  /marry  /brother  /sister\n"
            "  /runaway  /kiss  /hug  /slap\n\n"
            "<b>📦 Trade</b>  /trade &lt;item&gt; &lt;price&gt;\n\n"
            "<b>🏆</b>  /top"
        )
    else:  # back
        u  = q.from_user
        kb = [
            [InlineKeyboardButton(
                "➕ Add to Group",
                url=f"https://t.me/{context.bot.username}?startgroup=true",
            )],
            [
                InlineKeyboardButton("📜 Rules", callback_data="info_rules"),
                InlineKeyboardButton("❓ Help",  callback_data="info_help"),
            ],
        ] + bottom_kb()
        await q.edit_message_text(
            f"<b>⚔️ {BOT_NAME}</b>\n"
            "──────────────────────\n\n"
            f"👋 Hey <b>{u.first_name}</b>, welcome!\n\n"
            "<b>Build your life from zero.</b>\n"
            "💰 Earn  ·  🔫 Fight  ·  🐾 Pets\n"
            "📈 Trade  ·  🏆 Dominate\n\n"
            "<i>Add me to a group to start playing!</i>",
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode=ParseMode.HTML,
        )
        return

    await q.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(back + bottom_kb()),
        parse_mode=ParseMode.HTML,
    )


async def cmd_rules(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "<b>📜 Game Rules</b>\n"
        "──────────────────────\n\n"
        "<b>⚔️ Combat</b>\n"
        "  • Weapon required to kill\n"
        "  • Dead (HP=0) players are safe\n"
        "  • Kill limit: 10/day · CD: 3s\n\n"
        "<b>🕵️ Robbery</b>\n"
        "  • Only wallet can be robbed\n"
        "  • Bank is 100% safe\n"
        "  • Rob limit: 12/day · CD: 3s\n\n"
        "<b>🛡️ Protection</b>\n"
        "  • Hospital → 2 min shield\n"
        "  • Dead players can't be robbed\n\n"
        "<b>🐾 Pets</b>\n"
        "  • Hunger drops every 2h\n"
        "  • Hunger = 0 → pet runs away!\n\n"
        "<b>⚠️ Anti-Spam</b>  7 cmds/10s → 2 min block\n\n"
        "<i>Abuse / exploits = permanent ban</i>",
        parse_mode=ParseMode.HTML,
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "<b>❓ Help Center</b>\n"
        "──────────────────────\n\n"
        "<b>💰 Economy</b>\n"
        "  /bal  /deposit  /withdraw  /pay\n\n"
        "<b>❤️ Health</b>\n"
        "  /eat  /hospital  /medi\n\n"
        "<b>⚔️ Combat</b>\n"
        "  /kill  /rob  /bounty\n\n"
        "<b>🛒 Store & Items</b>\n"
        "  /store  /inv  /sell\n\n"
        "<b>🎲 Games</b>\n"
        "  /dice  /football  /dart  /bowling\n"
        "  /bet &lt;amount&gt;\n\n"
        "<b>🐾 Pet</b>  /feedpet\n\n"
        "<b>💞 Social</b>\n"
        "  /profile  /marry  /brother  /sister\n"
        "  /runaway  /kiss  /hug  /slap\n\n"
        "<b>📦 Trade</b>  /trade &lt;item&gt; &lt;price&gt;\n\n"
        "<b>🏆</b>  /top",
        parse_mode=ParseMode.HTML,
    )


# ─────────────────────────────────────────────────────────────
#  PROFILE  — clean game card
# ─────────────────────────────────────────────────────────────
async def cmd_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await guard(update, context): return
    uid = str(update.effective_user.id)
    rt  = reply_target(update)
    if rt:
        tuid, tname = rt
        user = ensure_user(tuid, tname)
        name = tname
    else:
        user = ensure_user(uid, update.effective_user.first_name)
        name = update.effective_user.first_name
    daily_reset(user)

    th  = get_theme(user)
    hp  = user["health"]
    bar = hp_bar(hp)
    hp_col = "🟢" if hp > 60 else ("🟡" if hp > 30 else "🔴")

    # Header line
    badge = th["badge"]
    tag   = f"  <b>· {th['tag']}</b>" if th["tag"] else ""
    header = f"{badge} <b>{name}</b>{tag}"

    # Weapon
    w     = user.get("weapon")
    wdata = STORE["weapons"].get(w["type"], {}) if w else {}
    w_str = f"{wdata.get('emoji','🔫')} <b>{w['type'].title()}</b> <i>({w['ammo']} ammo)</i>" if w else "<i>None</i>"

    # Pet
    pet   = user.get("pet_equipped")
    if pet:
        pd    = STORE["pets"].get(pet["type"], {})
        hun   = pet.get("hunger", 0)
        hbar  = "▪" * (hun // 20) + "▫" * (5 - hun // 20)
        sfx   = " 😴" if hun < 20 else (" 💨" if hun == 0 else "")
        p_str = f"{pd.get('emoji','')} <b>{pet['type'].title()}</b>  [{hbar}]{sfx}"
    else:
        p_str = "<i>No pet</i>"

    # Relationship
    rel   = user.get("relationship")
    rel_s = f"<b>{rel['type'].title()}</b> of {rel.get('name','?')}" if rel else "<i>Single</i>"

    # Cosmetics
    cos   = user.get("cos_equipped", {})
    fl_e  = STORE["cosmetics"].get(cos.get("flower"), {}).get("emoji", "") if cos.get("flower") else ""
    vg_e  = STORE["cosmetics"].get(cos.get("vegetable"), {}).get("emoji", "") if cos.get("vegetable") else ""
    decor = f"{fl_e}{vg_e}  " if (fl_e or vg_e) else ""

    # Bounty
    b_line = f"\n  🎯 <b>Bounty</b>  {fmt(user['bounty'])}" if user.get("bounty") else ""

    # Inventory counts
    inv    = user.get("inventory", {})
    food_n = sum(inv.get("food", {}).values())
    pets_n = len(inv.get("pets", []))
    cos_n  = len(inv.get("cosmetics", []))

    # ── Theme header ────────────────────────────────
    th_key = (user.get("cos_equipped") or {}).get("theme") or "default"
    if th_key == "gold_theme":
        div1  = "✦━━━━━━━━━━━━━━━━━━━━━✦"
        nline = f"  👑  <b>{name}</b>  ⭐ <b>PREMIUM</b>"
    elif th_key == "blue_theme":
        div1  = "▸▸━━━━━━━━━━━━━━━━━━━◂◂"
        nline = f"  💠  <b>{name}</b>  🔷 <b>ELITE</b>"
    elif th_key == "red_theme":
        div1  = "⚡━━━━━━━━━━━━━━━━━━━━━⚡"
        nline = f"  🔥  <b>{name}</b>  ⚔️ <b>WARRIOR</b>"
    else:
        div1  = "─────────────────────"
        nline = f"  👤  <b>{name}</b>"

    sdiv = "· · · · · · · · · · ·"

    text = (
        f"{div1}\n"
        f"{nline}\n"
        f"{div1}\n"
        f"\n"
        f"  {hp_col} <b>HP</b>  <code>{bar}</code>  <b>{hp}/100</b>\n"
        f"\n"
        f"  {sdiv}\n"
        f"  💳  <b>Wallet</b>  <b>{fmt(user['wallet'])}</b>\n"
        f"  🏦  <b>Bank</b>    <b>{fmt(user['bank'])}</b>\n"
        f"  {sdiv}\n"
        f"\n"
        f"  🔫  <b>Weapon</b>  {w_str}\n"
        f"  🐾  <b>Pet</b>     {p_str}\n"
        f"  💞  <b>Status</b>  {rel_s}"
        f"{b_line}\n"
        f"\n"
        f"  {sdiv}\n"
        f"  🎒  {decor}<b>Food</b>×{food_n}  <b>Pets</b>×{pets_n}  <b>Cos</b>×{cos_n}\n"
        f"  {sdiv}\n"
        f"\n"
        f"  ⚔️  Kills  <b>{user.get('kills_today',0)}/10</b>"
        f"    🕵️  Robs  <b>{user.get('robs_today',0)}/12</b>\n"
        f"{div1}"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


# ─────────────────────────────────────────────────────────────
#  ECONOMY
# ─────────────────────────────────────────────────────────────
async def cmd_bal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await guard(update, context): return
    uid  = str(update.effective_user.id)
    user = ensure_user(uid, update.effective_user.first_name)
    await update.message.reply_text(
        f"<b>💳 Balance</b>\n"
        f"──────────────────────\n"
        f"  👛 Wallet   <b>{fmt(user['wallet'])}</b>\n"
        f"  🏦 Bank     <b>{fmt(user['bank'])}</b>\n"
        f"  💎 Total    <b>{fmt(user['wallet']+user['bank'])}</b>",
        parse_mode=ParseMode.HTML,
    )


async def cmd_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await guard(update, context): return
    uid  = str(update.effective_user.id)
    user = ensure_user(uid, update.effective_user.first_name)
    daily_reset(user)
    if not context.args:
        await update.message.reply_text("Usage: /deposit <amount|all>"); return
    raw = context.args[0].lower()
    amt = user["wallet"] if raw == "all" else (int(raw) if raw.isdigit() else -1)
    if amt <= 0 or amt > user["wallet"]:
        await update.message.reply_text("❌ Invalid amount."); return
    user["wallet"] -= amt
    user["bank"]   += amt
    await save_data(context.application)
    await update.message.reply_text(
        f"🏦 Deposited <b>{fmt(amt)}</b>\n"
        f"  Wallet: {fmt(user['wallet'])}  ·  Bank: {fmt(user['bank'])}",
        parse_mode=ParseMode.HTML,
    )


async def cmd_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await guard(update, context): return
    uid  = str(update.effective_user.id)
    user = ensure_user(uid, update.effective_user.first_name)
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /withdraw <amount>"); return
    amt = int(context.args[0])
    if amt <= 0 or amt > user["bank"]:
        await update.message.reply_text("❌ Insufficient bank balance."); return
    user["bank"]   -= amt
    user["wallet"] += amt
    await save_data(context.application)
    await update.message.reply_text(
        f"💵 Withdrew <b>{fmt(amt)}</b>\n"
        f"  Wallet: {fmt(user['wallet'])}  ·  Bank: {fmt(user['bank'])}",
        parse_mode=ParseMode.HTML,
    )


async def cmd_pay(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await guard(update, context): return
    uid    = str(update.effective_user.id)
    user   = ensure_user(uid, update.effective_user.first_name)
    target = reply_target(update)
    if not target:
        await update.message.reply_text("❌ Reply a user:  /pay <amount>"); return
    tuid, tname = target
    if tuid == uid:
        await update.message.reply_text("❌ Can't pay yourself."); return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /pay <amount>  (reply user)"); return
    amt = int(context.args[0])
    if amt <= 0 or amt > user["wallet"]:
        await update.message.reply_text("❌ Not enough in wallet."); return
    tuser = ensure_user(tuid, tname)
    user["wallet"]  -= amt
    tuser["wallet"] += amt
    await save_data(context.application)
    await update.message.reply_text(
        f"✅ Sent <b>{fmt(amt)}</b> to <b>{tname}</b>",
        parse_mode=ParseMode.HTML,
    )


# ─────────────────────────────────────────────────────────────
#  HEALTH
# ─────────────────────────────────────────────────────────────
async def cmd_eat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await guard(update, context): return
    uid  = str(update.effective_user.id)
    user = ensure_user(uid, update.effective_user.first_name)
    if not context.args:
        await update.message.reply_text("Usage: /eat <item>"); return
    item  = context.args[0].lower()
    fdata = STORE["food"].get(item)
    if not fdata:
        await update.message.reply_text("❌ Not a food item. Check /store"); return
    finv  = user["inventory"].get("food", {})
    if finv.get(item, 0) < 1:
        await update.message.reply_text(f"❌ No {item} in bag."); return
    finv[item] -= 1
    if finv[item] <= 0: del finv[item]
    heal = random.randint(10, fdata["health"])
    user["health"] = min(100, user["health"] + heal)
    await save_data(context.application)
    await update.message.reply_text(
        f"{fdata['emoji']} Ate <b>{item.title()}</b>  +<b>{heal} HP</b>\n"
        f"❤️ Health: <b>{user['health']}/100</b>  <code>[{hp_bar(user['health'])}]</code>",
        parse_mode=ParseMode.HTML,
    )


async def cmd_hospital(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await guard(update, context): return
    uid  = str(update.effective_user.id)
    user = ensure_user(uid, update.effective_user.first_name)
    if user["wallet"] < 1000:
        await update.message.reply_text("❌ Need ₹1,000 in wallet."); return
    if user["health"] >= 100:
        await update.message.reply_text("❤️ Already at full HP!"); return
    old = user["health"]
    user["wallet"]    -= 1000
    user["health"]     = 100
    user["protection"] = time.time() + 120
    await save_data(context.application)
    await update.message.reply_text(
        f"<b>🏥 Healed!</b>\n"
        f"──────────────────────\n"
        f"  ❤️ HP  <b>{old} → 100</b>\n"
        f"  🛡️ Protection  <b>2 min</b>\n"
        f"  💰 Cost  <b>₹1,000</b>",
        parse_mode=ParseMode.HTML,
    )


async def cmd_medi(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await guard(update, context): return
    uid    = str(update.effective_user.id)
    user   = ensure_user(uid, update.effective_user.first_name)
    target = reply_target(update)
    if not target:
        await update.message.reply_text("❌ Reply a user to heal them."); return
    tuid, tname = target
    if user["wallet"] < 1000:
        await update.message.reply_text("❌ Need ₹1,000."); return
    tuser = ensure_user(tuid, tname)
    if tuser["health"] >= 100:
        await update.message.reply_text(f"❌ {tname} is already full HP!"); return
    old = tuser["health"]
    user["wallet"] -= 1000
    tuser["health"] = 100
    await save_data(context.application)
    await update.message.reply_text(
        f"💊 Healed <b>{tname}</b>  {old} → 100 HP\n"
        f"Cost: <b>₹1,000</b>",
        parse_mode=ParseMode.HTML,
    )
    await dm(context.bot, int(tuid),
             f"💊 <b>{update.effective_user.first_name}</b> healed you to full HP!")


# ─────────────────────────────────────────────────────────────
#  KILL
# ─────────────────────────────────────────────────────────────
async def cmd_kill(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await guard(update, context): return
    uid    = str(update.effective_user.id)
    atk    = ensure_user(uid, update.effective_user.first_name)
    daily_reset(atk)
    target = reply_target(update)
    if not target:
        await update.message.reply_text("❌ Reply a user to kill."); return
    tuid, tname = target
    if tuid == uid:
        await update.message.reply_text("❌ Can't kill yourself."); return
    if atk["health"] <= 0:
        await update.message.reply_text("☠️ You're dead! Use /hospital"); return
    if not atk.get("weapon"):
        await update.message.reply_text("❌ No weapon! Buy from /store"); return
    if atk["kills_today"] >= 10:
        await update.message.reply_text("❌ Kill limit: 10/day reached."); return
    now = time.time()
    if now < atk.get("last_kill", 0) + CD_KILL:
        await update.message.reply_text(
            f"⏳ Cooldown: <b>{int(atk['last_kill']+CD_KILL-now)}s</b>",
            parse_mode=ParseMode.HTML,
        )
        return

    vic = ensure_user(tuid, tname)
    daily_reset(vic)
    if vic["health"] <= 0:
        await update.message.reply_text("☠️ Target is already dead!"); return
    if vic.get("protection", 0) > now:
        await update.message.reply_text("🛡️ Target has active protection!"); return

    weapon = atk["weapon"]
    chance = STORE["weapons"].get(weapon["type"], {}).get("kill_chance", 0.5)
    pet    = atk.get("pet_equipped")
    if pet and pet.get("hunger", 0) >= 20:
        if pet["type"] == "tiger":  chance = min(0.98, chance + 0.10)
        if pet["type"] == "dragon": chance = min(0.99, chance + 0.15)

    atk["last_kill"]    = now
    atk["kills_today"] += 1
    weapon["ammo"]     -= 1
    destroyed = weapon["ammo"] <= 0
    if destroyed:
        atk["weapon"] = None

    aname = update.effective_user.first_name
    if random.random() < chance:
        stolen = int(vic["wallet"] * 0.20)
        vic["wallet"]     -= stolen
        atk["wallet"]     += stolen
        bounty             = vic.get("bounty", 0)
        if bounty:
            atk["wallet"] += bounty
            vic["bounty"]  = 0
        vic["health"]     = 0
        vic["protection"] = now + 180
        await save_data(context.application)

        cap = (
            f"<b>💀 Kill  ·  Success</b>\n"
            f"──────────────────────\n"
            f"  🔫 <b>{aname}</b> eliminated <b>{tname}</b>\n"
            f"  💸 Looted  <b>{fmt(stolen)}</b>"
            + (f"\n  🎯 Bounty  <b>{fmt(bounty)}</b>" if bounty else "")
            + (f"\n  💥 Weapon destroyed!" if destroyed else "")
        )
        if not await send_gif(context.bot, update.effective_chat.id, "kill_success", cap):
            await update.message.reply_text(cap, parse_mode=ParseMode.HTML)
        await dm(context.bot, int(tuid),
                 f"💀 Killed by <b>{aname}</b>!\n💸 Lost {fmt(stolen)}. Use /hospital")
    else:
        dmg = random.randint(15, 35)
        atk["health"] = max(0, atk["health"] - dmg)
        await save_data(context.application)
        cap = (
            f"<b>💥 Kill  ·  Failed</b>\n"
            f"──────────────────────\n"
            f"  ❌ <b>{aname}</b> missed <b>{tname}</b>\n"
            f"  💔 Took <b>{dmg} damage</b>  ·  HP: <b>{atk['health']}/100</b>"
            + (f"\n  💥 Weapon destroyed!" if destroyed else "")
        )
        if not await send_gif(context.bot, update.effective_chat.id, "kill_fail", cap):
            await update.message.reply_text(cap, parse_mode=ParseMode.HTML)


# ─────────────────────────────────────────────────────────────
#  ROB
# ─────────────────────────────────────────────────────────────
async def cmd_rob(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await guard(update, context): return
    uid    = str(update.effective_user.id)
    robber = ensure_user(uid, update.effective_user.first_name)
    daily_reset(robber)
    target = reply_target(update)
    if not target:
        await update.message.reply_text("❌ Reply a user to rob."); return
    tuid, tname = target
    if tuid == uid:
        await update.message.reply_text("❌ Can't rob yourself."); return
    if robber["health"] <= 0:
        await update.message.reply_text("☠️ You're dead! Use /hospital"); return
    if robber["robs_today"] >= 12:
        await update.message.reply_text("❌ Rob limit: 12/day reached."); return
    now = time.time()
    if now < robber.get("last_rob", 0) + CD_ROB:
        await update.message.reply_text(
            f"⏳ Cooldown: <b>{int(robber['last_rob']+CD_ROB-now)}s</b>",
            parse_mode=ParseMode.HTML,
        )
        return

    vic = ensure_user(tuid, tname)
    daily_reset(vic)
    if vic["health"] <= 0:
        await update.message.reply_text("☠️ Can't rob a dead player!"); return
    if vic.get("protection", 0) > now:
        await update.message.reply_text("🛡️ Target has protection!"); return
    if vic["wallet"] < 100:
        await update.message.reply_text("❌ Target's wallet is too low."); return

    success = 0.55
    pet     = robber.get("pet_equipped")
    if pet and pet.get("hunger", 0) >= 20:
        if pet["type"] == "dog":    success += 0.15
        if pet["type"] == "fox":    success += 0.20
        if pet["type"] == "dragon": success += 0.20

    robber["last_rob"]   = now
    robber["robs_today"] += 1
    aname = update.effective_user.first_name

    if random.random() < success:
        pct    = random.uniform(0.05, 0.20)
        stolen = max(50, int(vic["wallet"] * pct))
        vic["wallet"]    -= stolen
        robber["wallet"] += stolen
        await save_data(context.application)
        cap = (
            f"<b>🕵️ Rob  ·  Success</b>\n"
            f"──────────────────────\n"
            f"  🏃 <b>{aname}</b> robbed <b>{tname}</b>\n"
            f"  💸 Stole  <b>{fmt(stolen)}</b>  ({int(pct*100)}%)"
        )
        if not await send_gif(context.bot, update.effective_chat.id, "rob_success", cap):
            await update.message.reply_text(cap, parse_mode=ParseMode.HTML)
        await dm(context.bot, int(tuid),
                 f"🕵️ Robbed by <b>{aname}</b>! Lost {fmt(stolen)}.")
    else:
        # Fail type: police or beaten
        if random.random() < 0.5:
            fine = min(random.randint(100, 500), robber["wallet"])
            robber["wallet"] -= fine
            await save_data(context.application)
            cap = (
                f"<b>🚔 Caught by Police!</b>\n"
                f"──────────────────────\n"
                f"  ❌ <b>{aname}</b> got caught robbing <b>{tname}</b>\n"
                f"  💸 Fine paid  <b>{fmt(fine)}</b>"
            )
            if not await send_gif(context.bot, update.effective_chat.id, "police", cap):
                await update.message.reply_text(cap, parse_mode=ParseMode.HTML)
        else:
            dmg = random.randint(10, 25)
            robber["health"] = max(0, robber["health"] - dmg)
            await save_data(context.application)
            cap = (
                f"<b>👊 Beaten Up!</b>\n"
                f"──────────────────────\n"
                f"  ❌ <b>{aname}</b> got caught by <b>{tname}</b>\n"
                f"  💔 Took  <b>{dmg} damage</b>  ·  HP: <b>{robber['health']}/100</b>"
            )
            if not await send_gif(context.bot, update.effective_chat.id, "beaten", cap):
                await update.message.reply_text(cap, parse_mode=ParseMode.HTML)


# ─────────────────────────────────────────────────────────────
#  BOUNTY
# ─────────────────────────────────────────────────────────────
async def cmd_bounty(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await guard(update, context): return
    uid    = str(update.effective_user.id)
    user   = ensure_user(uid, update.effective_user.first_name)
    target = reply_target(update)
    if not target:
        await update.message.reply_text("Usage: /bounty <amount>  (reply user)"); return
    tuid, tname = target
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /bounty <amount>  (reply user)"); return
    amt = int(context.args[0])
    if amt < 100:
        await update.message.reply_text("❌ Minimum bounty: ₹100"); return
    if amt > user["wallet"]:
        await update.message.reply_text("❌ Not enough in wallet."); return
    tuser = ensure_user(tuid, tname)
    user["wallet"]  -= amt
    tuser["bounty"]  = tuser.get("bounty", 0) + amt
    await save_data(context.application)
    await update.message.reply_text(
        f"<b>🎯 Bounty Placed</b>\n"
        f"──────────────────────\n"
        f"  Target   <b>{tname}</b>\n"
        f"  Added    <b>{fmt(amt)}</b>\n"
        f"  Total    <b>{fmt(tuser['bounty'])}</b>\n\n"
        f"<i>Whoever kills them claims it!</i>",
        parse_mode=ParseMode.HTML,
    )


# ─────────────────────────────────────────────────────────────
#  BET  (with win/lose GIF + bigger card)
# ─────────────────────────────────────────────────────────────
async def cmd_bet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await guard(update, context): return
    uid  = str(update.effective_user.id)
    user = ensure_user(uid, update.effective_user.first_name)
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /bet <amount>"); return
    amt = int(context.args[0])
    if amt < 50:
        await update.message.reply_text("❌ Minimum bet: ₹50"); return
    if amt > user["wallet"]:
        await update.message.reply_text("❌ Not enough in wallet."); return
    now = time.time()
    if now < user.get("last_bet", 0) + CD_BET:
        await update.message.reply_text(
            f"⏳ Cooldown: <b>{int(user['last_bet']+CD_BET-now)}s</b>",
            parse_mode=ParseMode.HTML,
        )
        return

    user["last_bet"] = now
    win = random.random() < 0.50

    if win:
        user["wallet"] += amt
        await save_data(context.application)
        cap = (
            f"<b>🎰 BET  ·  YOU WON!</b>\n"
            f"──────────────────────\n"
            f"  🪙 Wagered   <b>{fmt(amt)}</b>\n"
            f"  💰 Won       <b>+{fmt(amt)}</b>\n"
            f"  💎 Wallet    <b>{fmt(user['wallet'])}</b>\n\n"
            f"  🎉 <i>Luck is on your side today!</i>"
        )
        if not await send_gif(context.bot, update.effective_chat.id, "bet_win", cap):
            await update.message.reply_text(cap, parse_mode=ParseMode.HTML)
    else:
        user["wallet"] -= amt
        await save_data(context.application)
        cap = (
            f"<b>🎰 BET  ·  YOU LOST</b>\n"
            f"──────────────────────\n"
            f"  🪙 Wagered   <b>{fmt(amt)}</b>\n"
            f"  📉 Lost      <b>-{fmt(amt)}</b>\n"
            f"  💳 Wallet    <b>{fmt(user['wallet'])}</b>\n\n"
            f"  😤 <i>Better luck next time...</i>"
        )
        if not await send_gif(context.bot, update.effective_chat.id, "bet_lose", cap):
            await update.message.reply_text(cap, parse_mode=ParseMode.HTML)


# ─────────────────────────────────────────────────────────────
#  FEED PET
# ─────────────────────────────────────────────────────────────
async def cmd_feedpet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await guard(update, context): return
    uid  = str(update.effective_user.id)
    user = ensure_user(uid, update.effective_user.first_name)
    if not user.get("pet_equipped"):
        await update.message.reply_text("❌ No pet equipped! Buy & equip from /store"); return
    if user["inventory"].get("petfood", 0) < 1:
        await update.message.reply_text("❌ No petfood! Buy from /store"); return
    user["inventory"]["petfood"] -= 1
    pet = user["pet_equipped"]
    old = pet.get("hunger", 50)
    pet["hunger"] = min(100, old + 30)
    await save_data(context.application)
    pd  = STORE["pets"].get(pet["type"], {})
    await update.message.reply_text(
        f"{pd.get('emoji','🐾')} Fed <b>{pet['type'].title()}</b>\n"
        f"  🍖 Hunger  <b>{old} → {pet['hunger']}/100</b>",
        parse_mode=ParseMode.HTML,
    )


# ─────────────────────────────────────────────────────────────
#  STORE  (full inline, food split into sub-categories)
# ─────────────────────────────────────────────────────────────
def _store_main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🍎  Food",          callback_data="s|foodcat|menu")],
        [
            InlineKeyboardButton("🔫  Weapons",    callback_data="s|cat|weapons"),
            InlineKeyboardButton("🐾  Pets",        callback_data="s|cat|pets"),
        ],
        [
            InlineKeyboardButton("🎨  Cosmetics",  callback_data="s|cat|cosmetics"),
            InlineKeyboardButton("🦴  Pet Food",    callback_data="s|cat|petfood"),
        ],
    ])


async def cmd_store(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await guard(update, context): return
    uid  = str(update.effective_user.id)
    user = ensure_user(uid, update.effective_user.first_name)
    await update.message.reply_text(
        f"<b>🛒 Store</b>  ·  💰 {fmt(user['wallet'])}\n"
        "──────────────────────\n"
        "Choose a category:",
        reply_markup=_store_main_kb(),
        parse_mode=ParseMode.HTML,
    )


async def cb_store(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q    = update.callback_query
    uid  = str(q.from_user.id)
    await q.answer()
    user = ensure_user(uid, q.from_user.first_name)
    parts  = q.data.split("|")
    action = parts[1]
    back   = [[InlineKeyboardButton("⬅️ Back", callback_data="s|back|main")]]

    # ── food main menu (sub-category picker) ─────────────
    if action == "foodcat":
        food_back = [[InlineKeyboardButton("⬅️ Back", callback_data="s|back|main")]]
        await q.edit_message_text(
            f"<b>🍎 Food</b>  ·  💰 {fmt(user['wallet'])}\nChoose a category:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🥦  Veg & Fruits",  callback_data="s|fsub|veg")],
                [InlineKeyboardButton("🍔  Fast Food",      callback_data="s|fsub|fast")],
                [InlineKeyboardButton("🍱  Meals",          callback_data="s|fsub|meal")],
            ] + food_back),
            parse_mode=ParseMode.HTML,
        )

    # ── food sub-category listing ──────────────────────────
    elif action == "fsub":
        sub   = parts[2]
        items = {k: v for k, v in STORE["food"].items() if v.get("sub") == sub}
        label = {"veg":"🥦 Veg & Fruits","fast":"🍔 Fast Food","meal":"🍱 Meals"}.get(sub,"🍎 Food")
        rows: List[List[InlineKeyboardButton]] = []
        for iname, idata in items.items():
            qty = user["inventory"].get("food", {}).get(iname, 0)
            suffix = f"  ×{qty}" if qty else ""
            rows.append([InlineKeyboardButton(
                f"{idata['emoji']} {iname.title()}  ·  {fmt(idata['price'])}  (+{idata['health']} HP){suffix}",
                callback_data=f"s|item|food|{iname}",
            )])
        rows += [[InlineKeyboardButton("⬅️ Back", callback_data="s|foodcat|menu")]]
        await q.edit_message_text(
            f"<b>{label}</b>  ·  💰 {fmt(user['wallet'])}",
            reply_markup=InlineKeyboardMarkup(rows),
            parse_mode=ParseMode.HTML,
        )

    # ── non-food category listing ──────────────────────────
    elif action == "cat":
        cat   = parts[2]
        items = STORE.get(cat, {})
        label = {"weapons":"🔫 Weapons","pets":"🐾 Pets","cosmetics":"🎨 Cosmetics","petfood":"🦴 Pet Food"}.get(cat, cat)
        rows  = []
        for iname, idata in items.items():
            # Check if already owned (one-time items)
            owned = False
            if cat == "weapons" and user.get("weapon") and user["weapon"]["type"] == iname:
                owned = True
            elif cat == "pets":
                ep = user.get("pet_equipped")
                in_bag = any(p["type"] == iname for p in user["inventory"].get("pets", []))
                if (ep and ep["type"] == iname) or in_bag:
                    owned = True
            elif cat == "cosmetics":
                cos_eq = user.get("cos_equipped", {})
                in_bag = iname in user["inventory"].get("cosmetics", [])
                if any(v == iname for v in cos_eq.values()) or in_bag:
                    owned = True
            label_text = (
                f"✅ {idata.get('emoji','')} {iname.replace('_',' ').title()}  · Owned"
                if owned else
                f"{idata.get('emoji','')} {iname.replace('_',' ').title()}  ·  {fmt(idata['price'])}"
            )
            rows.append([InlineKeyboardButton(
                label_text,
                callback_data=f"s|item|{cat}|{iname}",
            )])
        rows += back
        await q.edit_message_text(
            f"<b>{label}</b>  ·  💰 {fmt(user['wallet'])}",
            reply_markup=InlineKeyboardMarkup(rows),
            parse_mode=ParseMode.HTML,
        )

    # ── item detail page ───────────────────────────────────
    elif action == "item":
        cat, iname = parts[2], parts[3]
        idata = STORE[cat][iname]
        price = idata["price"]

        # Check ownership for one-time items
        owned = False
        if cat == "weapons" and user.get("weapon") and user["weapon"]["type"] == iname:
            owned = True
        elif cat == "pets":
            ep     = user.get("pet_equipped")
            in_bag = any(p["type"] == iname for p in user["inventory"].get("pets", []))
            owned  = (ep and ep["type"] == iname) or in_bag
        elif cat == "cosmetics":
            cos_eq = user.get("cos_equipped", {})
            in_bag = iname in user["inventory"].get("cosmetics", [])
            owned  = any(v == iname for v in cos_eq.values()) or in_bag

        lines = [
            f"<b>{idata.get('emoji','')} {iname.replace('_',' ').title()}</b>",
            "──────────────────────",
        ]
        if cat == "food":
            lines += [f"  ❤️ Heals    <b>+{idata['health']} HP</b>"]
        elif cat == "weapons":
            lines += [
                f"  🎯 Kill %   <b>{int(idata['kill_chance']*100)}%</b>",
                f"  🔹 Ammo     <b>{idata['ammo']} shots</b>",
            ]
        elif cat == "pets":
            lines += [f"  ⭐ Bonus   <b>{idata['bonus']}</b>"]
        elif cat == "cosmetics":
            lines += [f"  🏷️ Slot    <b>{idata['slot'].title()}</b>"]
        elif cat == "petfood":
            lines += [f"  🍖 Hunger  <b>+{idata['hunger']}</b>"]

        lines += ["──────────────────────"]
        if owned:
            lines += ["  ✅  <b>Already owned!</b>  Go to /inv to equip."]
        else:
            lines += [
                f"  💰 Price   <b>{fmt(price)}</b>",
                f"  👛 Wallet  {fmt(user['wallet'])}",
            ]

        # Back destination
        if cat == "food":
            back_cb = f"s|fsub|{idata.get('sub','veg')}"
        elif cat == "weapons":
            back_cb = "s|cat|weapons"
        else:
            back_cb = f"s|cat|{cat}"

        if owned:
            kb = [[InlineKeyboardButton("⬅️ Back", callback_data=back_cb)]]
        elif cat in ("food", "petfood"):
            qty_row = [
                InlineKeyboardButton(f"×{q_amt}  {fmt(price*q_amt)}",
                    callback_data=f"s|buy|{cat}|{iname}|{q_amt}")
                for q_amt in (1, 5, 10)
            ]
            kb = [qty_row, [InlineKeyboardButton("⬅️ Back", callback_data=back_cb)]]
        else:
            kb = [
                [InlineKeyboardButton(f"🛒 Buy  {fmt(price)}", callback_data=f"s|buy|{cat}|{iname}|1")],
                [InlineKeyboardButton("⬅️ Back", callback_data=back_cb)],
            ]

        await q.edit_message_text(
            "\n".join(lines),
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode=ParseMode.HTML,
        )

    # ── buy ────────────────────────────────────────────────
    elif action == "buy":
        cat, iname, qty = parts[2], parts[3], int(parts[4])
        idata = STORE[cat][iname]
        total = idata["price"] * qty
        inv   = user["inventory"]

        if user["wallet"] < total:
            await q.answer(f"❌ Need {fmt(total)}!", show_alert=True); return

        tip = ""
        if cat == "weapons":
            if user.get("weapon"):
                await q.answer("❌ Sell your weapon first!", show_alert=True); return
            user["weapon"] = {"type": iname, "ammo": idata["ammo"]}
        elif cat == "pets":
            inv.setdefault("pets", []).append({"type": iname, "hunger": 100})
            tip = "\n<i>Go to /inv to equip it!</i>"
        elif cat == "cosmetics":
            inv.setdefault("cosmetics", []).append(iname)
            tip = "\n<i>Go to /inv to equip it!</i>"
        elif cat == "food":
            inv.setdefault("food", {})[iname] = inv["food"].get(iname, 0) + qty
        elif cat == "petfood":
            inv["petfood"] = inv.get("petfood", 0) + qty

        user["wallet"] -= total
        await save_data(context.application)
        await q.edit_message_text(
            f"<b>✅ Purchased!</b>\n"
            f"──────────────────────\n"
            f"  {idata.get('emoji','')} <b>{iname.replace('_',' ').title()}</b>  ×{qty}\n"
            f"  💸 Spent   <b>{fmt(total)}</b>\n"
            f"  💰 Wallet  <b>{fmt(user['wallet'])}</b>"
            f"{tip}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🛒 Continue Shopping", callback_data="s|back|main")],
            ]),
            parse_mode=ParseMode.HTML,
        )

    # ── back to main ───────────────────────────────────────
    elif action == "back":
        await q.edit_message_text(
            f"<b>🛒 Store</b>  ·  💰 {fmt(user['wallet'])}\n"
            "──────────────────────\n"
            "Choose a category:",
            reply_markup=_store_main_kb(),
            parse_mode=ParseMode.HTML,
        )


# ─────────────────────────────────────────────────────────────
#  INVENTORY  + EQUIP / UNEQUIP
# ─────────────────────────────────────────────────────────────
def _build_inv_text_and_kb(user: dict) -> tuple:
    inv      = user.get("inventory", {})
    food_inv = inv.get("food", {})
    pf_qty   = inv.get("petfood", 0)
    pets_bag = inv.get("pets", [])
    cos_bag  = inv.get("cosmetics", [])
    ep       = user.get("pet_equipped")
    cos_eq   = user.get("cos_equipped", {})
    w        = user.get("weapon")

    lines = ["<b>🎒 Bag</b>", "─────────────────────"]

    # ── Weapon ───────────────────────────────────────────
    if w:
        wd = STORE["weapons"].get(w["type"], {})
        lines.append(
            f"🔫 {wd.get('emoji','')} <b>{w['type'].title()}</b>"
            f"  {w['ammo']} ammo  <i>· equipped</i>"
        )

    # ── Food + petfood (compact, one line each group) ────
    if food_inv:
        food_str = "  ".join(
            f"{STORE['food'].get(k,{}).get('emoji','')}<b>{k.title()}</b>×{v}"
            for k, v in food_inv.items()
        )
        lines.append(f"🍎 {food_str}")
    if pf_qty:
        lines.append(f"🦴 <b>Petfood</b> ×{pf_qty}")

    # ── Pets ─────────────────────────────────────────────
    btn_rows: List[List[InlineKeyboardButton]] = []

    if ep or pets_bag:
        lines.append("")
        lines.append("<b>🐾 Pets</b>")
        if ep:
            pd  = STORE["pets"].get(ep["type"], {})
            hun = ep.get("hunger", 0)
            hb  = "▪" * (hun // 20) + "▫" * (5 - hun // 20)
            lines.append(f"  {pd.get('emoji','')} <b>{ep['type'].title()}</b>  [{hb}] {hun}%  <i>· on</i>")
            btn_rows.append([
                InlineKeyboardButton(f"⏏️ Unequip {ep['type'].title()}", callback_data="inv|unequip_pet")
            ])
        # Pair bag pets into 2-per-row buttons
        bag_btns = [
            InlineKeyboardButton(
                f"▶️ {STORE['pets'].get(p['type'],{}).get('emoji','')} {p['type'].title()}",
                callback_data=f"inv|equip_pet|{i}"
            )
            for i, p in enumerate(pets_bag)
        ]
        if pets_bag:
            pet_lines = "  ".join(
                f"{STORE['pets'].get(p['type'],{}).get('emoji','')} <b>{p['type'].title()}</b>  🍖{p.get('hunger',100)}%"
                for p in pets_bag
            )
            lines.append(f"  <i>(bag)</i> {pet_lines}")
        for i in range(0, len(bag_btns), 2):
            btn_rows.append(bag_btns[i:i+2])

    # ── Cosmetics ────────────────────────────────────────
    if any(cos_eq.values()) or cos_bag:
        lines.append("")
        lines.append("<b>🎨 Cosmetics</b>")
        for slot, cname in cos_eq.items():
            if cname:
                cd = STORE["cosmetics"].get(cname, {})
                lines.append(
                    f"  {cd.get('emoji','')} <b>{cname.replace('_',' ').title()}</b>"
                    f"  <i>· {slot} on</i>"
                )
                btn_rows.append([
                    InlineKeyboardButton(
                        f"⏏️ {cd.get('emoji','')} {cname.replace('_',' ').title()}",
                        callback_data=f"inv|unequip_cos|{slot}"
                    )
                ])
        if cos_bag:
            bag_cos = "  ".join(
                f"{STORE['cosmetics'].get(c,{}).get('emoji','')} <b>{c.replace('_',' ').title()}</b>"
                for c in cos_bag
            )
            lines.append(f"  <i>(bag)</i> {bag_cos}")
            cos_btns = [
                InlineKeyboardButton(
                    f"▶️ {STORE['cosmetics'].get(c,{}).get('emoji','')} {c.replace('_',' ').title()}",
                    callback_data=f"inv|equip_cos|{c}"
                )
                for c in cos_bag
            ]
            for i in range(0, len(cos_btns), 2):
                btn_rows.append(cos_btns[i:i+2])

    if len(lines) <= 2:
        lines.append("  <i>Empty — visit /store!</i>")

    lines.append("")
    lines.append("─────────────────────")
    btn_rows.append([InlineKeyboardButton("🔄 Refresh", callback_data="inv|refresh")])
    return "\n".join(lines), InlineKeyboardMarkup(btn_rows)


async def cmd_inv(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await guard(update, context): return
    uid  = str(update.effective_user.id)
    user = ensure_user(uid, update.effective_user.first_name)
    text, kb = _build_inv_text_and_kb(user)
    await update.message.reply_text(text, reply_markup=kb, parse_mode=ParseMode.HTML)


async def cb_inv(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q    = update.callback_query
    uid  = str(q.from_user.id)
    await q.answer()
    user  = ensure_user(uid, q.from_user.first_name)
    parts = q.data.split("|")
    act   = parts[1]

    if act == "equip_pet":
        idx = int(parts[2])
        bag = user["inventory"].get("pets", [])
        if idx >= len(bag):
            await q.answer("❌ Not found.", show_alert=True); return
        if user.get("pet_equipped"):
            user["inventory"]["pets"].append(user["pet_equipped"])
        user["pet_equipped"] = bag.pop(idx)
        await save_data(context.application)
        await q.answer(f"✅ {user['pet_equipped']['type'].title()} equipped!")

    elif act == "unequip_pet":
        if not user.get("pet_equipped"):
            await q.answer("❌ None equipped.", show_alert=True); return
        user["inventory"]["pets"].append(user["pet_equipped"])
        user["pet_equipped"] = None
        await save_data(context.application)
        await q.answer("✅ Pet unequipped.")

    elif act == "equip_cos":
        cname  = parts[2]
        cos_bg = user["inventory"].get("cosmetics", [])
        if cname not in cos_bg:
            await q.answer("❌ Not in bag.", show_alert=True); return
        slot   = STORE["cosmetics"].get(cname, {}).get("slot", "")
        cos_eq = user.setdefault("cos_equipped", {"flower": None, "vegetable": None, "theme": None})
        old    = cos_eq.get(slot)
        if old:
            cos_bg.append(old)
        cos_bg.remove(cname)
        cos_eq[slot] = cname
        await save_data(context.application)
        await q.answer(f"✅ {cname.replace('_',' ').title()} equipped!")

    elif act == "unequip_cos":
        slot   = parts[2]
        cos_eq = user.get("cos_equipped", {})
        cname  = cos_eq.get(slot)
        if not cname:
            await q.answer("❌ Nothing in that slot.", show_alert=True); return
        user["inventory"].setdefault("cosmetics", []).append(cname)
        cos_eq[slot] = None
        await save_data(context.application)
        await q.answer(f"✅ Unequipped.")

    # Refresh display
    user = ensure_user(uid, q.from_user.first_name)
    text, kb = _build_inv_text_and_kb(user)
    await q.edit_message_text(text, reply_markup=kb, parse_mode=ParseMode.HTML)


# ─────────────────────────────────────────────────────────────
#  SELL
# ─────────────────────────────────────────────────────────────
async def cmd_sell(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await guard(update, context): return
    uid  = str(update.effective_user.id)
    user = ensure_user(uid, update.effective_user.first_name)
    if not context.args:
        await update.message.reply_text("Usage: /sell <item>"); return
    item = context.args[0].lower()

    def _kb(stype, sp, extra=""):
        return InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Confirm", callback_data=f"sell|{stype}|{item}|{sp}{extra}"),
            InlineKeyboardButton("❌ Cancel",  callback_data="sell|cancel"),
        ]])

    if user.get("weapon") and user["weapon"]["type"] == item:
        sp = STORE["weapons"].get(item, {}).get("price", 0) // 2
        await update.message.reply_text(
            f"🔫 Sell <b>{item.title()}</b> for <b>{fmt(sp)}</b>?",
            reply_markup=_kb("weapon", sp), parse_mode=ParseMode.HTML); return

    ep = user.get("pet_equipped")
    if ep and ep["type"] == item:
        sp = STORE["pets"].get(item, {}).get("price", 0) // 2
        await update.message.reply_text(
            f"🐾 Sell equipped <b>{item.title()}</b> for <b>{fmt(sp)}</b>?",
            reply_markup=_kb("epet", sp), parse_mode=ParseMode.HTML); return

    for i, p in enumerate(user["inventory"].get("pets", [])):
        if p["type"] == item:
            sp = STORE["pets"].get(item, {}).get("price", 0) // 2
            await update.message.reply_text(
                f"🐾 Sell <b>{item.title()}</b> (bag) for <b>{fmt(sp)}</b>?",
                reply_markup=_kb("bpet", sp, f"|{i}"), parse_mode=ParseMode.HTML); return

    if item in user["inventory"].get("cosmetics", []):
        sp = STORE["cosmetics"].get(item, {}).get("price", 0) // 2
        await update.message.reply_text(
            f"🎨 Sell <b>{item.replace('_',' ').title()}</b> for <b>{fmt(sp)}</b>?",
            reply_markup=_kb("cos", sp), parse_mode=ParseMode.HTML); return

    finv = user["inventory"].get("food", {})
    if finv.get(item, 0) > 0:
        sp = STORE["food"].get(item, {}).get("price", 0) // 2
        await update.message.reply_text(
            f"🍎 Sell <b>{item.title()}</b> for <b>{fmt(sp)}</b>?",
            reply_markup=_kb("food", sp), parse_mode=ParseMode.HTML); return

    await update.message.reply_text(f"❌ You don't have <b>{item}</b>.", parse_mode=ParseMode.HTML)


async def cb_sell(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q    = update.callback_query
    uid  = str(q.from_user.id)
    await q.answer()
    user = get_user(uid)
    if not user:
        await q.edit_message_text("❌ Not registered."); return
    if q.data == "sell|cancel":
        await q.edit_message_text("❌ Cancelled."); return

    parts = q.data.split("|")
    stype, item, sp = parts[1], parts[2], int(parts[3])

    if stype == "weapon":
        if not user.get("weapon") or user["weapon"]["type"] != item:
            await q.edit_message_text("❌ Weapon not found."); return
        user["weapon"] = None
    elif stype == "epet":
        if not user.get("pet_equipped") or user["pet_equipped"]["type"] != item:
            await q.edit_message_text("❌ Pet not found."); return
        user["pet_equipped"] = None
    elif stype == "bpet":
        idx  = int(parts[4])
        pets = user["inventory"].get("pets", [])
        if idx >= len(pets): await q.edit_message_text("❌ Not found."); return
        pets.pop(idx)
    elif stype == "cos":
        bag = user["inventory"].get("cosmetics", [])
        if item not in bag: await q.edit_message_text("❌ Not found."); return
        bag.remove(item)
    elif stype == "food":
        finv = user["inventory"].get("food", {})
        if finv.get(item, 0) < 1: await q.edit_message_text("❌ Not found."); return
        finv[item] -= 1
        if finv[item] <= 0: del finv[item]

    user["wallet"] += sp
    await save_data(context.application)
    await q.edit_message_text(
        f"✅ Sold <b>{item.replace('_',' ').title()}</b> for <b>{fmt(sp)}</b>\n"
        f"💰 Wallet: <b>{fmt(user['wallet'])}</b>",
        parse_mode=ParseMode.HTML,
    )


# ─────────────────────────────────────────────────────────────
#  TRADE
# ─────────────────────────────────────────────────────────────
_trades: Dict[str, dict] = {}


async def cmd_trade(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await guard(update, context): return
    uid    = str(update.effective_user.id)
    user   = ensure_user(uid, update.effective_user.first_name)
    target = reply_target(update)
    if not target:
        await update.message.reply_text("Usage: /trade <item> <price>  (reply user)"); return
    tuid, tname = target
    if tuid == uid:
        await update.message.reply_text("❌ Can't trade with yourself."); return
    if len(context.args) < 2 or not context.args[1].isdigit():
        await update.message.reply_text("Usage: /trade <item> <price>  (reply user)"); return

    item  = context.args[0].lower()
    price = int(context.args[1])
    inv   = user.get("inventory", {})
    itype = None
    emoji = "📦"

    if inv.get("food", {}).get(item, 0) > 0:
        itype, emoji = "food",     STORE["food"].get(item, {}).get("emoji", "🍎")
    elif item == "petfood" and inv.get("petfood", 0) > 0:
        itype, emoji = "petfood",  "🦴"
    elif any(p["type"] == item for p in inv.get("pets", [])):
        itype, emoji = "pet",      STORE["pets"].get(item, {}).get("emoji", "🐾")
    elif item in inv.get("cosmetics", []):
        itype, emoji = "cosmetic", STORE["cosmetics"].get(item, {}).get("emoji", "🎨")

    if not itype:
        await update.message.reply_text(f"❌ <b>{item}</b> not in bag.", parse_mode=ParseMode.HTML); return

    ensure_user(tuid, tname)
    tid = f"{uid}_{tuid}_{int(time.time())}"
    _trades[tid] = {
        "from_uid": uid, "from_name": update.effective_user.first_name,
        "to_uid": tuid, "item": item, "itype": itype, "price": price,
        "expires": time.time() + 60,
    }
    kb = [[
        InlineKeyboardButton("✅ Accept",  callback_data=f"trade|accept|{tid}"),
        InlineKeyboardButton("❌ Decline", callback_data=f"trade|decline|{tid}"),
    ]]
    await update.message.reply_text(
        f"<b>📦 Trade Offer</b>\n"
        f"──────────────────────\n"
        f"  From   <b>{update.effective_user.first_name}</b> → <b>{tname}</b>\n"
        f"  Item   {emoji} <b>{item.replace('_',' ').title()}</b>\n"
        f"  Price  <b>{fmt(price)}</b>\n\n"
        f"<i>⏳ Expires in 60s</i>",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode=ParseMode.HTML,
    )


async def cb_trade(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q      = update.callback_query
    await q.answer()
    parts  = q.data.split("|")
    tid    = parts[2]
    trade  = _trades.get(tid)

    if not trade or time.time() > trade.get("expires", 0):
        _trades.pop(tid, None)
        await q.edit_message_text("❌ Trade expired."); return
    if str(q.from_user.id) != trade["to_uid"]:
        await q.answer("❌ Not for you!", show_alert=True); return
    if parts[1] == "decline":
        _trades.pop(tid, None)
        await q.edit_message_text("❌ Trade declined."); return

    seller = get_user(trade["from_uid"])
    buyer  = get_user(trade["to_uid"])
    if not seller or not buyer:
        await q.edit_message_text("❌ Data error."); return
    if buyer["wallet"] < trade["price"]:
        await q.edit_message_text(f"❌ Need {fmt(trade['price'])} to accept."); return

    item, itype, price = trade["item"], trade["itype"], trade["price"]
    sinv = seller.get("inventory", {})
    binv = buyer.setdefault("inventory", {"food":{}, "petfood":0, "pets":[], "cosmetics":[]})

    if itype == "food":
        if sinv.get("food", {}).get(item, 0) < 1:
            await q.edit_message_text("❌ Seller no longer has item."); return
        sinv["food"][item] -= 1
        if sinv["food"][item] <= 0: del sinv["food"][item]
        binv.setdefault("food", {})[item] = binv["food"].get(item, 0) + 1
    elif itype == "petfood":
        if sinv.get("petfood", 0) < 1:
            await q.edit_message_text("❌ Seller no longer has item."); return
        sinv["petfood"] -= 1
        binv["petfood"] = binv.get("petfood", 0) + 1
    elif itype == "pet":
        idx = next((i for i, p in enumerate(sinv.get("pets", [])) if p["type"] == item), None)
        if idx is None:
            await q.edit_message_text("❌ Seller no longer has pet."); return
        pet = sinv["pets"].pop(idx)
        binv.setdefault("pets", []).append(pet)
    elif itype == "cosmetic":
        if item not in sinv.get("cosmetics", []):
            await q.edit_message_text("❌ Seller no longer has cosmetic."); return
        sinv["cosmetics"].remove(item)
        binv.setdefault("cosmetics", []).append(item)

    buyer["wallet"]  -= price
    seller["wallet"] += price
    _trades.pop(tid, None)
    await save_data(context.application)
    await q.edit_message_text(
        f"<b>✅ Trade Complete</b>\n"
        f"──────────────────────\n"
        f"  <b>{trade['from_name']}</b> → <b>{q.from_user.first_name}</b>\n"
        f"  Item   <b>{item.replace('_',' ').title()}</b>\n"
        f"  Paid   <b>{fmt(price)}</b>",
        parse_mode=ParseMode.HTML,
    )


# ─────────────────────────────────────────────────────────────
#  RELATIONSHIPS
# ─────────────────────────────────────────────────────────────
REL_MAP = {"marry": "partner", "brother": "brother", "sister": "sister"}


async def cmd_relationship(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await guard(update, context): return
    uid   = str(update.effective_user.id)
    user  = ensure_user(uid, update.effective_user.first_name)
    cmd   = update.message.text.split()[0].lstrip("/").split("@")[0].lower()
    rtype = REL_MAP.get(cmd, "partner")
    target = reply_target(update)
    if not target:
        await update.message.reply_text(f"❌ Reply to someone with /{cmd}."); return
    tuid, tname = target
    if tuid == uid:
        await update.message.reply_text("❌ Can't relate to yourself!"); return
    if rtype == "partner" and user.get("relationship"):
        await update.message.reply_text("❌ Already in a relationship! /runaway first."); return
    ensure_user(tuid, tname)
    kb = [[
        InlineKeyboardButton("✅ Accept",  callback_data=f"rel|accept|{uid}|{tuid}|{rtype}"),
        InlineKeyboardButton("❌ Decline", callback_data="rel|decline"),
    ]]
    await update.message.reply_text(
        f"💌 <b>{update.effective_user.first_name}</b> wants to be your <b>{rtype}</b>!\n"
        f"<i>{tname}, do you accept?</i>",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode=ParseMode.HTML,
    )


async def cb_relationship(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q     = update.callback_query
    await q.answer()
    parts = q.data.split("|")
    if parts[1] == "decline":
        await q.edit_message_text("❌ Request declined."); return
    uid1, uid2, rtype = parts[2], parts[3], parts[4]
    if str(q.from_user.id) != uid2:
        await q.answer("❌ Not for you!", show_alert=True); return
    u1 = get_user(uid1)
    u2 = get_user(uid2)
    if not u1 or not u2:
        await q.edit_message_text("❌ Data error."); return
    u1["relationship"] = {"type": rtype, "uid": uid2, "name": u2.get("name", uid2)}
    u2["relationship"] = {"type": rtype, "uid": uid1, "name": u1.get("name", uid1)}
    await save_data(context.application)
    await q.edit_message_text(
        f"💞 <b>{u1.get('name')}</b> & <b>{u2.get('name')}</b> are now <b>{rtype}s</b>! 🎉",
        parse_mode=ParseMode.HTML,
    )


async def cmd_runaway(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await guard(update, context): return
    uid  = str(update.effective_user.id)
    user = ensure_user(uid, update.effective_user.first_name)
    rel  = user.get("relationship")
    if not rel:
        await update.message.reply_text("❌ No active relationship."); return
    other = get_user(str(rel.get("uid", "")))
    rtype = rel.get("type", "relationship")
    user["relationship"] = None
    if other:
        other["relationship"] = None
    await save_data(context.application)
    await update.message.reply_text(
        f"💔 Left your <b>{rtype}</b> relationship.", parse_mode=ParseMode.HTML
    )


# ─────────────────────────────────────────────────────────────
#  MINI GAMES  — Telegram dice animation → 5s → result
# ─────────────────────────────────────────────────────────────
GAME_DICE = {
    "dice":     ("🎲", 6),
    "football": ("⚽", 5),
    "dart":     ("🎯", 6),
    "bowling":  ("🎳", 6),
}


async def _minigame(update: Update, context: ContextTypes.DEFAULT_TYPE, game: str) -> None:
    if await guard(update, context): return
    uid  = str(update.effective_user.id)
    user = ensure_user(uid, update.effective_user.first_name)
    daily_reset(user)
    mg   = user.setdefault("mg_last", {})
    now  = time.time()
    if now - mg.get(game, 0) < 86400:
        left = int(86400 - (now - mg.get(game, 0)))
        h, m = divmod(left // 60, 60)
        await update.message.reply_text(
            f"⏳ <b>{game.title()}</b> cooldown: <b>{h}h {m}m</b>",
            parse_mode=ParseMode.HTML,
        )
        return

    emoji, max_val = GAME_DICE[game]

    # Step 1: send the animated dice
    dice_msg = await context.bot.send_dice(
        chat_id=update.effective_chat.id,
        emoji=emoji,
    )
    dice_val = dice_msg.dice.value  # actual result 1–max_val

    # Step 2: wait for animation
    await asyncio.sleep(4)

    # Step 3: calculate reward based on dice value
    tier   = dice_val / max_val           # 0..1
    mult   = 1.0
    pet    = user.get("pet_equipped")
    if pet and pet.get("hunger", 0) >= 20:
        pt = pet["type"]
        if pt == "cat":    mult = 1.15
        if pt == "monkey": mult = 1.0 + random.uniform(0, 0.30)
        if pt == "dragon": mult = 1.25

    base   = int(100 + tier * 900)        # 100–1000 based on dice roll
    reward = int(base * mult)

    mg[game]       = now
    user["wallet"] += reward
    await save_data(context.application)

    outcome = "🎉 Perfect!" if dice_val == max_val else ("👍 Nice!" if tier >= 0.5 else "😅 Low roll.")

    await update.message.reply_text(
        f"<b>{emoji} {game.title()}  ·  Roll: {dice_val}/{max_val}</b>\n"
        f"──────────────────────\n"
        f"  💰 Won    <b>{fmt(reward)}</b>\n"
        f"  👛 Wallet <b>{fmt(user['wallet'])}</b>\n"
        f"  {outcome}",
        parse_mode=ParseMode.HTML,
    )


async def cmd_dice(u, c):     await _minigame(u, c, "dice")
async def cmd_football(u, c): await _minigame(u, c, "football")
async def cmd_dart(u, c):     await _minigame(u, c, "dart")
async def cmd_bowling(u, c):  await _minigame(u, c, "bowling")


# ─────────────────────────────────────────────────────────────
#  SOCIAL  (GIF via channel)
# ─────────────────────────────────────────────────────────────
SOCIAL_MSG = {
    "kiss": ("💋", "{a} kissed {b}! 😘"),
    "hug":  ("🤗", "{a} hugged {b}! 💞"),
    "slap": ("👋", "{a} slapped {b}! 💢"),
}


async def _social(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    if await guard(update, context): return
    target = reply_target(update)
    if not target:
        await update.message.reply_text(f"❌ Reply to someone with /{action}."); return
    _, tname = target
    em, tmpl = SOCIAL_MSG[action]
    caption  = f"{em}  <b>{tmpl.format(a=update.effective_user.first_name, b=tname)}</b>"
    if not await send_gif(context.bot, update.effective_chat.id, action, caption):
        await update.message.reply_text(caption, parse_mode=ParseMode.HTML)


async def cmd_kiss(u, c): await _social(u, c, "kiss")
async def cmd_hug(u, c):  await _social(u, c, "hug")
async def cmd_slap(u, c): await _social(u, c, "slap")


# ─────────────────────────────────────────────────────────────
#  LEADERBOARD  — with developer + channel buttons at bottom
# ─────────────────────────────────────────────────────────────
async def cmd_top(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if await guard(update, context): return
    users  = _cache.get("users", {})
    top    = sorted(
        users.items(),
        key=lambda x: x[1].get("wallet", 0) + x[1].get("bank", 0),
        reverse=True,
    )[:10]
    medals = ["🥇","🥈","🥉"] + ["🏅"]*7
    lines  = ["<b>🏆 Rich List</b>", "──────────────────────"]
    for i, (uid, u) in enumerate(top):
        total = u.get("wallet", 0) + u.get("bank", 0)
        lines.append(f"  {medals[i]}  <b>{u.get('name', uid)}</b>  ·  {fmt(total)}")
    lines.append("──────────────────────")
    await update.message.reply_text(
        "\n".join(lines),
        reply_markup=InlineKeyboardMarkup(bottom_kb()),
        parse_mode=ParseMode.HTML,
    )


# ─────────────────────────────────────────────────────────────
#  ADMIN
# ─────────────────────────────────────────────────────────────
async def cmd_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != OWNER_ID: return
    m   = "🟢 ON" if _cache.get("maintenance") else "🔴 OFF"
    tot = len(_cache.get("users", {}))
    grp = len(_cache.get("groups", []))
    kb  = [
        [InlineKeyboardButton(f"🔧 Maintenance: {m}", callback_data="adm|maint")],
        [
            InlineKeyboardButton("🚫 Ban",   callback_data="adm|ban_info"),
            InlineKeyboardButton("✅ Unban", callback_data="adm|unban_info"),
        ],
        [InlineKeyboardButton("💰 Give Money", callback_data="adm|money_info")],
        [InlineKeyboardButton(f"📊 {tot} users  ·  {grp} groups", callback_data="adm|noop")],
    ]
    await update.message.reply_text(
        "<b>⚙️ Admin Panel</b>",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode=ParseMode.HTML,
    )


async def cb_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    q = update.callback_query
    if q.from_user.id != OWNER_ID:
        await q.answer("❌ Owner only!", show_alert=True); return
    await q.answer()
    if q.data == "adm|maint":
        _cache["maintenance"] = not _cache.get("maintenance", False)
        await save_data(context.application)
        s = "🟢 ON" if _cache["maintenance"] else "🔴 OFF"
        await q.edit_message_text(f"🔧 Maintenance: {s}")
    elif q.data == "adm|ban_info":    await q.edit_message_text("Send: /ban <user_id>")
    elif q.data == "adm|unban_info":  await q.edit_message_text("Send: /unban <user_id>")
    elif q.data == "adm|money_info":  await q.edit_message_text("Send: /money <user_id> <amount>")


async def cmd_ban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != OWNER_ID: return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /ban <user_id>"); return
    u = _cache.get("users", {}).get(context.args[0])
    if not u: await update.message.reply_text("❌ Not found."); return
    u["banned"] = True
    await save_data(context.application)
    await update.message.reply_text(f"🚫 {context.args[0]} banned.")


async def cmd_unban(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != OWNER_ID: return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /unban <user_id>"); return
    u = _cache.get("users", {}).get(context.args[0])
    if not u: await update.message.reply_text("❌ Not found."); return
    u["banned"] = False
    await save_data(context.application)
    await update.message.reply_text(f"✅ {context.args[0]} unbanned.")


async def cmd_money(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != OWNER_ID: return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /money <id> <amount>"); return
    uid, raw = context.args[0], context.args[1]
    if not uid.isdigit() or not raw.lstrip("-").isdigit():
        await update.message.reply_text("❌ Invalid."); return
    u = _cache.get("users", {}).get(uid)
    if not u: await update.message.reply_text("❌ User not found."); return
    amt = int(raw)
    u["wallet"] += amt
    await save_data(context.application)
    await update.message.reply_text(
        f"✅ {'Gave' if amt>0 else 'Deducted'} {fmt(abs(amt))}\n"
        f"Wallet: {fmt(u['wallet'])}"
    )


async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != OWNER_ID: return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /broadcast <chat_id> <msg>"); return
    cid = context.args[0]
    msg = " ".join(context.args[1:])
    if not cid.lstrip("-").isdigit():
        await update.message.reply_text("❌ Invalid ID."); return
    try:
        await context.bot.send_message(int(cid), msg)
        await update.message.reply_text("✅ Sent!")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


async def cmd_gcbroadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != OWNER_ID: return
    if not context.args: await update.message.reply_text("Usage: /gcbroadcast <msg>"); return
    msg  = " ".join(context.args)
    sent = 0
    for gid in _cache.get("groups", []):
        try:
            await context.bot.send_message(int(gid), msg); sent += 1
        except Exception: pass
    await update.message.reply_text(f"✅ Sent to {sent} groups.")


async def cmd_broadcastall(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != OWNER_ID: return
    if not context.args: await update.message.reply_text("Usage: /broadcastall <msg>"); return
    msg  = " ".join(context.args)
    sent = 0
    for uid in list(_cache.get("users", {}).keys()):
        try:
            await context.bot.send_message(int(uid), msg); sent += 1
            await asyncio.sleep(0.05)
        except Exception: pass
    for gid in _cache.get("groups", []):
        try:
            await context.bot.send_message(int(gid), msg); sent += 1
            await asyncio.sleep(0.05)
        except Exception: pass
    await update.message.reply_text(f"✅ Broadcast done — {sent} chats.")


# ─────────────────────────────────────────────────────────────
#  GROUP AUTO-REGISTER
# ─────────────────────────────────────────────────────────────
async def on_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = update.my_chat_member
    if not result: return
    ns     = result.new_chat_member.status
    chat   = result.chat
    gid    = str(chat.id)
    groups = _cache.setdefault("groups", [])
    if ns in (ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR):
        if gid not in groups:
            groups.append(gid)
            await save_data(context.application)
        try:
            await context.bot.send_message(
                chat.id,
                f"<b>⚔️ {BOT_NAME} is here!</b>\n\n"
                "Use /start to register · /help for commands\n"
                "Let the games begin! 💰🔫",
                parse_mode=ParseMode.HTML,
            )
        except Exception: pass
    elif ns in (ChatMemberStatus.LEFT, ChatMemberStatus.BANNED):
        if gid in groups:
            groups.remove(gid)
            await save_data(context.application)


# ─────────────────────────────────────────────────────────────
#  BACKGROUND — pet hunger decay
# ─────────────────────────────────────────────────────────────
async def job_pet_decay(context: ContextTypes.DEFAULT_TYPE) -> None:
    changed, ran_away = False, []
    for uid, user in _cache.get("users", {}).items():
        pet = user.get("pet_equipped")
        if pet:
            old = pet.get("hunger", 100)
            new = max(0, old - 5)
            pet["hunger"] = new
            changed = True
            if new == 0 and old > 0:
                ran_away.append((uid, pet["type"]))
                user["pet_equipped"] = None
    if changed:
        await save_data(context.application)
    for uid, ptype in ran_away:
        pd = STORE["pets"].get(ptype, {})
        await dm(
            context.bot, int(uid),
            f"{pd.get('emoji','🐾')} <b>{ptype.title()}</b> ran away — it was starving! 😢\n"
            "Buy a new pet from /store",
        )


# ─────────────────────────────────────────────────────────────
#  APP INIT
# ─────────────────────────────────────────────────────────────
async def post_init(application: Application) -> None:
    await load_data(application)
    await application.bot.set_my_commands([
        BotCommand("start",       "Start / register"),
        BotCommand("help",        "All commands"),
        BotCommand("rules",       "Game rules"),
        BotCommand("profile",     "View profile"),
        BotCommand("bal",         "Check balance"),
        BotCommand("deposit",     "Deposit to bank"),
        BotCommand("withdraw",    "Withdraw from bank"),
        BotCommand("pay",         "Pay a player"),
        BotCommand("store",       "Open store"),
        BotCommand("inv",         "Inventory + equip"),
        BotCommand("sell",        "Sell an item"),
        BotCommand("eat",         "Eat food"),
        BotCommand("hospital",    "Full heal ₹1000"),
        BotCommand("medi",        "Heal others ₹1000"),
        BotCommand("kill",        "Kill a player"),
        BotCommand("rob",         "Rob a player"),
        BotCommand("bounty",      "Place a bounty"),
        BotCommand("bet",         "Bet money 50/50"),
        BotCommand("feedpet",     "Feed your pet"),
        BotCommand("marry",       "Propose marriage"),
        BotCommand("brother",     "Add brother"),
        BotCommand("sister",      "Add sister"),
        BotCommand("runaway",     "Leave relationship"),
        BotCommand("dice",        "🎲 Dice (24h)"),
        BotCommand("football",    "⚽ Football (24h)"),
        BotCommand("dart",        "🎯 Dart (24h)"),
        BotCommand("bowling",     "🎳 Bowling (24h)"),
        BotCommand("kiss",        "💋 Kiss someone"),
        BotCommand("hug",         "🤗 Hug someone"),
        BotCommand("slap",        "👋 Slap someone"),
        BotCommand("trade",       "Trade items"),
        BotCommand("top",         "Rich leaderboard"),
    ])
    logger.info("✅ Bot ready.")


# ─────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────
def main() -> None:
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )
    for cmd, fn in [
        ("start",        cmd_start),
        ("help",         cmd_help),
        ("rules",        cmd_rules),
        ("profile",      cmd_profile),
        ("bal",          cmd_bal),
        ("deposit",      cmd_deposit),
        ("withdraw",     cmd_withdraw),
        ("pay",          cmd_pay),
        ("eat",          cmd_eat),
        ("hospital",     cmd_hospital),
        ("medi",         cmd_medi),
        ("kill",         cmd_kill),
        ("rob",          cmd_rob),
        ("bounty",       cmd_bounty),
        ("bet",          cmd_bet),
        ("feedpet",      cmd_feedpet),
        ("store",        cmd_store),
        ("inv",          cmd_inv),
        ("sell",         cmd_sell),
        ("trade",        cmd_trade),
        ("top",          cmd_top),
        ("marry",        cmd_relationship),
        ("brother",      cmd_relationship),
        ("sister",       cmd_relationship),
        ("runaway",      cmd_runaway),
        ("dice",         cmd_dice),
        ("football",     cmd_football),
        ("dart",         cmd_dart),
        ("bowling",      cmd_bowling),
        ("kiss",         cmd_kiss),
        ("hug",          cmd_hug),
        ("slap",         cmd_slap),
        ("admin",        cmd_admin),
        ("ban",          cmd_ban),
        ("unban",        cmd_unban),
        ("money",        cmd_money),
        ("broadcast",    cmd_broadcast),
        ("gcbroadcast",  cmd_gcbroadcast),
        ("broadcastall", cmd_broadcastall),
    ]:
        app.add_handler(CommandHandler(cmd, fn))

    app.add_handler(CallbackQueryHandler(cb_info,         pattern=r"^info"))
    app.add_handler(CallbackQueryHandler(cb_store,        pattern=r"^s\|"))
    app.add_handler(CallbackQueryHandler(cb_inv,          pattern=r"^inv\|"))
    app.add_handler(CallbackQueryHandler(cb_sell,         pattern=r"^sell\|"))
    app.add_handler(CallbackQueryHandler(cb_relationship, pattern=r"^rel\|"))
    app.add_handler(CallbackQueryHandler(cb_trade,        pattern=r"^trade\|"))
    app.add_handler(CallbackQueryHandler(cb_admin,        pattern=r"^adm\|"))
    app.add_handler(ChatMemberHandler(on_chat_member, ChatMemberHandler.MY_CHAT_MEMBER))

    app.job_queue.run_repeating(job_pet_decay, interval=7200, first=300)
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
