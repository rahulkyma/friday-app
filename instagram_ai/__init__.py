"""
Instagram AI Automation Package
Complete AI-powered Instagram automation system
"""

from instagram_ai.config import *
from instagram_ai.secrets import SecretsManager, get_secrets
from instagram_ai.logger import Logger, get_logger
from instagram_ai.content_generator import ContentGenerator
from instagram_ai.image_handler import ImageHandler
from instagram_ai.instagram_api import InstagramAPI
from instagram_ai.comment_handler import CommentHandler
from instagram_ai.scheduler import TaskScheduler, get_scheduler

__version__ = "1.0.0"
__author__ = "Instagram AI Automation"

__all__ = [
    "SecretsManager",
    "get_secrets",
    "Logger",
    "get_logger",
    "ContentGenerator",
    "ImageHandler",
    "InstagramAPI",
    "CommentHandler",
    "TaskScheduler",
    "get_scheduler",
]
