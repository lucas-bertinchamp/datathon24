from summarization.summarization_pipeline import *
from stmt_analysis.reddit_analysis import *
from alpha.alpha_api import *
from utils import *

import praw

def generate_summary_from_sources(clients, company_name, pdfs = [], verbose=False):
    
    company_code = get_ticker_symbol(company_name)
    print(f"Company code: {company_code}") if verbose else None
    
    print("Reddit Analysis ...") if verbose else None
    subreddits = ['wallstreetbets', 'stocks', 'investing', 'options', 'pennystocks', 'SecurityAnalysis', 'ValueInvesting', 'DividendInvesting', 'Daytrading', 'algotrading', 'FinancialIndependence']
    all_reddit_posts = reddit_analysis_pipeline(clients["reddit"], subreddits, company_name, clients["boto"], n_post = 10, verbose=verbose)
    
    print("Alpha Analysis ...") if verbose else None
    all_alpha_sentiments = get_alpha_news_sentiment(clients["alpha"], company_code)
    
    print("Summarization ...") if verbose else None
    all_summaries = []
    for pdf in pdfs:
        summary = summarization_pdf(pdf, verbose=verbose)
        all_summaries.append(summary)
    
    print(all_reddit_posts)
    print(all_alpha_sentiments)  
    print(all_summaries)


if __name__ == "__main__":
    company_name = "Tesla"
    clients = {
        "reddit" : praw.Reddit(
        client_id='zzAJ_bRHjE-f9dJh5ivO1w',
        client_secret='JXTg1re8ADZYCkCFKFw48D-j8BTUyg',
        user_agent='script:multi_subreddit_extractor (by u/Legal-Assistance6692)',
        username='Legal-Assistance6692',
        password='f54Uk92Z'
    ),
        "boto" : boto3.client("bedrock-runtime", region_name="us-west-2"),
        "alpha" : ["L7AML53D7MCJ02DE", "IKOXZ7F7QT7662T2"]
    }
    
    pdfs = ["pdf/reports/Consommation de Base/Métro/2020-annuel-10Q-FR-FINAL.pdf"]
    
    generate_summary_from_sources(clients, company_name, pdfs=pdfs, verbose=True)