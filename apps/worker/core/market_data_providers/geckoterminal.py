from typing import Optional, Dict, List
import httpx
from config.settings import config
from core.market_data_providers.base import MarketDataProvider


class GeckoTerminalProvider(MarketDataProvider):
    """GeckoTerminal implementation of MarketDataProvider.

    This provider uses GeckoTerminal's JSON:API-based endpoints to fetch
    DEX market data. GeckoTerminal supports both mainnet and Sepolia testnet,
    making it suitable for testing environments.
    """

    # Network ID mapping: internal chain names -> GeckoTerminal network IDs
    NETWORK_MAPPING = {
        "mainnet": "eth",
        "sepolia": "sepolia-testnet",
        "ethereum": "eth",
    }

    def __init__(self, api_url: str = None):
        """Initialize the GeckoTerminal provider.

        Args:
            api_url (str, optional): The base URL for the GeckoTerminal API.
                If not provided, uses config.GECKOTERMINAL_API.
        """
        self.api_url = api_url or config.GECKOTERMINAL_API

    def _map_chain_to_network(self, chain: str) -> str:
        """Map internal chain name to GeckoTerminal network ID.

        Args:
            chain (str): Internal chain name (e.g., "mainnet", "sepolia").

        Returns:
            str: GeckoTerminal network ID (e.g., "eth", "sepolia-testnet").
        """
        return self.NETWORK_MAPPING.get(chain.lower(), chain.lower())

    def _extract_token_address(self, token_id: str) -> str:
        """Extract token address from GeckoTerminal's {network}_{address} format.

        Args:
            token_id (str): Token ID in format "{network}_{address}".

        Returns:
            str: The token address portion.
        """
        if "_" in token_id:
            return token_id.split("_", 1)[1]
        return token_id

    def search_token_pairs(self, query: str, network: Optional[str] = None) -> List[Dict]:
        """Search for token pairs using GeckoTerminal API.

        Args:
            query (str): The search query string.
            network (Optional[str]): Network to filter by (e.g., "eth", "sepolia-testnet").
                If not provided, searches across all networks.

        Returns:
            List[Dict]: A list of dictionaries containing token pair information
                from GeckoTerminal's search endpoint. Each dict includes:
                - Raw JSON:API response data
                - Extracted token addresses from relationships

        Raises:
            Exception: If there is an error during the API request or response processing.
        """
        try:
            params = {"query": query}
            if network:
                params["network"] = network

            response = httpx.get(f"{self.api_url}/search/pools", params=params)
            response.raise_for_status()
            data = response.json()

            # Enrich each pool with extracted token addresses for easier parsing
            pools = data.get("data", [])
            for pool in pools:
                if "relationships" in pool:
                    # Extract base token address
                    if "base_token" in pool["relationships"] and "data" in pool["relationships"]["base_token"]:
                        base_token_id = pool["relationships"]["base_token"]["data"].get("id", "")
                        pool["base_token_address"] = self._extract_token_address(base_token_id)

                    # Extract quote token address
                    if "quote_token" in pool["relationships"] and "data" in pool["relationships"]["quote_token"]:
                        quote_token_id = pool["relationships"]["quote_token"]["data"].get("id", "")
                        pool["quote_token_address"] = self._extract_token_address(quote_token_id)

            return pools
        except Exception as e:
            raise Exception(str(e))

    def get_realtime_data(self, chain: str, pair_address: str) -> Optional[Dict[str, float]]:
        """Get realtime data from GeckoTerminal for a given chain and pool address.

        Args:
            chain (str): The chain identifier (e.g., "mainnet", "sepolia").
            pair_address (str): The address of the specific pool.

        Returns:
            Optional[Dict[str, float]]: A dictionary containing:
                - "price": The current price in USD (float)
                - "liquidity": Liquidity value in USD (float)
                - "price_change_1h": Price change from 1 hour ago in percentage (float)

            Returns None if no data is found for the specified pool.
        """
        network = self._map_chain_to_network(chain)
        url = f"{self.api_url}/networks/{network}/pools/{pair_address}"

        try:
            response = httpx.get(url)
            response.raise_for_status()
            data = response.json()

            if "data" not in data or "attributes" not in data["data"]:
                return None

            attrs = data["data"]["attributes"]

            # Extract price (prefer base token price if available, otherwise quote)
            price = None
            if "base_token_price_usd" in attrs:
                price = float(attrs["base_token_price_usd"])
            elif "quote_token_price_usd" in attrs:
                price = float(attrs["quote_token_price_usd"])

            # Extract liquidity
            liquidity = float(attrs.get("reserve_in_usd", 0))

            # Extract 1h price change
            price_change_1h = 0.0
            if "price_change_percentage" in attrs and "h1" in attrs["price_change_percentage"]:
                price_change_1h = float(attrs["price_change_percentage"]["h1"])

            if price is None:
                return None

            return {
                "price": price,
                "liquidity": liquidity,
                "price_change_1h": price_change_1h,
            }
        except Exception:
            return None
