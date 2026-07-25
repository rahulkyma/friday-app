"""
Logging configuration for Instagram AI automation
"""
import logging
import os
from datetime import datetime
from typing import Optional
from instagram_ai.secrets import SecretsManager
from instagram_ai import config

class Logger:
    """Centralized logging setup"""
    
    _logger: Optional[logging.Logger] = None
    
    @classmethod
    def get_logger(cls, name: str = "instagram_ai") -> logging.Logger:
        """Get or create logger instance"""
        if cls._logger is not None:
            return cls._logger
        
        cls._logger = logging.getLogger(name)
        
        # Create logs directory if it doesn't exist
        os.makedirs(config.LOG_DIR, exist_ok=True)
        
        # Get log level from environment
        log_level = SecretsManager.get_log_level()
        cls._logger.setLevel(getattr(logging, log_level, logging.INFO))
        
        # Create formatter
        formatter = logging.Formatter(config.LOG_FORMAT)
        
        # File handler
        log_file_path = os.path.join(config.LOG_DIR, config.LOG_FILE)
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(formatter)
        cls._logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        cls._logger.addHandler(console_handler)
        
        return cls._logger
    
    @classmethod
    def info(cls, message: str):
        """Log info message"""
        logger = cls.get_logger()
        logger.info(message)
    
    @classmethod
    def error(cls, message: str, exception: Optional[Exception] = None):
        """Log error message"""
        logger = cls.get_logger()
        if exception:
            logger.error(f"{message}: {str(exception)}", exc_info=True)
        else:
            logger.error(message)
    
    @classmethod
    def warning(cls, message: str):
        """Log warning message"""
        logger = cls.get_logger()
        logger.warning(message)
    
    @classmethod
    def debug(cls, message: str):
        """Log debug message"""
        logger = cls.get_logger()
        logger.debug(message)


# Convenience function
def get_logger(name: str = "instagram_ai") -> logging.Logger:
    """Get logger instance"""
    return Logger.get_logger(name)
