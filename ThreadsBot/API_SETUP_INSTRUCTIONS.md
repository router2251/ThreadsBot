# API Key Setup Instructions

## Your API Key is Suspended

The API key you provided (`AIzaSyBisaaQ1dsEELVRYKFEIMQId-cR97So_X8`) has been suspended by Google. You need to get a new one.

## How to Get a New API Key

1. **Go to Google AI Studio**: https://makersuite.google.com/app/apikey
2. **Sign in** with your Google account
3. **Click "Create API Key"**
4. **Copy the new API key**

## How to Update Your Code

1. **Open `android_engagement.py`**
2. **Find line 15**: `GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"`
3. **Replace** `"YOUR_GEMINI_API_KEY_HERE"` with your new API key
4. **Save the file**

## Test Your API Key

Run this command to test if your new API key works:

```bash
py test_api.py
```

If it works, you should see:
```
✅ Gemini API is working correctly!
```

## Important Notes

- Keep your API key secret and don't share it publicly
- The API key is used for AI-powered engagement responses
- Without a valid API key, the bot will use fallback responses instead of AI-generated ones 