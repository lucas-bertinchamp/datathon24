import requests

def get_ticker_symbol(company_name, target_exchange="NASDAQ"):
    base_url = "https://financialmodelingprep.com/api/v3/search"
    params = {
        "query": company_name,
        "limit": 5,  # Request multiple results to filter locally
        "apikey": "QblgNeICcypTRGMUb8Vas9baxUBLMmUv"  # Replace with your FMP API key
    }
    response = requests.get(base_url, params=params)
    data = response.json()
    
    # Filter results for the target exchange
    for result in data:
        if result.get("exchangeShortName") == target_exchange:
            return result['symbol']
    
    # Return None if no match is found on the target exchange
    return None