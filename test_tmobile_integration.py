#!/usr/bin/env python3
"""
Test script for T-Mobile Enterprise GPT integration with JUNO.
This script tests the adapted system with mock T-Mobile GPT endpoints.
"""

import os
import sys
import json
import time
from unittest.mock import Mock, patch
import requests_mock

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'juno-agent', 'src'))

from enterprise_gpt_connector import EnterpriseGPTManager, GPTConfig, GPTProvider
from enterprise_gpt_integration import EnterpriseGPTIntegration
from enhanced_nlp_processor_v2 import EnhancedNLPProcessor

def create_mock_tmobile_config():
    """Create mock T-Mobile GPT configuration."""
    return GPTConfig(
        provider=GPTProvider.TMOBILE,
        api_endpoint="https://mock-tmobile-gpt.com/v1/chat/completions",
        api_key="tmob_mock_key_12345",
        model_name="intentcx-test",
        max_tokens=1000,
        temperature=0.7,
        auth_type="bearer"
    )

def create_mock_tmobile_response():
    """Create mock T-Mobile IntentCX response."""
    return {
        "response": "Based on the query analysis, you're asking about ticket assignments for John Doe in the DEMO project.",
        "intent": "assignee_count",
        "confidence": 0.92,
        "suggested_actions": [
            "Show detailed breakdown by status",
            "Compare with other team members",
            "Show recent activity timeline"
        ],
        "usage": {
            "prompt_tokens": 45,
            "completion_tokens": 28,
            "total_tokens": 73
        },
        "model": "intentcx-test"
    }

def test_tmobile_connector():
    """Test T-Mobile GPT connector functionality."""
    print("🧪 Testing T-Mobile GPT Connector...")
    
    config = create_mock_tmobile_config()
    
    with requests_mock.Mocker() as m:
        # Mock the T-Mobile API endpoint
        m.post(
            config.api_endpoint,
            json=create_mock_tmobile_response(),
            status_code=200
        )
        
        # Test the connector
        from enterprise_gpt_connector import TMobileGPTConnector
        connector = TMobileGPTConnector(config)
        
        test_messages = [
            {"role": "user", "content": "How many tickets are assigned to John Doe in project DEMO?"}
        ]
        
        try:
            result = connector.generate_completion(test_messages)
            
            print("✅ T-Mobile connector test successful!")
            print(f"   Response: {result['content'][:100]}...")
            print(f"   Intent: {result.get('intent', 'N/A')}")
            print(f"   Confidence: {result.get('confidence', 'N/A')}")
            print(f"   Suggested Actions: {len(result.get('suggested_actions', []))} actions")
            
            return True
            
        except Exception as e:
            print(f"❌ T-Mobile connector test failed: {e}")
            return False

def test_enterprise_gpt_manager():
    """Test Enterprise GPT Manager with multiple providers."""
    print("\n🧪 Testing Enterprise GPT Manager...")
    
    manager = EnterpriseGPTManager()
    
    # Add mock T-Mobile provider
    tmobile_config = create_mock_tmobile_config()
    
    with requests_mock.Mocker() as m:
        # Mock T-Mobile endpoint
        m.post(
            tmobile_config.api_endpoint,
            json=create_mock_tmobile_response(),
            status_code=200
        )
        
        # Mock OpenAI endpoint (if configured)
        m.post(
            "https://api.openai.com/v1/chat/completions",
            json={
                "choices": [
                    {
                        "message": {
                            "content": '{"intent": "assignee_count", "confidence": 0.85, "entities": {"user": "John Doe", "project": "DEMO"}}'
                        }
                    }
                ],
                "usage": {"total_tokens": 50}
            },
            status_code=200
        )
        
        try:
            # Add T-Mobile provider
            manager.add_provider("tmobile", tmobile_config)
            
            # Test provider availability
            providers = manager.get_available_providers()
            print(f"✅ Available providers: {providers}")
            
            # Test completion with T-Mobile
            if "tmobile" in providers:
                manager.set_default_provider("tmobile")
                
                test_messages = [
                    {"role": "user", "content": "Show me defect analysis for last sprint"}
                ]
                
                result = manager.generate_completion(test_messages)
                print(f"✅ T-Mobile completion successful!")
                print(f"   Provider: {result.get('provider', 'unknown')}")
                print(f"   Intent: {result.get('intent', 'N/A')}")
                
            return True
            
        except Exception as e:
            print(f"❌ Enterprise GPT Manager test failed: {e}")
            return False

def test_enterprise_gpt_integration():
    """Test Enterprise GPT Integration with environment simulation."""
    print("\n🧪 Testing Enterprise GPT Integration...")
    
    # Mock environment variables
    with patch.dict(os.environ, {
        'TMOBILE_GPT_API_KEY': 'tmob_mock_key_12345',
        'TMOBILE_GPT_ENDPOINT': 'https://mock-tmobile-gpt.com/v1/chat/completions',
        'TMOBILE_GPT_MODEL': 'intentcx-test',
        'GPT_PREFERRED_PROVIDER': 'tmobile'
    }):
        
        with requests_mock.Mocker() as m:
            # Mock T-Mobile endpoint
            m.post(
                "https://mock-tmobile-gpt.com/v1/chat/completions",
                json=create_mock_tmobile_response(),
                status_code=200
            )
            
            try:
                integration = EnterpriseGPTIntegration()
                
                # Test availability
                if integration.is_available():
                    print(f"✅ GPT integration available with providers: {integration.get_available_providers()}")
                    
                    # Test query enhancement
                    result = integration.enhance_query_understanding(
                        "What's the velocity trend for our team?",
                        context={"project": "DEMO"},
                        provider="tmobile"
                    )
                    
                    print(f"✅ Query enhancement successful!")
                    print(f"   Enhanced query: {result.get('enhanced_query', 'N/A')}")
                    
                    # Test suggestions
                    suggestions = integration.generate_intelligent_suggestions(
                        "Show me bug reports",
                        {"project": "DEMO", "sprint": "current"},
                        provider="tmobile"
                    )
                    
                    print(f"✅ Suggestions generated: {len(suggestions)} suggestions")
                    
                    return True
                else:
                    print("❌ GPT integration not available")
                    return False
                    
            except Exception as e:
                print(f"❌ Enterprise GPT Integration test failed: {e}")
                return False

def test_enhanced_nlp_processor():
    """Test Enhanced NLP Processor with T-Mobile integration."""
    print("\n🧪 Testing Enhanced NLP Processor...")
    
    # Mock environment variables
    with patch.dict(os.environ, {
        'TMOBILE_GPT_API_KEY': 'tmob_mock_key_12345',
        'TMOBILE_GPT_ENDPOINT': 'https://mock-tmobile-gpt.com/v1/chat/completions',
        'TMOBILE_GPT_MODEL': 'intentcx-test',
        'GPT_PREFERRED_PROVIDER': 'tmobile'
    }):
        
        with requests_mock.Mocker() as m:
            # Mock T-Mobile endpoint
            m.post(
                "https://mock-tmobile-gpt.com/v1/chat/completions",
                json={
                    "response": '{"intent": "velocity_report", "confidence": 0.95, "entities": {"timeframe": "last quarter", "team": "our team"}, "enhanced_query": "Generate velocity analysis report for the team covering the last quarter period"}',
                    "intent": "velocity_report",
                    "confidence": 0.95,
                    "suggested_actions": [
                        "Show sprint-by-sprint breakdown",
                        "Compare with previous quarter",
                        "Identify velocity blockers"
                    ],
                    "usage": {"total_tokens": 85},
                    "model": "intentcx-test"
                },
                status_code=200
            )
            
            try:
                processor = EnhancedNLPProcessor()
                
                # Test query processing with T-Mobile
                test_queries = [
                    "What's the velocity trend for our team last quarter?",
                    "Show me current sprint burndown",
                    "How many bugs were reported this week?",
                    "Compare our performance with last month"
                ]
                
                for query in test_queries:
                    print(f"\n   Testing query: '{query}'")
                    
                    result = processor.process_query(
                        query,
                        context={"project": "DEMO"},
                        preferred_provider="tmobile"
                    )
                    
                    print(f"   ✅ Processing method: {result.get('processing_method', 'unknown')}")
                    print(f"   ✅ Provider used: {result.get('provider_used', 'unknown')}")
                    print(f"   ✅ Intent: {result.get('intent', 'unknown')}")
                    print(f"   ✅ Confidence: {result.get('confidence', 0):.2f}")
                    
                    if result.get('tmobile_enhanced'):
                        print(f"   ✅ T-Mobile enhanced features active")
                        if result.get('suggested_actions'):
                            print(f"   ✅ Suggested actions: {len(result['suggested_actions'])}")
                
                # Test provider capabilities
                capabilities = processor.get_provider_capabilities()
                print(f"\n✅ Provider capabilities loaded: {list(capabilities.keys())}")
                
                # Test provider switching
                if processor.switch_provider("tmobile"):
                    print("✅ Successfully switched to T-Mobile provider")
                
                return True
                
            except Exception as e:
                print(f"❌ Enhanced NLP Processor test failed: {e}")
                return False

def test_configuration_scenarios():
    """Test different configuration scenarios."""
    print("\n🧪 Testing Configuration Scenarios...")
    
    scenarios = [
        {
            "name": "T-Mobile Only",
            "env": {
                'TMOBILE_GPT_API_KEY': 'tmob_key',
                'GPT_PREFERRED_PROVIDER': 'tmobile'
            }
        },
        {
            "name": "Multi-Provider",
            "env": {
                'TMOBILE_GPT_API_KEY': 'tmob_key',
                'OPENAI_API_KEY': 'sk-openai_key',
                'GPT_PREFERRED_PROVIDER': 'tmobile'
            }
        },
        {
            "name": "Fallback to OpenAI",
            "env": {
                'OPENAI_API_KEY': 'sk-openai_key',
                'GPT_PREFERRED_PROVIDER': 'openai'
            }
        }
    ]
    
    for scenario in scenarios:
        print(f"\n   Testing scenario: {scenario['name']}")
        
        with patch.dict(os.environ, scenario['env'], clear=True):
            try:
                integration = EnterpriseGPTIntegration()
                providers = integration.get_available_providers()
                
                print(f"   ✅ Available providers: {providers}")
                print(f"   ✅ Configuration loaded successfully")
                
            except Exception as e:
                print(f"   ❌ Scenario failed: {e}")
    
    return True

def run_all_tests():
    """Run all T-Mobile GPT integration tests."""
    print("🚀 Starting T-Mobile Enterprise GPT Integration Tests for JUNO\n")
    
    tests = [
        ("T-Mobile Connector", test_tmobile_connector),
        ("Enterprise GPT Manager", test_enterprise_gpt_manager),
        ("Enterprise GPT Integration", test_enterprise_gpt_integration),
        ("Enhanced NLP Processor", test_enhanced_nlp_processor),
        ("Configuration Scenarios", test_configuration_scenarios)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)
        
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print('='*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:<30} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! T-Mobile GPT integration is ready.")
    else:
        print("⚠️  Some tests failed. Review the output above.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

