from .reddit_api import *
from .analyse_text import *
import praw

def reddit_analysis_pipeline(reddit_client, subreddits, company_name, boto_client, n_post=10, verbose=False):
    all_analysis = {}
    posts = call_reddit_api(reddit_client, subreddits, company_name)[:n_post]
    formatted_posts = [format_post(post) for post in posts]
    
    print(f"Number of posts found: {len(formatted_posts)}") if verbose else None
    
    for i, post in enumerate(formatted_posts):
        print(f"Analyzing post {i+1} / {len(formatted_posts)} ...") if verbose and i % 10 == 0 else None
        all_analysis[str(post)] = stmt_analysis(boto_client, post["title"] + " " + post["body"], company_name)
        
    return all_analysis


if __name__ == "__main__":
    company_name = "Tesla"
    # Setup the Reddit connection
    reddit = praw.Reddit(
        client_id='zzAJ_bRHjE-f9dJh5ivO1w',
        client_secret='JXTg1re8ADZYCkCFKFw48D-j8BTUyg',
        user_agent='script:multi_subreddit_extractor (by u/Legal-Assistance6692)',
        username='Legal-Assistance6692',
        password='f54Uk92Z'
    )

    # Define the subreddits and company name you are searching for
    subreddits = ['wallstreetbets', 'stocks', 'investing', 'options', 'pennystocks', 'SecurityAnalysis', 'ValueInvesting', 'DividendInvesting', 'Daytrading', 'algotrading', 'FinancialIndependence']
    company_name = "Costco"  # Change this to the company you're interested in
    boto_client = boto3.client("bedrock-runtime", region_name="us-west-2")

    posts = call_reddit_api(reddit, subreddits, company_name)
    formatted_posts = [format_post(post) for post in posts]
    for post in formatted_posts:
        print(format_post(post))
        print(stmt_analysis(boto_client, post, company_name))
        print("\n\n")