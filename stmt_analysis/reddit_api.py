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
    
    try:
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
                    
    except Exception as e:
        return []
                
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
    pass