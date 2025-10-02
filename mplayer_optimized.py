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
import logging
from pathlib import Path
from PySide6 import QtCore, QtGui, QtWidgets

from audio_controller import AudioController
from media_manager import MediaManager
from video_player import VideoPlayer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('media_player.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


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
        
        # Setup UI
        self.setup_ui()
        self.apply_modern_stylesheet()
        
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
        layout.addWidget(self.playlist_view)
        
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
        
        self.progress_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
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
        
        media_menu.addSeparator()
        
        exit_action = QtGui.QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        media_menu.addAction(exit_action)
        
        # Playback menu
        playback_menu = menubar.addMenu("Playback")
        
        play_action = QtGui.QAction("Play", self)
        play_action.setShortcut("Space")
        play_action.triggered.connect(self.on_play_pause)
        playback_menu.addAction(play_action)
        
        stop_action = QtGui.QAction("Stop", self)
        stop_action.setShortcut("S")
        stop_action.triggered.connect(self.on_stop)
        playback_menu.addAction(stop_action)
        
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
                
            elif text == "Video Library":
                video_folder = self.media_manager.get_user_video_folder()
                self.current_playlist = self.media_manager.scan_directory(video_folder, 'video')
                self.update_playlist_view()
                self.statusbar.showMessage(f"Loaded video library: {len(self.current_playlist)} videos")
                
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
                if self.audio_controller.load(song_path):
                    if self.audio_controller.play():
                        self.now_playing_label.setText(f"Now Playing: {song_name}")
                        self.statusbar.showMessage(f"Playing: {song_name}")
                        self.btn_play.setText("⏸")
                        self.is_playing = True
                        
            elif self.media_manager.is_video_file(song_name):
                self.now_playing_label.setText(f"Playing video: {song_name}")
                self.statusbar.showMessage(f"Playing video: {song_name}")
                self.video_player.play_video(song_path)
                
        except Exception as e:
            logger.error(f"Error playing media: {e}")
            self.statusbar.showMessage("Error playing media file")
    
    def on_play_pause(self):
        """Handle play/pause button click"""
        try:
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
            self.audio_controller.stop()
            self.btn_play.setText("▶")
            self.is_playing = False
            self.statusbar.showMessage("Stopped")
        except Exception as e:
            logger.error(f"Error stopping playback: {e}")
    
    def on_next(self):
        """Handle next button click"""
        try:
            current_row = self.playlist_view.currentRow()
            if current_row < self.playlist_view.count() - 1:
                next_item = self.playlist_view.item(current_row + 1)
                self.playlist_view.setCurrentItem(next_item)
                self.on_song_double_clicked(next_item)
        except Exception as e:
            logger.error(f"Error playing next song: {e}")
    
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
            "<p>Version 2.0 - Optimized Edition</p>"
        )


def main():
    """Main entry point for the application"""
    try:
        app = QtWidgets.QApplication(sys.argv)
        app.setApplicationName("Pd Music Player")
        
        # Set application icon if available
        icon_path = Path(__file__).parent / "icon.png"
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
