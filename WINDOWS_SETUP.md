# Threads Bot - Windows Setup Guide

## Prerequisites

1. **Python Installation**
   - Download Python 3.9 from [python.org](https://www.python.org/downloads/release/python-3913/)
   - During installation, make sure to check "Add Python to PATH"
   - Choose "Customize installation" and ensure "tcl/tk and IDLE" is selected

2. **Android SDK Platform Tools**
   - Download from [Android SDK Platform Tools](https://developer.android.com/tools/releases/platform-tools)
   - Extract the zip file to a location like `C:\Android\platform-tools`
   - Add the platform-tools directory to your system PATH:
     1. Open System Properties (Win + Pause/Break)
     2. Click "Advanced system settings"
     3. Click "Environment Variables"
     4. Under "System variables", find and select "Path"
     5. Click "Edit"
     6. Click "New"
     7. Add the path to platform-tools (e.g., `C:\Android\platform-tools`)
     8. Click "OK" on all windows

## Installation Steps

1. **Download the Bot**
   - Download the bot files
   - Extract to a location like `C:\ThreadsBot`

2. **Install Dependencies**
   - Open Command Prompt as Administrator
   - Navigate to the bot directory:
     ```
     cd C:\ThreadsBot
     ```
   - Install required packages:
     ```
     pip install -r requirements.txt
     ```

3. **Configure Android Devices**
   - Connect your Android device via USB
   - Enable Developer Options on your device:
     1. Go to Settings
     2. Scroll to "About phone"
     3. Tap "Build number" 7 times
   - Enable USB Debugging:
     1. Go back to Settings
     2. Find "Developer options"
     3. Enable "USB debugging"
   - When prompted on your device, allow USB debugging

4. **Run the Bot**
   - Double-click `run_bot.bat`
   - Or open Command Prompt and run:
     ```
     python bot_gui.py
     ```

## Troubleshooting

1. **ADB not found**
   - Verify platform-tools is in your PATH
   - Open Command Prompt and type `adb version`
   - If not found, recheck PATH settings

2. **Python not found**
   - Verify Python is in your PATH
   - Open Command Prompt and type `python --version`
   - If not found, reinstall Python with "Add to PATH" option

3. **Device not detected**
   - Check USB connection
   - Verify USB debugging is enabled
   - Try different USB ports
   - Install device drivers if prompted

4. **Missing dependencies**
   - Run `pip install -r requirements.txt` again
   - If errors occur, try installing packages individually

## Support

For additional help or issues:
1. Check the troubleshooting section
2. Ensure all prerequisites are installed
3. Verify device connection with `adb devices`
4. Check Windows Event Viewer for system errors 