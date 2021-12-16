import requests
import json
import ast
import yaml
import re
from flair.models import TextClassifier
from flair.data import Sentence

search_url = "https://api.twitter.com/2/tweets/search/recent"

def create_query_params(candidates, max_results):
    search_string = ""
    for c in candidates:
        search_string += "(" + c + ")" + " OR "
    search_string = search_string[:-4]
    return {'query': search_string,
        "expansions":"author_id",
        "tweet.fields": "created_at,geo",
        "user.fields":"name,username,location,public_metrics",
        "max_results":max_results}


def create_bearer_token(data):
    return data["search_tweets_api"]["bearer_token"]

def process_yaml():
    with open("../config.yaml") as file:
        return yaml.safe_load(file)

def twitter_auth_and_query(bearer_token, candidates, max_results):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    response = requests.request("GET", search_url, headers=headers, params=create_query_params(candidates, max_results))
    return response.json()

# returns the list of users self-identifying as in California
def filter_local_users(users, locations):
    filtered_users_dict = {}
    filtered_users_ids = []
    for u in users:
        try:
            if any(x in u['location'].lower() for x in locations):
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
# includes sentiment and candidate mentioned
def tweets_cleaned_with_sentiment(tweets, users_dict, candidates):
    tweets_with_user = []
    alias_dict = get_alias_dict(candidates)
    classifier = TextClassifier.load('en-sentiment')
    for t in tweets:
        inner_dict = {}
        inner_dict['id'] = t['id']
        inner_dict['text'] = t['text']
        inner_dict['sentiment_score'] = sentiment_read(classifier, t['text'])
        inner_dict['created_at'] = t['created_at']
        inner_dict['candidates_mentioned'] = get_relevant_candidate(alias_dict, t['text'], candidates)
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
def sentiment_read(classifier, text):
    sentence = Sentence(text)
    classifier.predict(sentence)
    return sentence.labels

# returns list of candidates mentioned in the tweet
def get_relevant_candidate(alias_dict, text, candidates):
    alias_keys = alias_dict.keys()
    text_no_punc = re.sub(r'[^\w\s]', '', text)
    text_no_punc = text_no_punc.replace("_", "")
    text_list = text_no_punc.lower().split()
    overlap = set(text_list) & set(alias_keys)
    mentioned_candidates = []
    for m in overlap:
        mentioned_candidates.append(alias_dict[m])
    return list(set(mentioned_candidates))


# returns a dictionary of aliases (lowercase first, last name) mapped to dataset category (full candidate name) mapped to 
def get_alias_dict(candidates):
    alias_dict = {}
    for c in candidates:
        alias_list = c.lower().split()
        for a in alias_list:
            alias_dict[a] = c
        alias_dict[c.replace(" ", "").lower()] = c
    return alias_dict