import requests
import json
import ast
import yaml
from flair.models import TextClassifier
from flair.data import Sentence

search_url = "https://api.twitter.com/2/tweets/search/recent"
# filters for tweets within the radius of Los Angeles, removes retweets and advertisements
# has:geo point_radius:[-118.692601 34.0201598 25mi] -is:retweet -is:nullcast
query_params = {'query': '(Karen Bass) OR (Joe Buscaino) OR (Kevin de Leon) OR (Mike Feuer)',
    "expansions":"author_id",
    "tweet.fields": "created_at,geo",
    "user.fields":"name,username,location,public_metrics",
    "max_results":10}

location_filter = ['los angeles', 'la', 'california', 'ca', 'cali']

def create_bearer_token(data):
    return data["search_tweets_api"]["bearer_token"]

def process_yaml():
    with open("config.yaml") as file:
        return yaml.safe_load(file)

def twitter_auth_and_connect(bearer_token, url):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    response = requests.request("GET", url, headers=headers, params=query_params)
    return response.json()

# returns the list of users self-identifying as in California
def filter_local_users(users):
    filtered_users_dict = {}
    filtered_users_ids = []
    for u in users:
        try:
            if any(x in u['location'].lower() for x in location_filter):
                user_id = u['id']
                filtered_users_ids.append(user_id)
                filtered_users_dict[user_id] = u
        except Exception:
            pass
    return filtered_users_ids, filtered_users_dict

# returns the list of collected tweets from California-based users
def filter_local_tweets(user_ids, tweets):
    filtered_tweets = []
    for t in tweets:
        if t['author_id'] in user_ids:
            filtered_tweets.append(t)
    return filtered_tweets

# returns most pertinent information combined from tweets and users
def tweets_clean(tweets, users_dict):
    tweets_with_user = []
    for t in tweets:
        inner_dict = {}
        inner_dict['id'] = t['id']
        inner_dict['text'] = t['text']
        inner_dict['sentiment_score'] = sentiment_read(t['text'])
        inner_dict['created_at'] = t['created_at']
        author_id = t['author_id']
        user = users_dict[author_id]
        inner_dict['username'] = user['username']
        inner_dict['name'] = user['name']
        inner_dict['location'] = user['location']
        inner_dict['public_metrics'] = user['public_metrics']
        tweets_with_user.append(inner_dict)
    return tweets_with_user

# adds a sentiment score to each tweet
# using nlp package flair
def sentiment_read(text):
    classifier = TextClassifier.load('en-sentiment')
    sentence = Sentence(text)
    classifier.predict(sentence)
    return sentence.labels


def main():
    data = process_yaml()
    bearer_token = create_bearer_token(data)
    res_json = twitter_auth_and_connect(bearer_token, search_url)
    users_collected = res_json['includes']['users']
    tweets_collected = res_json['data']
    filtered_users_ids, filtered_users_dict = filter_local_users(users_collected)
    filtered_tweets = filter_local_tweets(filtered_users_ids, tweets_collected)
    print(tweets_clean(filtered_tweets, filtered_users_dict))

if __name__ == "__main__":
    main()