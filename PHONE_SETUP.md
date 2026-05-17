# AuraLink Phone Installation Guide

## 📱 Quick Start

AuraLink is a mobile-first communication app. Follow these steps to build and install it on your phone.

## Prerequisites

### Windows
- Python 3.8+
- Java Development Kit (JDK 11)
- Android SDK
- Git

```bash
# Install JDK
choco install openjdk11

# Install Android SDK
choco install android-sdk
```

### macOS
- Python 3.8+
- Xcode Command Line Tools
- JDK 11
- Android SDK

```bash
# Install JDK
brew install openjdk@11

# Install Android SDK
brew install android-sdk
```

### Linux (Ubuntu/Debian)
- Python 3.8+
- Build essentials
- JDK 11
- Android SDK

```bash
# Install dependencies
sudo apt-get install python3 python3-pip build-essential git openjdk-11-jdk

# Install Android SDK
cd ~
wget https://dl.google.com/android/repository/commandlinetools-linux-9123335_latest.zip
unzip commandlinetools-linux-9123335_latest.zip

export ANDROID_SDK_ROOT=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_SDK_ROOT/cmdline-tools/tools/bin
export PATH=$PATH:$ANDROID_SDK_ROOT/platform-tools

sdkmanager --install "platforms;android-33" "build-tools;33.0.0" "ndk;25.1.8937393"
```

## Installation Steps

### 1. Clone Repository

```bash
git clone https://github.com/hillarylweya-cpu/AuraLink.git
cd AuraLink
```

### 2. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install buildozer cython
```

### 3. Configure Buildozer (Optional)

Edit `buildozer.spec` if needed:

```bash
buildozer init  # Only if buildozer.spec doesn't exist
```

### 4. Build APK

```bash
# First build (takes 10-30 minutes)
buildozer android debug

# Subsequent builds (faster)
buildozer android debug --skip-update
```

### 5. Install on Phone

#### Option A: USB Connection

```bash
# Enable USB debugging on your Android phone:
# Settings > Developer Options > USB Debugging

# Connect phone via USB
adb install -r bin/auralink-1.0-debug.apk
```

#### Option B: Manual Install

1. Transfer `bin/auralink-1.0-debug.apk` to your phone
2. Tap the file to install
3. Grant permissions when prompted

#### Option C: Email/Download

1. Download APK from releases
2. Open file manager on phone
3. Locate and tap APK file
4. Install

## Configuration

### Server Connection

Edit `networking/client.py` to set your server:

```python
SERVER = "ws://your-server-ip:8765"  # Change this
```

### Database Location

Database automatically stores in app's data directory:
- `/data/data/org.auralink/files/aura.db`

## Troubleshooting

### Build Errors

**Error: `buildozer: command not found`**
```bash
pip install --upgrade buildozer
```

**Error: Java not found**
```bash
# Windows
set JAVA_HOME=C:\Program Files\Java\jdk-11

# macOS
export JAVA_HOME=$(/usr/libexec/java_home -v 11)

# Linux
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
```

**Error: Android SDK not found**
```bash
export ANDROID_SDK_ROOT=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_SDK_ROOT/cmdline-tools/tools/bin
export PATH=$PATH:$ANDROID_SDK_ROOT/platform-tools
```

### Runtime Errors

**App crashes on startup**
1. Check phone logs: `adb logcat | grep auralink`
2. Ensure permissions are granted
3. Check database permissions

**Can't connect to server**
1. Ensure server is running
2. Check firewall settings
3. Verify IP address in `networking/client.py`
4. Test connection: `ping server-ip`

**Messages not syncing**
1. Check internet connection
2. Verify server is accessible
3. Check app logs: `adb logcat`
4. Restart app

### ADB Commands

```bash
# List connected devices
adb devices

# View app logs
adb logcat | grep auralink

# Clear app data
adb shell pm clear org.auralink

# Uninstall app
adb uninstall org.auralink

# Push file to phone
adb push file.txt /sdcard/

# Pull file from phone
adb pull /sdcard/file.txt .
```

## Development

### Test on Emulator

```bash
# Create emulator
android create avd -n AuraLink -t android-33 -c 512M

# Start emulator
emulator -avd AuraLink

# Build and install
buildozer android debug
adb install -r bin/auralink-1.0-debug.apk
```

### Debug Mode

Edit `phone_app.py`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)  # Enable debug logs
```

View logs:
```bash
adb logcat -v threadtime | grep auralink
```

## Features

✅ Send/Receive encrypted messages
✅ Offline message queue
✅ Auto-sync when online
✅ End-to-end encryption
✅ Message history
✅ Settings panel
✅ Touch-optimized UI
✅ Background sync

## Next Steps

1. **Build APK**: Follow steps 1-4 above
2. **Install**: Use Option A, B, or C from step 5
3. **Configure**: Set server IP in `networking/client.py`
4. **Start using**: Open app and send messages

## Support

- GitHub Issues: https://github.com/hillarylweya-cpu/AuraLink/issues
- Documentation: https://github.com/hillarylweya-cpu/AuraLink
- Discord: (Coming soon)

## License

MIT License - See LICENSE file
