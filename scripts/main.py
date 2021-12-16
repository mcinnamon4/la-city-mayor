import scraper
import counter

candidates = ["Karen Bass", "Joe Buscaino", "Kevin de Leon", "Mike Feuer"]
locations = ['los angeles', 'la', 'california', 'ca', 'cali']

def main():
    data = scraper.process_yaml()
    bearer_token = scraper.create_bearer_token(data)
    res_json = scraper.twitter_auth_and_query(bearer_token, candidates, 10)
    users_collected = res_json['includes']['users']
    tweets_collected = res_json['data']
    filtered_users_ids, filtered_users_dict = scraper.filter_local_users(users_collected, locations)
    filtered_tweets = scraper.filter_local_tweets(filtered_users_ids, tweets_collected)
    tweet_list = scraper.tweets_cleaned_with_sentiment(filtered_tweets, filtered_users_dict, candidates)
    counter.create_file_of_candidate_mentions(candidates, tweet_list)

if __name__ == "__main__":
    main()