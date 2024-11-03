import requests

def get_data_from_alpha_api(api_key, symbol, verbose=False):
    url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={symbol}&apikey={api_key}'
    r = requests.get(url)
    data = r.json()
    return data

def get_alpha_news_sentiment(api_keys, symbol, verbose=False):
    all_news = []
    
    api_key_index = 0
    data = get_data_from_alpha_api(api_keys[api_key_index], symbol, verbose=verbose)
    
    while data.get("Information", "") == "Thank you for using Alpha Vantage! Our standard API rate limit is 25 requests per day. Please subscribe to any of the premium plans at https://www.alphavantage.co/premium/ to instantly remove all daily rate limits.":
        print(f"API key {api_key_index} limit reached. Switching to the next API key ...") if verbose else None
        api_key_index += 1
        if api_key_index >= len(api_keys):
            return []
        data = get_data_from_alpha_api(api_keys[api_key_index], symbol, verbose=verbose)
    
    # Check if 'feed' is in the data and format each news item
    if "feed" in data:
        
        for i, news in enumerate(data["feed"]):
            one_news = {}
            one_news["title"] = news.get("title", "No title available")
            one_news["time_published"] = news.get("publishedDate", "No date available")
            one_news["summary"] = news.get("summary", "No summary available")
            
            # Find the specific ticker sentiment score for the given symbol (e.g., AAPL)
            ticker_sentiment_found = False
            if "ticker_sentiment" in news:
                for ticker_info in news["ticker_sentiment"]:
                    if ticker_info.get("ticker") == symbol:
                        ticker_sentiment_score = ticker_info.get("ticker_sentiment_score", "No sentiment score available")
                        ticker_sentiment_label = ticker_info.get("ticker_sentiment_label", "No sentiment label available")
                        
                        one_news["sentiment_score"] = ticker_sentiment_score
                        one_news["sentiment_label"] = ticker_sentiment_label
                        ticker_sentiment_found = True
                        break  # Exit loop after finding the desired ticker
                    
                if not ticker_sentiment_found:
                    one_news["sentiment_score"] = "No sentiment score available"
                    one_news["sentiment_label"] = "No sentiment label available"
            else:
                one_news["sentiment_score"] = "No sentiment score available"
                one_news["sentiment_label"] = "No sentiment label available"
        
            all_news.append(one_news)
    
    return all_news
        
if __name__ == "__main__":
    symbol = "TSLA"  # Example symbol
    api_keys = ["L7AML53D7MCJ02DE", "IKOXZ7F7QT7662T2"]
    print(get_alpha_news_sentiment(api_keys, symbol, verbose=True))