"""
Video Player Module
Handles video playback functionality using OpenCV
OpenCV is better maintained and has pre-built wheels for all platforms
"""
import os
from pathlib import Path
import logging
import threading

logger = logging.getLogger(__name__)


class VideoPlayer:
    """Manages video playback operations using OpenCV"""
    
    def __init__(self):
        """Initialize the video player"""
        self._current_video = None
        self._is_playing = False
        self._playback_thread = None
        logger.info("VideoPlayer initialized")
    
    def play_video(self, filepath: str, width: int = 1280, height: int = 720):
        """
        Play a video file using OpenCV
        
        Args:
            filepath: Path to video file
            width: Display width (optional, will maintain aspect ratio)
            height: Display height (optional, will maintain aspect ratio)
        
        Returns:
            bool: True if playback started successfully
        """
        try:
            if not os.path.exists(filepath):
                logger.error(f"Video file not found: {filepath}")
                return False
            
            import cv2
            
            # Convert path for cross-platform compatibility
            filepath = str(Path(filepath))
            
            logger.info(f"Playing video: {filepath}")
            
            # Open video file
            cap = cv2.VideoCapture(filepath)
            
            if not cap.isOpened():
                logger.error(f"Failed to open video file: {filepath}")
                return False
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps == 0:
                fps = 30  # Default fallback
            
            frame_delay = int(1000 / fps)  # Delay in milliseconds
            
            # Create window
            window_name = f"Playing: {os.path.basename(filepath)}"
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            
            # Resize window if dimensions provided
            if width and height:
                cv2.resizeWindow(window_name, width, height)
            
            self._current_video = filepath
            self._is_playing = True
            
            # Play video
            while self._is_playing:
                ret, frame = cap.read()
                
                if not ret:
                    # End of video
                    break
                
                # Display frame
                cv2.imshow(window_name, frame)
                
                # Wait for frame delay and check for 'q' key or window close
                key = cv2.waitKey(frame_delay) & 0xFF
                if key == ord('q') or cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                    break
            
            # Clean up
            cap.release()
            cv2.destroyAllWindows()
            
            self._is_playing = False
            logger.info(f"Video playback completed: {filepath}")
            return True
            
        except ImportError:
            logger.error("opencv-python is not installed. Install it with: pip install opencv-python")
            return False
        except Exception as e:
            logger.error(f"Error playing video {filepath}: {e}")
            self._is_playing = False
            return False
    
    def play_video_async(self, filepath: str, width: int = 1280, height: int = 720):
        """
        Play video in a separate thread (non-blocking)
        
        Args:
            filepath: Path to video file
            width: Display width
            height: Display height
        """
        if self._is_playing:
            logger.warning("Video is already playing")
            return False
        
        self._playback_thread = threading.Thread(
            target=self.play_video,
            args=(filepath, width, height),
            daemon=True
        )
        self._playback_thread.start()
        return True
    
    def stop(self):
        """Stop video playback"""
        self._is_playing = False
        logger.info("Video playback stopped")
    
    @property
    def current_video(self):
        """Get the current video filepath"""
        return self._current_video
    
    @property
    def is_playing(self):
        """Check if video is currently playing"""
        return self._is_playing
