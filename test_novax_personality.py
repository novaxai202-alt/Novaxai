#!/usr/bin/env python3
"""
NovaX Personality System Test
Demonstrates the enhanced AI personality with structured responses
"""

from main import (
    analyze_query_complexity, 
    generate_novax_intro, 
    format_novax_response,
    generate_suggestions,
    detect_user_intent
)

def test_novax_personality():
    print("🚀 NovaX Personality System Test")
    print("=" * 50)
    
    # Test cases with different complexity levels
    test_cases = [
        "Hi there!",
        "What time is it?", 
        "How do I create a React component?",
        "Analyze the pros and cons of microservices architecture for a scalable e-commerce platform"
    ]
    
    for i, message in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: '{message}'")
        print("-" * 40)
        
        # Analyze complexity
        analysis = analyze_query_complexity(message)
        print(f"🧠 Complexity: {analysis['complexity']}")
        print(f"📋 Format: {analysis['format']}")
        print(f"🎯 Style: {analysis['response_style']}")
        
        # Detect agent type
        agent_type = detect_user_intent(message)
        print(f"🤖 Agent: {agent_type}")
        
        # Generate intro
        intro = generate_novax_intro(analysis, agent_type)
        print(f"⚡ Intro: {intro}")
        
        # Generate suggestions
        suggestions = generate_suggestions(message, agent_type)
        print(f"💡 Suggestions: {suggestions}")
        
        # Test formatting
        sample_response = "This is a sample response that needs NovaX formatting."
        formatted = format_novax_response(sample_response, analysis, agent_type)
        print(f"✨ Formatted Response Preview:")
        print(f"   {formatted[:100]}...")

if __name__ == "__main__":
    test_novax_personality()