#!/usr/bin/env python3
"""
Camera Debug Script for Raspberry Pi
Tests different backends and provides detailed diagnostics.
"""

import cv2
import os
import subprocess
import sys

def run_command(cmd):
    """Run shell command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return "", str(e)

def check_system_camera_detection():
    """Check if system detects the camera"""
    print("=== System Camera Detection ===")

    # Check USB devices
    print("\n1. USB Devices:")
    stdout, stderr = run_command("lsusb")
    if stdout:
        for line in stdout.split('\n'):
            if any(word in line.lower() for word in ['camera', 'webcam', 'video', 'uvc']):
                print(f"  📷 {line}")
    else:
        print("  No USB devices found or lsusb not available")

    # Check video devices
    print("\n2. Video Device Files:")
    stdout, stderr = run_command("ls -la /dev/video*")
    if stdout and "No such file" not in stdout:
        print(f"  {stdout}")
    else:
        print("  ❌ No /dev/video* devices found")
        return False

    # Check v4l2 devices
    print("\n3. V4L2 Device Info:")
    stdout, stderr = run_command("v4l2-ctl --list-devices")
    if stdout:
        print(f"  {stdout}")
    else:
        print("  ⚠️  v4l2-ctl not available (install with: sudo apt install v4l-utils)")

    return True

def test_opencv_backends():
    """Test different OpenCV backends"""
    print("\n=== OpenCV Backend Testing ===")

    backends = [
        (cv2.CAP_V4L2, "V4L2"),
        (cv2.CAP_GSTREAMER, "GStreamer"),
        (cv2.CAP_FFMPEG, "FFmpeg"),
        (cv2.CAP_ANY, "Any/Default")
    ]

    working_backends = []

    for backend_id, backend_name in backends:
        print(f"\nTesting {backend_name} backend...")

        for device_id in range(5):  # Test device IDs 0-4
            try:
                cap = cv2.VideoCapture(device_id, backend_id)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        h, w = frame.shape[:2]
                        print(f"  ✅ Device {device_id}: {w}x{h} - SUCCESS")
                        working_backends.append((backend_id, backend_name, device_id))
                        cap.release()
                        break
                    else:
                        print(f"  ⚠️  Device {device_id}: Opened but no frame")
                cap.release()
            except Exception as e:
                print(f"  ❌ Device {device_id}: Error - {e}")
        else:
            print(f"  ❌ {backend_name}: No working devices found")

    return working_backends

def test_camera_with_backend(backend_id, device_id, backend_name):
    """Test camera with specific backend"""
    print(f"\n=== Testing Camera: {backend_name} Device {device_id} ===")

    cap = cv2.VideoCapture(device_id, backend_id)

    if not cap.isOpened():
        print("❌ Failed to open camera")
        return False

    # Get camera properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    print(f"Resolution: {width}x{height}")
    print(f"FPS: {fps}")

    # Test frame capture
    print("Testing frame capture...")
    for i in range(5):
        ret, frame = cap.read()
        if ret:
            print(f"  Frame {i+1}: ✅ {frame.shape}")
        else:
            print(f"  Frame {i+1}: ❌ Failed")
            break
    else:
        print("✅ Camera working properly!")
        cap.release()
        return True

    cap.release()
    return False

def main():
    print("ROV Camera Debug Tool")
    print("=" * 50)

    # Check system detection
    if not check_system_camera_detection():
        print("\n❌ No cameras detected by system!")
        print("Make sure your USB camera is connected.")
        return 1

    # Test OpenCV backends
    working_backends = test_opencv_backends()

    if not working_backends:
        print("\n❌ No working camera backends found!")
        print("\nTroubleshooting suggestions:")
        print("1. Check camera connection: lsusb")
        print("2. Check permissions: ls -la /dev/video*")
        print("3. Try different USB port")
        print("4. Install camera drivers if needed")
        return 1

    print(f"\n✅ Found {len(working_backends)} working camera configuration(s):")
    for backend_id, backend_name, device_id in working_backends:
        print(f"  - {backend_name} backend, device {device_id}")

    # Test the first working backend
    backend_id, backend_name, device_id = working_backends[0]
    success = test_camera_with_backend(backend_id, device_id, backend_name)

    if success:
        print(f"\n🎉 Recommended configuration:")
        print(f"   Backend: {backend_name} (cv2.CAP_V4L2 = {cv2.CAP_V4L2})")
        print(f"   Device ID: {device_id}")
        print(f"   Usage: cv2.VideoCapture({device_id}, {backend_id})")

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())