from typing import Optional, Dict, List
import httpx
from config.settings import config
from core.market_data_providers.base import MarketDataProvider


class DexScreenerProvider(MarketDataProvider):
    """DexScreener implementation of MarketDataProvider.

    This provider wraps the existing DexScreener-based logic into the
    MarketDataProvider interface, maintaining backward compatibility.
    """

    def __init__(self):
        self.api_url = config.DEXSCREENER_API

    def search_token_pairs(self, query: str) -> List[Dict]:
        """Search for token pairs using DexScreener API.

        Args:
            query (str): The search query string.

        Returns:
            List[Dict]: A list of dictionaries containing token pair information
                from DexScreener's search endpoint.

        Raises:
            Exception: If there is an error during the API request or response processing.
        """
        try:
            response = httpx.get(f"{self.api_url}/search/?q={query}".replace("/pairs/", "/"))
            response.raise_for_status()
            data = response.json()
            return data.get("pairs", [])
        except Exception as e:
            raise Exception(str(e))

    def get_realtime_data(self, chain: str, pair_address: str) -> Optional[Dict[str, float]]:
        """Get realtime data from DexScreener for a given chain and address.

        Args:
            chain (str): The chain identifier (e.g., "ethereum", "solana").
            pair_address (str): The address of the specific pair.

        Returns:
            Optional[Dict[str, float]]: A dictionary containing:
                - "price": The bid/ask price in USD (float)
                - "liquidity": Liquidity value in USD (float)
                - "price_change_1h": Price change from 1 hour ago in USD (float)

            Returns None if no data is found for the specified pair.
        """
        url = f"{self.api_url}/pairs/{chain}/{pair_address}"
        response = httpx.get(url)
        data = response.json()

        if 'pairs' in data and len(data['pairs']) > 0:
            price_change = data['pairs'][0]["priceChange"]
            return {
                "price": float(data['pairs'][0]["priceUsd"]),
                "liquidity": float(data['pairs'][0]["liquidity"]["usd"]),
                "price_change_1h": float(price_change.get("h1", 0)),
            }
        return None
