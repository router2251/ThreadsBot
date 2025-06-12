import requests
import json

# Replace this with your actual Gemini API key from https://makersuite.google.com/app/apikey
GEMINI_API_KEY = "AIzaSyA2TYVMt3yzGr5TRtiSnp7mNepGxTaQZJM"

def test_gemini_api():
    """Test the Gemini API with a simple request."""
    if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        print("❌ Please replace 'YOUR_GEMINI_API_KEY_HERE' with your actual Gemini API key")
        print("📝 Get your API key from: https://makersuite.google.com/app/apikey")
        return False
    
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": "Hello! Please respond with 'API is working' if you can see this message."
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                text = result['candidates'][0]['content']['parts'][0]['text']
                print(f"\n✅ API Response: {text}")
                print("✅ Gemini API is working correctly!")
                return True
            else:
                print("❌ No response content found")
                return False
        else:
            print(f"❌ API request failed with status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

if __name__ == "__main__":
    print("Testing Gemini API...")
    test_gemini_api() 