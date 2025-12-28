#!/usr/bin/env python3

"""
Face tracking with MediaPipe Face Mesh + pygame

Optimized for Pepper's Ghost effect: black background, bright colors
"""

import cv2
import pygame
import numpy as np
import sys
import os
import argparse

# Try to import MediaPipe
try:
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    from mediapipe import Image as MPImage
    MP_AVAILABLE = True
    print("✅ Using MediaPipe Tasks API")
except ImportError as e:
    print(f"❌ MediaPipe not installed or not working: {e}")
    print("Install with: pip install mediapipe")
    sys.exit(1)

# Try to import picamera2 (only available on Raspberry Pi)
try:
    from picamera2 import Picamera2
    PICAMERA2_AVAILABLE = True
except ImportError:
    PICAMERA2_AVAILABLE = False
    print("ℹ️  picamera2 not available (not on Raspberry Pi) - will use webcam")

# Display settings
WIDTH = 1280
HEIGHT = 720
FPS = 30

# Colors for Pepper's Ghost (bright on black)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)  # Bright green for points
MAGENTA = (255, 0, 255)  # Bright magenta for lines
CYAN = (0, 255, 255)  # Bright cyan for highlights

# Face mesh connections (key facial features)
FACE_CONNECTIONS = [
    # Face outline
    [10, 338], [338, 297], [297, 332], [332, 284], [284, 251], [251, 389],
    [389, 356], [356, 454], [454, 323], [323, 361], [361, 288], [288, 397],
    [397, 365], [365, 379], [379, 378], [378, 400], [400, 377], [377, 152],
    [152, 148], [148, 176], [176, 149], [149, 150], [150, 136], [136, 172],
    [172, 58], [58, 132], [132, 93], [93, 234], [234, 127], [127, 162],
    [162, 21], [21, 54], [54, 103], [103, 67], [67, 109], [109, 10],
    # Left eyebrow
    [107, 55], [55, 65], [65, 52], [52, 53], [53, 46],
    # Right eyebrow
    [336, 296], [296, 334], [334, 293], [293, 300], [300, 276],
    # Left eye
    [33, 7], [7, 163], [163, 144], [144, 145], [145, 153], [153, 154],
    [154, 155], [155, 133], [133, 173], [173, 157], [157, 158], [158, 159],
    [159, 160], [160, 161], [161, 246], [246, 33],
    # Right eye
    [263, 249], [249, 390], [390, 373], [373, 374], [374, 380], [380, 381],
    [381, 382], [382, 362], [362, 398], [398, 384], [384, 385], [385, 386],
    [386, 387], [387, 388], [388, 466], [466, 263],
    # Nose
    [1, 2], [2, 5], [5, 4], [4, 6], [6, 19], [19, 20], [20, 94], [94, 2],
    [168, 8], [8, 9], [9, 10], [10, 151], [151, 337], [337, 299], [299, 333],
    [333, 298], [298, 301], [301, 168],
    # Mouth
    [61, 146], [146, 91], [91, 181], [181, 84], [84, 17], [17, 314],
    [314, 405], [405, 320], [320, 307], [307, 375], [375, 321], [321, 308],
    [308, 324], [324, 318], [318, 61],
    [78, 95], [95, 88], [88, 178], [178, 87], [87, 14], [14, 317],
    [317, 402], [402, 318], [318, 324], [324, 308], [308, 78],
]

# Key facial feature points for highlighting
KEY_POINTS = [33, 263, 1, 61, 291, 199]  # eyes, nose, mouth corners

def check_camera_available():
    """Check if camera hardware is available

    Note: libcamera-hello may not work with HyperPixel displays (preview conflicts)
    So we'll just try to initialize the camera directly
    """
    # With HyperPixel, libcamera-hello often fails due to preview conflicts
    # So we skip the check and just try to initialize the camera
    # The camera will work even if libcamera-hello doesn't
    return None  # Unknown - proceed anyway  # Unknown state

def init_camera():
    """Initialize Raspberry Pi camera"""
    if not PICAMERA2_AVAILABLE:
        print("ℹ️  picamera2 not available")
        return None
    
    # Note: With HyperPixel, libcamera-hello may not work (preview conflicts)
    # So we skip the hardware check and try to initialize directly
    # The camera will work with picamera2 even if libcamera-hello fails
    
    try:
        print("🔍 Attempting to initialize Raspberry Pi Camera...")
        picam2 = Picamera2()
        
        # Try to get available camera configurations
        try:
            camera_info = picam2.camera_properties
            print(f"📷 Camera detected: {camera_info.get('Model', 'Unknown')}")
        except:
            print("⚠️  Could not read camera properties")
        
        # Use default video configuration (like the reference code)
        # IMPORTANT: No preview mode - required for HyperPixel displays
        try:
            print("🔧 Configuring camera with default video configuration (no preview)...")
            video_config = picam2.create_video_configuration()
            picam2.configure(video_config)
            picam2.start()
            
            # Wait for camera to initialize (like reference code)
            import time
            time.sleep(0.2)
            
            # Test if we can actually capture a frame
            # Skip first few frames (camera warm-up)
            print("🧪 Testing camera capture (warming up)...")
            for i in range(3):
                try:
                    test_frame = picam2.capture_array()
                    if test_frame is not None:
                        break
                except:
                    time.sleep(0.1)
                    continue
            
            if test_frame is not None and test_frame.size > 0:
                print(f"✅ Raspberry Pi Camera initialized successfully!")
                print(f"   Resolution: {test_frame.shape[1]}x{test_frame.shape[0]}")
                print(f"   Format: {test_frame.shape}")
                print(f"   Dtype: {test_frame.dtype}")
                if len(test_frame.shape) == 3:
                    print(f"   Channels: {test_frame.shape[2]}")
                return picam2
            else:
                print("⚠️  Camera started but no frame captured")
                if test_frame is None:
                    print("   Frame is None")
                else:
                    print(f"   Frame size: {test_frame.size}")
                picam2.stop()
                return None
        except Exception as e:
            print(f"❌ Camera configuration failed: {e}")
            try:
                picam2.stop()
            except:
                pass
            return None
        
    except Exception as e:
        print(f"❌ Failed to initialize Raspberry Pi camera: {e}")
        print("💡 Troubleshooting tips:")
        print("   1. Check if camera is enabled: sudo raspi-config > Interface Options > Camera")
        print("   2. Verify camera connection: libcamera-hello --list-cameras")
        print("   3. Test camera: libcamera-hello -t 0")
        print("   4. Check permissions: ls -l /dev/video*")
        return None

def init_webcam():
    """Initialize webcam (fallback for non-Pi systems)"""
    try:
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
        cap.set(cv2.CAP_PROP_FPS, FPS)
        if not cap.isOpened():
            raise Exception("Could not open webcam")
        print("✅ Webcam initialized")
        return cap
    except Exception as e:
        print(f"❌ Failed to initialize webcam: {e}")
        return None

def get_frame(camera, webcam, debug=False):
    """Get frame from camera or webcam"""
    if camera:
        # Raspberry Pi camera (like reference code)
        try:
            frame = camera.capture_array()
            
            # Handle different frame formats (like reference code)
            if frame is None:
                if debug:
                    print("⚠️  Frame is None")
                return None
            
            if frame.ndim != 3:
                if debug:
                    print(f"⚠️  Unexpected frame dimensions: {frame.ndim}")
                return None
            
            # Check frame format and convert to RGB (like reference code)
            if frame.shape[2] == 4:
                # BGRA format - convert to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)
            elif frame.shape[2] == 3:
                # Could be BGR or RGB - check and convert if needed
                # picamera2 usually gives RGB888, but let's be safe
                # Try converting BGR to RGB (won't hurt if already RGB)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                if debug:
                    print(f"⚠️  Unexpected number of channels: {frame.shape[2]}")
                return None
            
            return frame
        except Exception as e:
            if debug:
                print(f"⚠️  Frame capture error: {e}")
                import traceback
                traceback.print_exc()
            return None
    elif webcam:
        # Webcam
        ret, frame = webcam.read()
        if ret:
            # Convert BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return frame
    return None

def draw_face_landmarks(screen, landmarks, width, height):
    """Draw face landmarks on pygame screen"""
    if not landmarks:
        return
    # Flip horizontally for mirror effect
    # We'll draw mirrored by calculating x as (width - x)
    
    # Draw connections (lines) - bright magenta
    for connection in FACE_CONNECTIONS:
        start_idx, end_idx = connection
        if start_idx < len(landmarks) and end_idx < len(landmarks):
            start = landmarks[start_idx]
            end = landmarks[end_idx]
            # Mirror horizontally
            x1 = int((1 - start.x) * width)
            y1 = int(start.y * height)
            x2 = int((1 - end.x) * width)
            y2 = int(end.y * height)
            pygame.draw.line(screen, MAGENTA, (x1, y1), (x2, y2), 1)
    
    # Draw all landmarks as points - bright green
    for landmark in landmarks:
        x = int((1 - landmark.x) * width)  # Mirror horizontally
        y = int(landmark.y * height)
        pygame.draw.circle(screen, GREEN, (x, y), 3)
    
    # Highlight key points - bright cyan
    for idx in KEY_POINTS:
        if idx < len(landmarks):
            landmark = landmarks[idx]
            x = int((1 - landmark.x) * width)  # Mirror horizontally
            y = int(landmark.y * height)
            pygame.draw.circle(screen, CYAN, (x, y), 6)

def main():
    """Main application loop"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Ghost Face - Face tracking visualization')
    parser.add_argument('--fullscreen', '-f', action='store_true',
                        help='Run in fullscreen mode')
    parser.add_argument('--width', '-w', type=int, default=WIDTH,
                        help=f'Window width (default: {WIDTH})')
    parser.add_argument('--height', type=int, default=HEIGHT,
                        help=f'Window height (default: {HEIGHT})')
    parser.add_argument('--display', '-d', type=int, default=None,
                        help='Display number (for multi-display setups)')
    parser.add_argument('--test-camera', '-t', action='store_true',
                        help='Test mode: show raw camera feed instead of face detection')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug output')
    args = parser.parse_args()
    
    # Initialize pygame
    pygame.init()
    
    # Set display mode
    if args.fullscreen:
        # Get fullscreen resolution
        screen_info = pygame.display.Info()
        display_width = screen_info.current_w
        display_height = screen_info.current_h
        print(f"🖥️  Fullscreen mode: {display_width}x{display_height}")
        screen = pygame.display.set_mode((display_width, display_height), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((args.width, args.height))
        print(f"🖥️  Window mode: {args.width}x{args.height}")
    
    pygame.display.set_caption("Ghost Face - Pepper's Ghost")
    clock = pygame.time.Clock()
    
    # Get actual screen dimensions for drawing
    screen_width, screen_height = screen.get_size()
    
    # Track fullscreen state
    is_fullscreen = args.fullscreen
    
    # Hide cursor
    pygame.mouse.set_visible(False)
    
    # Initialize camera
    print("\n" + "="*50)
    print("📷 Initializing Camera...")
    print("="*50)
    camera = init_camera()
    webcam = None
    if not camera:
        print("\n🔄 Falling back to webcam (OpenCV)...")
        webcam = init_webcam()
        if not webcam:
            print("\n❌ No camera available!")
            print("\n💡 Troubleshooting:")
            print("   - On Raspberry Pi: Ensure camera is enabled in raspi-config")
            print("   - Check camera connection and permissions")
            print("   - Try: libcamera-hello -t 0")
            sys.exit(1)
    print("="*50 + "\n")
    
    # Initialize MediaPipe Face Mesh using Tasks API
    # Download model if needed
    try:
        import mediapipe
        import os
        import urllib.request
        
        # Create models directory if it doesn't exist
        mediapipe_path = os.path.dirname(mediapipe.__file__)
        models_dir = os.path.join(mediapipe_path, 'tasks', 'models')
        os.makedirs(models_dir, exist_ok=True)
        model_path = os.path.join(models_dir, 'face_landmarker.task')
        
        # Download model if it doesn't exist
        if not os.path.exists(model_path):
            print("📥 Downloading MediaPipe face landmarker model...")
            model_url = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
            try:
                urllib.request.urlretrieve(model_url, model_path)
                print("✅ Model downloaded successfully")
            except Exception as e:
                print(f"❌ Failed to download model: {e}")
                print("Please download manually from:")
                print("https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task")
                print(f"Save to: {model_path}")
                sys.exit(1)
        
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )
        face_landmarker = vision.FaceLandmarker.create_from_options(options)
        print("✅ FaceLandmarker initialized")
    except Exception as e:
        print(f"❌ Failed to initialize FaceLandmarker: {e}")
        print("MediaPipe Tasks API requires a model file.")
        print("Please ensure MediaPipe is properly installed: pip install --upgrade mediapipe")
        sys.exit(1)
    
    if not args.test_camera:
        print("✅ Face tracking initialized")
    print("Press ESC or close window to exit")
    if args.test_camera:
        print("🧪 TEST MODE: Showing raw camera feed")
    
    running = True
    face_detected = False
    frame_count = 0
    last_debug_time = 0
    
    try:
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_f:
                        # Toggle fullscreen with 'F' key
                        if is_fullscreen:
                            screen = pygame.display.set_mode((args.width, args.height))
                            screen_width, screen_height = screen.get_size()
                            is_fullscreen = False
                            print(f"Switched to window mode: {screen_width}x{screen_height}")
                        else:
                            screen_info = pygame.display.Info()
                            screen = pygame.display.set_mode(
                                (screen_info.current_w, screen_info.current_h),
                                pygame.FULLSCREEN
                            )
                            screen_width, screen_height = screen.get_size()
                            is_fullscreen = True
                            print(f"Switched to fullscreen: {screen_width}x{screen_height}")
            
            # Get frame
            frame = get_frame(camera, webcam, args.debug if args else False)
            if frame is None:
                if args.debug:
                    print("⚠️  No frame captured")
                continue
            
            frame_count += 1
            
            # Debug output every 30 frames (~1 second at 30fps)
            if args.debug and frame_count % 30 == 0:
                print(f"📊 Frame {frame_count}: shape={frame.shape}, dtype={frame.dtype}")
            
            # TEST MODE: Show raw camera feed
            if args.test_camera:
                # Clear screen
                screen.fill(BLACK)
                
                # Convert frame to pygame surface
                # Frame is RGB numpy array, convert to pygame surface
                try:
                    # Ensure frame is uint8
                    if frame.dtype != np.uint8:
                        frame = (frame * 255).astype(np.uint8) if frame.max() <= 1.0 else frame.astype(np.uint8)
                    
                    # Convert RGB to surface (pygame uses (width, height) format)
                    frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
                    
                    # Scale to fit screen while maintaining aspect ratio
                    frame_w, frame_h = frame.shape[1], frame.shape[0]
                    scale_w = screen_width / frame_w
                    scale_h = screen_height / frame_h
                    scale = min(scale_w, scale_h)
                    new_w = int(frame_w * scale)
                    new_h = int(frame_h * scale)
                    
                    frame_surface = pygame.transform.scale(frame_surface, (new_w, new_h))
                    
                    # Center on screen
                    x_offset = (screen_width - new_w) // 2
                    y_offset = (screen_height - new_h) // 2
                    screen.blit(frame_surface, (x_offset, y_offset))
                    
                    # Show frame info
                    font = pygame.font.Font(None, 24)
                    info_text = f"Frame: {frame_count} | Camera: {frame_w}x{frame_h} | Screen: {screen_width}x{screen_height}"
                    text = font.render(info_text, True, (255, 255, 255))
                    screen.blit(text, (10, 10))
                except Exception as e:
                    # Fallback: show error
                    font = pygame.font.Font(None, 36)
                    error_text = f"Error displaying frame: {str(e)}"
                    text = font.render(error_text, True, (255, 0, 0))
                    screen.blit(text, (20, 20))
                    if args.debug:
                        print(f"❌ Error in test mode: {e}")
                
                pygame.display.flip()
                clock.tick(FPS)
                continue
            
            # Normal mode: Face detection
            try:
                # Convert frame to MediaPipe Image format
                # MediaPipe expects RGB format
                mp_image = MPImage(image_format=mp.ImageFormat.SRGB, data=frame)
                
                # Process with MediaPipe
                detection_result = face_landmarker.detect(mp_image)
                
                # Clear screen with black background
                screen.fill(BLACK)
                
                # Draw face landmarks if detected
                if detection_result.face_landmarks:
                    face_detected = True
                    # Get first face's landmarks
                    landmarks = detection_result.face_landmarks[0]
                    # Convert to list format for drawing function
                    landmark_list = [type('Landmark', (), {'x': p.x, 'y': p.y, 'z': p.z})() for p in landmarks]
                    draw_face_landmarks(screen, landmark_list, screen_width, screen_height)
                    
                    if args.debug and frame_count % 30 == 0:
                        print(f"✅ Face detected! {len(landmarks)} landmarks")
                else:
                    face_detected = False
                    # Show "No face detected" text
                    font = pygame.font.Font(None, 36)
                    text = font.render("No face detected", True, (255, 0, 0))
                    screen.blit(text, (20, 20))
                    
                    if args.debug and frame_count % 30 == 0:
                        print("❌ No face detected")
                
            except Exception as e:
                if args.debug:
                    print(f"❌ Error processing frame: {e}")
                # Show error on screen
                screen.fill(BLACK)
                font = pygame.font.Font(None, 24)
                error_text = f"Error: {str(e)[:50]}"
                text = font.render(error_text, True, (255, 0, 0))
                screen.blit(text, (20, 20))
            
            # Update display
            pygame.display.flip()
            clock.tick(FPS)
    
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        # Cleanup
        if camera:
            camera.stop()
        if webcam:
            webcam.release()
        pygame.quit()
        print("✅ Cleanup complete")

if __name__ == "__main__":
    main()

