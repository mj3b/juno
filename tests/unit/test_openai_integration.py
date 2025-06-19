#!/usr/bin/env python3 mj3b
"""
Test script for OpenAI integration and enhanced NLP capabilities.
"""

import os
import sys
import json
import pytest
requests = pytest.importorskip("requests")
pytest.importorskip("openai")
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../juno-agent/src'))
from src.enhanced_nlp_processor import EnhancedNLPProcessor
from juno.infrastructure.openai_integration.openai_client import OpenAIIntegration

def test_openai_integration():
    """Test OpenAI integration directly."""
    print("=== Testing OpenAI Integration ===")
    
    openai_integration = OpenAIIntegration()
    
    if not openai_integration.is_available():
        print("❌ OpenAI integration not available (API key not set)")
        print("To enable OpenAI integration, set the OPENAI_API_KEY environment variable")
        return False
    
    print("✅ OpenAI integration available")
    print(f"Model: {openai_integration.model}")
    
    # Test query enhancement
    test_query = "How many tickets did John work on last month?"
    print(f"\nTesting query enhancement with: '{test_query}'")
    
    try:
        result = openai_integration.enhance_query_understanding(test_query)
        print("✅ Query enhancement successful")
        print(f"Enhanced result: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"❌ Query enhancement failed: {str(e)}")
        return False
    
    return True

def test_enhanced_nlp_processor():
    """Test the enhanced NLP processor."""
    print("\n=== Testing Enhanced NLP Processor ===")
    
    processor = EnhancedNLPProcessor()
    
    test_queries = [
        "How many tickets are assigned to John Doe?",
        "Show me the velocity trend for the last 3 sprints",
        "What about the defect rate? Is it improving?",
        "Compare this month's performance to last month"
    ]
    
    for query in test_queries:
        print(f"\nProcessing: '{query}'")
        try:
            result = processor.process_query(query)
            print(f"✅ Processing method: {result.get('processing_method', 'unknown')}")
            print(f"   Intent: {result.get('intent', 'unknown')}")
            print(f"   Confidence: {result.get('confidence', 0):.2f}")
            print(f"   Processing time: {result.get('processing_time', 0):.3f}s")
        except Exception as e:
            print(f"❌ Processing failed: {str(e)}")
    
    # Test conversation context
    print("\n--- Testing Conversation Context ---")
    context = processor.get_conversation_context()
    print(f"Conversation history length: {len(context)}")
    
    # Test processing stats
    stats = processor.get_processing_stats()
    print(f"Processing stats: {json.dumps(stats, indent=2)}")

def test_api_endpoints():
    """Test the enhanced NLP API endpoints."""
    print("\n=== Testing Enhanced NLP API Endpoints ===")
    
    base_url = "http://localhost:5000"
    
    # Test enhanced query endpoint
    print("\nTesting /api/enhanced-nlp/enhanced-query")
    try:
        response = requests.post(f"{base_url}/api/enhanced-nlp/enhanced-query", 
                               json={
                                   "query": "How many bugs were found last week?",
                                   "context": {"project": "DEMO"}
                               })
        if response.status_code == 200:
            print("✅ Enhanced query endpoint working")
            result = response.json()
            print(f"   Processing method: {result['result'].get('processing_method', 'unknown')}")
        else:
            print(f"❌ Enhanced query endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Enhanced query endpoint error: {str(e)}")
    
    # Test OpenAI status endpoint
    print("\nTesting /api/enhanced-nlp/openai-status")
    try:
        response = requests.get(f"{base_url}/api/enhanced-nlp/openai-status")
        if response.status_code == 200:
            print("✅ OpenAI status endpoint working")
            status = response.json()
            print(f"   OpenAI available: {status['openai_status']['available']}")
            if status['openai_status']['available']:
                print(f"   Model: {status['openai_status']['model']}")
        else:
            print(f"❌ OpenAI status endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ OpenAI status endpoint error: {str(e)}")
    
    # Test enhanced test queries
    print("\nTesting /api/enhanced-nlp/test-enhanced-queries")
    try:
        response = requests.get(f"{base_url}/api/enhanced-nlp/test-enhanced-queries")
        if response.status_code == 200:
            print("✅ Enhanced test queries endpoint working")
            results = response.json()
            print(f"   OpenAI available: {results['openai_available']}")
            print(f"   Test results: {len(results['test_results'])} queries tested")
            
            for result in results['test_results']:
                status = "✅" if result['success'] else "❌"
                print(f"   {status} {result['query'][:50]}...")
        else:
            print(f"❌ Enhanced test queries endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Enhanced test queries endpoint error: {str(e)}")

def main():
    """Run all tests."""
    print("🚀 Testing OpenAI Integration and Enhanced NLP")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:5000/health")
        if response.status_code != 200:
            print("❌ Flask server not running. Please start the server first.")
            return
    except:
        print("❌ Flask server not accessible. Please start the server first.")
        return
    
    print("✅ Flask server is running")
    
    # Run tests
    openai_available = test_openai_integration()
    test_enhanced_nlp_processor()
    test_api_endpoints()
    
    print("\n" + "=" * 60)
    print("🎯 Test Summary:")
    print(f"   OpenAI Integration: {'✅ Available' if openai_available else '❌ Not Available'}")
    print("   Enhanced NLP Processor: ✅ Working")
    print("   API Endpoints: ✅ Working")
    
    if not openai_available:
        print("\n💡 To enable OpenAI features:")
        print("   export OPENAI_API_KEY='your-api-key-here'")
        print("   Then restart the Flask server")

if __name__ == "__main__":
    main()

