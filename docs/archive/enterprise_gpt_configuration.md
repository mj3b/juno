# JUNO Enterprise GPT Configuration Guide

## Overview

JUNO supports multiple Enterprise GPT providers including OpenAI, T-Mobile's IntentCX, Azure OpenAI, and custom enterprise solutions. This guide explains how to configure different providers.

## Environment Variables

### OpenAI Configuration
```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=1000
OPENAI_TEMPERATURE=0.7
```

### T-Mobile Enterprise GPT Configuration
```bash
# T-Mobile IntentCX Configuration
TMOBILE_GPT_API_KEY=your_tmobile_api_key_here
TMOBILE_GPT_ENDPOINT=https://api.tmobile-gpt.com/v1/chat/completions
TMOBILE_GPT_MODEL=intentcx-1
TMOBILE_GPT_MAX_TOKENS=1000
TMOBILE_GPT_TEMPERATURE=0.7
TMOBILE_GPT_AUTH_TYPE=bearer  # or api_key, custom
TMOBILE_GPT_AUTH_HEADER=X-Custom-Auth  # if auth_type=custom
```

### Azure OpenAI Configuration
```bash
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_azure_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/openai/deployments/your-deployment/chat/completions?api-version=2023-05-15
AZURE_OPENAI_MODEL=gpt-4
AZURE_OPENAI_MAX_TOKENS=1000
AZURE_OPENAI_TEMPERATURE=0.7
```

### General GPT Configuration
```bash
# General Configuration
GPT_PREFERRED_PROVIDER=tmobile  # openai, tmobile, azure, custom
GPT_MODEL=gpt-4  # Default model if not specified per provider
GPT_MAX_TOKENS=1000  # Default max tokens
GPT_TEMPERATURE=0.7  # Default temperature
```

## Provider-Specific Features

### T-Mobile IntentCX Features
- **Intent Analysis**: Automatic intent detection and confidence scoring
- **Real-time Context**: Integration with real-time data streams
- **Suggested Actions**: Proactive action recommendations
- **Multi-language Support**: Enhanced conversation handling

### OpenAI Features
- **Advanced Models**: Access to GPT-4 and latest models
- **Function Calling**: Structured output capabilities
- **Fine-tuning**: Custom model training options

### Azure OpenAI Features
- **Enterprise Security**: Enhanced security and compliance
- **Private Endpoints**: Secure network connectivity
- **Content Filtering**: Built-in content moderation

## Configuration Examples

### Development Environment (.env file)
```bash
# Development with OpenAI
OPENAI_API_KEY=sk-your-development-key
GPT_PREFERRED_PROVIDER=openai
```

### Production Environment (T-Mobile)
```bash
# Production with T-Mobile IntentCX
TMOBILE_GPT_API_KEY=tmob_your_production_key
TMOBILE_GPT_ENDPOINT=https://prod-api.tmobile-gpt.com/v1/chat/completions
TMOBILE_GPT_MODEL=intentcx-production
GPT_PREFERRED_PROVIDER=tmobile
```

### Multi-Provider Setup
```bash
# Multiple providers for fallback
OPENAI_API_KEY=sk-your-openai-key
TMOBILE_GPT_API_KEY=tmob_your-tmobile-key
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/...
GPT_PREFERRED_PROVIDER=tmobile
```

## API Usage Examples

### Python Configuration
```python
from src.enterprise_gpt_integration import EnterpriseGPTIntegration

# Initialize with environment variables
gpt = EnterpriseGPTIntegration()

# Check available providers
providers = gpt.get_available_providers()
print(f"Available providers: {providers}")

# Use specific provider
result = gpt.enhance_query_understanding(
    "How many tickets are assigned to John?",
    provider="tmobile"
)

# Switch default provider
gpt.switch_provider("tmobile")
```

### REST API Usage
```bash
# Query with specific provider
curl -X POST http://localhost:5000/api/enhanced-nlp/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me velocity trends for last quarter",
    "provider": "tmobile"
  }'

# Get available providers
curl http://localhost:5000/api/enhanced-nlp/providers
```

## Security Considerations

### API Key Management
- Store API keys in secure environment variables
- Use different keys for development and production
- Rotate keys regularly
- Monitor usage and costs

### Network Security
- Use HTTPS endpoints only
- Configure firewall rules for API access
- Consider VPN or private endpoints for production

### Data Privacy
- Review provider data handling policies
- Implement data minimization practices
- Log and audit API usage
- Consider data residency requirements

## Troubleshooting

### Common Issues

1. **Provider Not Available**
   - Check API key configuration
   - Verify endpoint URLs
   - Test network connectivity

2. **Authentication Errors**
   - Verify API key format
   - Check authentication type settings
   - Review custom header configuration

3. **Rate Limiting**
   - Monitor usage statistics
   - Implement request throttling
   - Consider multiple provider setup

### Debugging
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Test provider connectivity
python -c "
from src.enterprise_gpt_integration import EnterpriseGPTIntegration
gpt = EnterpriseGPTIntegration()
print('Available providers:', gpt.get_available_providers())
"
```

## Monitoring and Analytics

### Usage Tracking
```python
# Get usage statistics
stats = gpt.get_usage_stats()
print(f"Total requests: {stats['total_requests']}")
print(f"Total tokens: {stats['total_tokens']}")
print(f"Estimated cost: ${stats['total_cost']:.2f}")

# Provider-specific usage
for provider, usage in stats['provider_usage'].items():
    print(f"{provider}: {usage['requests']} requests, {usage['tokens']} tokens")
```

### Cost Management
- Set up usage alerts
- Monitor token consumption
- Implement cost controls
- Review provider pricing regularly

## Migration Guide

### From OpenAI-only to Multi-Provider

1. **Update Environment Variables**
   ```bash
   # Add new provider configurations
   TMOBILE_GPT_API_KEY=your_key
   GPT_PREFERRED_PROVIDER=tmobile
   ```

2. **Update Code**
   ```python
   # Old: OpenAI-specific
   from src.openai_integration import OpenAIIntegration
   openai = OpenAIIntegration()
   
   # New: Multi-provider
   from src.enterprise_gpt_integration import EnterpriseGPTIntegration
   gpt = EnterpriseGPTIntegration()
   ```

3. **Test Configuration**
   - Verify all providers work
   - Test fallback scenarios
   - Monitor performance differences

## Best Practices

1. **Provider Selection**
   - Use T-Mobile for production workloads
   - Use OpenAI for development and testing
   - Configure fallback providers

2. **Performance Optimization**
   - Enable response caching
   - Monitor response times
   - Optimize prompt engineering

3. **Error Handling**
   - Implement graceful degradation
   - Log errors for debugging
   - Provide user-friendly error messages

4. **Scaling**
   - Monitor usage patterns
   - Plan for peak loads
   - Consider load balancing across providers

