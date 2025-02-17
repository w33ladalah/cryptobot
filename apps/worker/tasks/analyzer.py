from celery import shared_task
from core.market_data import get_historical_data, get_realtime_data, combine_data, search_token_pairs
from llm.llm_analysis import analyze_with_llm
from devtools import debug
import json


@shared_task(name='perform_llm_analysis')
def perform_llm_analysis(token_id):
    # Fetch data
    historical_data = get_historical_data(token_id, days=30)

    # Fetch token pairs
    token_pairs = search_token_pairs(token_id)

    analysis_results = []
    for pair in token_pairs:
        # Fetch real-time data
        real_time_data = get_realtime_data(pair['chainId'], pair['pairAddress'])

        # Process data
        combined_data = combine_data(historical_data, real_time_data)

        # LLM-based analysis
        analysis_result = analyze_with_llm(token_id, chain=pair['chainId'], pair_address=pair['pairAddress'], data=combined_data)
        analysis_results.append(analysis_result)

    return analysis_results
