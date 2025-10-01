"""
Audio Controller Module
Handles all audio playback functionality
"""
import pygame
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class AudioController:
    """Manages audio playback operations"""
    
    def __init__(self):
        """Initialize the audio controller"""
        try:
            pygame.init()
            pygame.mixer.init()
            self._current_song = None
            self._playlist = []
            self._current_index = -1
            logger.info("AudioController initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AudioController: {e}")
            raise
    
    @property
    def volume(self):
        """Get current volume (0.0 to 1.0)"""
        try:
            return pygame.mixer.music.get_volume()
        except Exception as e:
            logger.error(f"Error getting volume: {e}")
            return 0.5
    
    @volume.setter
    def volume(self, value):
        """Set volume (0.0 to 1.0)"""
        try:
            value = max(0.0, min(1.0, value))  # Clamp between 0 and 1
            pygame.mixer.music.set_volume(value)
            logger.debug(f"Volume set to {value}")
        except Exception as e:
            logger.error(f"Error setting volume: {e}")
    
    def load(self, filepath):
        """Load an audio file"""
        try:
            if not os.path.exists(filepath):
                logger.error(f"File not found: {filepath}")
                return False
            
            # Convert path separators for cross-platform compatibility
            filepath = str(Path(filepath))
            pygame.mixer.music.load(filepath)
            self._current_song = filepath
            logger.info(f"Loaded: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error loading {filepath}: {e}")
            return False
    
    def play(self):
        """Play the loaded audio"""
        try:
            pygame.mixer.music.play()
            logger.info("Playback started")
            return True
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
            return False
    
    def pause(self):
        """Pause the audio playback"""
        try:
            pygame.mixer.music.pause()
            logger.info("Playback paused")
        except Exception as e:
            logger.error(f"Error pausing audio: {e}")
    
    def unpause(self):
        """Resume paused audio"""
        try:
            pygame.mixer.music.unpause()
            logger.info("Playback resumed")
        except Exception as e:
            logger.error(f"Error resuming audio: {e}")
    
    def stop(self):
        """Stop audio playback"""
        try:
            pygame.mixer.music.stop()
            logger.info("Playback stopped")
        except Exception as e:
            logger.error(f"Error stopping audio: {e}")
    
    def is_playing(self):
        """Check if audio is currently playing"""
        try:
            return pygame.mixer.music.get_busy()
        except Exception as e:
            logger.error(f"Error checking play status: {e}")
            return False
    
    def set_playlist(self, playlist):
        """Set the current playlist"""
        self._playlist = list(playlist)
        self._current_index = -1
        logger.info(f"Playlist set with {len(playlist)} items")
    
    def play_next(self):
        """Play the next song in the playlist"""
        if not self._playlist:
            logger.warning("No playlist available")
            return False
        
        self._current_index = (self._current_index + 1) % len(self._playlist)
        next_song = self._playlist[self._current_index]
        
        if self.load(next_song):
            return self.play()
        return False
    
    def play_previous(self):
        """Play the previous song in the playlist"""
        if not self._playlist:
            logger.warning("No playlist available")
            return False
        
        self._current_index = (self._current_index - 1) % len(self._playlist)
        prev_song = self._playlist[self._current_index]
        
        if self.load(prev_song):
            return self.play()
        return False
    
    def play_at_index(self, index):
        """Play song at specific index in playlist"""
        if not self._playlist or index < 0 or index >= len(self._playlist):
            logger.warning(f"Invalid playlist index: {index}")
            return False
        
        self._current_index = index
        song = self._playlist[index]
        
        if self.load(song):
            return self.play()
        return False
    
    @property
    def current_song(self):
        """Get the current song filepath"""
        return self._current_song
    
    @property
    def current_index(self):
        """Get the current song index in playlist"""
        return self._current_index
