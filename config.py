# Configuration File
# Edit this file and fill in your API keys

import os

# OpenAI API Key (Required)
OPENAI_API_KEY = "sk-RAsLpYYhKbtQx8HE4e7610064cE04180B55f561e40B2891d"

# OpenAI Base URL (Optional, for custom API endpoint or proxy)
# Default is None, uses official API endpoint https://api.openai.com/v1
# If using proxy or third-party compatible API, you can set this, for example:
# OPENAI_BASE_URL = "https://your-proxy.com/v1"
OPENAI_BASE_URL = "https://free.v36.cm/v1/"

# Tavily API Key (Optional, for better search results)
# Get free API key at https://tavily.com
TAVILY_API_KEY = "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"

# Search Provider (tavily or duckduckgo)
SEARCH_PROVIDER = "tavily"  # Using duckduckgo doesn't require API key

# Model Configuration
MODEL_NAME = "gpt-4o-mini"
TEMPERATURE = 0.7

# Memory Configuration
MAX_MEMORY_LENGTH = 10  # Save recent conversation rounds
