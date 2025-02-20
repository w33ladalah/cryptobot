from celery import shared_task
from core.market_data import get_historical_data, get_realtime_data, combine_data, search_token_pairs
from llm.llm_analysis import analyze_with_llm
from devtools import debug
from config.redis import redis_client
import json


@shared_task(name='perform_llm_analysis')
def perform_llm_analysis(token_id, store_results=False):
    # Fetch data
    historical_data = get_historical_data(token_id, days=30)

    # Fetch token pairs
    token_pairs = search_token_pairs(token_id)

    if store_results:
        # Store historical data in Redis
        historical_data_key = f"historical_data:{token_id}"
        redis_client.set(historical_data_key, json.dumps(historical_data))

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

        # Process data
        combined_data = combine_data(historical_data, real_time_data)

        if store_results:
            # Store combined data in Redis
            combined_data_key = f"combined_data:{pair['chainId']}:{pair['pairAddress']}"
            redis_client.set(combined_data_key, combined_data.to_json())

        # LLM-based analysis
        analysis_result = analyze_with_llm(token_id, chain=pair['chainId'], pair_address=pair['pairAddress'], data=combined_data)
        analysis_results.append(analysis_result)

    return analysis_results
