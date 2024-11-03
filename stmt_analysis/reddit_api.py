import praw
import datetime

# Function to convert Unix timestamp to readable date
def get_date(created):
    return datetime.datetime.fromtimestamp(created).strftime('%Y-%m-%d %H:%M:%S')

# Function to check if a post is within the last three weeks
def is_within_last_three_weeks(created_utc):
    current_time = datetime.datetime.utcnow()
    three_weeks_ago = current_time - datetime.timedelta(weeks=3)
    post_date = datetime.datetime.fromtimestamp(created_utc)
    return post_date >= three_weeks_ago

def call_reddit_api(client_reddit, subreddits, company_name):

    all_posts = []
    
    # Loop through each subreddit and fetch posts
    for subreddit_name in subreddits:
        subreddit = client_reddit.subreddit(subreddit_name)
        
        recent_posts = subreddit.search(f"title:{company_name}", sort='new', time_filter='month', limit=50)
        for post in recent_posts:  # Fetch recent posts up to a month
            if is_within_last_three_weeks(post.created_utc):
                all_posts.append(post)
        
        popular_posts = subreddit.search(f"title:{company_name}", sort='top', time_filter='month', limit=50)
        for post in popular_posts:  # Fetch recent popular posts up to a month
            if is_within_last_three_weeks(post.created_utc):
                all_posts.append(post)
                
    return all_posts

def format_post(post):
    return {
        "title": post.title,
        "body": post.selftext,
        "date": get_date(post.created_utc),
        "subreddit": post.subreddit.display_name,
        "score": post.score
    }

if __name__ == "__main__":
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
    all_posts = call_reddit_api(reddit, subreddits, company_name)
    formatted_posts = [format_post(post) for post in all_posts]
    print(formatted_posts)