"""
Video Player Module
Handles video playback functionality using Qt Multimedia (QMediaPlayer)
Audio and video play together, embedded inside the main window
"""
import os
from pathlib import Path
import logging

from PySide6 import QtCore
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QVideoWidget

logger = logging.getLogger(__name__)


class VideoPlayer(QtCore.QObject):
    """Manages video playback operations using Qt Multimedia"""

    playback_finished = QtCore.Signal()
    error_occurred = QtCore.Signal(str)

    def __init__(self, parent=None):
        """Initialize the video player"""
        super().__init__(parent)

        self.audio_output = QAudioOutput(self)
        self.media_player = QMediaPlayer(self)
        self.media_player.setAudioOutput(self.audio_output)

        # Widget that renders the video - embed this in the UI
        self.video_widget = QVideoWidget()
        self.media_player.setVideoOutput(self.video_widget)

        self._current_video = None

        self.media_player.mediaStatusChanged.connect(self._on_media_status)
        self.media_player.errorOccurred.connect(self._on_error)

        logger.info("VideoPlayer initialized")

    def _on_media_status(self, status):
        """Emit playback_finished when the video ends"""
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.playback_finished.emit()

    def _on_error(self, error, error_string):
        """Log and forward playback errors"""
        logger.error(f"Video playback error: {error_string}")
        self.error_occurred.emit(error_string)

    def play_video(self, filepath: str, width: int = 1280, height: int = 720):
        """
        Play a video file (non-blocking, audio + video)

        Args:
            filepath: Path to video file
            width: Ignored - kept for API compatibility
            height: Ignored - kept for API compatibility

        Returns:
            bool: True if playback started successfully
        """
        try:
            if not os.path.exists(filepath):
                logger.error(f"Video file not found: {filepath}")
                return False

            filepath = str(Path(filepath))
            logger.info(f"Playing video: {filepath}")

            self._current_video = filepath
            self.media_player.setSource(QtCore.QUrl.fromLocalFile(filepath))
            self.media_player.play()
            return True

        except Exception as e:
            logger.error(f"Error playing video {filepath}: {e}")
            return False

    def play_video_async(self, filepath: str, width: int = 1280, height: int = 720):
        """Play video - Qt Multimedia is already non-blocking"""
        return self.play_video(filepath, width, height)

    def pause(self):
        """Pause video playback"""
        self.media_player.pause()

    def resume(self):
        """Resume video playback"""
        self.media_player.play()

    def stop(self):
        """Stop video playback"""
        self.media_player.stop()
        logger.info("Video playback stopped")

    def set_volume(self, value: float):
        """Set volume (0.0 to 1.0)"""
        self.audio_output.setVolume(max(0.0, min(1.0, value)))

    @property
    def current_video(self):
        """Get the current video filepath"""
        return self._current_video

    @property
    def is_playing(self):
        """Check if video is currently playing"""
        return self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState
