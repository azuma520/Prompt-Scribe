"""
API Services
"""
from .supabase_client import get_supabase_service, SupabaseService

# 條件導入 GPT-5 Nano 客戶端
try:
    from .gpt5_nano_client import get_gpt5_nano_client, GPT5NanoClient
    GPT5_AVAILABLE = True
except ImportError:
    GPT5_AVAILABLE = False
    get_gpt5_nano_client = None
    GPT5NanoClient = None

__all__ = [
    'get_supabase_service', 
    'SupabaseService',
    'get_gpt5_nano_client',
    'GPT5NanoClient',
    'GPT5_AVAILABLE'
]

