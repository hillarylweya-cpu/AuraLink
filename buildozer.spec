[app]

# Application title
title = AuraLink

# Package name
package.name = auralink

# Package domain
package.domain = org.auralink

# Application source directory
source.dir = .

# Source code patterns
source.include_exts = py,png,jpg,kv,atlas,db,gguf

# Exclude patterns
source.exclude_exts = spec

# Version
version = 1.0.0

# Requirements
requirements = python3,kivy,aiosqlite,websockets,pynacl,zeroconf,bleak,opencv-python,pyaudio

# Permissions
permissions = INTERNET,CAMERA,RECORD_AUDIO,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,BLUETOOTH,BLUETOOTH_ADMIN,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION

# Orientation
orientation = portrait

# Icon
icon.filename = %(source.dir)s/media/icon.png

[buildozer]

# Log level
log_level = 2

# Display warnings
warn_on_root = 1

[app:android]

# Android API level
android.api = 33

# Android minimum API
android.minapi = 21

# Android NDK version
android.ndk = 25b

# Android SDK version
android.sdk = 33

# Gradle dependencies
android.gradle_dependencies = 

# Java classes
android.add_src =

# Broadcast receivers
android.broadcast_receivers =

# Services
android.services =

# Architectures
android.archs = arm64-v8a,armeabi-v7a

# Features
android.features = android.hardware.camera,android.hardware.camera.autofocus,android.hardware.microphone

# Permissions
android.permissions = INTERNET,CAMERA,RECORD_AUDIO,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,BLUETOOTH,BLUETOOTH_ADMIN,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION

# Uses features
android.uses_features = android.hardware.camera,android.hardware.camera.autofocus,android.hardware.microphone

# Meta data
android.meta_data =

# Application argument
android.arguments =

# Gradle options
android.gradle_options = org.gradle.jvmargs=-Xmx2048m
