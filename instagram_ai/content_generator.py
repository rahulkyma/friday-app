"""
Content generation using OpenAI API
Generates captions, hashtags, and CTAs for Instagram posts
"""
import json
from typing import Dict, List, Optional
import openai
from instagram_ai.secrets import SecretsManager
from instagram_ai.logger import Logger
from instagram_ai import config

class ContentGenerator:
    """Generate Instagram content using OpenAI"""
    
    def __init__(self):
        """Initialize content generator with OpenAI client"""
        self.logger = Logger.get_logger(__name__)
        self.api_key = SecretsManager.get_openai_api_key()
        self.model = SecretsManager.get_openai_model()
        openai.api_key = self.api_key
    
    def generate_caption(
        self,
        content_type: str = "post",
        niche: Optional[str] = None,
        language: Optional[str] = None,
        tone: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Generate Instagram caption with hashtags and CTA
        
        Args:
            content_type: Type of content (post, carousel, reel, story)
            niche: Content niche (e.g., technology, fitness)
            language: Content language (e.g., hi, en)
            tone: Tone of content (e.g., professional, casual, fun)
        
        Returns:
            Dictionary with caption, hashtags, cta, emojis
        """
        try:
            niche = niche or SecretsManager.get_content_niche()
            language = language or SecretsManager.get_content_language()
            tone = tone or SecretsManager.get_content_tone()
            
            # Build prompt
            prompt = f"""
Create an engaging Instagram {content_type} post in {language} language for {niche} niche.
Tone: {tone}

Requirements:
- Write a captivating main caption (2-3 sentences)
- Create 12-15 relevant hashtags that are popular in {niche}
- Include a clear call-to-action (CTA)
- Add 2-3 relevant emojis that match the content
- Keep tone authentic and engaging
- Make it suitable for {language} speaking audience

IMPORTANT: Respond ONLY with valid JSON in this format:
{{
    "caption": "Your caption here",
    "hashtags": ["#hashtag1", "#hashtag2", ...],
    "cta": "Your call-to-action here",
    "emojis": ["emoji1", "emoji2", "emoji3"]
}}

Do not include any text outside the JSON object.
"""
            
            self.logger.info(f"Generating content for {niche} niche in {language}")
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=config.OPENAI_TEMPERATURE,
                max_tokens=config.OPENAI_MAX_TOKENS,
                timeout=config.API_TIMEOUT
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            result = json.loads(content)
            
            # Validate response structure
            required_keys = ["caption", "hashtags", "cta", "emojis"]
            if not all(key in result for key in required_keys):
                raise ValueError(f"Response missing required keys: {required_keys}")
            
            # Validate caption length
            if len(result["caption"]) > config.MAX_CAPTION_LENGTH:
                self.logger.warning(f"Caption exceeds max length ({len(result['caption'])}/{config.MAX_CAPTION_LENGTH})")
                result["caption"] = result["caption"][:config.MAX_CAPTION_LENGTH]
            
            self.logger.info("Content generated successfully")
            return result
            
        except json.JSONDecodeError as e:
            self.logger.error("Failed to parse OpenAI response as JSON", e)
            raise ValueError("Invalid JSON response from OpenAI")
        except openai.error.AuthenticationError as e:
            self.logger.error("OpenAI authentication failed", e)
            raise
        except openai.error.RateLimitError as e:
            self.logger.error("OpenAI rate limit exceeded", e)
            raise
        except Exception as e:
            self.logger.error("Failed to generate content", e)
            raise
    
    def generate_comment_reply(
        self,
        comment_text: str,
        post_context: Optional[str] = None,
        language: Optional[str] = None
    ) -> str:
        """
        Generate a safe and engaging reply to a comment
        
        Args:
            comment_text: The comment to reply to
            post_context: Context about the original post
            language: Response language
        
        Returns:
            Generated reply text
        """
        try:
            language = language or SecretsManager.get_content_language()
            
            prompt = f"""
The following comment was received on an Instagram post:
"{comment_text}"

Post context: {post_context or "General social media post"}

Generate a brief, friendly, and engaging reply in {language} language that:
- Thanks the commenter for their engagement
- Provides value or relevant information (if applicable)
- Is authentic and not robotic
- Follows Instagram community guidelines (no spam, no promotional links)
- Is under 1000 characters
- Uses appropriate emojis (1-2)

Respond with ONLY the reply text, nothing else.
"""
            
            self.logger.info(f"Generating comment reply in {language}")
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=config.OPENAI_TEMPERATURE,
                max_tokens=200,
                timeout=config.API_TIMEOUT
            )
            
            reply = response.choices[0].message.content.strip()
            
            if len(reply) > config.COMMENT_REPLY_MAX_LENGTH:
                reply = reply[:config.COMMENT_REPLY_MAX_LENGTH]
            
            self.logger.info("Comment reply generated successfully")
            return reply
            
        except Exception as e:
            self.logger.error("Failed to generate comment reply", e)
            raise
    
    def format_caption_for_posting(
        self,
        caption_data: Dict[str, any]
    ) -> str:
        """
        Format caption data into Instagram-ready string
        
        Args:
            caption_data: Dictionary with caption, hashtags, cta, emojis
        
        Returns:
            Formatted caption string
        """
        try:
            caption = caption_data.get("caption", "")
            hashtags = caption_data.get("hashtags", [])
            cta = caption_data.get("cta", "")
            emojis = caption_data.get("emojis", [])
            
            # Build full caption
            full_caption = f"{caption}\n\n"
            
            if cta:
                full_caption += f"{cta}\n\n"
            
            if emojis:
                full_caption += " ".join(emojis) + "\n"
            
            if hashtags:
                full_caption += "\n" + " ".join(hashtags)
            
            return full_caption.strip()
            
        except Exception as e:
            self.logger.error("Failed to format caption", e)
            raise
