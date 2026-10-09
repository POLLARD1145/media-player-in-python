"""
Video Player Module
Handles video playback functionality using Qt Multimedia (QMediaPlayer)
Audio and video play together, embedded inside the main window
"""
import os
import re
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

    def subtitle_tracks(self):
        """Get embedded subtitle tracks as a list of dicts"""
        try:
            return self.media_player.subtitleTracks()
        except Exception as e:
            logger.error(f"Error getting subtitle tracks: {e}")
            return []

    def set_subtitle_track(self, index: int):
        """Activate an embedded subtitle track (-1 disables)"""
        try:
            self.media_player.setActiveSubtitleTrack(index)
        except Exception as e:
            logger.error(f"Error setting subtitle track: {e}")

    @property
    def current_video(self):
        """Get the current video filepath"""
        return self._current_video

    @property
    def is_playing(self):
        """Check if video is currently playing"""
        return self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState


def _timestamp_to_ms(ts: str) -> int:
    """Convert 'HH:MM:SS,mmm' or 'HH:MM:SS.mmm' to milliseconds"""
    ts = ts.replace(',', '.')
    h, m, rest = ts.split(':')
    s, ms = rest.split('.')
    return (int(h) * 3600 + int(m) * 60 + int(s)) * 1000 + int(ms)


def parse_subtitles(filepath: str):
    """
    Parse an .srt or .vtt subtitle file.

    Returns:
        List of (start_ms, end_ms, text) tuples, or [] on failure
    """
    try:
        text = Path(filepath).read_text(encoding='utf-8', errors='replace')
        cues = []
        timestamp_re = re.compile(
            r'(\d{2}:\d{2}:\d{2}[,.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,.]\d{3})'
        )
        for block in re.split(r'\n\s*\n', text):
            lines = [l for l in block.strip().splitlines() if l.strip()]
            for i, line in enumerate(lines):
                match = timestamp_re.search(line)
                if match:
                    cue_text = ' '.join(lines[i + 1:])
                    cue_text = re.sub(r'<[^>]+>', '', cue_text).strip()
                    if cue_text:
                        cues.append((
                            _timestamp_to_ms(match.group(1)),
                            _timestamp_to_ms(match.group(2)),
                            cue_text
                        ))
                    break
        cues.sort(key=lambda c: c[0])
        logger.info(f"Parsed {len(cues)} subtitle cues from {filepath}")
        return cues
    except Exception as e:
        logger.error(f"Error parsing subtitle file {filepath}: {e}")
        return []


def find_subtitle_file(video_path: str):
    """Look for a .srt/.vtt file matching the video's filename"""
    stem = Path(video_path).with_suffix('')
    for ext in ('.srt', '.vtt'):
        candidate = str(stem) + ext
        if os.path.exists(candidate):
            return candidate
    return None
