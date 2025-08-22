"""
LLM Service
===========

Service untuk berinteraksi dengan berbagai Large Language Models.
Mendukung Gemini, OpenAI, dan model lainnya.

Author: AI Assistant
Version: 2.0.0
Updated: Sesuai dengan instruksi Orchestrated RAG terbaru
"""

import asyncio
from typing import Dict, Any, Optional, List, Union
from abc import ABC, abstractmethod
import google.generativeai as genai
import openai
from openai import AsyncOpenAI

from ..core.models import LLMModel
from ..utils.logger import get_logger

# Import config from root directory
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.config import Config

logger = get_logger("LLMService")

class BaseLLMProvider(ABC):
    """Base class untuk LLM providers"""

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate text dari prompt"""
        pass

    @abstractmethod
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding dari text"""
        pass

class GeminiProvider(BaseLLMProvider):
    """Provider untuk Google Gemini"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model_mapping = {
            LLMModel.GEMINI_1_5_FLASH: "gemini-1.5-flash",
            LLMModel.GEMINI_1_5_PRO: "gemini-1.5-pro"
        }
        logger.info("Gemini provider initialized")

    async def generate_text(
        self,
        prompt: str,
        model: str = "gemini-1.5-flash",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate text menggunakan Gemini"""
        try:
            model_instance = genai.GenerativeModel(model)

            generation_config = genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature
            )

            response = await asyncio.to_thread(
                model_instance.generate_content,
                prompt,
                generation_config=generation_config
            )

            return response.text.strip()

        except Exception as e:
            logger.error(f"Error generating text with Gemini: {str(e)}")
            raise

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding menggunakan Gemini"""
        try:
            result = await asyncio.to_thread(
                genai.embed_content,
                model="models/embedding-001",
                content=text
            )
            return result['embedding']

        except Exception as e:
            logger.error(f"Error generating embedding with Gemini: {str(e)}")
            raise

class OpenAIProvider(BaseLLMProvider):
    """Provider untuk OpenAI"""

    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model_mapping = {
            LLMModel.GPT_4: "gpt-4",
            LLMModel.GPT_4_TURBO: "gpt-4-turbo-preview",
            LLMModel.GPT_3_5_TURBO: "gpt-3.5-turbo"
        }
        logger.info("OpenAI provider initialized")

    async def generate_text(
        self,
        prompt: str,
        model: str = "gpt-4",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate text menggunakan OpenAI"""
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error generating text with OpenAI: {str(e)}")
            raise

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding menggunakan OpenAI"""
        try:
            response = await self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )

            return response.data[0].embedding

        except Exception as e:
            logger.error(f"Error generating embedding with OpenAI: {str(e)}")
            raise

class LLMService:
    """
    Main LLM Service yang mengatur semua providers
    """

    def __init__(self):
        self.providers: Dict[str, BaseLLMProvider] = {}
        self._initialize_providers()
        logger.info("LLM Service initialized")

    def _initialize_providers(self):
        """Initialize semua available providers"""
        # Initialize Gemini if API key available
        if Config.GEMINI_API_KEY:
            try:
                self.providers["gemini"] = GeminiProvider(Config.GEMINI_API_KEY)
                logger.success("Gemini provider initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini provider: {str(e)}")

        # Initialize OpenAI if API key available
        if Config.OPENAI_API_KEY:
            try:
                self.providers["openai"] = OpenAIProvider(Config.OPENAI_API_KEY)
                logger.success("OpenAI provider initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI provider: {str(e)}")

        if not self.providers:
            logger.error("No LLM providers available. Please check API keys.")
            raise ValueError("No LLM providers available")

    async def generate_text(
        self,
        prompt: str,
        model: str = "gemini",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Generate text menggunakan model yang dipilih

        Args:
            prompt: Text prompt
            model: Model choice ("gemini", "openai", atau specific model)
            max_tokens: Maximum tokens to generate
            temperature: Generation temperature

        Returns:
            str: Generated text
        """
        try:
            # Determine provider and model
            provider_name, model_name = self._parse_model_choice(model)

            if provider_name not in self.providers:
                raise ValueError(f"Provider {provider_name} not available")

            provider = self.providers[provider_name]

            # Generate text
            result = await provider.generate_text(
                prompt=prompt,
                model=model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )

            logger.debug(f"Text generated successfully using {provider_name}")
            return result

        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            raise

    async def generate_embedding(self, text: str, provider: str = "gemini") -> List[float]:
        """
        Generate embedding untuk text

        Args:
            text: Input text
            provider: Provider choice ("gemini" atau "openai")

        Returns:
            List[float]: Embedding vector
        """
        try:
            if provider not in self.providers:
                raise ValueError(f"Provider {provider} not available")

            embedding = await self.providers[provider].generate_embedding(text)
            logger.debug(f"Embedding generated successfully using {provider}")
            return embedding

        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise

    def _parse_model_choice(self, model: str) -> tuple[str, str]:
        """
        Parse model choice ke provider dan model name

        Args:
            model: Model choice string

        Returns:
            tuple: (provider_name, model_name)
        """
        # Map common model choices
        model_mappings = {
            "gemini": ("gemini", "gemini-1.5-flash"),
            "gemini-flash": ("gemini", "gemini-1.5-flash"),
            "gemini-pro": ("gemini", "gemini-1.5-pro"),
            "openai": ("openai", "gpt-4"),
            "gpt-4": ("openai", "gpt-4"),
            "gpt-4-turbo": ("openai", "gpt-4-turbo-preview"),
            "gpt-3.5": ("openai", "gpt-3.5-turbo")
        }

        if model in model_mappings:
            return model_mappings[model]

        # Default fallback
        if "gemini" in self.providers:
            return ("gemini", "gemini-1.5-flash")
        elif "openai" in self.providers:
            return ("openai", "gpt-4")
        else:
            raise ValueError("No available providers")

    def get_available_models(self) -> Dict[str, List[str]]:
        """Get list of available models by provider"""
        available = {}

        if "gemini" in self.providers:
            available["gemini"] = ["gemini-1.5-flash", "gemini-1.5-pro"]

        if "openai" in self.providers:
            available["openai"] = ["gpt-4", "gpt-4-turbo-preview", "gpt-3.5-turbo"]

        return available

    def is_provider_available(self, provider: str) -> bool:
        """Check if provider is available"""
        return provider in self.providers

    async def health_check(self) -> Dict[str, bool]:
        """Check health of all providers"""
        health_status = {}

        for provider_name, provider in self.providers.items():
            try:
                # Simple test generation
                await provider.generate_text("Test", max_tokens=10)
                health_status[provider_name] = True
                logger.debug(f"Provider {provider_name} health check passed")
            except Exception as e:
                health_status[provider_name] = False
                logger.warning(f"Provider {provider_name} health check failed: {str(e)}")

        return health_status

# Singleton instance
_llm_service_instance: Optional[LLMService] = None

def get_llm_service() -> LLMService:
    """Get singleton LLM service instance"""
    global _llm_service_instance
    if _llm_service_instance is None:
        _llm_service_instance = LLMService()
    return _llm_service_instance
