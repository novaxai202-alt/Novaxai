#!/usr/bin/env python3
"""
Test script to demonstrate NovaX AI's adaptive response complexity
"""

from main import analyze_query_complexity

def test_query_complexity():
    """Test different types of queries and their complexity classification"""
    
    test_cases = [
        # Simple factual questions (should get concise responses)
        ("who is ceo of google", "simple"),
        ("what is the capital of france", "simple"), 
        ("what time is it", "simple"),
        ("who was the first president", "simple"),
        ("when did world war 2 end", "simple"),
        
        # Medium complexity (should get moderate structure)
        ("how do I learn python", "medium"),
        ("what are the benefits of exercise", "medium"),
        ("compare react vs vue", "medium"),
        
        # High complexity (should get full 6-part structure)
        ("analyze the pros and cons of microservices architecture", "high"),
        ("design a scalable database system for e-commerce", "high"),
        ("recommend a strategy for digital transformation", "high"),
        
        # Greetings (should get simple responses)
        ("hi", "simple"),
        ("hello there", "simple"),
        ("thanks", "simple")
    ]
    
    print("🧪 NovaX AI Response Complexity Test")
    print("=" * 50)
    
    correct = 0
    total = len(test_cases)
    
    for query, expected in test_cases:
        result = analyze_query_complexity(query)
        actual = result['complexity']
        status = "✅" if actual == expected else "❌"
        
        print(f"{status} '{query}' -> {actual} (expected: {expected})")
        
        if actual == expected:
            correct += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {correct}/{total} correct ({correct/total*100:.1f}%)")
    
    if correct == total:
        print("🎉 All tests passed! NovaX AI will now give:")
        print("   • Concise answers for simple questions")
        print("   • Moderate detail for medium complexity")
        print("   • Full structured analysis for complex queries")
    else:
        print("⚠️  Some tests failed. Check the complexity analysis logic.")

if __name__ == "__main__":
    test_query_complexity()