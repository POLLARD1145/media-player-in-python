"""
Video Player Module
Handles video playback functionality
"""
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class VideoPlayer:
    """Manages video playback operations"""
    
    def __init__(self):
        """Initialize the video player"""
        self._current_video = None
        logger.info("VideoPlayer initialized")
    
    def play_video(self, filepath: str, width: int = 1280, height: int = 720):
        """
        Play a video file
        
        Args:
            filepath: Path to video file
            width: Display width
            height: Display height
        """
        try:
            if not os.path.exists(filepath):
                logger.error(f"Video file not found: {filepath}")
                return False
            
            from moviepy.editor import VideoFileClip
            
            # Convert path for cross-platform compatibility
            filepath = str(Path(filepath))
            
            logger.info(f"Playing video: {filepath}")
            
            # Create video clip with optimized settings
            video = VideoFileClip(
                filepath,
                audio=True,
                target_resolution=(height, width)
            )
            
            # Resize if needed
            if video.size != (width, height):
                video = video.resize(height=height)
            
            # Play video
            video.preview()
            
            # Clean up
            video.close()
            
            self._current_video = filepath
            logger.info(f"Video playback completed: {filepath}")
            return True
            
        except ImportError:
            logger.error("moviepy is not installed. Install it with: pip install moviepy")
            return False
        except Exception as e:
            logger.error(f"Error playing video {filepath}: {e}")
            return False
    
    @property
    def current_video(self):
        """Get the current video filepath"""
        return self._current_video
