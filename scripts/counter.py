import csv
import re

# creates a structured csv of the number of instances a candidate is mentioned
def create_file_of_candidate_mentions(candidates, tweet_list):
    candidate_count_dict = {}
    for c in candidates:
        candidate_count_dict[c] = 0
    for t in tweet_list:
        candidates_mentioned = t['candidates_mentioned']
        for c in candidates_mentioned:
            candidate_count_dict[c] += 1
    filename = "../data/candidate_mentions.csv"
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = candidates)
        writer.writeheader()
        writer.writerow(candidate_count_dict)