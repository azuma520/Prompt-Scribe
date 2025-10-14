#!/usr/bin/env python3
"""
⚙️ Database Test Configuration

Configuration settings and constants for database testing suite.
"""

import os
from pathlib import Path
from typing import Dict, Any

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
ENV_FILE = PROJECT_ROOT / "specs" / "001-sqlite-ags-db" / ".env"

# Database configuration
DATABASE_CONFIG = {
    'expected_record_count': 140782,
    'table_name': 'tags_final',
    'required_columns': [
        'id', 'name', 'danbooru_cat', 'post_count', 
        'main_category', 'sub_category', 'confidence', 
        'classification_source'
    ],
    'main_categories': [
        'character', 'action_pose', 'theme_concept', 'adult_content'
    ]
}

# Performance benchmarks
PERFORMANCE_BENCHMARKS = {
    'primary_key_query_ms': 100,
    'name_exact_match_ms': 200,
    'name_prefix_search_ms': 300,
    'category_query_ms': 250,
    'range_query_ms': 500,
    'complex_query_ms': 600,
    'sorting_query_ms': 400,
    'aggregation_query_ms': 1000,
    'concurrent_query_ms': 500,
    'min_success_rate': 95.0,
    'min_ops_per_second': 10.0
}

# Test configuration
TEST_CONFIG = {
    'quick_test': {
        'timeout_seconds': 60,
        'max_retries': 3
    },
    'comprehensive_test': {
        'timeout_seconds': 600,
        'sample_size': 100,
        'max_retries': 3
    },
    'performance_test': {
        'timeout_seconds': 300,
        'iterations': {
            'primary_key': 200,
            'name_match': 150,
            'prefix_search': 100,
            'category': 100,
            'range': 80,
            'complex': 60,
            'sorting': 50,
            'aggregation': 30
        },
        'concurrent_test': {
            'threads': [5, 10],
            'queries_per_thread': 10
        }
    }
}

# Environment variables
REQUIRED_ENV_VARS = [
    'SUPABASE_URL',
    'SUPABASE_ANON_KEY'
]

OPTIONAL_ENV_VARS = [
    'SUPABASE_SERVICE_ROLE_KEY'  # Required for CRUD tests
]

def load_environment() -> Dict[str, str]:
    """Load environment variables from .env file if available"""
    env_vars = {}
    
    # Try to load from .env file
    if ENV_FILE.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(ENV_FILE)
        except ImportError:
            print("⚠️  python-dotenv not installed. Using system environment variables.")
    
    # Collect environment variables
    for var in REQUIRED_ENV_VARS + OPTIONAL_ENV_VARS:
        value = os.getenv(var)
        if value:
            env_vars[var] = value
    
    return env_vars

def validate_environment() -> tuple[bool, list[str]]:
    """Validate that required environment variables are set"""
    missing_vars = []
    
    for var in REQUIRED_ENV_VARS:
        if not os.getenv(var):
            missing_vars.append(var)
    
    return len(missing_vars) == 0, missing_vars

def get_test_config(test_type: str) -> Dict[str, Any]:
    """Get configuration for specific test type"""
    return TEST_CONFIG.get(test_type, {})

def get_performance_benchmark(metric: str) -> float:
    """Get performance benchmark for specific metric"""
    return PERFORMANCE_BENCHMARKS.get(metric, 0.0)

# Test data samples for performance testing
SAMPLE_QUERIES = {
    'popular_tags': ['1girl', '1boy', 'solo', 'long_hair', 'breasts'],
    'categories': ['character', 'action_pose', 'theme_concept', 'adult_content'],
    'search_terms': ['girl', 'hair', 'dress', 'eye', 'smile'],
    'post_count_ranges': [
        (1, 100),
        (100, 1000),
        (1000, 10000),
        (10000, 100000)
    ],
    'confidence_ranges': [
        (0.5, 0.7),
        (0.7, 0.9),
        (0.9, 1.0)
    ]
}

# Error messages and codes
ERROR_MESSAGES = {
    'connection_failed': 'Failed to connect to Supabase database',
    'missing_env_vars': 'Missing required environment variables',
    'record_count_mismatch': 'Database record count does not match expected value',
    'query_timeout': 'Query execution timed out',
    'performance_degraded': 'Query performance below acceptable threshold',
    'data_integrity_violation': 'Data integrity check failed',
    'concurrent_test_failed': 'Concurrent access test failed'
}

# Success messages
SUCCESS_MESSAGES = {
    'all_tests_passed': 'All database tests passed successfully',
    'performance_excellent': 'Database performance is excellent',
    'data_integrity_good': 'Data integrity checks passed',
    'ready_for_production': 'Database is ready for production use'
}

def get_error_message(error_code: str) -> str:
    """Get error message for specific error code"""
    return ERROR_MESSAGES.get(error_code, f'Unknown error: {error_code}')

def get_success_message(success_code: str) -> str:
    """Get success message for specific success code"""
    return SUCCESS_MESSAGES.get(success_code, f'Success: {success_code}')

# Export main configuration
__all__ = [
    'DATABASE_CONFIG',
    'PERFORMANCE_BENCHMARKS', 
    'TEST_CONFIG',
    'SAMPLE_QUERIES',
    'load_environment',
    'validate_environment',
    'get_test_config',
    'get_performance_benchmark',
    'get_error_message',
    'get_success_message'
]
