"""
Urban Dictionary API Client Module

Provides functionality to fetch term definitions from Urban Dictionary's public API
with built-in rate limiting to prevent API bans. The main function retrieves the
highest-rated definition and example for a given search term.

Features:
    - Fetches definitions from Urban Dictionary's API (v0)
    - Automatic rate limiting (2 requests/second max)
    - Best definition selection by thumbs-up votes
    - Robust error handling (network, timeout, rate limits)
    - Consistent return format (always tuple[str, str])

Configuration:
    RATE_LIMIT = 2  # Max requests per second
    TIMEOUT = 35    # Request timeout in seconds

Functions:
    get_best_definition(term: str) -> tuple[str, str]:
        Retrieves the top definition and example for the given term.
        Returns tuple of (definition, example) or (error_message, empty_string)

Error Handling:
    - HTTP errors (non-200 status codes)
    - Request timeouts
    - Rate limit violations
    - Network exceptions
    - Returns descriptive error messages

Dependencies:
    - requests
    - time (for rate limiting)

Example Usage:
    >>> definition, example = get_best_definition("python")
    >>> if not definition.startswith("Error:"):
    ...     print(f"Definition: {definition}")
    ...     print(f"Example: {example}")

Rate Limiting:
    Uses simple time-based throttling to maintain:
    - Max 2 requests per second (configurable)
    - Thread-safe operation for concurrent use

Note:
    The Urban Dictionary API enforces strict rate limits. This implementation
    helps prevent 429 errors but cannot guarantee against API-side throttling.
"""
import requests
import time
from requests.exceptions import Timeout, RequestException

# Rate limiting configuration
RATE_LIMIT = 2  # requests per second
MIN_INTERVAL = 1.0 / RATE_LIMIT
last_request_time = 0

def get_best_definition(term):
    """
    Fetches the best Urban Dictionary definition with rate limiting.
    
    Args:
        term: The term to look up (str)
        
    Returns:
        tuple: (definition, example) or (error_message, "")
    """
    global last_request_time
    
    # Rate limiting
    elapsed = time.time() - last_request_time
    if elapsed < MIN_INTERVAL:
        time.sleep(MIN_INTERVAL - elapsed)
    
    url = "https://api.urbandictionary.com/v0/define"
    params = {'term': term}
    
    try:
        last_request_time = time.time()
        response = requests.get(url, params=params, timeout=35)
        
        if response.status_code == 200:
            data = response.json()
            
            if data['list']:
                sorted_defs = sorted(
                    data['list'], 
                    key=lambda x: x['thumbs_up'],
                    reverse=True
                    )
                return sorted_defs[0]['definition'], sorted_defs[0]['example']
            return "No definitions found.", ""
            
        elif response.status_code == 429:
            return "Error: Rate limited - try again later.", ""
        else:
            return f"Error: HTTP {response.status_code}", ""

    except Timeout:
        return "Error: Request timed out after 35 seconds.", ""
    except RequestException as e:
        return f"Error: Request failed - {str(e)}", ""