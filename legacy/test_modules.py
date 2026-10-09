"""
Test script to verify all modules work correctly
"""
import sys
import os

def test_imports():
    """Test that all modules can be imported"""
    print("Testing module imports...")
    
    try:
        from audio_controller import AudioController
        print("✓ audio_controller imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import audio_controller: {e}")
        return False
    
    try:
        from media_manager import MediaManager
        print("✓ media_manager imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import media_manager: {e}")
        return False
    
    try:
        from video_player import VideoPlayer
        print("✓ video_player imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import video_player: {e}")
        return False
    
    print("\nAll modules imported successfully!\n")
    return True


def test_audio_controller():
    """Test audio controller initialization"""
    print("Testing AudioController...")
    
    try:
        from audio_controller import AudioController
        
        controller = AudioController()
        print(f"✓ AudioController initialized")
        print(f"  - Initial volume: {controller.volume}")
        
        # Test volume setting
        controller.volume = 0.5
        assert abs(controller.volume - 0.5) < 0.01, "Volume setting failed"
        print(f"✓ Volume control works")
        
        return True
    except Exception as e:
        print(f"✗ AudioController test failed: {e}")
        return False


def test_media_manager():
    """Test media manager"""
    print("\nTesting MediaManager...")
    
    try:
        from media_manager import MediaManager
        
        manager = MediaManager()
        print(f"✓ MediaManager initialized")
        
        # Test getting music folder
        music_folder = manager.get_user_music_folder()
        print(f"✓ Music folder: {music_folder}")
        
        # Test file extension checking
        assert manager.is_audio_file("test.mp3"), "Audio file detection failed"
        assert manager.is_video_file("test.mp4"), "Video file detection failed"
        assert not manager.is_audio_file("test.txt"), "Non-audio file wrongly detected"
        print(f"✓ File type detection works")
        
        # Test scanning (if music folder exists and has files)
        if os.path.exists(music_folder):
            files = manager.scan_directory(music_folder, 'audio')
            print(f"✓ Found {len(files)} audio files in music folder")
        
        return True
    except Exception as e:
        print(f"✗ MediaManager test failed: {e}")
        return False


def test_video_player():
    """Test video player initialization"""
    print("\nTesting VideoPlayer...")
    
    try:
        from video_player import VideoPlayer
        
        player = VideoPlayer()
        print(f"✓ VideoPlayer initialized")
        
        return True
    except Exception as e:
        print(f"✗ VideoPlayer test failed: {e}")
        return False


def test_requirements():
    """Test that all required packages are installed"""
    print("\nTesting requirements...")
    
    required_packages = {
        'PyQt6': 'PyQt6',
        'pygame': 'pygame',
        'moviepy': 'moviepy.editor',
        'numpy': 'numpy'
    }
    
    all_installed = True
    
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✓ {package_name} is installed")
        except ImportError:
            print(f"✗ {package_name} is NOT installed")
            all_installed = False
    
    return all_installed


def main():
    """Run all tests"""
    print("=" * 60)
    print("Pd Music Player - Module Tests")
    print("=" * 60)
    print()
    
    # Test requirements
    if not test_requirements():
        print("\n⚠ Some required packages are missing!")
        print("Please run: pip install -r requirements.txt")
        return False
    
    print()
    print("=" * 60)
    print()
    
    # Test imports
    if not test_imports():
        return False
    
    # Test individual modules
    tests_passed = 0
    tests_total = 3
    
    if test_audio_controller():
        tests_passed += 1
    
    if test_media_manager():
        tests_passed += 1
    
    if test_video_player():
        tests_passed += 1
    
    print()
    print("=" * 60)
    print(f"Tests completed: {tests_passed}/{tests_total} passed")
    print("=" * 60)
    
    if tests_passed == tests_total:
        print("\n✓ All tests passed! You can run the application with:")
        print("  python mplayer_optimized.py")
        return True
    else:
        print("\n⚠ Some tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
