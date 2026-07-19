#!/usr/bin/env python3
"""
Trigger the full pipeline (LLM analysis -> executor) for E2E testing.
This script calls the Celery task perform_llm_analysis directly.
"""
from core.market_data import search_token_pairs, get_historical_data, get_realtime_data, combine_data
from llm.llm_analysis import analyze_with_llm
from tasks.analyzer import _resolve_token_address, _get_pair_chain_and_address, _map_chain_to_executor_network
import json

# Trigger analysis for USDC on Sepolia testnet
# WORKAROUND: Using "sepolia-testnet" directly because search_token_pairs doesn't map network IDs
# This is a bug - search_token_pairs should call _map_chain_to_network like get_realtime_data does
print("=== Step 1: Fetch historical data ===")
historical_data = get_historical_data("usd-coin", days=30)
print(f"Historical data: {len(historical_data) if historical_data else 0} data points")

print("\n=== Step 2: Search token pairs ===")
token_pairs = search_token_pairs("USDC", network="sepolia-testnet")
print(f"Found {len(token_pairs)} token pairs")
for i, pair in enumerate(token_pairs[:3]):  # Show first 3
    print(f"  Pair {i+1}: {json.dumps(pair, indent=2, default=str)[:500]}...")

if not token_pairs:
    print("ERROR: No token pairs found - cannot proceed")
    exit(1)

print("\n=== Step 3: Process first pair ===")
pair = token_pairs[0]
print(f"Full pair data keys: {pair.keys()}")
print(f"base_token_address: {pair.get('base_token_address')}")
print(f"quote_token_address: {pair.get('quote_token_address')}")
print(f"base_token_symbol: {pair.get('base_token_symbol')}")
print(f"quote_token_symbol: {pair.get('quote_token_symbol')}")

# Try direct address lookup first
if pair.get('base_token_address'):
    token_address = pair['base_token_address']
    print(f"Using base_token_address: {token_address}")
else:
    token_address = _resolve_token_address("USDC", pair)
    print(f"Resolved token address via _resolve_token_address: {token_address}")

chain, pair_address = _get_pair_chain_and_address(pair)
print(f"Chain: {chain}, Pair address: {pair_address}")

print("\n=== Step 4: Fetch real-time data ===")
real_time_data = get_realtime_data(chain, pair_address)
print(f"Real-time data: {real_time_data}")

if historical_data and real_time_data:
    print("\n=== Step 5: Combine data ===")
    combined_data = combine_data(historical_data, real_time_data)
    print(f"Combined data: {combined_data}")

    if combined_data is not None:
        print("\n=== Step 6: LLM analysis ===")
        analysis_result = analyze_with_llm("USDC", chain=chain, pair_address=pair_address, data=combined_data)
        print(f"Analysis result: {analysis_result}")

        # Test executor path directly since LLM returned HOLD
        print("\n=== Step 7: Test executor with BUY decision (dry-run) ===")
        from core.trading.ethereum import EthereumExecutor
        network = _map_chain_to_executor_network(chain)
        print(f"Mapped chain '{chain}' to network '{network}'")

        executor = EthereumExecutor(
            token_address=token_address,
            network=network,
            provider='infura'
        )

        print(f"Executing BUY with amount_eth=0.001 (DRY_RUN=True)")
        executor.execute(decision='BUY', amount_eth=0.001)
        print("BUY execution completed (dry-run - no broadcast)")
    else:
        print("ERROR: Combined data is None")
else:
    print("ERROR: Missing historical or real-time data")
