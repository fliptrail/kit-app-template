"""Simple ZincSearch client for USD asset search"""

import aiohttp
import logging

logger = logging.getLogger(__name__)

class SimpleZincClient:
    def __init__(self, url, username, password):
        self.url = url
        self.index = "usd_assets"
        self.auth = aiohttp.BasicAuth(username, password)

    async def search(self, query, size=10):
        """Simple search in ZincSearch"""
        search_body = {
            "search_type": "match",
            "query": {
                "term": query,
                "field": "_all"
            },
            "from": 0,
            "max_results": size
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.url}/api/{self.index}/_search",
                    json=search_body,
                    auth=self.auth
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        hits = result.get("hits", {}).get("hits", [])
                        return [hit["_source"] for hit in hits]
                    return []
        except Exception as e:
            logger.error(f"ZincSearch error: {e}")
            return []
