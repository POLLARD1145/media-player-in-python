"""
Media Manager Module
Handles file discovery and media library management
"""
import os
import re
from pathlib import Path
from typing import List, Set
import logging

logger = logging.getLogger(__name__)


class MediaManager:
    """Manages media file discovery and organization"""
    
    # Supported media formats
    AUDIO_EXTENSIONS = {'.mp3', '.wav', '.ogg', '.flac', '.aac', '.m4a'}
    VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv'}
    
    def __init__(self):
        """Initialize the media manager"""
        self.current_directory = None
        logger.info("MediaManager initialized")
    
    def get_user_music_folder(self) -> str:
        """Get the user's default music folder"""
        try:
            user = os.getlogin()
            music_folder = Path.home() / "Music"
            
            if music_folder.exists():
                return str(music_folder)
            
            # Fallback
            return str(Path.home())
        except Exception as e:
            logger.error(f"Error getting user music folder: {e}")
            return str(Path.home())
    
    def get_user_video_folder(self) -> str:
        """Get the user's default video folder"""
        try:
            video_folder = Path.home() / "Videos"
            
            if video_folder.exists():
                return str(video_folder)
            
            return str(Path.home())
        except Exception as e:
            logger.error(f"Error getting user video folder: {e}")
            return str(Path.home())
    
    def scan_directory(self, directory: str, media_type: str = 'all') -> List[str]:
        """
        Scan a directory for media files
        
        Args:
            directory: Path to directory to scan
            media_type: 'audio', 'video', or 'all'
        
        Returns:
            List of media file paths
        """
        try:
            if not os.path.exists(directory):
                logger.warning(f"Directory does not exist: {directory}")
                return []
            
            self.current_directory = directory
            media_files = []
            
            # Determine which extensions to look for
            if media_type == 'audio':
                extensions = self.AUDIO_EXTENSIONS
            elif media_type == 'video':
                extensions = self.VIDEO_EXTENSIONS
            else:
                extensions = self.AUDIO_EXTENSIONS | self.VIDEO_EXTENSIONS
            
            # Scan directory
            for file in os.listdir(directory):
                file_path = os.path.join(directory, file)
                
                # Skip directories
                if os.path.isdir(file_path):
                    continue
                
                # Check extension
                _, ext = os.path.splitext(file)
                if ext.lower() in extensions:
                    media_files.append(file)
            
            logger.info(f"Found {len(media_files)} media files in {directory}")
            return sorted(media_files)
            
        except Exception as e:
            logger.error(f"Error scanning directory {directory}: {e}")
            return []
    
    def get_subdirectories(self, directory: str) -> List[str]:
        """Get list of subdirectories in a directory"""
        try:
            if not os.path.exists(directory):
                logger.warning(f"Directory does not exist: {directory}")
                return []
            
            subdirs = []
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isdir(item_path):
                    subdirs.append(item)
            
            return sorted(subdirs)
            
        except PermissionError:
            logger.warning(f"Permission denied accessing: {directory}")
            return []
        except Exception as e:
            logger.error(f"Error getting subdirectories of {directory}: {e}")
            return []
    
    def is_audio_file(self, filename: str) -> bool:
        """Check if a file is an audio file"""
        _, ext = os.path.splitext(filename)
        return ext.lower() in self.AUDIO_EXTENSIONS
    
    def is_video_file(self, filename: str) -> bool:
        """Check if a file is a video file"""
        _, ext = os.path.splitext(filename)
        return ext.lower() in self.VIDEO_EXTENSIONS
    
    def get_file_path(self, filename: str) -> str:
        """Get full path to a file in the current directory"""
        if self.current_directory:
            return os.path.join(self.current_directory, filename)
        return filename
    
    def get_available_drives(self) -> List[str]:
        """Get list of available drives (Windows specific)"""
        try:
            import string
            drives = []
            for letter in string.ascii_uppercase:
                drive = f"{letter}:"
                if os.path.exists(drive):
                    drives.append(drive)
            return drives
        except Exception as e:
            logger.error(f"Error getting available drives: {e}")
            return []
    
    def search_media_files(self, directory: str, query: str, 
                          media_type: str = 'all') -> List[str]:
        """
        Search for media files matching a query
        
        Args:
            directory: Directory to search in
            query: Search query (case-insensitive)
            media_type: 'audio', 'video', or 'all'
        
        Returns:
            List of matching file paths
        """
        try:
            all_files = self.scan_directory(directory, media_type)
            query_lower = query.lower()
            
            matching_files = [
                f for f in all_files 
                if query_lower in f.lower()
            ]
            
            logger.info(f"Found {len(matching_files)} files matching '{query}'")
            return matching_files
            
        except Exception as e:
            logger.error(f"Error searching for media files: {e}")
            return []
