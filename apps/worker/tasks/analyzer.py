from celery import shared_task
from core.market_data import get_historical_data, get_realtime_data, combine_data, search_token_pairs
from llm.llm_analysis import analyze_with_llm
from core.trading.ethereum import EthereumExecutor
from devtools import debug
from config.redis import redis_client
import json


def _resolve_token_address(token_id: str, pair: dict) -> str:
    """
    Resolve the real ERC20 token contract address for a given token_id from pair data.

    This function matches the token_id against the base/quote token metadata in the pair
    data (case-insensitively) and returns the corresponding token address. If neither
    side matches, returns None.

    Args:
        token_id (str): The token identifier to resolve (e.g., "USDC", "usdc", "0x...").
        pair (dict): The pair/pool data from the market data provider.

    Returns:
        str: The ERC20 token contract address, or None if no match found.
    """
    token_id_lower = token_id.lower()

    # Handle DexScreener format
    if 'baseToken' in pair and 'quoteToken' in pair:
        base_token = pair['baseToken']
        quote_token = pair['quoteToken']

        # Check base token
        if (base_token.get('address', '').lower() == token_id_lower or
            base_token.get('symbol', '').lower() == token_id_lower or
            base_token.get('name', '').lower() == token_id_lower):
            return base_token.get('address')

        # Check quote token
        if (quote_token.get('address', '').lower() == token_id_lower or
            quote_token.get('symbol', '').lower() == token_id_lower or
            quote_token.get('name', '').lower() == token_id_lower):
            return quote_token.get('address')

    # Handle GeckoTerminal format
    elif 'base_token_address' in pair and 'quote_token_address' in pair:
        base_address = pair.get('base_token_address', '').lower()
        quote_address = pair.get('quote_token_address', '').lower()
        base_symbol = pair.get('base_token_symbol', '').lower()
        quote_symbol = pair.get('quote_token_symbol', '').lower()

        # Check base token
        if (base_address == token_id_lower or base_symbol == token_id_lower):
            return pair.get('base_token_address')

        # Check quote token
        if (quote_address == token_id_lower or quote_symbol == token_id_lower):
            return pair.get('quote_token_address')

    # No match found
    return None


def _map_chain_to_executor_network(chain: str) -> str:
    """
    Map provider chain names to EthereumExecutor-compatible network names.

    Args:
        chain (str): Chain identifier from provider (e.g., "ethereum", "mainnet", "sepolia").

    Returns:
        str: Network name compatible with EthereumExecutor ("mainnet" or "sepolia").
    """
    chain_lower = chain.lower()
    if chain_lower in ['ethereum', 'mainnet', 'eth']:
        return 'mainnet'
    elif chain_lower in ['sepolia', 'sepolia-testnet']:
        return 'sepolia'
    else:
        # Default to mainnet for unknown chains
        return 'mainnet'


def _get_pair_chain_and_address(pair: dict) -> tuple:
    """
    Extract chain and pair address from pair data, handling different provider formats.

    Args:
        pair (dict): The pair/pool data from the market data provider.

    Returns:
        tuple: (chain, pair_address)
    """
    # DexScreener format
    if 'chainId' in pair and 'pairAddress' in pair:
        return pair['chainId'], pair['pairAddress']

    # GeckoTerminal format - use address as pair address, need to infer chain
    if 'address' in pair:
        # For GeckoTerminal, we'll use the pool address directly
        # The chain needs to be determined from context or config
        # For now, default to mainnet if not specified
        return 'mainnet', pair['address']

    # Fallback
    return None, None


@shared_task(name='perform_llm_analysis')
def perform_llm_analysis(token_id, store_results=False):
    # Fetch data
    historical_data = get_historical_data(token_id, days=30)

    if store_results and historical_data:
        # Store historical data in Redis
        historical_data_key = f"historical_data:{token_id}"
        redis_client.set(historical_data_key, json.dumps(historical_data))

    # Fetch token pairs
    token_pairs = search_token_pairs(token_id)

    if store_results:
        # Store token pairs in Redis
        token_pairs_key = f"token_pairs:{token_id}"
        redis_client.set(token_pairs_key, json.dumps(token_pairs))

    analysis_results = []
    for pair in token_pairs:
        # Resolve token address from pair data
        token_address = _resolve_token_address(token_id, pair)
        if not token_address:
            # Skip pairs where we can't resolve the token address
            continue

        # Get chain and pair address (provider-agnostic)
        chain, pair_address = _get_pair_chain_and_address(pair)
        if not chain or not pair_address:
            continue

        # Fetch real-time data
        real_time_data = get_realtime_data(chain, pair_address)

        if store_results:
            # Store real-time data in Redis
            real_time_data_key = f"real_time_data:{chain}:{pair_address}"
            redis_client.set(real_time_data_key, json.dumps(real_time_data))

        if historical_data and real_time_data:
            # Process data
            combined_data = combine_data(historical_data, real_time_data)

            if combined_data is not None:
                if store_results:
                    # Store combined data in Redis
                    combined_data_key = f"combined_data:{chain}:{pair_address}"
                    redis_client.set(combined_data_key, combined_data.to_json())

                # LLM-based analysis with resolved token address
                analysis_result = analyze_with_llm(token_id, chain=chain, pair_address=pair_address, data=combined_data)
                analysis_results.append(analysis_result)

                # Execute trade if analysis returns a BUY/SELL decision
                if analysis_result and analysis_result.get('decision'):
                    decision = analysis_result['decision'].upper()
                    if decision in ['BUY', 'SELL']:
                        # Map chain to EthereumExecutor-compatible network
                        network = _map_chain_to_executor_network(chain)

                        executor = EthereumExecutor(
                            token_address=token_address,
                            network=network,
                            provider='infura'
                        )

                        if decision == 'BUY':
                            executor.execute(decision='BUY', amount_eth=0.001)
                        elif decision == 'SELL':
                            executor.execute(decision='SELL', amount_tokens=None)
                    else:
                        print(f"HOLD decision for token {token_id} - no execution")

    debug(analysis_results)

    return analysis_results
