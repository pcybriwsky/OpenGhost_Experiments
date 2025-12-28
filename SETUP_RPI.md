# Raspberry Pi Setup Instructions

This guide will help you set up the OpenGhost project on your Raspberry Pi.

## Prerequisites

- Raspberry Pi 5 (or compatible version)
- Raspberry Pi OS Bookworm (comes with Python 3.11)
- SD card with OS installed
- Display configured (e.g., HyperPixel 4.0 Square)

## Step-by-Step Setup

### 1. Initial System Setup

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y
```

### 2. Install Java (Required for py5)

```bash
sudo apt install default-jdk -y
```

Verify installation:
```bash
java -version
```

### 3. Clone/Transfer Repository

If you haven't already, clone this repository or transfer it to your Pi:
```bash
cd ~
git clone <your-repo-url>
cd OpenGhost_Experiments
```

### 4. Create Virtual Environment

```bash
# Create venv with system site packages (important for hardware access)
python3 -m venv .venv --system-site-packages

# Activate the virtual environment
source .venv/bin/activate
```

### 5. Install Python Dependencies

```bash
# Install core dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 6. Camera Setup (Optional - Only if using camera-based scripts)

If you plan to use camera-based scripts (`boids_finger_tracking.py` or `face_tracking.py`):

```bash
# Install system dependencies
sudo apt install libcap-dev libcamera-apps python3-libcamera python3-picamera2 -y

# Downgrade numpy (required for picamera2 compatibility)
pip install "numpy==1.26.4"

# Install picamera2
pip install picamera2
```

**Note:** The numpy downgrade is important - picamera2 doesn't work with numpy 2.0+

## Running the Scripts

### Basic Setup for Each Terminal Session

```bash
# Navigate to project directory
cd ~/OpenGhost_Experiments  # or wherever you cloned it

# Activate virtual environment
source .venv/bin/activate

# Set display (if running in a new terminal session)
export DISPLAY=:0.0
```

### Run Scripts

```bash
# Boids simulation (no camera needed)
python3 boids.py

# Lorenz attractor visualization
python3 lorenz_attractor.py

# Snowflakes visualization (no camera needed)
python3 snowflakes.py

# Boids with finger tracking (requires camera)
python3 boids_finger_tracking.py

# Face tracking visualization (requires camera)
python3 face_tracking.py
# Or with options:
python3 face_tracking.py --fullscreen  # Fullscreen mode
python3 face_tracking.py --test-camera  # Test camera feed
python3 face_tracking.py --debug       # Enable debug output
```

## Troubleshooting

### Display Issues
- Make sure your display is properly configured according to manufacturer instructions
- Verify display is enabled: `sudo raspi-config` → Display Options
- Check if display is detected: `xrandr`

### Java Issues
- If py5 fails to start, verify Java is installed: `java -version`
- Try reinstalling: `sudo apt install --reinstall default-jdk`

### Camera Issues
- Verify camera is enabled: `sudo raspi-config` → Interface Options → Camera
- Test camera: `libcamera-hello`
- Check numpy version: `pip show numpy` (should be 1.26.4 for camera scripts)

### Virtual Environment Issues
- Always activate the venv before running scripts: `source .venv/bin/activate`
- If packages aren't found, reinstall: `pip install -r requirements.txt`

## Quick Reference

**Essential commands for each session:**
```bash
cd ~/OpenGhost_Experiments
source .venv/bin/activate
export DISPLAY=:0.0
python3 boids.py  # or your script of choice
```

