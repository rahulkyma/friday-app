"""
Configuration management for Instagram AI automation
"""
import os
from typing import Dict, List

# API Endpoints
INSTAGRAM_GRAPH_API_VERSION = "v18.0"
INSTAGRAM_GRAPH_API_URL = f"https://graph.instagram.com/{INSTAGRAM_GRAPH_API_VERSION}"

# Content Configuration
DEFAULT_CONTENT_NICHE = "technology"
DEFAULT_CONTENT_LANGUAGE = "hi"
DEFAULT_CONTENT_TONE = "professional"

# Posting Configuration
DEFAULT_SCHEDULE_TIME = "09:00"
DEFAULT_TIMEZONE = "Asia/Kolkata"
MAX_CAPTION_LENGTH = 2200
MIN_CAPTION_LENGTH = 10

# Comment Handling
MAX_COMMENTS_PER_RUN = 50
MIN_COMMENT_LENGTH = 10
COMMENT_REPLY_MAX_LENGTH = 1000
SPAM_KEYWORDS = [
    "spam", "buy", "click", "link", "follow me",
    "dm", "check out", "limited offer", "free", "click here"
]

# Safety Settings
ENABLE_CONTENT_MODERATION = True
CONTENT_MODERATION_THRESHOLD = 0.7  # 0-1 scale

# Logging
LOG_DIR = "logs"
LOG_FILE = "instagram_automation.log"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL_DEFAULT = "INFO"

# OpenAI Configuration
OPENAI_MODEL_DEFAULT = "gpt-4"
OPENAI_MAX_TOKENS = 500
OPENAI_TEMPERATURE = 0.7

# Image Configuration
SUPPORTED_IMAGE_FORMATS = ["jpg", "jpeg", "png", "gif", "bmp"]
MAX_IMAGE_SIZE_MB = 8
IMAGE_QUALITY = 95
IMAGE_RESIZE_WIDTH = 1080
IMAGE_RESIZE_HEIGHT = 1350

# Retry Configuration
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 5

# Rate Limiting
REQUEST_TIMEOUT = 30  # seconds
RATE_LIMIT_DELAY = 1  # seconds between API calls

# Features Toggle
FEATURES = {
    "POSTING": True,
    "COMMENTS": True,
    "ANALYTICS": True,
    "SCHEDULING": True,
}

# Content Prompt Templates
CONTENT_PROMPT_TEMPLATE = """
Create an engaging Instagram {niche} {content_type} post in {language} language.
Tone: {tone}

Requirements:
- Main content/caption
- 10-15 relevant hashtags
- Call-to-action
- Emoji usage (2-3 emojis)
- Keep it authentic and engaging

Format the response as JSON with keys: caption, hashtags, cta, emojis
"""

# API Response Timeout
API_TIMEOUT = 30

# Batch Processing
BATCH_SIZE = 10
