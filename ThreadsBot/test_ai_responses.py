#!/usr/bin/env python3
"""
Test script to verify AI-generated responses are working
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clean_bot import AIAnalyzer

def test_ai_responses():
    """Test AI response generation"""
    print("Testing AI-generated responses...")
    
    # Initialize AI analyzer
    ai_analyzer = AIAnalyzer()
    
    # Test data
    test_cases = [
        {
            "username": "johnsmith_usa",
            "comment": "This is such a great post! Really love the insights here.",
            "profile": {"bio": "Tech enthusiast from California", "gender": "male", "is_usa": True}
        },
        {
            "username": "mike_fitness",
            "comment": "Totally agree with this perspective on fitness.",
            "profile": {"bio": "Fitness coach in Texas", "gender": "male", "is_usa": True}
        },
        {
            "username": "alex_crypto",
            "comment": "Great analysis of the crypto market trends.",
            "profile": {"bio": "Crypto investor from NYC", "gender": "male", "is_usa": True}
        }
    ]
    
    print("\n" + "="*60)
    print("TESTING AI-GENERATED FEMALE RESPONSES")
    print("="*60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Username: {test_case['username']}")
        print(f"Comment: {test_case['comment']}")
        print(f"Profile: {test_case['profile']}")
        
        try:
            # Generate AI response
            response = ai_analyzer.generate_female_engagement_response(
                post_content="Social media engagement post",
                user_profile=test_case['profile'],
                comment_text=test_case['comment']
            )
            
            print(f"AI Response: {response}")
            
            # Check if response looks AI-generated (not a fallback)
            fallback_indicators = [
                "Love your perspective! 💕",
                "This is so relatable! ✨",
                "You're absolutely right! 🔥",
                "Thanks for sharing this! 💯"
            ]
            
            is_ai_generated = response not in fallback_indicators
            print(f"Is AI-generated: {'✅ YES' if is_ai_generated else '❌ NO (fallback)'}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 40)
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    test_ai_responses() 