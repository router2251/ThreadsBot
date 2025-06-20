# ThreadsBot

An automated engagement bot for the Threads app that uses UIAutomator2 to interact with Android devices. The bot scans for viral posts, analyzes user profiles with AI, and generates flirty female responses to male USA users.

## Features

- **Viral Post Detection**: Scans for posts with high engagement (50+ likes by default)
- **AI Profile Analysis**: Uses Google Gemini API to analyze user profiles and determine gender/location
- **Smart Username Detection**: Finds usernames in comments with advanced filtering
- **Timestamp Protection**: Prevents timestamps (4m, 32m, 3m) from being interpreted as massive like counts
- **Targeted Engagement**: Only engages with male USA users
- **Flirty Response Generation**: Creates contextual flirty responses using AI
- **Safe Navigation**: Multiple fallback methods for UI navigation

## Recent Critical Fixes

### ✅ Timestamp Detection Bug (Fixed)
- **Issue**: Bot was interpreting timestamps like "4m", "32m", "3m" as 4 million, 32 million, 3 million likes
- **Fix**: Enhanced `extract_number_from_text()` method with robust regex patterns to block all time formats
- **Impact**: Prevents false viral post detection and improves accuracy

### ✅ AI Integration (Working)
- **API**: Google Gemini API with working key
- **Features**: Real AI-generated responses instead of fallback messages
- **Analysis**: Proper gender and location detection

### ✅ Navigation Improvements
- **Back Navigation**: Prioritizes top-left arrow (navigation_bar_back_button)
- **Post Detection**: Enhanced post detail view detection
- **Error Handling**: Multiple fallback methods for robust operation

## Configuration

### Minimum Engagement Thresholds
- **Viral Posts**: 50+ likes (configurable)
- **Comments**: Processes up to 5 commenters per post
- **Filtering**: Excludes post authors and system accounts

### Target Demographics
- **Gender**: Male users (with female exclusion patterns)
- **Location**: USA users (defaults to USA unless clearly non-USA)
- **Language**: English content

## Installation

1. **Clone Repository**
   ```bash
   git clone https://github.com/router2251/ThreadsBot.git
   cd ThreadsBot
   ```

2. **Install Dependencies**
   ```bash
   pip install uiautomator2 requests
   ```

3. **Setup Android Device**
   - Enable USB Debugging
   - Install UIAutomator2 server: `python -m uiautomator2 init`
   - Connect device via USB or WiFi

4. **Configure API Keys**
   - Set Google Gemini API key in the code
   - Update device configuration in `android_config.json`

## Usage

### Basic Usage
```bash
python clean_bot.py
```

### Testing Timestamp Detection
```bash
python test_timestamp_detection.py
```

## File Structure

- `clean_bot.py` - Main bot implementation with all fixes
- `test_timestamp_detection.py` - Test script for timestamp detection
- `android_config.json` - Device configuration
- `bot_config.json` - Bot settings and thresholds

## Key Classes

### `AIAnalyzer`
- Handles Google Gemini API integration
- Analyzes user profiles for gender/location
- Generates contextual flirty responses

### `AndroidEngagement`
- Main bot logic and UI automation
- Viral post detection and processing
- Comment analysis and user engagement

## Debugging Features

- **Comprehensive Logging**: Detailed logs for all operations
- **UI Element Dumping**: Debug mode for UI analysis
- **Engagement Tracking**: Monitors successful interactions
- **Error Recovery**: Automatic fallback mechanisms

## Background Agents Support

This repository is configured for background agents with:
- ✅ Public GitHub repository
- ✅ Regular commits with descriptive messages
- ✅ Comprehensive documentation
- ✅ Working codebase with recent fixes

## Recent Commits

- `Fix critical timestamp detection bug` - Prevents 4m, 32m, 3m from being interpreted as millions
- `Enhanced AI integration` - Working Gemini API with real responses
- `Improved navigation` - Better post detection and back navigation

## Safety Features

- **Rate Limiting**: Prevents excessive API calls
- **Error Handling**: Graceful failure recovery
- **Content Filtering**: Avoids inappropriate content
- **User Validation**: Ensures target demographic accuracy

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational purposes. Use responsibly and in accordance with Threads' terms of service.

## Support

For issues or questions:
1. Check the logs for detailed error information
2. Run the test scripts to verify functionality
3. Review the recent commits for known fixes
4. Open an issue on GitHub with detailed information

---

**Note**: This bot requires proper Android device setup and API keys to function. Always test in a controlled environment before production use.
#   T h r e a d s B o t 
 
 