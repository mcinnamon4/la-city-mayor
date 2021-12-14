import scraper
import counter

candidates = ["Karen Bass", "Joe Buscaino", "Kevin de Leon", "Mike Feuer"]

def main():
    data = scraper.process_yaml()
    bearer_token = scraper.create_bearer_token(data)
    res_json = scraper.twitter_auth_and_query(bearer_token, candidates, 10)
    users_collected = res_json['includes']['users']
    tweets_collected = res_json['data']
    filtered_users_ids, filtered_users_dict = scraper.filter_local_users(users_collected)
    filtered_tweets = scraper.filter_local_tweets(filtered_users_ids, tweets_collected)
    print(scraper.tweets_clean(filtered_tweets, filtered_users_dict))

if __name__ == "__main__":
    main()