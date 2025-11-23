DOMAIN = "cleanme"

PLATFORMS = ["sensor", "binary_sensor"]

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
# Using gemini-2.0-flash-exp for best balance of speed, cost, and vision capabilities
# Alternative: gemini-1.5-pro-latest for higher quality
GEMINI_MODEL = "gemini-2.0-flash-exp"
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

# Services
SERVICE_REQUEST_CHECK = "request_check"
SERVICE_SNOOZE_ZONE = "snooze_zone"
SERVICE_CLEAR_TASKS = "clear_tasks"
SERVICE_ADD_ZONE = "add_zone"

# Service parameters
ATTR_ZONE = "zone"
ATTR_DURATION_MINUTES = "duration_minutes"

# Dashboard/status attributes
ATTR_ZONE_COUNT = "zone_count"
ATTR_DASHBOARD_PATH = "dashboard_path"
ATTR_DASHBOARD_LAST_GENERATED = "dashboard_last_generated"
ATTR_DASHBOARD_LAST_ERROR = "dashboard_last_error"
ATTR_DASHBOARD_PANEL = "dashboard_panel"
ATTR_DASHBOARD_STATUS = "dashboard_status"
ATTR_TASK_TOTAL = "task_total"
ATTR_READY = "ready"

# Dispatcher signals
SIGNAL_SYSTEM_STATE_UPDATED = "cleanme_system_state_updated"
SIGNAL_ZONE_STATE_UPDATED = "cleanme_zone_state_updated"
