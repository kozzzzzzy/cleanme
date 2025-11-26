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

# AI Personality options
PERSONALITY_CHILL = "chill"
PERSONALITY_THOROUGH = "thorough"
PERSONALITY_STRICT = "strict"
PERSONALITY_SARCASTIC = "sarcastic"
PERSONALITY_PROFESSIONAL = "professional"

PERSONALITY_OPTIONS = {
    PERSONALITY_CHILL: "😊 Chill - Relaxed, supportive tone",
    PERSONALITY_THOROUGH: "🤓 Thorough - Detailed, helpful",
    PERSONALITY_STRICT: "😤 Strict - Critical, demanding",
    PERSONALITY_SARCASTIC: "🤪 Sarcastic - Funny, snarky",
    PERSONALITY_PROFESSIONAL: "💼 Professional - Formal, clinical",
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
