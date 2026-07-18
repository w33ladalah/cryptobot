from abc import ABC, abstractmethod
from typing import Optional, Dict, List


class MarketDataProvider(ABC):
    """Abstract base class for market data providers.
    
    All market data providers must implement this interface to ensure
    consistent behavior across different data sources (DexScreener, GeckoTerminal, etc.).
    """
    
    @abstractmethod
    def search_token_pairs(self, query: str) -> List[Dict]:
        """Search for token pairs matching the given query.
        
        Args:
            query (str): The search query string (e.g., token name, symbol, or address).
            
        Returns:
            List[Dict]: A list of dictionaries containing token pair information.
                The exact structure varies by provider, but should include at minimum:
                - Pool/pair address
                - Token information (addresses, symbols, names)
                - Basic market data (price, liquidity if available)
        """
        pass
    
    @abstractmethod
    def get_realtime_data(self, chain: str, pair_address: str) -> Optional[Dict[str, float]]:
        """Get realtime market data for a specific pair.
        
        Args:
            chain (str): The chain/network identifier (format varies by provider).
            pair_address (str): The address of the specific pair/pool.
            
        Returns:
            Optional[Dict[str, float]]: A dictionary containing:
                - "price": The current price in USD (float)
                - "liquidity": Liquidity value in USD (float)
                - "price_change_1h": Price change from 1 hour ago in percentage (float)
                
            Returns None if no data is found for the specified pair.
            
        Note:
            This return contract is fixed regardless of provider, since
            combine_data/analyze_with_llm depend on these exact field names and types.
        """
        pass
