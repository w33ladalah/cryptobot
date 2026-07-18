#!/usr/bin/env python3
"""
Script to trigger the perform_llm_analysis Celery task for end-to-end testing.
"""
import sys
import os

# Add the worker app directory to the path
sys.path.insert(0, '/app')

from tasks.analyzer import perform_llm_analysis

if __name__ == "__main__":
    # Use USDC as the test token (same as issue #5)
    token_id = "USDC"
    
    print(f"Triggering LLM analysis for token: {token_id}")
    print(f"DRY_RUN mode: {os.environ.get('DRY_RUN', 'not set')}")
    
    # Trigger the task synchronously for testing
    result = perform_llm_analysis(token_id, store_results=True)
    
    print(f"\nAnalysis completed. Results: {result}")
