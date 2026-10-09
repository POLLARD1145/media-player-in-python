"""
Pd Music Player - Optimized Version
A modern, modular media player application

Uses PySide6 (official Qt for Python), pygame-ce, and opencv-python
All dependencies are self-contained with pre-built wheels

DEVELOPER: POLLARD SAMBA
GITHUB: POLLARD1145
EMAIL: POLLADSAMBA1@GMAIL.COM
"""
import sys
import os
import json
import logging
from pathlib import Path
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtMultimedia import QMediaPlayer

from audio_controller import AudioController
from media_manager import MediaManager
from video_player import VideoPlayer, parse_subtitles, find_subtitle_file

# Configure logging - write to home dir because a .app launched from
# Finder has '/' as its working directory, which isn't writable
_log_handlers = [logging.StreamHandler()]
try:
    _log_handlers.append(logging.FileHandler(Path.home() / 'pd_player.log'))
except OSError:
    pass
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=_log_handlers
)
logger = logging.getLogger(__name__)

APP_VERSION = "1.0.0"
RECENT_FILE = Path.home() / ".pd_player_recent.json"
MAX_RECENT = 15


class SeekSlider(QtWidgets.QSlider):
    """Slider that seeks to wherever the user clicks, not just on drags"""
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            ratio = event.position().x() / max(1, self.width())
            self.setValue(int(self.minimum() + ratio * (self.maximum() - self.minimum())))
            self.sliderMoved.emit(self.value())
        super().mousePressEvent(event)


class MediaPlayerUI(QtWidgets.QMainWindow):
    """Main window for the media player application"""
    
    def __init__(self):
        """Initialize the media player UI"""
        super().__init__()
        
        # Initialize controllers
        self.audio_controller = AudioController()
        self.media_manager = MediaManager()
        self.video_player = VideoPlayer()
        
        # State variables
        self.current_playlist = []
        self.is_playing = False
        self.is_video_mode = False
        # Repeat modes: 0 = off, 1 = repeat all, 2 = repeat one
        self.repeat_mode = 0
        self._audio_was_playing = False
        self.recent_media = self._load_recent()
        # Subtitle state: 'off', 'external', or 'embedded'
        self._sub_mode = "off"
        self._external_subs = []
        self._external_subs_name = ""
        
        # Setup UI
        self.setup_ui()
        self.apply_modern_stylesheet()
        
        # Poll for audio track end - pygame has no end-of-track signal
        self._end_check_timer = QtCore.QTimer(self)
        self._end_check_timer.setInterval(500)
        self._end_check_timer.timeout.connect(self._check_track_end)
        self._end_check_timer.start()
        
        # Wire up video player signals
        self.video_player.playback_finished.connect(self._on_video_finished)
        self.video_player.error_occurred.connect(
            lambda msg: self.statusbar.showMessage(f"Video error: {msg}")
        )
        self.video_player.media_player.positionChanged.connect(self._on_video_position)
        self.video_player.media_player.durationChanged.connect(self._on_video_duration)
        self.progress_slider.sliderMoved.connect(self._on_seek)
        
        # Load initial playlist
        self.load_default_library()
        
        logger.info("MediaPlayerUI initialized successfully")
    
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("Pd Music Player")
        self.setObjectName("MainWindow")
        
        # Get screen dimensions
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        screen_width = screen.width()
        screen_height = screen.height()
        
        # Set window size (80% of screen)
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        self.resize(window_width, window_height)
        
        # Center window on screen
        self.center_on_screen()
        
        # Create central widget
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main layout
        main_layout = QtWidgets.QHBoxLayout(self.central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Left panel (navigation and visualization)
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, stretch=1)
        
        # Right panel (playlist and controls)
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, stretch=3)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.statusbar = QtWidgets.QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Ready")
    
    def center_on_screen(self):
        """Center the window on the screen"""
        frame_geometry = self.frameGeometry()
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        center_point = screen.center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())
    
    def create_left_panel(self):
        """Create the left navigation panel"""
        panel = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(panel)
        layout.setSpacing(10)
        
        # Navigation label
        nav_label = QtWidgets.QLabel("LIBRARY")
        nav_label.setObjectName("SectionLabel")
        nav_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(nav_label)
        
        # Navigation list
        self.nav_list = QtWidgets.QListWidget()
        self.nav_list.setObjectName("NavigationList")
        self.nav_list.addItems([
            "Current Playlist",
            "Music Library",
            "Video Library",
            "Browse Folders"
        ])
        self.nav_list.itemDoubleClicked.connect(self.on_nav_item_clicked)
        layout.addWidget(self.nav_list)
        
        # Folder tree
        folder_label = QtWidgets.QLabel("FOLDERS")
        folder_label.setObjectName("SectionLabel")
        folder_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(folder_label)
        
        self.folder_tree = QtWidgets.QListWidget()
        self.folder_tree.setObjectName("FolderTree")
        self.folder_tree.itemDoubleClicked.connect(self.on_folder_clicked)
        layout.addWidget(self.folder_tree)
        
        # Visualization placeholder
        self.visualization = QtWidgets.QLabel("♫")
        self.visualization.setObjectName("Visualization")
        self.visualization.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.visualization.setMinimumHeight(200)
        layout.addWidget(self.visualization)
        
        return panel
    
    def create_right_panel(self):
        """Create the right panel with playlist and controls"""
        panel = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(panel)
        layout.setSpacing(10)
        
        # Search bar
        search_layout = QtWidgets.QHBoxLayout()
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText("Search media...")
        self.search_input.setObjectName("SearchInput")
        self.search_input.returnPressed.connect(self.on_search)
        
        search_button = QtWidgets.QPushButton("Search")
        search_button.setObjectName("SearchButton")
        search_button.clicked.connect(self.on_search)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        layout.addLayout(search_layout)
        
        # Playlist label
        playlist_label = QtWidgets.QLabel("PLAYLIST")
        playlist_label.setObjectName("SectionLabel")
        layout.addWidget(playlist_label)
        
        # Playlist view
        self.playlist_view = QtWidgets.QListWidget()
        self.playlist_view.setObjectName("PlaylistView")
        self.playlist_view.itemClicked.connect(self.on_song_clicked)
        self.playlist_view.itemDoubleClicked.connect(self.on_song_double_clicked)

        # Stacked widget: page 0 = playlist, page 1 = embedded video
        self.content_stack = QtWidgets.QStackedWidget()
        self.content_stack.addWidget(self.playlist_view)

        video_page = QtWidgets.QWidget()
        video_layout = QtWidgets.QVBoxLayout(video_page)
        video_layout.setContentsMargins(0, 0, 0, 0)
        video_layout.setSpacing(5)
        self.video_player.video_widget.setMinimumHeight(300)
        video_layout.addWidget(self.video_player.video_widget)
        
        # Double-click video to toggle fullscreen, Esc to exit
        self.video_player.video_widget.setMouseTracking(True)
        self.video_player.video_widget.installEventFilter(self)
        QtGui.QShortcut(
            QtGui.QKeySequence(QtCore.Qt.Key.Key_Escape),
            self.video_player.video_widget,
            activated=lambda: self.video_player.video_widget.setFullScreen(False)
        )
        QtGui.QShortcut(
            QtGui.QKeySequence("F"),
            self,
            activated=self._maybe_fullscreen
        )
        
        video_buttons = QtWidgets.QHBoxLayout()
        self.btn_back_to_playlist = QtWidgets.QPushButton("← Back to Playlist")
        self.btn_back_to_playlist.setObjectName("SearchButton")
        self.btn_back_to_playlist.clicked.connect(self.show_playlist)
        video_buttons.addWidget(self.btn_back_to_playlist)
        
        self.btn_fullscreen = QtWidgets.QPushButton("⛶ Fullscreen")
        self.btn_fullscreen.setObjectName("SearchButton")
        self.btn_fullscreen.clicked.connect(self.toggle_fullscreen)
        video_buttons.addWidget(self.btn_fullscreen)
        video_layout.addLayout(video_buttons)

        self.content_stack.addWidget(video_page)
        
        # Floating control bar shown on hover in fullscreen mode
        self._build_fullscreen_bar()
        layout.addWidget(self.content_stack)
        
        # Now playing info
        self.now_playing_label = QtWidgets.QLabel("No media loaded")
        self.now_playing_label.setObjectName("NowPlayingLabel")
        self.now_playing_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.now_playing_label)
        
        # Progress bar
        progress_layout = QtWidgets.QHBoxLayout()
        
        self.time_start = QtWidgets.QLabel("00:00")
        self.time_start.setObjectName("TimeLabel")
        progress_layout.addWidget(self.time_start)
        
        self.progress_slider = SeekSlider(QtCore.Qt.Orientation.Horizontal)
        self.progress_slider.setObjectName("ProgressSlider")
        progress_layout.addWidget(self.progress_slider, stretch=1)
        
        self.time_end = QtWidgets.QLabel("00:00")
        self.time_end.setObjectName("TimeLabel")
        progress_layout.addWidget(self.time_end)
        
        layout.addLayout(progress_layout)
        
        # Control buttons
        controls_layout = self.create_controls()
        layout.addLayout(controls_layout)
        
        return panel
    
    def create_controls(self):
        """Create playback control buttons"""
        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(10)
        
        # Previous button
        self.btn_previous = QtWidgets.QPushButton("⏮")
        self.btn_previous.setObjectName("ControlButton")
        self.btn_previous.setToolTip("Previous")
        self.btn_previous.clicked.connect(self.on_previous)
        layout.addWidget(self.btn_previous)
        
        # Play/Pause button
        self.btn_play = QtWidgets.QPushButton("▶")
        self.btn_play.setObjectName("PlayButton")
        self.btn_play.setToolTip("Play")
        self.btn_play.clicked.connect(self.on_play_pause)
        layout.addWidget(self.btn_play)
        
        # Stop button
        self.btn_stop = QtWidgets.QPushButton("⏹")
        self.btn_stop.setObjectName("ControlButton")
        self.btn_stop.setToolTip("Stop")
        self.btn_stop.clicked.connect(self.on_stop)
        layout.addWidget(self.btn_stop)
        
        # Next button
        self.btn_next = QtWidgets.QPushButton("⏭")
        self.btn_next.setObjectName("ControlButton")
        self.btn_next.setToolTip("Next")
        self.btn_next.clicked.connect(self.on_next)
        layout.addWidget(self.btn_next)
        
        # Repeat mode button (cycles: Off -> All -> One)
        self.btn_repeat = QtWidgets.QPushButton("Repeat: Off")
        self.btn_repeat.setObjectName("ControlButton")
        self.btn_repeat.setToolTip("Cycle repeat mode: Off / All / One")
        self.btn_repeat.clicked.connect(self.on_repeat_cycle)
        layout.addWidget(self.btn_repeat)
        
        # Spacer
        layout.addStretch()
        
        # Volume control
        volume_label = QtWidgets.QLabel("🔊")
        volume_label.setObjectName("VolumeIcon")
        layout.addWidget(volume_label)
        
        self.volume_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.volume_slider.setObjectName("VolumeSlider")
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(int(self.audio_controller.volume * 100))
        self.volume_slider.setMaximumWidth(150)
        self.volume_slider.valueChanged.connect(self.on_volume_change)
        layout.addWidget(self.volume_slider)
        
        self.volume_label = QtWidgets.QLabel(f"{int(self.audio_controller.volume * 100)}%")
        self.volume_label.setObjectName("VolumeLabel")
        self.volume_label.setMinimumWidth(40)
        layout.addWidget(self.volume_label)
        
        return layout
    
    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()
        
        # Media menu
        media_menu = menubar.addMenu("Media")
        
        load_action = QtGui.QAction("Load Playlist", self)
        load_action.triggered.connect(self.on_load_playlist)
        media_menu.addAction(load_action)
        
        # Recent media submenu - rebuilt each time it opens
        self.recent_menu = media_menu.addMenu("Recent Media")
        self.recent_menu.aboutToShow.connect(self._populate_recent_menu)
        
        media_menu.addSeparator()
        
        exit_action = QtGui.QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        media_menu.addAction(exit_action)
        
        # Playback menu
        playback_menu = menubar.addMenu("Playback")
        
        # Subtitles submenu - rebuilt each time it opens
        self.sub_menu = playback_menu.addMenu("Subtitles")
        self.sub_menu.aboutToShow.connect(self._populate_sub_menu)
        playback_menu.addSeparator()
        
        play_action = QtGui.QAction("Play", self)
        play_action.setShortcut("Space")
        play_action.triggered.connect(self.on_play_pause)
        playback_menu.addAction(play_action)
        
        stop_action = QtGui.QAction("Stop", self)
        stop_action.setShortcut("S")
        stop_action.triggered.connect(self.on_stop)
        playback_menu.addAction(stop_action)
        
        playback_menu.addSeparator()
        
        repeat_action = QtGui.QAction("Repeat Mode", self)
        repeat_action.setShortcut("R")
        repeat_action.triggered.connect(self.on_repeat_cycle)
        playback_menu.addAction(repeat_action)
        
        playback_menu.addSeparator()
        
        forward_action = QtGui.QAction("Forward 10s", self)
        forward_action.setShortcut("Right")
        forward_action.triggered.connect(lambda: self._seek_relative(10000))
        playback_menu.addAction(forward_action)
        
        backward_action = QtGui.QAction("Backward 10s", self)
        backward_action.setShortcut("Left")
        backward_action.triggered.connect(lambda: self._seek_relative(-10000))
        playback_menu.addAction(backward_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QtGui.QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def apply_modern_stylesheet(self):
        """Apply modern dark theme stylesheet"""
        stylesheet = """
            QMainWindow {
                background-color: #1e1e1e;
            }
            
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 10pt;
            }
            
            QLabel#SectionLabel {
                font-size: 12pt;
                font-weight: bold;
                color: #4fc3f7;
                padding: 5px;
                background-color: #2d2d2d;
                border-radius: 5px;
            }
            
            QLabel#NowPlayingLabel {
                font-size: 11pt;
                color: #4fc3f7;
                padding: 10px;
                background-color: #2d2d2d;
                border-radius: 5px;
            }
            
            QLabel#TimeLabel, QLabel#VolumeLabel {
                color: #b0b0b0;
                font-size: 9pt;
            }
            
            QLabel#VolumeIcon {
                font-size: 14pt;
            }
            
            QLabel#Visualization {
                font-size: 48pt;
                color: #4fc3f7;
                background-color: #2d2d2d;
                border-radius: 10px;
            }
            
            QListWidget {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 5px;
            }
            
            QListWidget::item {
                padding: 8px;
                border-radius: 3px;
            }
            
            QListWidget::item:hover {
                background-color: #3d3d3d;
            }
            
            QListWidget::item:selected {
                background-color: #4fc3f7;
                color: #000000;
            }
            
            QLineEdit {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 8px;
                color: #ffffff;
            }
            
            QLineEdit:focus {
                border: 1px solid #4fc3f7;
            }
            
            QPushButton {
                background-color: #3d3d3d;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                color: #ffffff;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #4d4d4d;
            }
            
            QPushButton:pressed {
                background-color: #2d2d2d;
            }
            
            QPushButton#PlayButton {
                background-color: #4fc3f7;
                color: #000000;
                font-size: 14pt;
                min-width: 60px;
            }
            
            QPushButton#PlayButton:hover {
                background-color: #6fd8ff;
            }
            
            QPushButton#ControlButton {
                font-size: 12pt;
                min-width: 50px;
            }
            
            QPushButton#SearchButton {
                background-color: #4fc3f7;
                color: #000000;
            }
            
            QPushButton#SearchButton:hover {
                background-color: #6fd8ff;
            }
            
            QSlider::groove:horizontal {
                border: 1px solid #3d3d3d;
                height: 6px;
                background: #2d2d2d;
                border-radius: 3px;
            }
            
            QSlider::handle:horizontal {
                background: #4fc3f7;
                border: none;
                width: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }
            
            QSlider::handle:horizontal:hover {
                background: #6fd8ff;
            }
            
            QSlider#VolumeSlider::groove:horizontal {
                height: 4px;
            }
            
            QSlider#VolumeSlider::handle:horizontal {
                width: 12px;
                margin: -4px 0;
            }
            
            QMenuBar {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 2px;
            }
            
            QMenuBar::item:selected {
                background-color: #3d3d3d;
            }
            
            QMenu {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                color: #ffffff;
            }
            
            QMenu::item:selected {
                background-color: #4fc3f7;
                color: #000000;
            }
            
            QStatusBar {
                background-color: #2d2d2d;
                color: #b0b0b0;
            }
        """
        self.setStyleSheet(stylesheet)
    
    def load_default_library(self):
        """Load default music library"""
        try:
            music_folder = self.media_manager.get_user_music_folder()
            self.current_playlist = self.media_manager.scan_directory(music_folder, 'audio')
            self.update_playlist_view()
            self.statusbar.showMessage(f"Loaded {len(self.current_playlist)} songs from Music folder")
            logger.info(f"Loaded default library: {len(self.current_playlist)} songs")
        except Exception as e:
            logger.error(f"Error loading default library: {e}")
            self.statusbar.showMessage("Error loading default library")
    
    def update_playlist_view(self):
        """Update the playlist view with current playlist"""
        self.playlist_view.clear()
        self.playlist_view.addItems(self.current_playlist)
    
    # Event Handlers
    
    def on_nav_item_clicked(self, item):
        """Handle navigation item click"""
        text = item.text()
        
        try:
            if text == "Current Playlist":
                self.update_playlist_view()
                self.statusbar.showMessage("Showing current playlist")
                
            elif text == "Music Library":
                music_folder = self.media_manager.get_user_music_folder()
                self.current_playlist = self.media_manager.scan_directory(music_folder, 'audio')
                self.update_playlist_view()
                self.statusbar.showMessage(f"Loaded music library: {len(self.current_playlist)} songs")
                self._add_recent(music_folder, "dir")
                
            elif text == "Video Library":
                video_folder = self.media_manager.get_user_video_folder()
                self.current_playlist = self.media_manager.scan_directory(video_folder, 'video')
                self.update_playlist_view()
                self.statusbar.showMessage(f"Loaded video library: {len(self.current_playlist)} videos")
                self._add_recent(video_folder, "dir")
                
            elif text == "Browse Folders":
                self.on_load_playlist()
                
        except Exception as e:
            logger.error(f"Error handling navigation: {e}")
            self.statusbar.showMessage("Error loading library")
    
    def on_folder_clicked(self, item):
        """Handle folder item click"""
        folder_name = item.text()
        
        try:
            current_dir = self.media_manager.current_directory or self.media_manager.get_user_music_folder()
            new_path = os.path.join(current_dir, folder_name)
            
            if os.path.exists(new_path) and os.path.isdir(new_path):
                self.current_playlist = self.media_manager.scan_directory(new_path)
                self.update_playlist_view()
                self.update_folder_tree(new_path)
                self.statusbar.showMessage(f"Browsing: {new_path}")
                self._add_recent(new_path, "dir")
                
        except Exception as e:
            logger.error(f"Error browsing folder: {e}")
            self.statusbar.showMessage("Error browsing folder")
    
    def update_folder_tree(self, directory):
        """Update folder tree with subdirectories"""
        try:
            subdirs = self.media_manager.get_subdirectories(directory)
            self.folder_tree.clear()
            self.folder_tree.addItems(subdirs)
        except Exception as e:
            logger.error(f"Error updating folder tree: {e}")
    
    def on_song_clicked(self, item):
        """Handle song single click (load song)"""
        song_name = item.text()
        
        try:
            song_path = self.media_manager.get_file_path(song_name)
            
            if self.media_manager.is_audio_file(song_name):
                if self.audio_controller.load(song_path):
                    self.now_playing_label.setText(f"Loaded: {song_name}")
                    self.statusbar.showMessage(f"Loaded: {song_name}")
                    self.btn_play.setText("▶")
                    self.is_playing = False
                    
        except Exception as e:
            logger.error(f"Error loading song: {e}")
            self.statusbar.showMessage("Error loading media file")
    
    def on_song_double_clicked(self, item):
        """Handle song double click (play immediately)"""
        song_name = item.text()
        
        try:
            song_path = self.media_manager.get_file_path(song_name)
            
            if self.media_manager.is_audio_file(song_name):
                if self.is_video_mode:
                    self.video_player.stop()
                    self.show_playlist()
                if self.audio_controller.load(song_path):
                    if self.audio_controller.play():
                        self.now_playing_label.setText(f"Now Playing: {song_name}")
                        self.statusbar.showMessage(f"Playing: {song_name}")
                        self.btn_play.setText("⏸")
                        self.is_playing = True
                        self._add_recent(song_path, "file")
                        
            elif self.media_manager.is_video_file(song_name):
                self.audio_controller.stop()
                self._prepare_subtitles(song_path)
                if self.video_player.play_video(song_path):
                    self.now_playing_label.setText(f"Playing video: {song_name}")
                    self.statusbar.showMessage(f"Playing video: {song_name}")
                    self.content_stack.setCurrentIndex(1)
                    self.is_video_mode = True
                    self.is_playing = True
                    self.btn_play.setText("⏸")
                    self._add_recent(song_path, "file")
                
        except Exception as e:
            logger.error(f"Error playing media: {e}")
            self.statusbar.showMessage("Error playing media file")
    
    def on_play_pause(self):
        """Handle play/pause button click"""
        try:
            if self.is_video_mode:
                if self.is_playing:
                    self.video_player.pause()
                    self.btn_play.setText("▶")
                    self.is_playing = False
                    self.statusbar.showMessage("Paused")
                else:
                    self.video_player.resume()
                    self.btn_play.setText("⏸")
                    self.is_playing = True
                    self.statusbar.showMessage("Playing")
                return

            if not self.is_playing:
                # Play
                if self.audio_controller.play():
                    self.btn_play.setText("⏸")
                    self.is_playing = True
                    self.statusbar.showMessage("Playing")
            else:
                # Pause
                self.audio_controller.pause()
                self.btn_play.setText("▶")
                self.is_playing = False
                self.statusbar.showMessage("Paused")
                
        except Exception as e:
            logger.error(f"Error in play/pause: {e}")
    
    def on_stop(self):
        """Handle stop button click"""
        try:
            if self.is_video_mode:
                self.video_player.stop()
                self.subtitle_label.hide()
            else:
                self.audio_controller.stop()
            self.btn_play.setText("▶")
            self.is_playing = False
            self.statusbar.showMessage("Stopped")
        except Exception as e:
            logger.error(f"Error stopping playback: {e}")
    
    def show_playlist(self):
        """Switch back from video view to playlist view"""
        self.content_stack.setCurrentIndex(0)
        # Only exit video mode if the video actually stopped - if it's still
        # playing in the background the controls must keep controlling it
        stopped = self.video_player.media_player.playbackState() == QMediaPlayer.PlaybackState.StoppedState
        self.is_video_mode = not stopped
        if stopped:
            self.subtitle_label.hide()
            self.progress_slider.setValue(0)
            self.time_start.setText("00:00")
            self.time_end.setText("00:00")
    
    def _on_video_position(self, position_ms):
        """Update progress sliders as the video plays"""
        if not self.progress_slider.isSliderDown():
            self.progress_slider.setValue(position_ms)
        if not self.fs_slider.isSliderDown():
            self.fs_slider.setValue(position_ms)
        formatted = self._format_time(position_ms)
        self.time_start.setText(formatted)
        self.fs_time_start.setText(formatted)
        self.fs_btn_play.setText("⏸" if self.is_playing else "▶")
        self._update_subtitle_display(position_ms)
        # Some files report duration late - keep refreshing it
        duration = self.video_player.media_player.duration()
        if duration > 0 and self.progress_slider.maximum() != duration:
            self.progress_slider.setRange(0, duration)
            self.fs_slider.setRange(0, duration)
            formatted_end = self._format_time(duration)
            self.time_end.setText(formatted_end)
            self.fs_time_end.setText(formatted_end)
    
    def _on_video_duration(self, duration_ms):
        """Set slider range when the video duration is known"""
        duration_ms = max(0, duration_ms)
        self.progress_slider.setRange(0, duration_ms)
        self.fs_slider.setRange(0, duration_ms)
        formatted = self._format_time(duration_ms)
        self.time_end.setText(formatted)
        self.fs_time_end.setText(formatted)
    
    def _build_fullscreen_bar(self):
        """Create the floating controls overlay used in fullscreen mode"""
        video_widget = self.video_player.video_widget
        
        # Separate borderless window - child widgets get hidden behind
        # the video widget's native render surface
        self.fs_bar = QtWidgets.QWidget(
            None,
            QtCore.Qt.WindowType.ToolTip | QtCore.Qt.WindowType.FramelessWindowHint
        )
        self.fs_bar.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.fs_bar.setAttribute(QtCore.Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.fs_bar.setStyleSheet(
            "QWidget { background-color: rgba(0, 0, 0, 160); border-radius: 8px; }"
        )
        fs_layout = QtWidgets.QHBoxLayout(self.fs_bar)
        fs_layout.setContentsMargins(12, 6, 12, 6)
        fs_layout.setSpacing(8)
        
        self.fs_btn_play = QtWidgets.QPushButton("⏸")
        self.fs_btn_play.setObjectName("PlayButton")
        self.fs_btn_play.clicked.connect(self.on_play_pause)
        fs_layout.addWidget(self.fs_btn_play)
        
        fs_stop = QtWidgets.QPushButton("⏹")
        fs_stop.setObjectName("ControlButton")
        fs_stop.clicked.connect(self.on_stop)
        fs_layout.addWidget(fs_stop)
        
        self.fs_time_start = QtWidgets.QLabel("00:00")
        fs_layout.addWidget(self.fs_time_start)
        
        self.fs_slider = SeekSlider(QtCore.Qt.Orientation.Horizontal)
        self.fs_slider.sliderMoved.connect(self._on_seek)
        fs_layout.addWidget(self.fs_slider, stretch=1)
        
        self.fs_time_end = QtWidgets.QLabel("00:00")
        fs_layout.addWidget(self.fs_time_end)
        
        fs_exit = QtWidgets.QPushButton("⛶")
        fs_exit.setObjectName("ControlButton")
        fs_exit.setToolTip("Exit Fullscreen")
        fs_exit.clicked.connect(lambda: video_widget.setFullScreen(False))
        fs_layout.addWidget(fs_exit)
        
        # Manual hide button on the bar
        fs_hide = QtWidgets.QPushButton("⌄")
        fs_hide.setObjectName("ControlButton")
        fs_hide.setToolTip("Hide Controls")
        fs_hide.clicked.connect(lambda: self._collapse_fs_bar(force=True))
        fs_layout.addWidget(fs_hide)
        
        self.fs_bar.setFixedHeight(48)
        self.fs_bar.hide()
        
        # Tiny semi-transparent button to bring the bar back
        self.fs_handle = QtWidgets.QPushButton(
            "⌃",
            None,
            QtCore.Qt.WindowType.ToolTip | QtCore.Qt.WindowType.FramelessWindowHint
        )
        self.fs_handle.setAttribute(QtCore.Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.fs_handle.setFixedSize(36, 20)
        self.fs_handle.setStyleSheet(
            "QPushButton { background-color: rgba(0,0,0,60); color: rgba(255,255,255,120);"
            " border: none; border-radius: 5px; font-size: 9pt; padding: 0; }"
            "QPushButton:hover { background-color: rgba(0,0,0,140); color: white; }"
        )
        self.fs_handle.clicked.connect(self._expand_fs_bar)
        self.fs_handle.hide()
        
        # Auto-hide the bar 10s after it's shown
        self._fs_hide_timer = QtCore.QTimer(self)
        self._fs_hide_timer.setSingleShot(True)
        self._fs_hide_timer.setInterval(10000)
        self._fs_hide_timer.timeout.connect(self._collapse_fs_bar)
        
        # Poll the cursor position - the video surface doesn't deliver
        # mouse-move events, so we watch the global cursor instead
        self._fs_poll_timer = QtCore.QTimer(self)
        self._fs_poll_timer.setInterval(200)
        self._fs_poll_timer.timeout.connect(self._poll_fs_cursor)
        
        video_widget.fullScreenChanged.connect(self._on_fullscreen_changed)
        
        # External subtitle overlay - a separate borderless window because
        # the video widget's native render surface hides child widgets
        self.subtitle_label = QtWidgets.QLabel(
            None,
            QtCore.Qt.WindowType.ToolTip | QtCore.Qt.WindowType.FramelessWindowHint
        )
        self.subtitle_label.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.subtitle_label.setAttribute(QtCore.Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.subtitle_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setWordWrap(True)
        self.subtitle_label.setStyleSheet(
            "QLabel { color: white; background-color: rgba(0,0,0,140);"
            " border-radius: 6px; padding: 4px 10px; font-size: 15pt; }"
        )
        self.subtitle_label.hide()
    
    def _layout_fs_bar(self):
        """Position the floating bar and handle over the bottom of the video"""
        video_widget = self.video_player.video_widget
        top_left = video_widget.mapToGlobal(QtCore.QPoint(0, 0))
        margin = 20
        self.fs_bar.setGeometry(
            top_left.x() + margin,
            top_left.y() + video_widget.height() - self.fs_bar.height() - margin,
            video_widget.width() - 2 * margin,
            self.fs_bar.height()
        )
        self.fs_handle.move(
            top_left.x() + video_widget.width() - self.fs_handle.width() - 12,
            top_left.y() + video_widget.height() - self.fs_handle.height() - 12
        )
        self._layout_subtitle_label()
    
    def _layout_subtitle_label(self):
        """Position the subtitle overlay over the bottom of the video"""
        video_widget = self.video_player.video_widget
        top_left = video_widget.mapToGlobal(QtCore.QPoint(0, 0))
        self.subtitle_label.setGeometry(
            top_left.x() + 40,
            top_left.y() + video_widget.height() - 160,
            video_widget.width() - 80,
            70
        )
    
    def _on_fullscreen_changed(self, fullscreen):
        """Show the bar on fullscreen entry, hide everything on exit"""
        if fullscreen:
            self._layout_fs_bar()
            self.fs_bar.show()
            self.fs_bar.raise_()
            self.fs_handle.hide()
            self._fs_hide_timer.start()
            self._fs_poll_timer.start()
        else:
            self._fs_poll_timer.stop()
            self._fs_hide_timer.stop()
            self.fs_bar.hide()
            self.fs_handle.hide()
    
    def _poll_fs_cursor(self):
        """Show the bar when the cursor nears the bottom of the video"""
        video_widget = self.video_player.video_widget
        if not video_widget.isFullScreen():
            return
        # Keep the floating windows glued to the video widget
        self._layout_fs_bar()
        
        pos = video_widget.mapFromGlobal(QtGui.QCursor.pos())
        inside = (0 <= pos.x() <= video_widget.width()
                  and 0 <= pos.y() <= video_widget.height())
        if not inside:
            return
        if pos.y() > video_widget.height() - 120 or self.fs_bar.underMouse():
            if not self.fs_bar.isVisible():
                self.fs_bar.show()
                self.fs_bar.raise_()
            self.fs_handle.hide()
            self._fs_hide_timer.start()
    
    def _collapse_fs_bar(self, force=False):
        """Hide the bar, leaving only the small corner handle"""
        if self.fs_bar.underMouse() and not force:
            self._fs_hide_timer.start()
            return
        self.fs_bar.hide()
        if self.video_player.video_widget.isFullScreen():
            self._layout_fs_bar()
            self.fs_handle.show()
            self.fs_handle.raise_()
    
    def _expand_fs_bar(self):
        """Restore the bar from the corner handle, restart auto-hide"""
        self.fs_handle.hide()
        self._layout_fs_bar()
        self.fs_bar.show()
        self.fs_bar.raise_()
        self._fs_hide_timer.start()
    
    def _maybe_fullscreen(self):
        """F key toggles fullscreen only while the video page is showing"""
        if self.content_stack.currentIndex() == 1:
            self.toggle_fullscreen()
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode for the video widget"""
        video_widget = self.video_player.video_widget
        video_widget.setFullScreen(not video_widget.isFullScreen())
    
    def eventFilter(self, obj, event):
        """Video widget events: double-click fullscreen, hover controls, resize"""
        if obj is self.video_player.video_widget:
            if event.type() == QtCore.QEvent.Type.MouseButtonDblClick:
                self.toggle_fullscreen()
                return True
            if event.type() == QtCore.QEvent.Type.Resize:
                self._layout_fs_bar()
        return super().eventFilter(obj, event)
    
    def _on_seek(self, position_ms):
        """Seek video when the user drags or clicks the progress slider"""
        if self.is_video_mode:
            self.video_player.media_player.setPosition(position_ms)
    
    def _seek_relative(self, delta_ms):
        """Seek video forward/backward by a relative amount (arrow keys)"""
        if self.is_video_mode:
            player = self.video_player.media_player
            new_pos = max(0, min(player.position() + delta_ms, player.duration()))
            player.setPosition(new_pos)
    
    @staticmethod
    def _format_time(ms):
        """Format milliseconds as MM:SS"""
        seconds = max(0, int(ms / 1000))
        return f"{seconds // 60:02d}:{seconds % 60:02d}"
    
    def on_next(self):
        """Handle next button click"""
        try:
            current_row = self.playlist_view.currentRow()
            if current_row < self.playlist_view.count() - 1:
                self._play_row(current_row + 1)
        except Exception as e:
            logger.error(f"Error playing next song: {e}")
    
    # Recent media
    
    def _load_recent(self):
        """Load recent media list from disk"""
        try:
            if RECENT_FILE.exists():
                data = json.loads(RECENT_FILE.read_text())
                return [e for e in data
                        if isinstance(e, dict) and e.get("path") and e.get("kind")]
        except Exception as e:
            logger.error(f"Error loading recent media: {e}")
        return []
    
    def _save_recent(self):
        """Persist recent media list to disk"""
        try:
            RECENT_FILE.write_text(json.dumps(self.recent_media, indent=2))
        except Exception as e:
            logger.error(f"Error saving recent media: {e}")
    
    def _add_recent(self, path, kind):
        """Add a folder or file to the most-recently-used list"""
        self.recent_media = [e for e in self.recent_media if e["path"] != path]
        self.recent_media.insert(0, {"path": path, "kind": kind})
        self.recent_media = self.recent_media[:MAX_RECENT]
        self._save_recent()
    
    def _clear_recent(self):
        """Clear the recent media list"""
        self.recent_media = []
        self._save_recent()
    
    def _populate_recent_menu(self):
        """Rebuild the Recent Media submenu each time it opens"""
        self.recent_menu.clear()
        if not self.recent_media:
            empty = self.recent_menu.addAction("(no recent media)")
            empty.setEnabled(False)
            return
        
        for entry in self.recent_media:
            path, kind = entry["path"], entry["kind"]
            if kind == "dir":
                label = f"📁 {path}"
            else:
                icon = "🎬" if self.media_manager.is_video_file(path) else "🎵"
                label = f"{icon} {os.path.basename(path)}  —  {os.path.dirname(path)}"
            action = self.recent_menu.addAction(label)
            action.triggered.connect(
                lambda checked=False, e=entry: self._open_recent(e)
            )
        
        self.recent_menu.addSeparator()
        clear_action = self.recent_menu.addAction("Clear Recent")
        clear_action.triggered.connect(self._clear_recent)
    
    def _open_recent(self, entry):
        """Open a recent folder as a playlist or play a recent file"""
        path = entry["path"]
        if entry["kind"] == "dir":
            if not os.path.isdir(path):
                self.statusbar.showMessage(f"Folder no longer exists: {path}")
                return
            self.current_playlist = self.media_manager.scan_directory(path)
            self.update_playlist_view()
            self.update_folder_tree(path)
            self.statusbar.showMessage(f"Loaded {len(self.current_playlist)} media files")
            self._add_recent(path, "dir")
        else:
            if not os.path.isfile(path):
                self.statusbar.showMessage(f"File no longer exists: {path}")
                return
            self._play_path(path)
    
    def _play_path(self, song_path):
        """Play a media file given its full path"""
        song_name = os.path.basename(song_path)
        if self.media_manager.is_audio_file(song_name):
            if self.is_video_mode:
                self.video_player.stop()
                self.show_playlist()
            if self.audio_controller.load(song_path) and self.audio_controller.play():
                self.now_playing_label.setText(f"Now Playing: {song_name}")
                self.statusbar.showMessage(f"Playing: {song_name}")
                self.btn_play.setText("⏸")
                self.is_playing = True
                self._add_recent(song_path, "file")
        elif self.media_manager.is_video_file(song_name):
            self.audio_controller.stop()
            self._prepare_subtitles(song_path)
            if self.video_player.play_video(song_path):
                self.now_playing_label.setText(f"Playing video: {song_name}")
                self.statusbar.showMessage(f"Playing video: {song_name}")
                self.content_stack.setCurrentIndex(1)
                self.is_video_mode = True
                self.is_playing = True
                self.btn_play.setText("⏸")
                self._add_recent(song_path, "file")
    
    # Subtitles
    
    def _prepare_subtitles(self, video_path):
        """Reset subtitle state and auto-load a matching .srt/.vtt file"""
        self._external_subs = []
        self._external_subs_name = ""
        self._sub_mode = "off"
        self.subtitle_label.hide()
        
        sub_file = find_subtitle_file(video_path)
        if sub_file:
            cues = parse_subtitles(sub_file)
            if cues:
                self._external_subs = cues
                self._external_subs_name = os.path.basename(sub_file)
                self._sub_mode = "external"
                self.video_player.set_subtitle_track(-1)
                self.statusbar.showMessage(
                    f"Loaded subtitles: {self._external_subs_name}"
                )
    
    def _update_subtitle_display(self, position_ms):
        """Show the external subtitle cue for the current position"""
        if self._sub_mode != "external" or not self._external_subs:
            if self.subtitle_label.isVisible():
                self.subtitle_label.hide()
            return
        
        for start, end, text in self._external_subs:
            if start <= position_ms <= end:
                self.subtitle_label.setText(text)
                self._layout_subtitle_label()
                if not self.subtitle_label.isVisible():
                    self.subtitle_label.show()
                    self.subtitle_label.raise_()
                return
            if start > position_ms:
                break
        self.subtitle_label.hide()
    
    def _populate_sub_menu(self):
        """Rebuild the Subtitles submenu each time it opens"""
        self.sub_menu.clear()
        has_video = bool(self.video_player.current_video)
        
        off_action = self.sub_menu.addAction("Off")
        off_action.setCheckable(True)
        off_action.setChecked(self._sub_mode == "off")
        off_action.setEnabled(has_video)
        off_action.triggered.connect(lambda: self._set_sub_mode("off"))
        
        if self._external_subs:
            ext_action = self.sub_menu.addAction(
                f"📄 {self._external_subs_name}"
            )
            ext_action.setCheckable(True)
            ext_action.setChecked(self._sub_mode == "external")
            ext_action.triggered.connect(lambda: self._set_sub_mode("external"))
        
        for i, track in enumerate(self.video_player.subtitle_tracks()):
            title = track.get('title') or track.get('language') or f"Track {i + 1}"
            action = self.sub_menu.addAction(f"🎬 {title}")
            action.setCheckable(True)
            action.setChecked(
                self._sub_mode == "embedded"
                and self.video_player.media_player.activeSubtitleTrack() == i
            )
            action.triggered.connect(
                lambda checked=False, idx=i: self._set_sub_mode("embedded", idx)
            )
        
        self.sub_menu.addSeparator()
        load_action = self.sub_menu.addAction("Load Subtitle File…")
        load_action.setEnabled(has_video)
        load_action.triggered.connect(self._load_subtitle_file)
    
    def _set_sub_mode(self, mode, track_index=None):
        """Switch between off / external / embedded subtitles"""
        self._sub_mode = mode
        if mode == "embedded":
            self.video_player.set_subtitle_track(track_index)
            self.subtitle_label.hide()
        elif mode == "external":
            self.video_player.set_subtitle_track(-1)
        else:
            self.video_player.set_subtitle_track(-1)
            self.subtitle_label.hide()
    
    def _load_subtitle_file(self):
        """Let the user pick an .srt/.vtt file for the current video"""
        video_path = self.video_player.current_video
        start_dir = os.path.dirname(video_path) if video_path else str(Path.home())
        filepath, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select Subtitle File",
            start_dir,
            "Subtitles (*.srt *.vtt)"
        )
        if filepath:
            cues = parse_subtitles(filepath)
            if cues:
                self._external_subs = cues
                self._external_subs_name = os.path.basename(filepath)
                self._set_sub_mode("external")
                self.statusbar.showMessage(
                    f"Loaded subtitles: {self._external_subs_name}"
                )
            else:
                self.statusbar.showMessage("Could not parse subtitle file")
    
    def _play_row(self, row):
        """Select and play the playlist item at the given row"""
        item = self.playlist_view.item(row)
        if item:
            self.playlist_view.setCurrentItem(item)
            self.on_song_double_clicked(item)
    
    def on_repeat_cycle(self):
        """Cycle repeat mode: Off -> All -> One"""
        self.repeat_mode = (self.repeat_mode + 1) % 3
        labels = ["Off", "All", "One"]
        self.btn_repeat.setText(f"Repeat: {labels[self.repeat_mode]}")
        self.statusbar.showMessage(f"Repeat mode: {labels[self.repeat_mode]}")
    
    def _check_track_end(self):
        """Detect when an audio track finishes (pygame has no end signal)"""
        if self.is_video_mode:
            return
        busy = self.audio_controller.is_playing()
        # Only treat as "finished" if we think we're playing (ignores paused state)
        if self.is_playing and self._audio_was_playing and not busy:
            self._on_track_finished()
        self._audio_was_playing = busy
    
    def _on_track_finished(self):
        """Handle end of an audio track based on repeat mode"""
        if self.repeat_mode == 2:
            self.audio_controller.play()
            return
        
        current_row = self.playlist_view.currentRow()
        last_row = self.playlist_view.count() - 1
        if current_row < last_row:
            self._play_row(current_row + 1)
        elif self.repeat_mode == 1 and last_row >= 0:
            self._play_row(0)
        else:
            self.is_playing = False
            self.btn_play.setText("▶")
            self.statusbar.showMessage("Finished")
    
    def _on_video_finished(self):
        """Handle end of a video based on repeat mode"""
        if self.repeat_mode == 2:
            self.video_player.play_video(self.video_player.current_video)
            return
        
        current_row = self.playlist_view.currentRow()
        last_row = self.playlist_view.count() - 1
        if current_row < last_row:
            self._play_row(current_row + 1)
        elif self.repeat_mode == 1 and last_row >= 0:
            self._play_row(0)
        else:
            self.is_playing = False
            self.btn_play.setText("▶")
            self.video_player.video_widget.setFullScreen(False)
            self.show_playlist()
    
    def on_previous(self):
        """Handle previous button click"""
        try:
            current_row = self.playlist_view.currentRow()
            if current_row > 0:
                prev_item = self.playlist_view.item(current_row - 1)
                self.playlist_view.setCurrentItem(prev_item)
                self.on_song_double_clicked(prev_item)
        except Exception as e:
            logger.error(f"Error playing previous song: {e}")
    
    def on_volume_change(self, value):
        """Handle volume slider change"""
        try:
            volume = value / 100.0
            self.audio_controller.volume = volume
            self.video_player.set_volume(volume)
            self.volume_label.setText(f"{value}%")
        except Exception as e:
            logger.error(f"Error changing volume: {e}")
    
    def on_load_playlist(self):
        """Handle load playlist action"""
        try:
            directory = QtWidgets.QFileDialog.getExistingDirectory(
                self,
                "Select Folder Containing Media",
                self.media_manager.get_user_music_folder()
            )
            
            if directory:
                self.current_playlist = self.media_manager.scan_directory(directory)
                self.update_playlist_view()
                self.update_folder_tree(directory)
                self.statusbar.showMessage(f"Loaded {len(self.current_playlist)} media files")
                self._add_recent(directory, "dir")
                logger.info(f"Loaded playlist from: {directory}")
                
        except Exception as e:
            logger.error(f"Error loading playlist: {e}")
            self.statusbar.showMessage("Error loading playlist")
    
    def on_search(self):
        """Handle search"""
        try:
            query = self.search_input.text().strip()
            if not query:
                self.update_playlist_view()
                return
            
            current_dir = self.media_manager.current_directory or self.media_manager.get_user_music_folder()
            results = self.media_manager.search_media_files(current_dir, query)
            
            self.playlist_view.clear()
            self.playlist_view.addItems(results)
            self.statusbar.showMessage(f"Found {len(results)} matches for '{query}'")
            
        except Exception as e:
            logger.error(f"Error searching: {e}")
            self.statusbar.showMessage("Error searching")
    
    def closeEvent(self, event):
        """Stop all playback when the window closes"""
        self.subtitle_label.hide()
        self.video_player.stop()
        self.audio_controller.stop()
        super().closeEvent(event)
    
    def show_about(self):
        """Show about dialog"""
        QtWidgets.QMessageBox.about(
            self,
            "About Pd Music Player",
            "<h2>Pd Music Player</h2>"
            "<p>A modern, modular media player application</p>"
            "<p><b>Developer:</b> POLLARD SAMBA</p>"
            "<p><b>GitHub:</b> POLLARD1145</p>"
            "<p><b>Email:</b> POLLADSAMBA1@GMAIL.COM</p>"
            f"<p>Version {APP_VERSION}</p>"
        )


def main():
    """Main entry point for the application"""
    try:
        app = QtWidgets.QApplication(sys.argv)
        app.setApplicationName("Pd Music Player")
        
        # Set application icon - works both from source and inside a
        # PyInstaller bundle (sys._MEIPASS is the bundled assets dir)
        bundle_dir = Path(getattr(sys, '_MEIPASS', Path(__file__).parent.parent))
        icon_path = bundle_dir / "assets" / "images" / "logo" / "Pd Player Logo.png"
        if icon_path.exists():
            app.setWindowIcon(QtGui.QIcon(str(icon_path)))
        
        # Create and show main window
        window = MediaPlayerUI()
        window.show()
        
        logger.info("Application started successfully")
        sys.exit(app.exec())
        
    except Exception as e:
        logger.critical(f"Critical error starting application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
