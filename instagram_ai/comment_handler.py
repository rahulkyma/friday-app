"""
Comment handling and safety filtering
Detects, filters, and replies to comments safely
"""
import re
from typing import List, Dict, Optional
from instagram_ai.logger import Logger
from instagram_ai.content_generator import ContentGenerator
from instagram_ai.instagram_api import InstagramAPI
from instagram_ai import config

class CommentHandler:
    """Handle Instagram comments with safety filtering"""
    
    def __init__(self):
        """Initialize comment handler"""
        self.logger = Logger.get_logger(__name__)
        self.content_generator = ContentGenerator()
        self.instagram_api = InstagramAPI()
        self.spam_keywords = config.SPAM_KEYWORDS
    
    def is_spam(self, comment_text: str) -> bool:
        """
        Check if comment is spam
        
        Args:
            comment_text: Comment text to check
        
        Returns:
            True if spam, False otherwise
        """
        try:
            text_lower = comment_text.lower().strip()
            
            # Check minimum length
            if len(text_lower) < config.MIN_COMMENT_LENGTH:
                self.logger.debug(f"Comment too short: {len(text_lower)} chars")
                return True
            
            # Check for spam keywords
            for keyword in self.spam_keywords:
                if keyword.lower() in text_lower:
                    self.logger.debug(f"Spam keyword found: {keyword}")
                    return True
            
            # Check for excessive URLs
            url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            urls = re.findall(url_pattern, text_lower)
            if len(urls) > 2:
                self.logger.debug("Too many URLs in comment")
                return True
            
            # Check for repetitive characters (indicates spam)
            if self._has_excessive_repetition(text_lower):
                self.logger.debug("Excessive character repetition detected")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error("Error checking spam", e)
            return True  # Default to spam on error
    
    def _has_excessive_repetition(self, text: str, threshold: int = 3) -> bool:
        """
        Check for excessive character repetition
        
        Args:
            text: Text to check
            threshold: Max repetitions allowed
        
        Returns:
            True if excessive repetition found
        """
        for char in set(text):
            if char.isalpha() or char.isdigit():
                pattern = char * threshold
                if pattern in text:
                    return True
        return False
    
    def is_safe_response(self, comment_text: str) -> bool:
        """
        Determine if comment deserves a response
        
        Args:
            comment_text: Comment text
        
        Returns:
            True if safe to respond, False otherwise
        """
        try:
            # Don't respond to spam
            if self.is_spam(comment_text):
                self.logger.debug("Not responding to spam comment")
                return False
            
            # Check for negative indicators
            negative_keywords = [
                'hate', 'bad', 'worst', 'terrible', 'awful',
                'delete', 'remove', 'block', 'report', 'fake'
            ]
            
            text_lower = comment_text.lower()
            negative_count = sum(1 for keyword in negative_keywords if keyword in text_lower)
            
            if negative_count >= 2:
                self.logger.debug("Comment contains too many negative keywords")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error("Error checking if response is safe", e)
            return False
    
    def filter_comments(self, comments: List[Dict]) -> List[Dict]:
        """
        Filter comments to find ones worth responding to
        
        Args:
            comments: List of comment objects from API
        
        Returns:
            Filtered list of safe comments
        """
        try:
            filtered = []
            
            for comment in comments:
                comment_text = comment.get('text', '')
                comment_id = comment.get('id', '')
                
                if self.is_safe_response(comment_text):
                    filtered.append(comment)
                    self.logger.debug(f"Comment approved for response: {comment_id}")
                else:
                    self.logger.debug(f"Comment filtered out: {comment_id}")
            
            self.logger.info(f"Filtered {len(comments)} comments to {len(filtered)} safe responses")
            return filtered
            
        except Exception as e:
            self.logger.error("Error filtering comments", e)
            return []
    
    def generate_safe_reply(
        self,
        comment_text: str,
        post_context: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate a safe reply to a comment
        
        Args:
            comment_text: Comment text to reply to
            post_context: Context about the post
        
        Returns:
            Generated reply or None if not safe
        """
        try:
            # Check if safe to respond
            if not self.is_safe_response(comment_text):
                self.logger.warning("Cannot generate reply for unsafe comment")
                return None
            
            # Generate reply using content generator
            reply = self.content_generator.generate_comment_reply(
                comment_text=comment_text,
                post_context=post_context
            )
            
            # Final safety check on reply
            if not reply or len(reply) < 5:
                self.logger.warning("Generated reply is too short")
                return None
            
            self.logger.info("Safe reply generated successfully")
            return reply
            
        except Exception as e:
            self.logger.error("Error generating safe reply", e)
            return None
    
    def process_post_comments(
        self,
        post_id: str,
        post_context: Optional[str] = None,
        max_comments: Optional[int] = None
    ) -> Dict:
        """
        Process all comments on a post and reply to safe ones
        
        Args:
            post_id: Instagram post ID
            post_context: Context about the post
            max_comments: Max comments to process (default from config)
        
        Returns:
            Summary of processed comments
        """
        try:
            max_comments = max_comments or config.MAX_COMMENTS_PER_RUN
            
            self.logger.info(f"Processing comments for post: {post_id}")
            
            # Get recent comments
            comments = self.instagram_api.get_recent_comments(post_id, limit=max_comments)
            self.logger.info(f"Retrieved {len(comments)} comments")
            
            # Filter safe comments
            safe_comments = self.filter_comments(comments)
            self.logger.info(f"Found {len(safe_comments)} safe comments to respond to")
            
            # Process each comment
            results = {
                'total_comments': len(comments),
                'safe_comments': len(safe_comments),
                'successful_replies': 0,
                'failed_replies': 0,
                'replies': []
            }
            
            for comment in safe_comments[:config.MAX_COMMENTS_PER_RUN]:
                try:
                    comment_id = comment.get('id', '')
                    comment_text = comment.get('text', '')
                    
                    # Generate reply
                    reply_text = self.generate_safe_reply(comment_text, post_context)
                    
                    if not reply_text:
                        results['failed_replies'] += 1
                        continue
                    
                    # Send reply
                    reply_id = self.instagram_api.reply_to_comment(comment_id, reply_text)
                    
                    results['successful_replies'] += 1
                    results['replies'].append({
                        'comment_id': comment_id,
                        'reply_id': reply_id,
                        'reply_text': reply_text
                    })
                    
                    self.logger.info(f"Reply sent to comment {comment_id}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to reply to comment {comment.get('id')}", e)
                    results['failed_replies'] += 1
            
            self.logger.info(f"Processed comments: {results}")
            return results
            
        except Exception as e:
            self.logger.error("Error processing post comments", e)
            raise
    
    def get_comment_sentiment(self, comment_text: str) -> str:
        """
        Estimate sentiment of comment (positive, neutral, negative)
        
        Args:
            comment_text: Comment text
        
        Returns:
            Sentiment label
        """
        try:
            text_lower = comment_text.lower()
            
            positive_keywords = [
                'love', 'amazing', 'awesome', 'great', 'excellent',
                'wonderful', 'fantastic', 'perfect', 'best', 'good',
                'like', 'nice', 'beautiful', 'cool', 'awesome'
            ]
            
            negative_keywords = [
                'hate', 'bad', 'worst', 'terrible', 'awful',
                'horrible', 'poor', 'disappointing', 'dislike'
            ]
            
            positive_count = sum(1 for keyword in positive_keywords if keyword in text_lower)
            negative_count = sum(1 for keyword in negative_keywords if keyword in text_lower)
            
            if positive_count > negative_count:
                return "positive"
            elif negative_count > positive_count:
                return "negative"
            else:
                return "neutral"
                
        except Exception as e:
            self.logger.error("Error analyzing sentiment", e)
            return "neutral"
