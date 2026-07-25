"""
Meta/Instagram Graph API integration
Handles posting, commenting, and analytics
"""
import requests
import json
from typing import Dict, List, Optional
from instagram_ai.secrets import SecretsManager
from instagram_ai.logger import Logger
from instagram_ai import config

class InstagramAPI:
    """Instagram/Meta Graph API client"""
    
    def __init__(self):
        """Initialize Instagram API client"""
        self.logger = Logger.get_logger(__name__)
        self.access_token = SecretsManager.get_instagram_access_token()
        self.business_account_id = SecretsManager.get_instagram_business_account_id()
        self.page_id = SecretsManager.get_instagram_page_id()
        self.base_url = config.INSTAGRAM_GRAPH_API_URL
        self.timeout = config.REQUEST_TIMEOUT
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None
    ) -> Dict:
        """
        Make API request to Instagram Graph API
        
        Args:
            method: HTTP method (GET, POST, etc)
            endpoint: API endpoint
            params: Query parameters
            json_data: JSON body data
        
        Returns:
            Response data
        """
        try:
            if params is None:
                params = {}
            
            # Add access token to params
            params['access_token'] = self.access_token
            
            url = f"{self.base_url}/{endpoint}"
            
            self.logger.debug(f"Making {method} request to {url}")
            
            response = requests.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP error in API request: {e.response.status_code} - {e.response.text}", e)
            raise
        except requests.exceptions.Timeout as e:
            self.logger.error("API request timeout", e)
            raise
        except Exception as e:
            self.logger.error(f"API request failed", e)
            raise
    
    def upload_image(self, image_path: str) -> str:
        """
        Upload image to Instagram
        
        Args:
            image_path: Path to image file
        
        Returns:
            Media ID
        """
        try:
            self.logger.info(f"Uploading image: {image_path}")
            
            with open(image_path, 'rb') as image_file:
                files = {'file': image_file}
                params = {'access_token': self.access_token}
                
                response = requests.post(
                    f"{self.base_url}/{self.business_account_id}/media",
                    files=files,
                    params=params,
                    timeout=self.timeout
                )
                
                response.raise_for_status()
                data = response.json()
                
                media_id = data.get('id')
                if not media_id:
                    raise ValueError("No media ID in response")
                
                self.logger.info(f"Image uploaded successfully: {media_id}")
                return media_id
            
        except Exception as e:
            self.logger.error("Failed to upload image", e)
            raise
    
    def create_post(
        self,
        image_path: str,
        caption: str,
        content_type: str = "IMAGE"
    ) -> str:
        """
        Create and publish Instagram post
        
        Args:
            image_path: Path to image
            caption: Post caption
            content_type: Type of content (IMAGE, VIDEO, CAROUSEL)
        
        Returns:
            Post ID
        """
        try:
            self.logger.info(f"Creating {content_type} post")
            
            # Upload image
            media_id = self.upload_image(image_path)
            
            # Create media object
            media_payload = {
                'image_url': image_path if content_type == "IMAGE" else None,
                'caption': caption,
                'media_type': content_type,
                'user_tags': [],
            }
            
            # Remove None values
            media_payload = {k: v for k, v in media_payload.items() if v is not None}
            
            response = self._make_request(
                method="POST",
                endpoint=f"{self.business_account_id}/media",
                json_data=media_payload
            )
            
            post_id = response.get('id')
            if not post_id:
                raise ValueError("No post ID in response")
            
            self.logger.info(f"Post created successfully: {post_id}")
            return post_id
            
        except Exception as e:
            self.logger.error("Failed to create post", e)
            raise
    
    def publish_post(self, media_id: str) -> str:
        """
        Publish a created post
        
        Args:
            media_id: Media ID to publish
        
        Returns:
            Published post ID
        """
        try:
            self.logger.info(f"Publishing post: {media_id}")
            
            response = self._make_request(
                method="POST",
                endpoint=f"{self.business_account_id}/media_publish",
                json_data={"creation_id": media_id}
            )
            
            post_id = response.get('id')
            if not post_id:
                raise ValueError("Failed to publish post")
            
            self.logger.info(f"Post published successfully: {post_id}")
            return post_id
            
        except Exception as e:
            self.logger.error("Failed to publish post", e)
            raise
    
    def get_recent_comments(self, post_id: str, limit: int = 50) -> List[Dict]:
        """
        Get recent comments on a post
        
        Args:
            post_id: Post ID
            limit: Max comments to retrieve
        
        Returns:
            List of comments
        """
        try:
            self.logger.info(f"Fetching recent comments for post: {post_id}")
            
            response = self._make_request(
                method="GET",
                endpoint=f"{post_id}/comments",
                params={
                    'fields': 'id,text,timestamp,from',
                    'limit': limit
                }
            )
            
            comments = response.get('data', [])
            self.logger.info(f"Retrieved {len(comments)} comments")
            return comments
            
        except Exception as e:
            self.logger.error("Failed to get comments", e)
            raise
    
    def reply_to_comment(self, comment_id: str, reply_text: str) -> str:
        """
        Reply to a comment
        
        Args:
            comment_id: Comment ID
            reply_text: Reply text
        
        Returns:
            Reply ID
        """
        try:
            self.logger.info(f"Replying to comment: {comment_id}")
            
            if len(reply_text) > config.COMMENT_REPLY_MAX_LENGTH:
                self.logger.warning(f"Reply text too long, truncating to {config.COMMENT_REPLY_MAX_LENGTH} chars")
                reply_text = reply_text[:config.COMMENT_REPLY_MAX_LENGTH]
            
            response = self._make_request(
                method="POST",
                endpoint=f"{comment_id}/replies",
                json_data={"message": reply_text}
            )
            
            reply_id = response.get('id')
            if not reply_id:
                raise ValueError("Failed to create reply")
            
            self.logger.info(f"Reply sent successfully: {reply_id}")
            return reply_id
            
        except Exception as e:
            self.logger.error("Failed to reply to comment", e)
            raise
    
    def get_post_insights(self, post_id: str) -> Dict:
        """
        Get insights/analytics for a post
        
        Args:
            post_id: Post ID
        
        Returns:
            Post insights
        """
        try:
            self.logger.info(f"Fetching insights for post: {post_id}")
            
            response = self._make_request(
                method="GET",
                endpoint=f"{post_id}/insights",
                params={
                    'metric': 'engagement,impressions,reach,saved'
                }
            )
            
            insights = response.get('data', {})
            self.logger.info("Post insights retrieved successfully")
            return insights
            
        except Exception as e:
            self.logger.error("Failed to get post insights", e)
            raise
    
    def schedule_post(
        self,
        image_path: str,
        caption: str,
        scheduled_time: int
    ) -> str:
        """
        Schedule a post for later publishing
        
        Args:
            image_path: Path to image
            caption: Post caption
            scheduled_time: Unix timestamp for publishing
        
        Returns:
            Scheduled post ID
        """
        try:
            self.logger.info(f"Scheduling post for timestamp: {scheduled_time}")
            
            # Upload image
            media_id = self.upload_image(image_path)
            
            response = self._make_request(
                method="POST",
                endpoint=f"{self.business_account_id}/media",
                json_data={
                    'image_url': image_path,
                    'caption': caption,
                    'media_type': 'IMAGE',
                    'publish_date': scheduled_time,
                    'status': 'SCHEDULED'
                }
            )
            
            post_id = response.get('id')
            if not post_id:
                raise ValueError("Failed to schedule post")
            
            self.logger.info(f"Post scheduled successfully: {post_id}")
            return post_id
            
        except Exception as e:
            self.logger.error("Failed to schedule post", e)
            raise
    
    def validate_access(self) -> bool:
        """
        Validate API access token
        
        Returns:
            True if valid, False otherwise
        """
        try:
            response = self._make_request(
                method="GET",
                endpoint="me",
                params={'fields': 'id,username'}
            )
            
            if response.get('id'):
                self.logger.info("Access token validated successfully")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error("Access token validation failed", e)
            return False
