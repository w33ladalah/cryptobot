#!/usr/bin/env python3
"""
Trigger the full pipeline (LLM analysis -> executor) for E2E testing.
This script calls the Celery task perform_llm_analysis directly.
"""
from tasks.analyzer import perform_llm_analysis

# Trigger analysis for USDC on Sepolia testnet
# Using network="sepolia" to target Sepolia testnet
print("Triggering full pipeline with DRY_RUN=True...")
result = perform_llm_analysis(token_id="USDC", store_results=True, network="sepolia")
print(f"Analysis result: {result}")
