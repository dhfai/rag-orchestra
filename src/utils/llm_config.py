"""
LLM Client Configuration
========================

Configuration dan client untuk multiple LLM APIs
Mendukung OpenAI, Google Gemini, Anthropic Claude, dan Groq
"""

import os
from typing import Dict, Any, Optional, List
from enum import Enum
import asyncio

from ..utils.logger import get_logger

logger = get_logger("LLMConfig")

class LLMProvider(Enum):
    """Enum untuk LLM providers"""
    OPENAI = "openai"
    GOOGLE = "google"
    ANTHROPIC = "anthropic"
    GROQ = "groq"

class LLMConfig:
    """Configuration untuk LLM clients"""

    def __init__(self):
        # OpenAI Configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4")
        self.openai_temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        self.openai_max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))

        # Google Gemini Configuration
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.google_model = os.getenv("GOOGLE_MODEL", "gemini-pro")
        self.google_temperature = float(os.getenv("GOOGLE_TEMPERATURE", "0.7"))

        # Anthropic Claude Configuration
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
        self.anthropic_temperature = float(os.getenv("ANTHROPIC_TEMPERATURE", "0.7"))

        # Groq Configuration
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.groq_model = os.getenv("GROQ_MODEL", "llama3-70b-8192")

        # Embedding Configuration
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
        self.embedding_api_key = os.getenv("EMBEDDING_API_KEY", self.openai_api_key)

        # Initialize clients
        self._clients: Dict[LLMProvider, Any] = {}
        self._initialize_clients()

        logger.info("LLM Configuration initialized")

    def _initialize_clients(self):
        """Initialize LLM clients"""

        # OpenAI Client
        if self.openai_api_key:
            try:
                import openai
                self._clients[LLMProvider.OPENAI] = openai.AsyncOpenAI(
                    api_key=self.openai_api_key
                )
                logger.info("OpenAI client initialized")
            except ImportError:
                logger.warning("OpenAI package not installed")
            except Exception as e:
                logger.error(f"Error initializing OpenAI client: {str(e)}")

        # Google Gemini Client
        if self.google_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.google_api_key)
                self._clients[LLMProvider.GOOGLE] = genai.GenerativeModel(self.google_model)
                logger.info("Google Gemini client initialized")
            except ImportError:
                logger.warning("Google Generative AI package not installed")
            except Exception as e:
                logger.error(f"Error initializing Google client: {str(e)}")

        # Anthropic Claude Client
        if self.anthropic_api_key:
            try:
                import anthropic
                self._clients[LLMProvider.ANTHROPIC] = anthropic.AsyncAnthropic(
                    api_key=self.anthropic_api_key
                )
                logger.info("Anthropic client initialized")
            except ImportError:
                logger.warning("Anthropic package not installed")
            except Exception as e:
                logger.error(f"Error initializing Anthropic client: {str(e)}")

        # Groq Client
        if self.groq_api_key:
            try:
                import groq
                self._clients[LLMProvider.GROQ] = groq.AsyncGroq(
                    api_key=self.groq_api_key
                )
                logger.info("Groq client initialized")
            except ImportError:
                logger.warning("Groq package not installed")
            except Exception as e:
                logger.error(f"Error initializing Groq client: {str(e)}")

    def get_client(self, provider: LLMProvider) -> Optional[Any]:
        """Get LLM client untuk provider tertentu"""
        return self._clients.get(provider)

    def get_available_providers(self) -> List[LLMProvider]:
        """Get list available LLM providers"""
        return list(self._clients.keys())

    def is_provider_available(self, provider: LLMProvider) -> bool:
        """Check if provider is available"""
        return provider in self._clients

    async def generate_text(
        self,
        provider: LLMProvider,
        prompt: str,
        **kwargs
    ) -> Optional[str]:
        """Generate text menggunakan provider tertentu"""

        client = self.get_client(provider)
        if not client:
            logger.error(f"Provider {provider.value} not available")
            return None

        try:
            if provider == LLMProvider.OPENAI:
                response = await client.chat.completions.create(
                    model=kwargs.get("model", self.openai_model),
                    messages=[{"role": "user", "content": prompt}],
                    temperature=kwargs.get("temperature", self.openai_temperature),
                    max_tokens=kwargs.get("max_tokens", self.openai_max_tokens)
                )
                return response.choices[0].message.content

            elif provider == LLMProvider.GOOGLE:
                response = await client.generate_content_async(prompt)
                return response.text

            elif provider == LLMProvider.ANTHROPIC:
                response = await client.messages.create(
                    model=kwargs.get("model", self.anthropic_model),
                    max_tokens=kwargs.get("max_tokens", 2000),
                    temperature=kwargs.get("temperature", self.anthropic_temperature),
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text

            elif provider == LLMProvider.GROQ:
                response = await client.chat.completions.create(
                    model=kwargs.get("model", self.groq_model),
                    messages=[{"role": "user", "content": prompt}],
                    temperature=kwargs.get("temperature", 0.7)
                )
                return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error generating text with {provider.value}: {str(e)}")
            return None

    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding menggunakan OpenAI"""

        client = self.get_client(LLMProvider.OPENAI)
        if not client:
            logger.error("OpenAI client not available for embeddings")
            return None

        try:
            response = await client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return None

    def get_provider_info(self) -> Dict[str, Any]:
        """Get information tentang available providers"""
        info = {}

        for provider in LLMProvider:
            is_available = self.is_provider_available(provider)
            config = {}

            if provider == LLMProvider.OPENAI:
                config = {
                    "model": self.openai_model,
                    "temperature": self.openai_temperature,
                    "max_tokens": self.openai_max_tokens,
                    "has_api_key": bool(self.openai_api_key)
                }
            elif provider == LLMProvider.GOOGLE:
                config = {
                    "model": self.google_model,
                    "temperature": self.google_temperature,
                    "has_api_key": bool(self.google_api_key)
                }
            elif provider == LLMProvider.ANTHROPIC:
                config = {
                    "model": self.anthropic_model,
                    "temperature": self.anthropic_temperature,
                    "has_api_key": bool(self.anthropic_api_key)
                }
            elif provider == LLMProvider.GROQ:
                config = {
                    "model": self.groq_model,
                    "has_api_key": bool(self.groq_api_key)
                }

            info[provider.value] = {
                "available": is_available,
                "config": config
            }

        return info

# Global LLM config instance
llm_config = LLMConfig()

def get_llm_client(provider: LLMProvider):
    """Get LLM client dependency untuk FastAPI"""
    return llm_config.get_client(provider)

def get_default_llm_provider() -> LLMProvider:
    """Get default LLM provider (first available)"""
    available = llm_config.get_available_providers()
    if available:
        return available[0]
    else:
        raise Exception("No LLM providers available")

async def generate_with_fallback(prompt: str, **kwargs) -> Optional[str]:
    """Generate text dengan fallback ke provider lain jika gagal"""

    available_providers = llm_config.get_available_providers()

    for provider in available_providers:
        logger.info(f"Trying to generate with {provider.value}")

        result = await llm_config.generate_text(provider, prompt, **kwargs)
        if result:
            logger.success(f"Successfully generated with {provider.value}")
            return result

        logger.warning(f"Failed to generate with {provider.value}, trying next provider")

    logger.error("All LLM providers failed")
    return None
