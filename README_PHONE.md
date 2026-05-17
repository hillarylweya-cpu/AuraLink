# AuraLink Mobile - Communication without barriers 🔗

**AuraLink** is a decentralized, end-to-end encrypted messaging application designed for barrier-free communication on mobile devices.

## ✨ Features

### Core Features
- 🔐 **End-to-End Encryption** - Messages secured with NaCl cryptography
- 💬 **Instant Messaging** - Real-time message delivery via WebSocket
- 📴 **Offline Support** - Messages queued offline, sent when connection restored
- 🔄 **Auto-Sync** - Automatic background synchronization
- 📱 **Mobile-First UI** - Touch-optimized Kivy interface
- 📊 **Message History** - All messages stored locally
- ⚙️ **Settings** - Configurable app settings
- 🎯 **Zero Setup** - Works out of the box

### Advanced Features
- 🎤 **Voice** - Audio message support
- 📹 **Video** - Video streaming capability
- 📎 **File Transfer** - Secure file sharing
- 🔍 **Message Search** - Find past conversations
- 👥 **Group Chat** - (Coming soon)
- 🌍 **Offline-First** - Works without internet

## 📥 Installation

### Quick Download

**Pre-built APK**: [Download Latest Release](https://github.com/hillarylweya-cpu/AuraLink/releases)

**Requirements**: Android 5.0+ (API 21)

### Build from Source

```bash
# 1. Clone
git clone https://github.com/hillarylweya-cpu/AuraLink.git
cd AuraLink

# 2. Install
pip install buildozer cython
pip install -r requirements.txt

# 3. Build
buildozer android debug

# 4. Install
adb install -r bin/auralink-1.0-debug.apk
```

See [PHONE_SETUP.md](PHONE_SETUP.md) for detailed instructions.

## 🚀 Usage

### First Run

1. **Open App** - Tap AuraLink icon
2. **Grant Permissions** - Allow internet, camera, microphone
3. **Connect** - App automatically connects to server
4. **Start Messaging** - Type and send messages

### Send Message

1. Type message in input box
2. Tap "Send" button
3. Message appears locally
4. When online, message is sent immediately
5. When offline, message is queued

### Manage Messages

- **Sync**: Manually sync pending messages (Sync button)
- **Clear**: Clear message display (Clear button)
- **Settings**: View app settings (Settings button)

### Server Configuration

Edit `networking/client.py`:

```python
SERVER = "ws://your-server.com:8765"
```

Then rebuild APK:

```bash
buildozer android debug
```

## 🔧 Architecture

```
AuraLink/
├── phone_app.py              # Mobile UI (Kivy)
├── database/
│   └── db.py                # SQLite database
├── networking/
│   ├── client.py            # WebSocket client
│   └── server.py            # (Optional) Server
├── messaging/
│   ├── queue.py             # Offline queue
│   └── sync.py              # Auto-sync engine
├── security/
│   └── encryption.py        # NaCl encryption
├── media/                   # Icons & assets
├── ui/                      # UI definitions
├── buildozer.spec           # Build config
└── requirements.txt         # Dependencies
```

## 🏗️ Building Custom APK

### Customize App

1. **Change Title**: Edit `buildozer.spec` `title = YourApp`
2. **Change Package**: Edit `package.name = yourapp`
3. **Add Icon**: Place icon at `media/icon.png` (512x512)
4. **Modify UI**: Edit `phone_app.py` build() method

### Build Release APK

```bash
# Generate keystore
keytool -genkey -v -keystore release-key.keystore -keyalg RSA -keysize 2048 -validity 10000 -alias release

# Build release
buildozer android release

# Sign APK
jarsigner -verbose -sigalg MD5withRSA -digestalg SHA1 -keystore release-key.keystore bin/auralink-1.0-release-unsigned.apk release

# Align APK
zipalign -v 4 bin/auralink-1.0-release-unsigned.apk bin/auralink-1.0-release.apk
```

## 📊 Technical Specs

| Feature | Details |
|---------|----------|
| **Platform** | Android 5.0+ (API 21-33) |
| **Architecture** | ARM64, ARMv7 |
| **Size** | ~50 MB |
| **RAM** | 100 MB minimum |
| **Storage** | 50 MB minimum |
| **Network** | WiFi or mobile data |
| **Encryption** | NaCl (Libsodium) |
| **Protocol** | WebSocket (ws://) |

## 🔐 Security

- **End-to-End Encryption**: All messages encrypted with NaCl
- **No Server Storage**: Messages only stored locally
- **Open Source**: Full source code available for audit
- **No Tracking**: No analytics or telemetry
- **Privacy First**: No account required

## 🐛 Troubleshooting

### App Won't Install
- Enable "Unknown Sources" in Settings > Security
- Check Android version (5.0+)
- Free up storage space (50 MB+)

### App Crashes on Start
- Check device logs: `adb logcat`
- Reinstall app: `adb uninstall org.auralink`
- Clear cache: Settings > Apps > AuraLink > Storage > Clear Cache

### Can't Send Messages
- Check internet connection
- Verify server is running
- Check firewall settings
- Restart app

### Messages Not Syncing
- Tap "Sync" button manually
- Check connection
- Restart app
- Reinstall app

For more help, see [PHONE_SETUP.md](PHONE_SETUP.md) or open an [issue](https://github.com/hillarylweya-cpu/AuraLink/issues).

## 📚 Documentation

- [Phone Setup Guide](PHONE_SETUP.md) - Detailed installation
- [API Docs](docs/api.md) - Server API reference
- [Developer Guide](docs/development.md) - Building from source

## 📝 License

MIT License - Free for personal and commercial use

## 🙌 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md)

## 📞 Contact

- **GitHub**: [@hillarylweya-cpu](https://github.com/hillarylweya-cpu)
- **Issues**: [Report Bug](https://github.com/hillarylweya-cpu/AuraLink/issues)
- **Discussions**: [Join Discussion](https://github.com/hillarylweya-cpu/AuraLink/discussions)

---

**Made with ❤️ by Hillary Lweya**

*Communication without barriers.*
