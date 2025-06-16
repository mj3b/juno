# JUNO: GPT Integration Guide
## Complete GPT Provider Setup and Configuration

---

## **Overview**

JUNO supports multiple GPT providers to meet diverse enterprise requirements. This guide covers setup and configuration for OpenAI, Azure OpenAI, and Enterprise GPT providers, enabling you to choose the optimal AI backend for your organization's needs.

## 🔧 **Supported Providers**

### **1. OpenAI GPT**
- **Best for:** General-purpose analytics and conversational AI
- **Models:** GPT-3.5-turbo, GPT-4, GPT-4-turbo
- **Strengths:** Broad knowledge, excellent natural language understanding
- **Use cases:** Complex analysis, report generation, conversational queries

### **2. Azure OpenAI**
- **Best for:** Enterprise environments requiring data residency
- **Models:** GPT-3.5-turbo, GPT-4 (Azure-hosted)
- **Strengths:** Enterprise security, compliance, regional deployment
- **Use cases:** Regulated industries, private cloud deployments

### **3. Enterprise GPT Providers**
- **Best for:** Organizations with custom AI infrastructure
- **Models:** Custom enterprise models, specialized intent engines
- **Strengths:** Domain-specific training, private deployment, custom features
- **Use cases:** Specialized analytics, custom business logic, enhanced security

---

## ⚙**Configuration Setup**

### **Environment Variables**

Create a `.env` file in your project root:

```bash
# === JIRA CONFIGURATION ===
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-jira-api-token

# === GPT PROVIDER SELECTION ===
GPT_PREFERRED_PROVIDER=openai  # Options: openai, azure, enterprise, local

# === OPENAI CONFIGURATION ===
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.7

# === AZURE OPENAI CONFIGURATION ===
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-azure-api-key
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# === ENTERPRISE GPT CONFIGURATION ===
ENTERPRISE_GPT_API_KEY=your-enterprise-api-key
ENTERPRISE_GPT_ENDPOINT=https://your-enterprise-endpoint.com/api/v1
ENTERPRISE_GPT_MODEL=enterprise-intent-engine
ENTERPRISE_GPT_AUTH_TYPE=bearer

# === PERFORMANCE TUNING ===
GPT_CACHE_TIMEOUT=300  # seconds
GPT_MAX_RETRIES=3
GPT_REQUEST_TIMEOUT=30
API_RATE_LIMIT=60  # requests per minute
```

---

## **Provider-Specific Setup**

### **OpenAI Setup**

1. **Get API Key**
   ```bash
   # Visit https://platform.openai.com/api-keys
   # Create new API key
   # Add to .env file
   OPENAI_API_KEY=sk-your-key-here
   ```

2. **Configure Model**
   ```bash
   # Choose model based on needs
   OPENAI_MODEL=gpt-3.5-turbo      # Fast, cost-effective
   OPENAI_MODEL=gpt-4              # Higher quality, slower
   OPENAI_MODEL=gpt-4-turbo        # Best performance
   ```

3. **Test Connection**
   ```bash
   python -c "
   from juno-agent.src.openai_integration import OpenAIIntegration
   client = OpenAIIntegration()
   print(client.test_connection())
   "
   ```

### **Azure OpenAI Setup**

1. **Create Azure Resource**
   ```bash
   # Create Azure OpenAI resource in Azure Portal
   # Deploy a model (e.g., gpt-35-turbo)
   # Get endpoint and API key
   ```

2. **Configure Environment**
   ```bash
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_API_KEY=your-32-character-key
   AZURE_OPENAI_DEPLOYMENT=your-deployment-name
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   ```

3. **Test Deployment**
   ```bash
   python -c "
   from juno-agent.src.openai_integration import AzureOpenAIIntegration
   client = AzureOpenAIIntegration()
   print(client.test_connection())
   "
   ```

### **Enterprise GPT Setup**

1. **Configure Provider**
   ```bash
   ENTERPRISE_GPT_ENDPOINT=https://your-enterprise-endpoint.com
   ENTERPRISE_GPT_API_KEY=your-enterprise-key
   ENTERPRISE_GPT_MODEL=your-model-name
   ENTERPRISE_GPT_AUTH_TYPE=bearer  # or api_key, oauth
   ```

2. **Advanced Configuration**
   ```bash
   # Optional: Custom headers
   ENTERPRISE_GPT_CUSTOM_HEADERS='{"X-Custom-Header": "value"}'
   
   # Optional: Tenant/Organization ID
   ENTERPRISE_GPT_TENANT_ID=your-tenant-id
   
   # Optional: Private network settings
   ENTERPRISE_GPT_PRIVATE_ENDPOINT=true
   ```

---

## 🧠 **Intelligent Provider Selection**

JUNO automatically selects the optimal provider based on query characteristics:

### **Selection Logic**

```python
def select_provider(query, context):
    """Intelligent provider selection based on query analysis"""
    
    complexity = analyze_query_complexity(query)
    intent_type = detect_intent_type(query)
    
    if complexity < 0.3:
        return "local"  # Fast local processing
    elif intent_type == "specialized":
        return "enterprise"  # Domain-specific processing
    elif complexity > 0.8:
        return "openai"  # Complex analysis
    else:
        return get_preferred_provider()  # User preference
```

### **Query Routing Examples**

| **Query Type** | **Complexity** | **Recommended Provider** | **Reason** |
|----------------|----------------|-------------------------|------------|
| "Show my tickets" | Low | Local NLP | Simple data retrieval |
| "Analyze velocity trends" | Medium | OpenAI/Azure | Statistical analysis |
| "Predict sprint capacity" | High | OpenAI GPT-4 | Complex forecasting |
| "Intent analysis" | Variable | Enterprise GPT | Specialized processing |

---

## **Performance Optimization**

### **Caching Strategy**

```python
# Cache configuration
CACHE_CONFIG = {
    "simple_queries": 3600,    # 1 hour
    "complex_analysis": 1800,  # 30 minutes
    "real_time_data": 300,     # 5 minutes
    "static_reports": 86400    # 24 hours
}
```

### **Rate Limiting**

```python
# Provider-specific rate limits
RATE_LIMITS = {
    "openai": 60,      # requests per minute
    "azure": 120,      # higher enterprise limits
    "enterprise": 200, # custom enterprise limits
    "local": 1000      # no external API limits
}
```

### **Cost Optimization**

```python
# Cost-aware provider selection
def optimize_for_cost(query):
    """Select provider based on cost efficiency"""
    
    if is_simple_query(query):
        return "local"  # Free processing
    elif is_standard_analysis(query):
        return "azure"  # Enterprise rates
    else:
        return "openai"  # Pay-per-use
```

---

## 🔒 **Security Configuration**

### **API Key Management**

```bash
# Use environment variables (never hardcode)
export OPENAI_API_KEY="sk-your-key"
export AZURE_OPENAI_API_KEY="your-azure-key"

# Use secret management systems in production
# - Azure Key Vault
# - AWS Secrets Manager
# - HashiCorp Vault
```

### **Network Security**

```python
# SSL/TLS configuration
SSL_CONFIG = {
    "verify_ssl": True,
    "ssl_cert_path": "/path/to/cert.pem",
    "ssl_key_path": "/path/to/key.pem"
}

# Proxy configuration for enterprise networks
PROXY_CONFIG = {
    "http_proxy": "http://proxy.company.com:8080",
    "https_proxy": "https://proxy.company.com:8080"
}
```

### **Data Privacy**

```python
# Data handling configuration
PRIVACY_CONFIG = {
    "log_queries": False,        # Don't log sensitive queries
    "anonymize_data": True,      # Remove PII before processing
    "data_retention": 30,        # Days to retain processed data
    "audit_logging": True        # Log access patterns
}
```

---

## 🧪 **Testing and Validation**

### **Connection Testing**

```python
def test_all_providers():
    """Test connectivity to all configured providers"""
    
    providers = ["openai", "azure", "enterprise"]
    results = {}
    
    for provider in providers:
        try:
            client = get_provider_client(provider)
            response = client.test_connection()
            results[provider] = "✅ Connected"
        except Exception as e:
            results[provider] = f"❌ Failed: {str(e)}"
    
    return results
```

### **Performance Benchmarking**

```python
def benchmark_providers():
    """Compare response times across providers"""
    
    test_query = "Show me sprint velocity for the last 3 months"
    
    for provider in ["local", "openai", "azure", "enterprise"]:
        start_time = time.time()
        response = process_query(test_query, provider)
        end_time = time.time()
        
        print(f"{provider}: {end_time - start_time:.2f}s")
```

---

## **Advanced Features**

### **Multi-Provider Responses**

```python
def get_enhanced_response(query):
    """Combine responses from multiple providers"""
    
    # Get fast local response
    local_response = process_with_local_nlp(query)
    
    # Enhance with GPT analysis
    gpt_enhancement = process_with_gpt(query, local_response)
    
    # Merge results
    return merge_responses(local_response, gpt_enhancement)
```

### **Fallback Mechanisms**

```python
def process_with_fallback(query):
    """Automatic fallback between providers"""
    
    providers = ["enterprise", "azure", "openai", "local"]
    
    for provider in providers:
        try:
            return process_query(query, provider)
        except Exception as e:
            log_provider_error(provider, e)
            continue
    
    raise Exception("All providers failed")
```

### **Custom Provider Integration**

```python
class CustomGPTProvider:
    """Template for custom provider integration"""
    
    def __init__(self, config):
        self.config = config
        self.client = self._initialize_client()
    
    def process_query(self, query, context=None):
        """Process query with custom provider"""
        
        # Implement custom processing logic
        payload = self._prepare_payload(query, context)
        response = self.client.send_request(payload)
        return self._parse_response(response)
```

---

## **Troubleshooting**

### **Common Issues**

1. **Authentication Errors**
   ```bash
   # Check API key format
   echo $OPENAI_API_KEY | grep "sk-"
   
   # Verify Azure configuration
   curl -H "api-key: $AZURE_OPENAI_API_KEY" $AZURE_OPENAI_ENDPOINT
   ```

2. **Rate Limiting**
   ```python
   # Monitor rate limit headers
   def check_rate_limits():
       response = make_api_request()
       remaining = response.headers.get('x-ratelimit-remaining')
       reset_time = response.headers.get('x-ratelimit-reset')
       print(f"Remaining: {remaining}, Reset: {reset_time}")
   ```

3. **Network Connectivity**
   ```bash
   # Test endpoint connectivity
   curl -I https://api.openai.com/v1/models
   curl -I $AZURE_OPENAI_ENDPOINT
   ```

### **Monitoring and Alerting**

```python
def setup_monitoring():
    """Configure monitoring for GPT integrations"""
    
    # Response time monitoring
    monitor_response_times()
    
    # Error rate tracking
    monitor_error_rates()
    
    # Cost tracking
    monitor_api_usage_costs()
    
    # Availability monitoring
    monitor_provider_availability()
```

---

## **Best Practices**

### **Configuration Management**
- Use environment variables for all sensitive configuration
- Implement configuration validation on startup
- Document all configuration options
- Use different configurations for development/staging/production

### **Performance Optimization**
- Implement intelligent caching strategies
- Use appropriate provider for query complexity
- Monitor and optimize API usage patterns
- Implement request batching where possible

### **Security**
- Never commit API keys to version control
- Use secure secret management systems
- Implement proper access controls
- Regular security audits and key rotation

### **Cost Management**
- Monitor API usage and costs
- Implement usage quotas and alerts
- Optimize provider selection for cost efficiency
- Regular cost analysis and optimization

---

**This integration guide provides comprehensive setup instructions for all supported GPT providers, enabling you to choose the optimal AI backend for your JUNO deployment.**

