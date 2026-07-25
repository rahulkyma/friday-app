"""
Environment variables and secrets management
All secrets are loaded from environment variables only - NO hardcoding
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

class SecretsManager:
    """Centralized secrets management from environment variables"""
    
    @staticmethod
    def get_openai_api_key() -> str:
        """Get OpenAI API key from environment"""
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        return key
    
    @staticmethod
    def get_instagram_access_token() -> str:
        """Get Instagram/Meta access token from environment"""
        token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
        if not token:
            raise ValueError("INSTAGRAM_ACCESS_TOKEN environment variable not set")
        return token
    
    @staticmethod
    def get_instagram_business_account_id() -> str:
        """Get Instagram Business Account ID from environment"""
        account_id = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
        if not account_id:
            raise ValueError("INSTAGRAM_BUSINESS_ACCOUNT_ID environment variable not set")
        return account_id
    
    @staticmethod
    def get_instagram_page_id() -> str:
        """Get Facebook Page ID from environment"""
        page_id = os.getenv("INSTAGRAM_PAGE_ID")
        if not page_id:
            raise ValueError("INSTAGRAM_PAGE_ID environment variable not set")
        return page_id
    
    @staticmethod
    def get_meta_app_id() -> str:
        """Get Meta App ID from environment"""
        app_id = os.getenv("META_APP_ID")
        if not app_id:
            raise ValueError("META_APP_ID environment variable not set")
        return app_id
    
    @staticmethod
    def get_meta_app_secret() -> str:
        """Get Meta App Secret from environment"""
        secret = os.getenv("META_APP_SECRET")
        if not secret:
            raise ValueError("META_APP_SECRET environment variable not set")
        return secret
    
    @staticmethod
    def get_content_niche() -> str:
        """Get content niche from environment"""
        return os.getenv("CONTENT_NICHE", "technology")
    
    @staticmethod
    def get_content_language() -> str:
        """Get content language from environment"""
        return os.getenv("CONTENT_LANGUAGE", "hi")
    
    @staticmethod
    def get_content_tone() -> str:
        """Get content tone from environment"""
        return os.getenv("CONTENT_TONE", "professional")
    
    @staticmethod
    def get_schedule_time() -> str:
        """Get schedule time from environment"""
        return os.getenv("SCHEDULE_TIME", "09:00")
    
    @staticmethod
    def get_timezone() -> str:
        """Get timezone from environment"""
        return os.getenv("TIMEZONE", "Asia/Kolkata")
    
    @staticmethod
    def get_log_level() -> str:
        """Get log level from environment"""
        return os.getenv("LOG_LEVEL", "INFO")
    
    @staticmethod
    def get_openai_model() -> str:
        """Get OpenAI model from environment"""
        return os.getenv("OPENAI_MODEL", "gpt-4")
    
    @staticmethod
    def is_posting_enabled() -> bool:
        """Check if posting is enabled"""
        return os.getenv("ENABLE_POSTING", "true").lower() == "true"
    
    @staticmethod
    def is_comments_enabled() -> bool:
        """Check if comment handling is enabled"""
        return os.getenv("ENABLE_COMMENTS", "true").lower() == "true"
    
    @staticmethod
    def is_analytics_enabled() -> bool:
        """Check if analytics is enabled"""
        return os.getenv("ENABLE_ANALYTICS", "true").lower() == "true"
    
    @staticmethod
    def validate_all_secrets() -> bool:
        """Validate that all required secrets are set"""
        required_keys = [
            "OPENAI_API_KEY",
            "INSTAGRAM_ACCESS_TOKEN",
            "INSTAGRAM_BUSINESS_ACCOUNT_ID",
            "INSTAGRAM_PAGE_ID",
            "META_APP_ID",
            "META_APP_SECRET"
        ]
        
        missing_keys = []
        for key in required_keys:
            if not os.getenv(key):
                missing_keys.append(key)
        
        if missing_keys:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_keys)}")
        
        return True


# Convenience exports
def get_secrets() -> SecretsManager:
    """Get SecretsManager instance"""
    return SecretsManager()
