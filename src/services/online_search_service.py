"""
Online Search Service
====================

Service untuk pencarian online menggunakan DuckDuckGo Search API.
Digunakan ketika data yang dibutuhkan tidak ditemukan di dataset lokal.

Author: AI Assistant
Version: 2.0.0
Updated: Sesuai dengan instruksi Orchestrated RAG terbaru
"""

import asyncio
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import re

try:
    # Try new package first (ddgs)
    from ddgs import DDGS
except ImportError:
    try:
        # Fallback to old package (duckduckgo_search)
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None

import requests
from bs4 import BeautifulSoup

from ..utils.logger import get_logger

logger = get_logger("OnlineSearchService")

class OnlineSearchService:
    """
    Service untuk pencarian online dan web scraping
    """

    def __init__(self):
        self.search_engine = None
        self.max_retries = 3
        self.timeout = 10

        # Keywords untuk filter hasil pencarian yang relevan
        self.relevant_keywords = {
            "cp": ["capaian pembelajaran", "cp", "kurikulum merdeka", "pembelajaran"],
            "atp": ["alur tujuan pembelajaran", "atp", "tujuan pembelajaran", "learning objectives"],
            "modul": ["modul ajar", "lesson plan", "rpp", "teaching module"]
        }

        self._initialize_search_engine()
        logger.info("Online Search Service initialized")

    def _initialize_search_engine(self):
        """Initialize search engine"""
        if DDGS is None:
            logger.warning("DuckDuckGo Search not available. Install with: pip install duckduckgo-search")
            return

        try:
            self.search_engine = DDGS()
            logger.success("DuckDuckGo Search engine initialized")
        except Exception as e:
            logger.error(f"Failed to initialize search engine: {str(e)}")

    async def search(
        self,
        query: str,
        max_results: int = 5,
        doc_type: str = "general",
        language: str = "id"
    ) -> List[Dict[str, Any]]:
        """
        Perform online search

        Args:
            query: Search query
            max_results: Maximum number of results
            doc_type: Type of document being searched (cp, atp, modul, general)
            language: Language preference (id for Indonesian)

        Returns:
            List[Dict]: Search results with content
        """
        if not self.search_engine:
            logger.warning("Search engine not available")
            return []

        try:
            # Enhance query with relevant keywords
            enhanced_query = self._enhance_query(query, doc_type, language)

            logger.info(f"Searching online for: {enhanced_query}")

            # Perform search
            search_results = await self._perform_search(enhanced_query, max_results)

            # Filter and process results
            filtered_results = self._filter_relevant_results(search_results, doc_type)

            # Extract content from URLs
            content_results = await self._extract_content_from_urls(filtered_results)

            logger.info(f"Found {len(content_results)} relevant results")
            return content_results

        except Exception as e:
            logger.error(f"Error in online search: {str(e)}")
            return []

    def _enhance_query(self, query: str, doc_type: str, language: str) -> str:
        """Enhance query dengan keywords yang relevan"""
        # Add relevant keywords based on doc_type
        if doc_type in self.relevant_keywords:
            keywords = self.relevant_keywords[doc_type]
            # Add first relevant keyword to query
            enhanced = f"{query} {keywords[0]}"
        else:
            enhanced = query

        # Add language-specific terms
        if language == "id":
            enhanced += " kurikulum pendidikan Indonesia"

        return enhanced

    async def _perform_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Perform actual search using DuckDuckGo"""
        try:
            # Use asyncio.to_thread to make sync call async
            results = await asyncio.to_thread(
                self._sync_search,
                query,
                max_results
            )
            return results

        except Exception as e:
            logger.error(f"Error performing search: {str(e)}")
            return []

    def _sync_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Synchronous search function"""
        try:
            results = []
            search_results = self.search_engine.text(
                query,  # Use positional argument instead of keywords
                max_results=max_results,
                region="id-id",  # Indonesia region
                safesearch="moderate"
            )

            for result in search_results:
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "snippet": result.get("body", ""),
                    "source": "duckduckgo"
                })

            return results

        except Exception as e:
            logger.error(f"Error in sync search: {str(e)}")
            return []

    def _filter_relevant_results(self, results: List[Dict[str, Any]], doc_type: str) -> List[Dict[str, Any]]:
        """Filter hasil search untuk mendapatkan yang paling relevan"""
        if not results:
            return []

        filtered = []
        relevant_keywords = self.relevant_keywords.get(doc_type, [])

        for result in results:
            # Check relevance based on title and snippet
            title = result.get("title", "").lower()
            snippet = result.get("snippet", "").lower()

            relevance_score = 0

            # Check for relevant keywords
            for keyword in relevant_keywords:
                if keyword.lower() in title:
                    relevance_score += 2
                if keyword.lower() in snippet:
                    relevance_score += 1

            # Check for educational domains
            url = result.get("url", "").lower()
            if any(domain in url for domain in ["edu", "ac.id", "kemdikbud", "pembelajaran"]):
                relevance_score += 1

            # Only include results with some relevance
            if relevance_score > 0:
                result["relevance_score"] = relevance_score
                filtered.append(result)

        # Sort by relevance score
        filtered.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

        return filtered[:5]  # Return top 5 most relevant

    async def _extract_content_from_urls(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract content dari URLs hasil pencarian"""
        content_results = []

        for result in search_results:
            url = result.get("url", "")
            if not url:
                continue

            try:
                # Extract content from URL
                content = await self._extract_url_content(url)

                if content:
                    content_result = {
                        "title": result.get("title", ""),
                        "url": url,
                        "content": content,
                        "snippet": result.get("snippet", ""),
                        "relevance_score": result.get("relevance_score", 0),
                        "source": "online_search",
                        "extracted_at": datetime.now().isoformat()
                    }
                    content_results.append(content_result)

            except Exception as e:
                logger.warning(f"Failed to extract content from {url}: {str(e)}")
                continue

        return content_results

    async def _extract_url_content(self, url: str) -> Optional[str]:
        """Extract content dari single URL"""
        try:
            # Use asyncio.to_thread untuk make requests async
            response = await asyncio.to_thread(
                self._fetch_url_content,
                url
            )

            if not response:
                return None

            # Parse HTML content
            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Extract text content
            text = soup.get_text()

            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)

            # Limit content length
            max_length = 3000
            if len(text) > max_length:
                text = text[:max_length] + "..."

            return text

        except Exception as e:
            logger.warning(f"Error extracting content from {url}: {str(e)}")
            return None

    def _fetch_url_content(self, url: str) -> Optional[requests.Response]:
        """Fetch content dari URL dengan proper headers"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'id,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }

            response = requests.get(
                url,
                headers=headers,
                timeout=self.timeout,
                verify=False  # For testing, should be True in production
            )

            response.raise_for_status()
            return response

        except Exception as e:
            logger.warning(f"Failed to fetch {url}: {str(e)}")
            return None

    async def search_educational_content(
        self,
        mata_pelajaran: str,
        kelas: str,
        topik: str,
        content_type: str = "cp"
    ) -> List[Dict[str, Any]]:
        """
        Specialized search untuk educational content

        Args:
            mata_pelajaran: Subject
            kelas: Grade level
            topik: Topic
            content_type: Type of content (cp, atp, modul)

        Returns:
            List[Dict]: Educational content results
        """
        # Build specialized query
        query_parts = [mata_pelajaran, f"kelas {kelas}", topik]

        if content_type == "cp":
            query_parts.append("capaian pembelajaran")
        elif content_type == "atp":
            query_parts.append("alur tujuan pembelajaran")
        elif content_type == "modul":
            query_parts.append("modul ajar")

        query = " ".join(query_parts)

        # Perform search with educational focus
        results = await self.search(
            query=query,
            max_results=8,
            doc_type=content_type,
            language="id"
        )

        # Additional filtering untuk educational content
        educational_results = []
        for result in results:
            content = result.get("content", "").lower()

            # Check for educational indicators
            educational_indicators = [
                "kurikulum", "pembelajaran", "siswa", "guru", "pendidikan",
                "kompetensi", "indikator", "materi", "evaluasi"
            ]

            indicator_count = sum(1 for indicator in educational_indicators if indicator in content)

            if indicator_count >= 3:  # Must have at least 3 educational indicators
                result["educational_score"] = indicator_count
                educational_results.append(result)

        # Sort by educational relevance
        educational_results.sort(key=lambda x: x.get("educational_score", 0), reverse=True)

        return educational_results[:5]  # Return top 5 most educational

    def is_available(self) -> bool:
        """Check if online search is available"""
        return self.search_engine is not None

    async def health_check(self) -> Dict[str, Any]:
        """Health check untuk online search service"""
        if not self.is_available():
            return {
                "status": "unavailable",
                "message": "DuckDuckGo Search not installed or initialized"
            }

        try:
            # Test search
            test_results = await self.search("test kurikulum", max_results=1)

            return {
                "status": "healthy",
                "test_results_count": len(test_results),
                "last_check": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }

# Singleton instance
_online_search_service_instance: Optional[OnlineSearchService] = None

def get_online_search_service() -> OnlineSearchService:
    """Get singleton Online Search service instance"""
    global _online_search_service_instance
    if _online_search_service_instance is None:
        _online_search_service_instance = OnlineSearchService()
    return _online_search_service_instance
