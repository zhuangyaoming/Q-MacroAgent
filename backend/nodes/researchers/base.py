import asyncio
import logging
import os
from datetime import datetime
from typing import Any, Dict, List

from openai import AsyncOpenAI
from openai import OpenAI

from tavily import AsyncTavilyClient

from ...classes import ResearchState
from ...utils.references import clean_title

logger = logging.getLogger(__name__)

class BaseResearcher:
    def __init__(self):
        tavily_key = os.getenv("TAVILY_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        if not tavily_key or not openai_key:
            raise ValueError("Missing API keys")
            
        self.tavily_client = AsyncTavilyClient(api_key=tavily_key)
        self.openai_client = OpenAI(
                                api_key=openai_key,
                                base_url="https://api.deepseek.com"  # DeepSeek API endpoint
                            )
        self.analyst_type = "base_researcher"  # Default type
        
    @property
    def analyst_type(self) -> str:
        if not hasattr(self, '_analyst_type'):
            raise ValueError("Analyst type not set by subclass")
        return self._analyst_type

    @analyst_type.setter
    def analyst_type(self, value: str):
        self._analyst_type = value

    async def generate_queries(self, state: Dict, prompt: str) -> List[str]:
        company = state.get("company", "Unknown Company")
        industry = state.get("industry", "Unknown Industry")
        hq = state.get("hq", "Unknown HQ")
        current_year = datetime.now().year
        websocket_manager = state.get('websocket_manager')
        job_id = state.get('job_id')
        
        try:
            logger.info(f"Generating queries for {company} as {self.analyst_type}")
            
            response = await self.openai_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are researching {company}, a company in the {industry} industry."
                    },
                    {
                        "role": "user",
                        "content": f"""Researching {company} on {datetime.now().strftime("%B %d, %Y")}.
{self._format_query_prompt(prompt, company, hq, current_year)}"""
                    }
                ],
                temperature=0.01,
                max_tokens=4096,
                stream=True
            )
            
            queries = []
            current_query = ""
            current_query_number = 1

            async for chunk in response:
                if chunk.choices[0].finish_reason == "stop":
                    break
                    
                content = chunk.choices[0].delta.content
                if content:
                    current_query += content
                    
                    # Stream the current state to the UI.
                    if websocket_manager and job_id:
                        await websocket_manager.send_status_update(
                            job_id=job_id,
                            status="query_generating",
                            message="Generating research query",
                            result={
                                "query": current_query,
                                "query_number": current_query_number,
                                "category": self.analyst_type,
                                "is_complete": False
                            }
                        )
                    
                    # If a newline is detected, treat it as a complete query.
                    if '\n' in current_query:
                        parts = current_query.split('\n')
                        current_query = parts[-1]  # The last part is the start of the next query.
                        
                        for query in parts[:-1]:
                            query = query.strip()
                            if query:
                                queries.append(query)
                                if websocket_manager and job_id:
                                    await websocket_manager.send_status_update(
                                        job_id=job_id,
                                        status="query_generated",
                                        message="Generated new research query",
                                        result={
                                            "query": query,
                                            "query_number": len(queries),
                                            "category": self.analyst_type,
                                            "is_complete": True
                                        }
                                    )
                                current_query_number += 1

            # Add any remaining query (even if not newline terminated)
            if current_query.strip():
                query = current_query.strip()
                queries.append(query)
                if websocket_manager and job_id:
                    await websocket_manager.send_status_update(
                        job_id=job_id,
                        status="query_generated",
                        message="Generated final research query",
                        result={
                            "query": query,
                            "query_number": len(queries),
                            "category": self.analyst_type,
                            "is_complete": True
                        }
                    )
                current_query_number += 1
            
            logger.info(f"Generated {len(queries)} queries for {self.analyst_type}: {queries}")

            if not queries:
                raise ValueError(f"No queries generated for {company}")

            # Limit to at most 4 queries.
            queries = queries[:4]
            logger.info(f"Final queries for {self.analyst_type}: {queries}")
            
            return queries
            
        except Exception as e:
            logger.error(f"Error generating queries for {company}: {e}")
            if websocket_manager and job_id:
                await websocket_manager.send_status_update(
                    job_id=job_id,
                    status="error",
                    message=f"Failed to generate research queries: {str(e)}",
                    error=f"Query generation failed: {str(e)}"
                )
            return []

    def _format_query_prompt(self, prompt, company, hq, year):
        return f"""{prompt}

        Important Guidelines:
        - Focus ONLY on {company}-specific information
        - Make queries very brief and to the point
        - Provide exactly 4 search queries (one per line), with no hyphens or dashes
        - DO NOT make assumptions about the industry - use only the provided industry information"""

    def _fallback_queries(self, company, year):
        return [
            f"{company} overview {year}",
            f"{company} recent news {year}",
            f"{company} financial reports {year}",
            f"{company} industry analysis {year}"
        ]

    async def search_single_query(self, query: str, websocket_manager=None, job_id=None) -> Dict[str, Any]:
        """Execute a single search query with proper error handling."""
        if not query or len(query.split()) < 3:
            return {}

        try:
            if websocket_manager and job_id:
                await websocket_manager.send_status_update(
                    job_id=job_id,
                    status="query_searching",
                    message=f"Searching: {query}",
                    result={
                        "step": "Searching",
                        "query": query
                    }
                )

            # Add news topic for news analysts
            search_params = {
                "search_depth": "basic",
                "include_raw_content": False,
                "max_results": 5
            }
            
            if self.analyst_type == "news_analyst":
                search_params["topic"] = "news"
            elif self.analyst_type == "financial_analyst":
                search_params["topic"] = "finance"

            results = await self.tavily_client.search(
                query,
                **search_params
            )
            
            docs = {}
            for result in results.get("results", []):
                if not result.get("content") or not result.get("url"):
                    continue
                    
                url = result.get("url")
                title = result.get("title", "")
                
                # Clean up and validate the title using the references module
                if title:
                    title = clean_title(title)
                    # If title is the same as URL or empty, set to empty to trigger extraction later
                    if title.lower() == url.lower() or not title.strip():
                        title = ""
                
                logger.info(f"Tavily search result for '{query}': URL={url}, Title='{title}'")
                
                docs[url] = {
                    "title": title,
                    "content": result.get("content", ""),
                    "query": query,
                    "url": url,
                    "source": "web_search",
                    "score": result.get("score", 0.0)
                }

            if websocket_manager and job_id:
                await websocket_manager.send_status_update(
                    job_id=job_id,
                    status="query_searched",
                    message=f"Found {len(docs)} results for: {query}",
                    result={
                        "step": "Searching",
                        "query": query,
                        "results_count": len(docs)
                    }
                )

            return docs
            
        except Exception as e:
            logger.error(f"Error searching query '{query}': {e}")
            if websocket_manager and job_id:
                await websocket_manager.send_status_update(
                    job_id=job_id,
                    status="query_error",
                    message=f"Search failed for: {query}",
                    result={
                        "step": "Searching",
                        "query": query,
                        "error": str(e)
                    }
                )
            return {}

    async def search_documents(self, state: ResearchState, queries: List[str]) -> Dict[str, Any]:
        """
        Execute all Tavily searches in parallel at maximum speed
        """
        websocket_manager = state.get('websocket_manager')
        job_id = state.get('job_id')

        if not queries:
            logger.error("No valid queries to search")
            return {}

        # Send status update for generated queries
        if websocket_manager and job_id:
            await websocket_manager.send_status_update(
                job_id=job_id,
                status="queries_generated",
                message=f"Generated {len(queries)} queries for {self.analyst_type}",
                result={
                    "step": "Searching",
                    "analyst": self.analyst_type,
                    "queries": queries,
                    "total_queries": len(queries)
                }
            )

        # Prepare all search parameters upfront
        search_params = {
            "search_depth": "basic",
            "include_raw_content": False,
            "max_results": 5
        }
        
        if self.analyst_type == "news_analyst":
            search_params["topic"] = "news"
        elif self.analyst_type == "financial_analyst":
            search_params["topic"] = "finance"

        if websocket_manager and job_id:
            await websocket_manager.send_status_update(
                job_id=job_id,
                status="search_started",
                message=f"Using Tavily to search for {len(queries)} queries",
                result={
                    "step": "Searching",
                    "total_queries": len(queries)
                }
            )
        # Create all API calls upfront - direct Tavily client calls without the extra wrapper
        search_tasks = [
            self.tavily_client.search(query, **search_params)
            for query in queries
        ]

        # Execute all API calls in parallel
        try:
            results = await asyncio.gather(*search_tasks)
        except Exception as e:
            logger.error(f"Error during parallel search execution: {e}")
            return {}

        # Process results
        merged_docs = {}
        for query, result in zip(queries, results):
            for item in result.get("results", []):
                if not item.get("content") or not item.get("url"):
                    continue
                    
                url = item.get("url")
                title = item.get("title", "")
                
                if title:
                    title = clean_title(title)
                    if title.lower() == url.lower() or not title.strip():
                        title = ""

                merged_docs[url] = {
                    "title": title,
                    "content": item.get("content", ""),
                    "query": query,
                    "url": url,
                    "source": "web_search",
                    "score": item.get("score", 0.0)
                }

        # Send completion status
        if websocket_manager and job_id:
            await websocket_manager.send_status_update(
                job_id=job_id,
                status="search_complete",
                message=f"Search completed with {len(merged_docs)} documents found",
                result={
                    "step": "Searching",
                    "total_documents": len(merged_docs),
                    "queries_processed": len(queries)
                }
            )

        return merged_docs
