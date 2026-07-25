"""
Image handling and processing for Instagram posts
Handles image validation, resizing, and optimization
"""
import os
from typing import Optional, List
from PIL import Image
import io
from instagram_ai.logger import Logger
from instagram_ai import config

class ImageHandler:
    """Handle image processing and validation"""
    
    def __init__(self):
        """Initialize image handler"""
        self.logger = Logger.get_logger(__name__)
        self.supported_formats = config.SUPPORTED_IMAGE_FORMATS
        self.max_size_mb = config.MAX_IMAGE_SIZE_MB
        self.quality = config.IMAGE_QUALITY
        self.resize_width = config.IMAGE_RESIZE_WIDTH
        self.resize_height = config.IMAGE_RESIZE_HEIGHT
    
    def validate_image(self, image_path: str) -> bool:
        """
        Validate image file
        
        Args:
            image_path: Path to image file
        
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check if file exists
            if not os.path.exists(image_path):
                self.logger.error(f"Image file not found: {image_path}")
                return False
            
            # Check file extension
            file_ext = os.path.splitext(image_path)[1].lower().lstrip('.')
            if file_ext not in self.supported_formats:
                self.logger.error(f"Unsupported image format: {file_ext}")
                return False
            
            # Check file size
            file_size_mb = os.path.getsize(image_path) / (1024 * 1024)
            if file_size_mb > self.max_size_mb:
                self.logger.error(f"Image too large: {file_size_mb}MB (max: {self.max_size_mb}MB)")
                return False
            
            # Try to open image
            with Image.open(image_path) as img:
                img.verify()
            
            self.logger.info(f"Image validated successfully: {image_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Image validation failed: {image_path}", e)
            return False
    
    def resize_image(
        self,
        image_path: str,
        output_path: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None
    ) -> str:
        """
        Resize image to Instagram standard dimensions
        
        Args:
            image_path: Path to input image
            output_path: Path to save resized image (default: overwrites original)
            width: Target width (default: 1080)
            height: Target height (default: 1350)
        
        Returns:
            Path to resized image
        """
        try:
            width = width or self.resize_width
            height = height or self.resize_height
            output_path = output_path or image_path
            
            with Image.open(image_path) as img:
                # Convert RGBA to RGB if needed
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                # Resize with aspect ratio preservation
                img.thumbnail((width, height), Image.Resampling.LANCZOS)
                
                # Create new image with target dimensions and paste resized image
                final_img = Image.new('RGB', (width, height), (255, 255, 255))
                offset = ((width - img.width) // 2, (height - img.height) // 2)
                final_img.paste(img, offset)
                
                # Save optimized image
                final_img.save(output_path, 'JPEG', quality=self.quality, optimize=True)
            
            self.logger.info(f"Image resized and saved: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to resize image: {image_path}", e)
            raise
    
    def optimize_image(self, image_path: str) -> str:
        """
        Optimize image for Instagram (resize + compress)
        
        Args:
            image_path: Path to image
        
        Returns:
            Path to optimized image
        """
        try:
            # Validate first
            if not self.validate_image(image_path):
                raise ValueError(f"Invalid image: {image_path}")
            
            # Resize and optimize
            optimized_path = self.resize_image(image_path)
            
            self.logger.info(f"Image optimized successfully: {optimized_path}")
            return optimized_path
            
        except Exception as e:
            self.logger.error(f"Failed to optimize image", e)
            raise
    
    def get_image_info(self, image_path: str) -> dict:
        """
        Get image information
        
        Args:
            image_path: Path to image
        
        Returns:
            Dictionary with image info
        """
        try:
            with Image.open(image_path) as img:
                file_size_mb = os.path.getsize(image_path) / (1024 * 1024)
                
                return {
                    "path": image_path,
                    "format": img.format,
                    "width": img.width,
                    "height": img.height,
                    "size_mb": round(file_size_mb, 2),
                    "mode": img.mode,
                    "file_size": os.path.getsize(image_path)
                }
        except Exception as e:
            self.logger.error(f"Failed to get image info", e)
            raise
    
    def prepare_carousel_images(
        self,
        image_paths: List[str],
        output_dir: Optional[str] = None
    ) -> List[str]:
        """
        Prepare multiple images for carousel post
        
        Args:
            image_paths: List of image paths
            output_dir: Directory to save optimized images
        
        Returns:
            List of optimized image paths
        """
        try:
            if len(image_paths) < 2 or len(image_paths) > 10:
                raise ValueError("Carousel must have 2-10 images")
            
            optimized_paths = []
            
            for idx, image_path in enumerate(image_paths):
                if not self.validate_image(image_path):
                    raise ValueError(f"Invalid image at index {idx}: {image_path}")
                
                # Create output path if specified
                if output_dir:
                    os.makedirs(output_dir, exist_ok=True)
                    output_path = os.path.join(output_dir, f"carousel_{idx}.jpg")
                else:
                    output_path = None
                
                optimized_path = self.resize_image(image_path, output_path)
                optimized_paths.append(optimized_path)
            
            self.logger.info(f"Prepared {len(optimized_paths)} carousel images")
            return optimized_paths
            
        except Exception as e:
            self.logger.error(f"Failed to prepare carousel images", e)
            raise
