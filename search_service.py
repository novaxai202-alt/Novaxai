import os
from googleapiclient.discovery import build
from typing import List, Dict
from datetime import datetime, timezone

class NovaXSearch:
    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        self.search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")

        
    async def search(self, query: str, num_results: int = 5) -> Dict:
        """Search using Google Programmable Search Engine with real-time optimization"""
        try:
            # Enhance query for real-time results
            enhanced_query = self._enhance_query_for_realtime(query)
            
            # Try Google Programmable Search Engine first
            if self.google_api_key and self.search_engine_id:
                results = await self._google_search(enhanced_query, num_results)
                if results["results"]:
                    return results
            
            return {"results": [], "source": "no_api", "error": "No search APIs configured"}
            
        except Exception as e:
            return {"results": [], "source": "error", "error": str(e)}
    
    def _enhance_query_for_realtime(self, query: str) -> str:
        """Enhance search query for better real-time results"""
        realtime_keywords = ['latest', 'current', 'today', 'now', 'recent', 'breaking', 'live']
        query_lower = query.lower()
        
        # Add time-based modifiers for better real-time results
        if any(keyword in query_lower for keyword in ['news', 'update', 'happening']):
            if not any(rt_keyword in query_lower for rt_keyword in realtime_keywords):
                query += " latest news"
        
        # Add current year for time-sensitive queries
        current_year = datetime.now().year
        if any(keyword in query_lower for keyword in ['price', 'stock', 'rate', 'statistics']):
            if str(current_year) not in query:
                query += f" {current_year}"
        
        return query
    
    async def _google_search(self, query: str, num_results: int) -> Dict:
        """Google Programmable Search Engine implementation with real-time focus"""
        try:
            service = build("customsearch", "v1", developerKey=self.google_api_key)
            
            # Search parameters optimized for real-time results
            search_params = {
                'q': query,
                'cx': self.search_engine_id,
                'num': num_results,
                'sort': 'date'  # Sort by date for more recent results
            }
            
            result = service.cse().list(**search_params).execute()
            
            results = []
            for item in result.get('items', []):
                # Extract publish date if available
                publish_date = self._extract_publish_date(item)
                
                results.append({
                    "title": item.get('title', ''),
                    "link": item.get('link', ''),
                    "snippet": item.get('snippet', ''),
                    "source": self._extract_domain(item.get('link', '')),
                    "publish_date": publish_date,
                    "relevance_score": self._calculate_relevance_score(item, query)
                })
            
            # Sort by relevance and recency
            results.sort(key=lambda x: (x.get('relevance_score', 0), x.get('publish_date', '')), reverse=True)
            
            return {
                "results": results,
                "source": "google_pse",
                "query": query,
                "total_results": result.get('searchInformation', {}).get('totalResults', '0'),
                "search_time": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            print(f"Google Search error: {e}")
            return {"results": [], "source": "google_pse", "error": str(e)}
    

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL for citation"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc.replace('www.', '')
        except:
            return url
    
    def _extract_publish_date(self, item: dict) -> str:
        """Extract publish date from search result"""
        try:
            # Try to get date from pagemap or other metadata
            pagemap = item.get('pagemap', {})
            
            # Check various date fields
            date_fields = ['metatags', 'article', 'newsarticle']
            for field in date_fields:
                if field in pagemap:
                    for meta in pagemap[field]:
                        for date_key in ['publishedtime', 'datePublished', 'article:published_time', 'pubdate']:
                            if date_key in meta:
                                return meta[date_key]
            
            return datetime.now(timezone.utc).isoformat()
        except:
            return datetime.now(timezone.utc).isoformat()
    
    def _calculate_relevance_score(self, item: dict, query: str) -> float:
        """Calculate relevance score for search result"""
        try:
            score = 0.0
            query_words = query.lower().split()
            
            title = item.get('title', '').lower()
            snippet = item.get('snippet', '').lower()
            
            # Score based on query word matches
            for word in query_words:
                if word in title:
                    score += 2.0
                if word in snippet:
                    score += 1.0
            
            # Bonus for recent content indicators
            recent_indicators = ['today', 'latest', 'breaking', 'live', '2024']
            for indicator in recent_indicators:
                if indicator in title or indicator in snippet:
                    score += 0.5
            
            return score
        except:
            return 0.0
    
    def format_search_context(self, search_results: Dict, query: str) -> str:
        """Format search results for AI context with real-time information"""
        if not search_results.get("results"):
            return f"No search results found for: {query}"
        
        search_time = search_results.get('search_time', datetime.now(timezone.utc).isoformat())
        context = f"🔍 Real-time Search Results for '{query}' (Retrieved: {search_time}):\n\n"
        
        for i, result in enumerate(search_results["results"], 1):
            context += f"{i}. **{result['title']}**\n"
            context += f"   📍 Source: {result['source']}\n"
            context += f"   🔗 URL: {result['link']}\n"
            context += f"   📄 Summary: {result['snippet']}\n"
            
            if result.get('publish_date'):
                context += f"   📅 Published: {result['publish_date']}\n"
            
            context += "\n"
        
        context += f"🚀 Search powered by NovaX Search Engine\n"
        context += f"📊 Total results available: {search_results.get('total_results', 'Unknown')}\n"
        context += f"⏰ Search completed at: {search_time}"
        
        return context
    
    def generate_citations(self, search_results: Dict) -> List[str]:
        """Generate citation format for search results with timestamps"""
        citations = []
        search_time = search_results.get('search_time', datetime.now(timezone.utc).isoformat())
        
        for i, result in enumerate(search_results.get("results", []), 1):
            citation = f"[{i}] {result['title']} - {result['source']}"
            if result.get('publish_date'):
                citation += f" (Published: {result['publish_date'][:10]})"
            citation += f" - {result['link']}"
            citations.append(citation)
        
        citations.append(f"\n🕐 Search performed: {search_time[:19]} UTC")
        return citations

# Global search instance
novax_search = NovaXSearch()