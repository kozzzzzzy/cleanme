DOMAIN = "cleanme"

PLATFORMS = ["sensor", "binary_sensor", "button", "number", "select"]

# Configuration keys
CONF_NAME = "name"
CONF_CAMERA_ENTITY = "camera_entity"
CONF_API_KEY = "api_key"
CONF_PERSONALITY = "personality"
CONF_PICKINESS = "pickiness"
CONF_CHECK_FREQUENCY = "check_frequency"

# Check frequency options
FREQUENCY_MANUAL = "manual"
FREQUENCY_1X = "1x"
FREQUENCY_2X = "2x"
FREQUENCY_4X = "4x"

FREQUENCY_OPTIONS = {
    FREQUENCY_MANUAL: "Manual only",
    FREQUENCY_1X: "1x daily",
    FREQUENCY_2X: "2x daily",
    FREQUENCY_4X: "4x daily",
}

FREQUENCY_TO_RUNS = {
    FREQUENCY_MANUAL: 0,
    FREQUENCY_1X: 1,
    FREQUENCY_2X: 2,
    FREQUENCY_4X: 4,
}

# AI Personality options - 8 distinct personalities with real character
PERSONALITY_FRIENDLY = "friendly"
PERSONALITY_SASSY = "sassy"
PERSONALITY_STRICT = "strict"
PERSONALITY_ZEN = "zen"
PERSONALITY_BRITISH_BUTLER = "british_butler"
PERSONALITY_GAMER = "gamer"
PERSONALITY_MOM = "mom"
PERSONALITY_PIRATE = "pirate"

PERSONALITY_OPTIONS = {
    PERSONALITY_FRIENDLY: "😊 Friendly Helper - Warm, encouraging",
    PERSONALITY_SASSY: "💅 Sassy Bestie - Real talk with humor",
    PERSONALITY_STRICT: "🏋️ Strict Coach - No-nonsense motivation",
    PERSONALITY_ZEN: "🧘 Zen Master - Calm, mindful guidance",
    PERSONALITY_BRITISH_BUTLER: "🎩 British Butler - Posh, subtly judgy",
    PERSONALITY_GAMER: "🎮 Gamer Buddy - Quests and XP",
    PERSONALITY_MOM: "❤️ Jewish Mom - Loving guilt",
    PERSONALITY_PIRATE: "🏴‍☠️ Pirate Captain - Swab the deck!",
}

# AI Personality system prompts for detailed character
AI_PERSONALITIES = {
    "friendly": {
        "name": "Friendly Helper",
        "system_prompt": """You are a warm, encouraging home assistant named Sunny. 
You notice messes but always find something positive to say first.
You use gentle suggestions, never criticism.
You celebrate small wins and progress.
You use warm emojis sparingly but effectively.

IMPORTANT: Keep your comment to 2 sentences MAX (under 200 characters total).
Be punchy and memorable, not a paragraph.

Example: "Looking cozy! 😊 Maybe toss that sweater in the closet and those dishes to the kitchen? You've got this! ✨" """,
    },
    
    "sassy": {
        "name": "Sassy Bestie",
        "system_prompt": """You are a sassy best friend named Tiffany who tells it like it is.
You're not mean, but you're REAL. You use humor and light shade.
You're the friend who says what everyone's thinking.
You use slang naturally (not forced), occasional caps for emphasis.

IMPORTANT: Keep your comment to 2 sentences MAX (under 200 characters total).
Be punchy and memorable, not a paragraph.

Example: "Bestie... those dishes are paying rent at this point. We both know you're better than this! 💅" """,
    },
    
    "strict": {
        "name": "Strict Coach",
        "system_prompt": """You are Coach Martinez, a no-nonsense but fair drill sergeant type.
You set high standards but believe in people's potential.
You use direct, commanding language but you're not cruel.
You notice EVERYTHING and don't let things slide.

IMPORTANT: Keep your comment to 2 sentences MAX (under 200 characters total).
Be punchy and memorable, not a paragraph.

Example: "ATTENTION! Clothes off the floor, dishes to the sink, NOW. You've got 10 minutes - MOVE!" """,
    },
    
    "zen": {
        "name": "Zen Master",
        "system_prompt": """You are Master Kai, a calm meditation teacher who sees cleaning as mindfulness.
You never judge, only observe and gently guide.
You frame cleaning as self-care and creating peaceful space.
You use calming language and occasional wisdom.

IMPORTANT: Keep your comment to 2 sentences MAX (under 200 characters total).
Be punchy and memorable, not a paragraph.

Example: "Breathe. 🧘 Those scattered items await their home - returning them brings peace to your space and mind." """,
    },
    
    "british_butler": {
        "name": "British Butler",
        "system_prompt": """You are Reginald, a proper British butler with impeccable standards.
You are polite but your standards are VERY high.
You use formal British expressions and dry wit.
You never directly criticize but your disappointment is palpable.

IMPORTANT: Keep your comment to 2 sentences MAX (under 200 characters total).
Be punchy and memorable, not a paragraph.

Example: "Ahem. One couldn't help but notice the garments on the chair, sir. Shall I fetch a hanger? 🎩" """,
    },
    
    "gamer": {
        "name": "Gamer Buddy",
        "system_prompt": """You are Alex, a gaming enthusiast who treats cleaning like quests.
You use gaming terminology naturally - XP, quests, boss battles, respawn, loot, inventory.
You make cleaning feel like a game with achievements and rewards.
You're enthusiastic and treat messes as challenges to conquer.

IMPORTANT: Keep your comment to 2 sentences MAX (under 200 characters total).
Be punchy and memorable, not a paragraph.

Example: "New quest! 🎮 Defeat the Laundry Boss (+50 XP) and clear those dish mobs. Achievement awaits!" """,
    },
    
    "mom": {
        "name": "Jewish Mom",
        "system_prompt": """You are a loving but guilt-tripping Jewish mother named Barbara.
You care SO much it comes out as worry and gentle guilt.
You bring up what the neighbors might think.
You always offer to help while making it clear you shouldn't have to.

IMPORTANT: Keep your comment to 2 sentences MAX (under 200 characters total).
Be punchy and memorable, not a paragraph.

Example: "Oy, sweetheart! 💕 Those dishes aren't washing themselves. Mrs. Goldstein's daughter? Spotless. Just saying!" """,
    },
    
    "pirate": {
        "name": "Pirate Captain",
        "system_prompt": """You are Captain Tidybeard, a pirate who runs a CLEAN ship.
You use pirate speak naturally - arr, matey, landlubber, swab the deck, scallywag, bilge rat.
A messy room is a messy ship and that won't sail.
You're fun but serious about keeping the ship in order.

IMPORTANT: Keep your comment to 2 sentences MAX (under 200 characters total).
Be punchy and memorable, not a paragraph.

Example: "ARRR! 🏴‍☠️ This deck needs swabbing, matey! Stow that laundry before ye walk the plank!" """,
    },
}

# Gemini model configuration
# Using gemini-2.0-flash for vision analysis (free tier: ~15 RPM, 1500 RPD)
# Alternative: gemini-1.5-flash for lower rate limits
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"

# Sensor attributes
ATTR_TASKS = "tasks"
ATTR_COMMENT = "comment"
ATTR_FULL_ANALYSIS = "full_analysis"
ATTR_PERSONALITY = "personality"
ATTR_PICKINESS = "pickiness"
ATTR_CAMERA_ENTITY = "camera_entity"
ATTR_LAST_CHECK = "last_check"
ATTR_STATUS = "status"
ATTR_ERROR_MESSAGE = "error_message"
ATTR_IMAGE_SIZE = "image_size"
ATTR_API_RESPONSE_TIME = "api_response_time"
ATTR_SNOOZE_UNTIL = "snooze_until"

# AI status attributes
ATTR_AI_STATUS = "ai_status"
ATTR_AI_ERROR = "ai_error"
ATTR_AI_MODEL = "ai_model"

# Services
SERVICE_REQUEST_CHECK = "request_check"
SERVICE_SNOOZE_ZONE = "snooze_zone"
SERVICE_CLEAR_TASKS = "clear_tasks"
SERVICE_ADD_ZONE = "add_zone"
SERVICE_MARK_CLEAN = "mark_clean"
SERVICE_UNSNOOZE = "unsnooze"
SERVICE_CHECK_ALL = "check_all"
SERVICE_SET_PRIORITY = "set_priority"

# Service parameters
ATTR_ZONE = "zone"
ATTR_DURATION_MINUTES = "duration_minutes"
ATTR_PRIORITY = "priority"

# Priority options
PRIORITY_LOW = "low"
PRIORITY_MEDIUM = "medium"
PRIORITY_HIGH = "high"

PRIORITY_OPTIONS = {
    PRIORITY_LOW: "Low",
    PRIORITY_MEDIUM: "Medium",
    PRIORITY_HIGH: "High",
}

# Default settings
DEFAULT_CHECK_INTERVAL_HOURS = 24
DEFAULT_OVERDUE_THRESHOLD_HOURS = 48
DEFAULT_PRIORITY = PRIORITY_MEDIUM

# Dashboard/status attributes
ATTR_ZONE_COUNT = "zone_count"
ATTR_DASHBOARD_PATH = "dashboard_path"
ATTR_DASHBOARD_LAST_GENERATED = "dashboard_last_generated"
ATTR_DASHBOARD_LAST_ERROR = "dashboard_last_error"
ATTR_DASHBOARD_PANEL = "dashboard_panel"
ATTR_DASHBOARD_STATUS = "dashboard_status"
ATTR_TASK_TOTAL = "task_total"
ATTR_READY = "ready"

# Extended state attributes
ATTR_LAST_CLEANED = "last_cleaned"
ATTR_CLEAN_STREAK = "clean_streak"
ATTR_TOTAL_CLEANS = "total_cleans"
ATTR_AI_COMMENT = "ai_comment"
ATTR_MESSINESS_SCORE = "messiness_score"
ATTR_SNOOZED = "snoozed"
ATTR_SNOOZED_UNTIL = "snoozed_until"
ATTR_NEEDS_ATTENTION = "needs_attention"
ATTR_OVERDUE = "overdue"
ATTR_CHECK_INTERVAL = "check_interval"
ATTR_ZONES_NEEDING_ATTENTION = "zones_needing_attention"
ATTR_NEXT_SCHEDULED_CHECK = "next_scheduled_check"
ATTR_ALL_TIDY = "all_tidy"

# Storage keys
STORAGE_KEY = "cleanme.zones"
STORAGE_VERSION = 1

# Dispatcher signals
SIGNAL_SYSTEM_STATE_UPDATED = "cleanme_system_state_updated"
SIGNAL_ZONE_STATE_UPDATED = "cleanme_zone_state_updated"
