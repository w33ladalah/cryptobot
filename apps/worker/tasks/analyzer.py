from celery import shared_task
from core.market_data import get_historical_data, get_realtime_data, combine_data, search_token_pairs
from llm.llm_analysis import analyze_with_llm
from core.trading.ethereum import EthereumExecutor
from devtools import debug
from config.redis import redis_client
from config.settings import config
import json
import logging

logger = logging.getLogger(__name__)


# Known token addresses per network (ground truth for verification)
# This allowlist is used to verify that the on-chain address resolved from GeckoTerminal
# matches the expected real-world asset before combining with CoinGecko historical data.
# See issue #31 for context on why this check exists.
KNOWN_TOKEN_ADDRESSES = {
    'sepolia': {
        'USDC': '0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238',  # Sepolia USDC
        'WETH': '0xfff9976782d46cc05630d1f6ebab18b2324d6b14',  # Sepolia WETH
    },
    'mainnet': {
        'USDC': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',  # Mainnet USDC
        'WETH': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',  # Mainnet WETH
    },
}

# Stablecoins that should be subject to price-plausibility checks
# These tokens have an expected ~$1 peg, so large deviations from historical prices
# are suspicious (e.g., testnet pool quoting $0.10 for a token that should be ~$1.00).
# See issue #34 for context on why this check exists.
STABLECOINS = {'USDC', 'USDT'}


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

        # Check base token by address
        if base_address == token_id_lower:
            return pair.get('base_token_address')

        # Check quote token by address
        if quote_address == token_id_lower:
            return pair.get('quote_token_address')

        # Check base token by symbol (if present)
        base_symbol = pair.get('base_token_symbol', '').lower()
        if base_symbol == token_id_lower:
            return pair.get('base_token_address')

        # Check quote token by symbol (if present)
        quote_symbol = pair.get('quote_token_symbol', '').lower()
        if quote_symbol == token_id_lower:
            return pair.get('quote_token_address')

        # Also check relationships for GeckoTerminal format
        if 'relationships' in pair:
            # Check base token from relationships
            if 'base_token' in pair['relationships'] and 'data' in pair['relationships']['base_token']:
                base_token_id = pair['relationships']['base_token']['data'].get('id', '')
                # Extract address from "network_address" format
                if '_' in base_token_id:
                    base_addr_from_id = base_token_id.split('_', 1)[1].lower()
                    if base_addr_from_id == token_id_lower:
                        return pair.get('base_token_address')

            # Check quote token from relationships
            if 'quote_token' in pair['relationships'] and 'data' in pair['relationships']['quote_token']:
                quote_token_id = pair['relationships']['quote_token']['data'].get('id', '')
                # Extract address from "network_address" format
                if '_' in quote_token_id:
                    quote_addr_from_id = quote_token_id.split('_', 1)[1].lower()
                    if quote_addr_from_id == token_id_lower:
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

    # GeckoTerminal format - address is in attributes.address
    if 'attributes' in pair and 'address' in pair['attributes']:
        # Extract chain from the id field (format: "network_address")
        pair_id = pair.get('id', '')
        if '_' in pair_id:
            chain = pair_id.split('_', 1)[0]  # Extract network part
            pair_address = pair['attributes']['address']
            return chain, pair_address
        else:
            # Fallback to mainnet if we can't extract chain
            return 'mainnet', pair['attributes']['address']

    # Fallback for legacy GeckoTerminal format (address at top level)
    if 'address' in pair:
        return 'mainnet', pair['address']

    # Fallback
    return None, None


def _is_price_plausible(historical_data: list, real_time_price: float, token_id: str) -> tuple:
    """
    Check if the real-time price is plausible given the historical price trend.

    This is a heuristic sanity check to prevent combining economically meaningless
    data series (e.g., mainnet USDC at ~$1.00 with a testnet pool quoting ~$0.10).
    The check only applies to stablecoins, which have an expected ~$1 peg. Non-stablecoins
    like WETH are exempt since their prices can legitimately move.

    Args:
        historical_data (list): List of historical price data points from CoinGecko.
        real_time_price (float): Current real-time price from the market data provider.
        token_id (str): Token identifier (e.g., "USDC", "WETH").

    Returns:
        tuple: (is_plausible: bool, deviation: float or None, reference_price: float or None)
               - is_plausible: True if price is plausible, False if deviation exceeds threshold
               - deviation: Percentage deviation from reference price (None if check not applicable)
               - reference_price: Historical reference price used for comparison (None if check not applicable)
    """
    # Only apply plausibility check to stablecoins
    token_id_upper = token_id.upper()
    if token_id_upper not in STABLECOINS:
        # Non-stablecoins can legitimately move; skip check
        return True, None, None

    # Need at least some historical data to compute a reference
    if not historical_data or len(historical_data) == 0:
        # No historical data to compare against; skip check
        return True, None, None

    # Use the most recent historical price as reference
    # Historical data format from CoinGecko: list of dicts with 'price' key
    most_recent = historical_data[-1]
    reference_price = most_recent.get('price')

    if reference_price is None or reference_price == 0:
        # Invalid reference price; skip check
        return True, None, None

    # Compute percentage deviation
    deviation = abs((real_time_price - reference_price) / reference_price) * 100

    # Threshold: 50% deviation is considered implausible for stablecoins
    # This is a heuristic starting point, not a precisely-derived value.
    # It's wide enough to avoid false positives on legitimate small deviations
    # but narrow enough to catch the ~90% deviation observed in issue #34.
    PLAUSIBILITY_THRESHOLD_PERCENT = 50.0

    is_plausible = deviation <= PLAUSIBILITY_THRESHOLD_PERCENT

    return is_plausible, deviation, reference_price


@shared_task(name='perform_llm_analysis')
def perform_llm_analysis(token_id, store_results=False, network=None):
    # Token ID mapping for common symbols to CoinGecko IDs
    token_id_mapping = {
        'USDC': 'usd-coin',
        'USDT': 'tether',
        'WETH': 'weth',
        'ETH': 'ethereum',
        'BTC': 'bitcoin',
    }

    # Use mapped ID if available, otherwise use original
    coingecko_token_id = token_id_mapping.get(token_id.upper(), token_id)

    # Fetch data
    historical_data = get_historical_data(coingecko_token_id, days=30)

    if store_results and historical_data:
        # Store historical data in Redis
        historical_data_key = f"historical_data:{token_id}"
        redis_client.set(historical_data_key, json.dumps(historical_data))

    # Fetch token pairs - network must be explicitly provided by caller
    if network is None:
        raise ValueError("network parameter is required and must be explicitly provided")
    token_pairs = search_token_pairs(token_id, network=network)

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

        # Verify resolved address matches known allowlist if present (issue #31)
        # This prevents combining historical CoinGecko data with real-time GeckoTerminal data
        # for different underlying tokens (e.g., mainnet USDC vs. testnet USDC-test)
        normalized_network = _map_chain_to_executor_network(network)
        if normalized_network in KNOWN_TOKEN_ADDRESSES:
            known_addresses = KNOWN_TOKEN_ADDRESSES[normalized_network]
            token_id_upper = token_id.upper()
            if token_id_upper in known_addresses:
                expected_address = known_addresses[token_id_upper]
                if token_address.lower() != expected_address.lower():
                    logger.warning(
                        f"Token address mismatch for {token_id} on {network}: "
                        f"expected {expected_address} (from allowlist), "
                        f"resolved {token_address} from GeckoTerminal. "
                        f"Skipping this pair to prevent combining data for different assets."
                    )
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

        # Price plausibility check (issue #34)
        # Verify that real-time price is plausible given historical trend for stablecoins
        # This prevents combining economically meaningless data series (e.g., mainnet USDC
        # at ~$1.00 with a testnet pool quoting ~$0.10) even when token identity is correct.
        if historical_data and real_time_data and 'price' in real_time_data:
            real_time_price = real_time_data['price']
            is_plausible, deviation, reference_price = _is_price_plausible(
                historical_data, real_time_price, token_id
            )
            if not is_plausible:
                logger.warning(
                    f"Price implausibility detected for {token_id} on {network}: "
                    f"historical reference price ${reference_price:.4f}, "
                    f"real-time price ${real_time_price:.4f}, "
                    f"deviation {deviation:.1f}%. "
                    f"Skipping this pair to prevent combining economically meaningless data series."
                )
                continue

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
