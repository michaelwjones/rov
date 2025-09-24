#!/usr/bin/env python3
"""
USB Camera Livestream Test for Raspberry Pi ROV Controller
Detects camera capabilities and streams video at optimal settings.
"""

import cv2
import time
import sys

def detect_camera_capabilities(cap):
    """Detect and display camera capabilities"""
    print("=== Camera Capabilities Detection ===")

    # Get current settings
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    print(f"Default Resolution: {width}x{height}")
    print(f"Default FPS: {fps}")
    print(f"Aspect Ratio: {width/height:.2f}:1")

    # Test common resolutions to find supported ones
    test_resolutions = [
        (1920, 1080),  # 1080p
        (1280, 720),   # 720p
        (640, 480),    # VGA
        (320, 240),    # QVGA
    ]

    supported_resolutions = []
    print("\n=== Testing Resolutions ===")

    for w, h in test_resolutions:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

        # Read a frame to test if resolution is actually set
        ret, frame = cap.read()
        if ret:
            actual_w = frame.shape[1]
            actual_h = frame.shape[0]

            if actual_w == w and actual_h == h:
                supported_resolutions.append((w, h))
                print(f"✓ {w}x{h} - SUPPORTED")
            else:
                print(f"✗ {w}x{h} - Not supported (got {actual_w}x{actual_h})")
        else:
            print(f"✗ {w}x{h} - Failed to capture")

    # Reset to default
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    return supported_resolutions, width, height, fps

def test_framerate(cap, target_fps=30):
    """Test and set optimal framerate"""
    print(f"\n=== Testing {target_fps}FPS ===")

    # Try to set target FPS
    cap.set(cv2.CAP_PROP_FPS, target_fps)

    # Measure actual FPS over 30 frames
    frame_count = 0
    start_time = time.time()
    test_frames = 30

    while frame_count < test_frames:
        ret, frame = cap.read()
        if ret:
            frame_count += 1
        else:
            print("Failed to read frame during FPS test")
            return False

    end_time = time.time()
    actual_fps = test_frames / (end_time - start_time)

    print(f"Requested FPS: {target_fps}")
    print(f"Actual FPS: {actual_fps:.2f}")

    return actual_fps >= (target_fps * 0.8)  # Accept if within 80% of target

def main():
    print("ROV Camera Livestream Test")
    print("Press 'q' to quit, 's' to take screenshot")
    print("=" * 40)

    # Initialize camera with V4L2 backend (recommended for Raspberry Pi)
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

    if not cap.isOpened():
        print("V4L2 backend failed, trying default backend...")
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            # Try other camera indices
            for i in range(1, 5):
                print(f"Trying camera index {i}...")
                cap = cv2.VideoCapture(i, cv2.CAP_V4L2)
                if cap.isOpened():
                    print(f"Camera found at index {i}")
                    break
            else:
                print("ERROR: No USB camera found!")
                print("Make sure your camera is connected and recognized by the system.")
                print("You can check with: python3 camera_debug.py")
                return 1

    try:
        # Detect capabilities
        supported_res, default_w, default_h, default_fps = detect_camera_capabilities(cap)

        # Test framerate (your camera supports 15fps native)
        fps_ok = test_framerate(cap, 15)
        if not fps_ok:
            print("Warning: Even 15fps may not be achievable")
            test_framerate(cap, 10)  # Fallback to 10fps

        # Use best available resolution
        if supported_res:
            best_res = max(supported_res, key=lambda x: x[0] * x[1])
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, best_res[0])
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, best_res[1])
            print(f"\nUsing resolution: {best_res[0]}x{best_res[1]}")

        print("\n=== Starting Livestream ===")
        print("Camera window should open. Press 'q' to quit.")

        frame_count = 0
        fps_start = time.time()

        while True:
            ret, frame = cap.read()

            if not ret:
                print("Failed to read frame from camera")
                break

            # Calculate and display FPS
            frame_count += 1
            if frame_count % 30 == 0:
                fps_end = time.time()
                measured_fps = 30 / (fps_end - fps_start)
                fps_start = fps_end
                print(f"Live FPS: {measured_fps:.1f}")

            # Add frame info overlay
            h, w = frame.shape[:2]
            cv2.putText(frame, f"Resolution: {w}x{h}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Frame: {frame_count}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, "Press 'q' to quit", (10, h-20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # Display frame
            cv2.imshow('ROV Camera Test', frame)

            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                screenshot_name = f"rov_camera_test_{int(time.time())}.jpg"
                cv2.imwrite(screenshot_name, frame)
                print(f"Screenshot saved: {screenshot_name}")

        print("Livestream ended successfully")
        return 0

    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    sys.exit(main())