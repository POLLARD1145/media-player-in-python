# 🏗️ Architecture Documentation

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Pd Media Player v2.0                        │
│                   (mplayer_optimized.py)                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ coordinates
                              ▼
        ┌─────────────────────────────────────────────┐
        │         MediaPlayerUI (Main Window)         │
        │  - User Interface                           │
        │  - Event Handling                           │
        │  - Layout Management                        │
        └─────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ AudioController  │ │  MediaManager    │ │  VideoPlayer     │
│                  │ │                  │ │                  │
│ - Play/Pause     │ │ - File Scanning  │ │ - Video Play     │
│ - Stop           │ │ - Extensions     │ │ - Resource Mgmt  │
│ - Volume         │ │ - Path Handling  │ │                  │
│ - Playlist Mgmt  │ │ - Search         │ │                  │
└──────────────────┘ └──────────────────┘ └──────────────────┘
          │                   │                   │
          ▼                   ▼                   ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│     pygame       │ │   os / pathlib   │ │    moviepy       │
│  (audio engine)  │ │  (file system)   │ │  (video engine)  │
└──────────────────┘ └──────────────────┘ └──────────────────┘
```

## Module Breakdown

### 1. MediaPlayerUI (Main Application)

**Responsibilities:**
- Window management
- UI layout and styling
- Event handling
- Coordination between modules

**Key Components:**
```
MediaPlayerUI
├── Left Panel
│   ├── Navigation List (Library, Music, Videos, Folders)
│   ├── Folder Tree (Subdirectories)
│   └── Visualization (Now Playing indicator)
│
├── Right Panel
│   ├── Search Bar
│   ├── Playlist View
│   ├── Now Playing Label
│   ├── Progress Bar
│   └── Control Panel
│       ├── Previous Button
│       ├── Play/Pause Button
│       ├── Stop Button
│       ├── Next Button
│       └── Volume Control
│
├── Menu Bar
│   ├── Media Menu
│   ├── Playback Menu
│   └── Help Menu
│
└── Status Bar
```

### 2. AudioController

**Responsibilities:**
- Audio playback control
- Volume management
- Playlist handling

**Key Methods:**
```python
class AudioController:
    def __init__()              # Initialize pygame
    def load(filepath)          # Load audio file
    def play()                  # Start playback
    def pause()                 # Pause playback
    def unpause()               # Resume playback
    def stop()                  # Stop playback
    def is_playing()            # Check status
    def set_playlist(playlist)  # Set playlist
    def play_next()             # Next track
    def play_previous()         # Previous track
    
    # Properties
    volume                      # Get/set volume (0.0-1.0)
    current_song                # Current file path
    current_index               # Playlist position
```

### 3. MediaManager

**Responsibilities:**
- File system operations
- Media file discovery
- Format detection

**Key Methods:**
```python
class MediaManager:
    def __init__()
    def get_user_music_folder()       # Default music path
    def get_user_video_folder()       # Default video path
    def scan_directory(dir, type)     # Find media files
    def get_subdirectories(dir)       # List folders
    def is_audio_file(filename)       # Check if audio
    def is_video_file(filename)       # Check if video
    def search_media_files(dir, query) # Search by name
    
    # Constants
    AUDIO_EXTENSIONS = {'.mp3', '.wav', ...}
    VIDEO_EXTENSIONS = {'.mp4', '.avi', ...}
```

### 4. VideoPlayer

**Responsibilities:**
- Video playback
- Resource cleanup

**Key Methods:**
```python
class VideoPlayer:
    def __init__()
    def play_video(filepath, width, height)  # Play video
    
    # Properties
    current_video                            # Current video path
```

## Data Flow Diagrams

### Playing an Audio File

```
User Double-Clicks Song
        │
        ▼
MediaPlayerUI.on_song_double_clicked()
        │
        ├─→ MediaManager.get_file_path()
        │   └─→ Returns full path
        │
        ├─→ AudioController.load(path)
        │   └─→ pygame.mixer.music.load()
        │
        ├─→ AudioController.play()
        │   └─→ pygame.mixer.music.play()
        │
        └─→ Update UI
            ├─→ now_playing_label.setText()
            ├─→ btn_play.setText("⏸")
            └─→ statusbar.showMessage()
```

### Loading a Playlist

```
User Clicks "Load Playlist"
        │
        ▼
MediaPlayerUI.on_load_playlist()
        │
        ├─→ QFileDialog.getExistingDirectory()
        │   └─→ User selects folder
        │
        ├─→ MediaManager.scan_directory(folder)
        │   ├─→ os.listdir(folder)
        │   ├─→ Filter by extensions
        │   └─→ Returns list of files
        │
        └─→ Update UI
            ├─→ playlist_view.clear()
            ├─→ playlist_view.addItems(files)
            ├─→ update_folder_tree()
            └─→ statusbar.showMessage()
```

### Volume Control

```
User Moves Volume Slider
        │
        ▼
MediaPlayerUI.on_volume_change(value)
        │
        ├─→ Convert to 0.0-1.0 range
        │
        ├─→ AudioController.volume = value
        │   └─→ pygame.mixer.music.set_volume()
        │
        └─→ Update UI
            └─→ volume_label.setText()
```

## Design Patterns Used

### 1. **Model-View-Controller (MVC)**
- **Model**: AudioController, MediaManager, VideoPlayer
- **View**: MediaPlayerUI (PyQt6 widgets)
- **Controller**: MediaPlayerUI (event handlers)

### 2. **Separation of Concerns**
- Each module has ONE clear responsibility
- No module depends on implementation details of others
- Clean interfaces between modules

### 3. **Dependency Injection**
- Controllers instantiated in MediaPlayerUI
- Passed as needed, not created in nested functions

### 4. **Error Handling Pattern**
```python
try:
    # Operation
    result = perform_operation()
    # Success handling
    update_ui_success()
except SpecificError as e:
    # Error handling
    logger.error(f"Error: {e}")
    update_ui_error()
```

### 5. **Property Pattern**
```python
@property
def volume(self):
    return self._volume

@volume.setter
def volume(self, value):
    self._volume = clamp(value, 0.0, 1.0)
```

## File Organization

```
media-player-in-python/
│
├── Core Application
│   ├── mplayer_optimized.py     (656 lines) - Main UI
│   ├── audio_controller.py      (167 lines) - Audio module
│   ├── media_manager.py         (159 lines) - File module
│   └── video_player.py          (60 lines)  - Video module
│
├── Configuration & Dependencies
│   ├── requirements.txt         (4 lines)   - Dependencies
│   └── media_player.log         (generated) - Logs
│
├── Documentation
│   ├── README_OPTIMIZED.md      - User guide
│   ├── QUICK_START.md           - Quick reference
│   ├── IMPROVEMENTS.md          - Technical details
│   ├── MIGRATION_GUIDE.md       - Migration help
│   ├── ARCHITECTURE.md          - This file
│   └── SUMMARY.md               - Overview
│
├── Testing
│   └── test_modules.py          (156 lines) - Module tests
│
└── Original (Reference)
    ├── mplayer.py               (501 lines) - Original code
    ├── README.md                - Original README
    └── LICENSE                  - License file
```

## Class Relationships

```
┌─────────────────────────────────────────────────────────┐
│                    MediaPlayerUI                        │
│ ┌─────────────────────────────────────────────────────┐ │
│ │  UI Components                                      │ │
│ │  - QMainWindow                                      │ │
│ │  - QWidgets (buttons, sliders, lists)               │ │
│ │  - QLayouts (organization)                          │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                           │
│ ┌─────────────────────────────────────────────────────┐ │
│ │  Controllers (injected)                             │ │
│ │  ┌───────────────────┐ ┌──────────────────┐        │ │
│ │  │ audio_controller  │ │  media_manager   │        │ │
│ │  └───────────────────┘ └──────────────────┘        │ │
│ │  ┌───────────────────┐                             │ │
│ │  │   video_player    │                             │ │
│ │  └───────────────────┘                             │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                           │
│ ┌─────────────────────────────────────────────────────┐ │
│ │  State Variables                                    │ │
│ │  - current_playlist: List[str]                      │ │
│ │  - is_playing: bool                                 │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                           │
│ ┌─────────────────────────────────────────────────────┐ │
│ │  Event Handlers                                     │ │
│ │  - on_play_pause()                                  │ │
│ │  - on_song_clicked()                                │ │
│ │  - on_load_playlist()                               │ │
│ │  - on_volume_change()                               │ │
│ │  - ... and more                                     │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Logging Architecture

```
Application Events
        │
        ▼
┌────────────────────────────────┐
│   Python Logging System        │
│   (level: INFO)                 │
└────────────────────────────────┘
        │
        ├─────────────────┬─────────────────┐
        ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ FileHandler  │  │StreamHandler │  │    Format    │
│              │  │              │  │              │
│ media_player │  │   Console    │  │ timestamp    │
│   .log       │  │    Output    │  │ level        │
│              │  │              │  │ message      │
└──────────────┘  └──────────────┘  └──────────────┘
```

## Error Handling Flow

```
User Action
    │
    ▼
Try Block
    ├─→ Normal Operation
    │   └─→ Success: Update UI with result
    │
    └─→ Exception Occurs
        ├─→ logger.error(message)
        │   └─→ Written to log file
        │
        ├─→ statusbar.showMessage(error)
        │   └─→ User sees friendly message
        │
        └─→ Application continues
            (no crash!)
```

## Performance Optimizations

### 1. **Extension-Based Filtering**
```
Before:                  After:
regex.compile()          ext in EXTENSIONS_SET
  ↓ O(n)                   ↓ O(1)
filter()                 Simple check
  ↓ Slow                   ↓ Fast
```

### 2. **Lazy Loading**
- UI components created on demand
- Files scanned only when needed
- Resources released after use

### 3. **Efficient Path Handling**
- pathlib for automatic conversion
- No repeated string operations
- Cross-platform compatible

## State Management

```
Application State
├── Audio State (AudioController)
│   ├── current_song: str
│   ├── volume: float (0.0-1.0)
│   ├── _playlist: List[str]
│   └── _current_index: int
│
├── Media State (MediaManager)
│   └── current_directory: str
│
├── UI State (MediaPlayerUI)
│   ├── current_playlist: List[str]
│   ├── is_playing: bool
│   └── Widget states (selected, enabled, etc.)
│
└── Video State (VideoPlayer)
    └── _current_video: str
```

## Extension Points

Want to add features? Here's where:

### Add New Audio Format
```python
# In media_manager.py
AUDIO_EXTENSIONS = {'.mp3', '.wav', '.newformat'}
```

### Add New Control Button
```python
# In mplayer_optimized.py → create_controls()
self.btn_new = QtWidgets.QPushButton("Icon")
self.btn_new.clicked.connect(self.on_new_action)
```

### Add Keyboard Shortcut
```python
# In mplayer_optimized.py → create_menu_bar()
action = QtGui.QAction("Feature", self)
action.setShortcut("Ctrl+N")
action.triggered.connect(self.on_feature)
```

### Add New Theme
```python
# In mplayer_optimized.py → apply_modern_stylesheet()
# Modify colors in the stylesheet string
```

## Threading Model

Current: **Single-threaded** (sufficient for current needs)

Future considerations:
- Background file scanning → QThread
- Progress bar updates → QTimer
- Video loading → Separate thread

## Security Considerations

1. **Path Validation**: All paths validated before use
2. **Error Handling**: No sensitive data in error messages
3. **Resource Limits**: File operations have timeouts
4. **Permission Checks**: Graceful handling of access denied

## Testing Strategy

```
Unit Tests (planned)
├── test_audio_controller.py
│   ├── test_volume_control()
│   ├── test_play_pause()
│   └── test_playlist_navigation()
│
├── test_media_manager.py
│   ├── test_file_detection()
│   ├── test_directory_scanning()
│   └── test_search()
│
└── test_video_player.py
    └── test_video_playback()

Integration Tests
└── test_full_workflow()

Current Tests
└── test_modules.py (basic verification)
```

## Deployment

```
Development          Production
    │                    │
    ├─→ Local Install    ├─→ pip install -r requirements.txt
    │                    │
    ├─→ Run & Test       ├─→ python mplayer_optimized.py
    │                    │
    └─→ Logs in CWD      └─→ Check media_player.log
```

---

**This architecture provides:**
- ✅ **Maintainability**: Clear structure
- ✅ **Extensibility**: Easy to add features
- ✅ **Testability**: Separated concerns
- ✅ **Performance**: Optimized operations
- ✅ **Reliability**: Robust error handling

**Ready for production! 🚀**
