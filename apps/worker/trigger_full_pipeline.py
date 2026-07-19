#!/usr/bin/env python3
"""
Trigger the full pipeline (LLM analysis -> executor) for E2E testing.
This script calls the Celery task perform_llm_analysis directly.
"""
import logging
from tasks.analyzer import perform_llm_analysis

# Configure logging to see warnings from perform_llm_analysis (e.g., address mismatches)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

print("=== Triggering full pipeline ===")
print("Calling perform_llm_analysis with token_id='USDC', network='sepolia-testnet', store_results=False")
print("This will exercise the real pipeline logic including the KNOWN_TOKEN_ADDRESSES check from issue #31")
print()

analysis_results = perform_llm_analysis(token_id="USDC", store_results=False, network="sepolia-testnet")

print()
print("=== Analysis Results ===")
if analysis_results:
    print(f"Received {len(analysis_results)} analysis result(s):")
    for i, result in enumerate(analysis_results):
        print(f"  Result {i+1}: {result}")
else:
    print("No analysis results returned.")
    print("This means every candidate pair was filtered out before reaching analysis.")
    print("Possible reasons (check logs above for specific warnings):")
    print("  - Token address resolution failed for all pairs")
    print("  - Resolved address didn't match KNOWN_TOKEN_ADDRESSES allowlist (issue #31 check)")
    print("  - Historical or real-time data fetch failed")
