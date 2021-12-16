import csv
import re

# creates a structured csv of the number of instances a candidate is mentioned
def create_file_of_candidate_mentions(candidates, tweet_list):
    candidate_count_dict = {}
    # initializes dict
    for c in candidates:
        candidate_count_dict[c] = 0
    filename = "../data/candidate_mentions.csv"
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = candidates)
        writer.writeheader()
    return 1


