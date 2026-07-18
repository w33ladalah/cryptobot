from celery import shared_task
from core.market_data import get_historical_data, get_realtime_data, combine_data, search_token_pairs
from llm.llm_analysis import analyze_with_llm
from core.trading.ethereum import EthereumExecutor
from devtools import debug
from config.redis import redis_client
from config.settings import config
import json


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
        # Fetch real-time data
        real_time_data = get_realtime_data(pair['chainId'], pair['pairAddress'])

        if store_results:
            # Store real-time data in Redis
            real_time_data_key = f"real_time_data:{pair['chainId']}:{pair['pairAddress']}"
            redis_client.set(real_time_data_key, json.dumps(real_time_data))

        if historical_data and real_time_data:
            # Process data
            combined_data = combine_data(historical_data, real_time_data)

            if combined_data is not None:
                if store_results:
                    # Store combined data in Redis
                    combined_data_key = f"combined_data:{pair['chainId']}:{pair['pairAddress']}"
                    redis_client.set(combined_data_key, combined_data.to_json())

                # LLM-based analysis
                analysis_result = analyze_with_llm(token_id, chain=pair['chainId'], pair_address=pair['pairAddress'], data=combined_data)
                analysis_results.append(analysis_result)

                # Execute trade if decision is BUY or SELL
                if analysis_result and analysis_result.get('decision'):
                    decision = analysis_result['decision'].upper()
                    if decision in ['BUY', 'SELL']:
                        print(f"Executing {decision} order for token {token_id} on chain {pair['chainId']}")

                        # Resolve token address from baseToken or quoteToken
                        base_token = pair.get('baseToken', {})
                        quote_token = pair.get('quoteToken', {})
                        token_address = None

                        # Check baseToken first
                        if (base_token.get('symbol', '').lower() == token_id.lower() or
                            base_token.get('name', '').lower() == token_id.lower()):
                            token_address = base_token.get('address')
                        # Check quoteToken if baseToken didn't match
                        elif (quote_token.get('symbol', '').lower() == token_id.lower() or
                              quote_token.get('name', '').lower() == token_id.lower()):
                            token_address = quote_token.get('address')

                        # Skip this pair if token_address couldn't be resolved
                        if not token_address:
                            print(f"Warning: Could not resolve token address for {token_id} in pair {pair.get('pairAddress')} - skipping")
                            continue

                        executor = EthereumExecutor(
                            token_address=token_address,
                            network='sepolia',  # Using Sepolia testnet
                            provider='infura'  # Using Infura as provider
                        )

                        if decision == 'BUY':
                            # Use small amount for testing (0.001 ETH)
                            executor.execute(decision='BUY', amount_eth=0.001)
                        elif decision == 'SELL':
                            # Sell all available tokens (amount_tokens=None triggers balance fetch)
                            executor.execute(decision='SELL', amount_tokens=None)
                    else:
                        print(f"HOLD decision for token {token_id} - no execution")

    debug(analysis_results)

    return analysis_results
