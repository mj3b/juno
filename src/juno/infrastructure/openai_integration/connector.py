import os
import logging
from typing import Dict, List, Optional, Any, Union
from abc import ABC, abstractmethod
import requests
import json
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GPTProvider(Enum):
    """Enumeration of supported GPT providers"""
    OPENAI = "openai"
    ENTERPRISE = "enterprise"
    AZURE_OPENAI = "azure_openai"
    CUSTOM = "custom"

@dataclass
class GPTConfig:
    """Configuration for GPT providers"""
    provider: GPTProvider
    api_endpoint: str
    api_key: str
    model_name: str
    max_tokens: int = 1000
    temperature: float = 0.7
    timeout: int = 30
    headers: Optional[Dict[str, str]] = None
    auth_type: str = "bearer"  # bearer, api_key, custom
    custom_auth_header: Optional[str] = None

class BaseGPTConnector(ABC):
    """Abstract base class for GPT connectors"""
    
    def __init__(self, config: GPTConfig):
        self.config = config
        self.session = requests.Session()
        self._setup_authentication()
    
    @abstractmethod
    def _setup_authentication(self):
        """Setup authentication for the specific provider"""
        pass
    
    @abstractmethod
    def _format_request(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Format the request payload for the specific provider"""
        pass
    
    @abstractmethod
    def _parse_response(self, response: requests.Response) -> Dict[str, Any]:
        """Parse the response from the specific provider"""
        pass
    
    def generate_completion(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Generate completion using the GPT provider"""
        try:
            payload = self._format_request(messages, **kwargs)
            
            response = self.session.post(
                self.config.api_endpoint,
                json=payload,
                timeout=self.config.timeout
            )
            
            response.raise_for_status()
            return self._parse_response(response)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {self.config.provider.value}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error with {self.config.provider.value}: {e}")
            raise

class OpenAIConnector(BaseGPTConnector):
    """OpenAI GPT connector"""
    
    def _setup_authentication(self):
        """Setup OpenAI authentication"""
        self.session.headers.update({
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        })
        if self.config.headers:
            self.session.headers.update(self.config.headers)
    
    def _format_request(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Format request for OpenAI API"""
        return {
            "model": self.config.model_name,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
            "stream": False
        }
    
    def _parse_response(self, response: requests.Response) -> Dict[str, Any]:
        """Parse OpenAI response"""
        data = response.json()
        return {
            "content": data["choices"][0]["message"]["content"],
            "usage": data.get("usage", {}),
            "model": data.get("model"),
            "provider": self.config.provider.value
     class EnterpriseGPTConnector(BaseGPTConnector):
    """Enterprise GPT connector"""
    
    def _setup_authentication(self):
        """Setup Enterprise GPT authentication"""
        if self.config.auth_type == "bearer":
            self.session.headers.update({
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            })
        elif self.config.auth_type == "api_key":
            self.session.headers.update({
                "X-API-Key": self.config.api_key,
                "Content-Type": "application/json"
            })
        elif self.config.auth_type == "custom" and self.config.custom_auth_header:
            self.session.headers.update({
                self.config.custom_auth_header: self.config.api_key,
                "Content-Type": "application/json"
            })
        
        # Add any custom headers
        if self.config.headers:
            self.session.headers.update(self.config.headers)
    
    def _format_request(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Format request for Enterprise GPT API"""
        # Enterprise GPT might have a different request format
        return {
            "messages": messages,
            "model": self.config.model_name,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            **kwargs
        }
    
    def _parse_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Enterprise GPT response"""
        
        # Handle Enterprise GPT response format
        if "response" in response_data:
            # Direct response format
            return {
                "content": response_data["response"],
                "intent": response_data.get("intent"),
                "confidence": response_data.get("confidence"),
                "suggested_actions": response_data.get("suggested_actions", []),
                "usage": response_data.get("usage", {}),
                "model": response_data.get("model", self.config.model_name)
            }
        elif "choices" in response_data and len(response_data["choices"]) > 0:
            # OpenAI-compatible format
            choice = response_data["choices"][0]
            message = choice.get("message", {})
            return {
                "content": message.get("content", ""),
                "usage": response_data.get("usage", {}),
                "model": response_data.get("model", self.config.model_name)
            }
        else:
            raise ValueError(f"Unexpected response format: {response_data}")nAI GPT connector"""
    
    def _setup_authentication(self):
        """Setup Azure OpenAI authentication"""
        self.session.headers.update({
            "api-key": self.config.api_key,
            "Content-Type": "application/json"
        })
        if self.config.headers:
            self.session.headers.update(self.config.headers)
    
    def _format_request(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Format request for Azure OpenAI API"""
        return {
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature),
            "stream": False
        }
    
    def _parse_response(self, response: requests.Response) -> Dict[str, Any]:
        """Parse Azure OpenAI response"""
        data = response.json()
        return {
            "content": data["choices"][0]["message"]["content"],
            "usage": data.get("usage", {}),
            "model": self.config.model_name,
            "provider": self.config.provider.value
        }

class CustomGPTConnector(BaseGPTConnector):
    """Custom GPT connector for other enterprise providers"""
    
    def _setup_authentication(self):
        """Setup custom authentication"""
        if self.config.auth_type == "bearer":
            self.session.headers.update({
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            })
        elif self.config.auth_type == "api_key":
            self.session.headers.update({
                "X-API-Key": self.config.api_key,
                "Content-Type": "application/json"
            })
        elif self.config.auth_type == "custom" and self.config.custom_auth_header:
            self.session.headers.update({
                self.config.custom_auth_header: self.config.api_key,
                "Content-Type": "application/json"
            })
        
        if self.config.headers:
            self.session.headers.update(self.config.headers)
    
    def _format_request(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Format request for custom GPT API"""
        return {
            "model": self.config.model_name,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature)
        }
    
    def _parse_response(self, response: requests.Response) -> Dict[str, Any]:
        """Parse custom GPT response"""
        data = response.json()
        
        # Try to handle different response formats
        content = ""
        if "choices" in data and len(data["choices"]) > 0:
            content = data["choices"][0].get("message", {}).get("content", "")
        elif "response" in data:
            content = data["response"]
        elif "content" in data:
            content = data["content"]
        
        return {
            "content": content,
            "usage": data.get("usage", {}),
            "model": data.get("model", self.config.model_name),
            "provider": self.config.provider.value
        }

class EnterpriseGPTManager:
    """Manager for multiple GPT providers"""
    
    def __init__(self):
        self.connectors: Dict[str, BaseGPTConnector] = {}
        self.default_provider: Optional[str] = None
    
    def add_provider(self, name: str, config: GPTConfig) -> None:
        """Add a GPT provider"""
        connector_map = {
            GPTProvider.OPENAI: OpenAIConnector,
            GPTProvider.ENTERPRISE: EnterpriseGPTConnector,
            GPTProvider.AZURE_OPENAI: AzureOpenAIConnector,
            GPTProvider.CUSTOM: CustomGPTConnector
        }
        
        connector_class = connector_map.get(config.provider)
        if not connector_class:
            raise ValueError(f"Unsupported provider: {config.provider}")
        
        self.connectors[name] = connector_class(config)
        
        if self.default_provider is None:
            self.default_provider = name
    
    def set_default_provider(self, name: str) -> None:
        """Set the default GPT provider"""
        if name not in self.connectors:
            raise ValueError(f"Provider '{name}' not found")
        self.default_provider = name
    
    def generate_completion(self, messages: List[Dict[str, str]], 
                          provider: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Generate completion using specified or default provider"""
        provider_name = provider or self.default_provider
        
        if not provider_name or provider_name not in self.connectors:
            raise ValueError(f"No valid provider specified or found")
        
        return self.connectors[provider_name].generate_completion(messages, **kwargs)
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return list(self.connectors.keys())

def create_gpt_config_from_env() -> Dict[str, GPTConfig]:
    """Create GPT configurations from environment variables"""
    configs = {}
    
    # OpenAI Configuration
    if os.getenv("OPENAI_API_KEY"):
        configs["openai"] = GPTConfig(
            provider=GPTProvider.OPENAI,
            api_endpoint="https://api.openai.com/v1/chat/completions",
            api_key=os.getenv("OPENAI_API_KEY"),
            model_name=os.getenv("OPENAI_MODEL", "gpt-4"),
            max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "1000")),
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        )
    
    # Enterprise GPT Configuration
    if os.getenv("ENTERPRISE_GPT_API_KEY"):
        configs["enterprise"] = GPTConfig(
            provider=GPTProvider.ENTERPRISE,
            api_endpoint=os.getenv("ENTERPRISE_GPT_ENDPOINT", "https://api.enterprise-gpt.com/v1/chat/completions"),
            api_key=os.getenv("ENTERPRISE_GPT_API_KEY"),
            model_name=os.getenv("ENTERPRISE_GPT_MODEL", "enterprise-intent-engine"),
            max_tokens=int(os.getenv("ENTERPRISE_GPT_MAX_TOKENS", "1000")),
            temperature=float(os.getenv("ENTERPRISE_GPT_TEMPERATURE", "0.7")),
            auth_type=os.getenv("ENTERPRISE_GPT_AUTH_TYPE", "bearer"),
            custom_auth_header=os.getenv("ENTERPRISE_GPT_AUTH_HEADER")
        )
    
    # Azure OpenAI Configuration
    if os.getenv("AZURE_OPENAI_API_KEY"):
        configs["azure"] = GPTConfig(
            provider=GPTProvider.AZURE_OPENAI,
            api_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            model_name=os.getenv("AZURE_OPENAI_MODEL", "gpt-4"),
            max_tokens=int(os.getenv("AZURE_OPENAI_MAX_TOKENS", "1000")),
            temperature=float(os.getenv("AZURE_OPENAI_TEMPERATURE", "0.7"))
        )
    
    return configs

# Example usage and testing
if __name__ == "__main__":
    # Initialize the manager
    manager = EnterpriseGPTManager()
    
    # Load configurations from environment
    configs = create_gpt_config_from_env()
    
    # Add providers
    for name, config in configs.items():
        try:
            manager.add_provider(name, config)
            logger.info(f"Added provider: {name}")
        except Exception as e:
            logger.error(f"Failed to add provider {name}: {e}")
    
    # Test completion (if providers are available)
    if manager.get_available_providers():
        test_messages = [
            {"role": "user", "content": "How many tickets are assigned to John Doe in project DEMO?"}
        ]
        
        try:
            result = manager.generate_completion(test_messages)
            logger.info(f"Test completion successful: {result['provider']}")
        except Exception as e:
            logger.error(f"Test completion failed: {e}")
    else:
        logger.warning("No GPT providers configured")

