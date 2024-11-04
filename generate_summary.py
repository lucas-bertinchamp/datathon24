from summarization.summarization_pipeline import *
from stmt_analysis.reddit_analysis import *
from alpha.alpha_api import *
from utils import *
from stock_fetcher.functions_general import get_financial_metrics

import praw

def call_model(prompt, client, model_id):
    conversation = [
        {
            "role": "user",
            "content": [{"text": prompt}],
        }
    ]
    
    try:
        # Send the message to the model, using a basic inference configuration.
        response = client.converse(
            modelId=model_id,
            messages=conversation,
            inferenceConfig={"maxTokens":2048,"temperature":0.2},
        )

        # Extract and print the response text.
        response_text = response["output"]["message"]["content"][0]["text"]

    except (ClientError, Exception) as e:
        print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
        return "Error in generating summary"
    
    return response_text

def generate_summary_from_sources(clients, company_name, company_code, model_id, pdfs = [], verbose=False):

    print(f"Company code: {company_code}") if verbose else None
    
    print("Reddit Analysis ...") if verbose else None
    subreddits = ['wallstreetbets', 'stocks', 'investing', 'options', 'pennystocks', 'SecurityAnalysis', 'ValueInvesting', 'DividendInvesting', 'Daytrading', 'algotrading', 'FinancialIndependence','CanadianInvestor','CanadaStocks','BayStreetBets']
    all_reddit_posts = reddit_analysis_pipeline(clients["reddit"], subreddits, company_name, clients["boto"], n_post = 10, verbose=verbose)
    print("No reddit posts found") if len(all_reddit_posts) == 0 and verbose == True else None
    
    print("Alpha Analysis ...") if verbose else None
    all_alpha_sentiments = get_alpha_news_sentiment(clients["alpha"], company_code)
    print("No alpha news found") if len(all_alpha_sentiments) == 0 and verbose == True else None
    
    print("Summarization ...") if verbose else None
    all_summaries = []
    for pdf in pdfs:
        summary = summarization_pdf(pdf, verbose=verbose)
        all_summaries.append(summary)
        
    print("Financial Metrics ...") if verbose else None
    kpi_data, non_historical_kpi, current_info = get_financial_metrics(company_code)
    
    
    prompt = f"""
    Give a financial analysis of the following company according to the information. Be exhaustive and concise by avoiding unnecessary words. 
    Give a fundamental analysis of the company, including its financial statements, its market position, its competitors, and its future prospects.
    Give a technical analysis of the company, including its stock price, its trading volume, and its moving averages.
    Give a sentiment analysis of the company, including the sentiment of the news and the sentiment of the social media.
    Do not give more details than necessary, be precise in your analysis. Do not write your answer in LaTeX.
    
    Company: {company_name}
    
    Social Media Analysis:
    {all_reddit_posts}
    
    Alpha Analysis:
    {all_alpha_sentiments}
    """
    
    if len(all_summaries) > 0:
        prompt += f"""
        Summarization of documents related to the company:
        {all_summaries}
        """
        
    if len(kpi_data) > 0:
        prompt += f"""
        Financial Metrics (KPIs):
        {kpi_data}
        """
        
    if len(non_historical_kpi) > 0:
        prompt += f"""
        Financial Metrics (Non-Historical KPIs):
        {non_historical_kpi}
        """
        
    if len(current_info) > 0:
        prompt += f"""
        Global and financial information:
        {current_info}
    """

    print(f"Calling model to generate summary of {company_name}") if verbose else None
    summary = call_model(prompt, clients["boto"], model_id)
    
    return summary

if __name__ == "__main__":
    company_name = "Couche-Tard"
    company_code = "ATD.TO"
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
    
    pdfs = ["pdf/reports/Consommation de Base/Couche-Tard/2023-ACT_Annual-Report_FR.pdf"]
    pdfs = []
    
    model_id = "meta.llama3-1-405b-instruct-v1:0"
    try:
        summary = generate_summary_from_sources(clients, company_name, company_code, model_id, pdfs=pdfs, verbose=True)
    except Exception as e:
        summary = f"Error in generating summary"
    
    with open(f"final_summary/{company_name}_summary.txt", "w") as f:
        f.write(summary)