import os
import time
import json

from pymongo import MongoClient
from nltk.stem.wordnet import WordNetLemmatizer

from settings import Settings

def normalize_text(text):
    norm_text = text.lower()
    lem = WordNetLemmatizer()
    words = [lem.lemmatize(w) for w in text.split()]
    txt = ' '
    for w in words:
        txt += w + ' '

    # Replace breaks with spaces
    norm_text = norm_text.replace('\n', ' ')

    # Pad punctuation with spaces on both sides
    for char in ['. ', '"', ',', ' (', ')', '!', '?', ';', ':', '|']:
        norm_text = norm_text.replace(char, ' ' + char + ' ')

    return norm_text

def main():
    dataset_file = Settings.DATASET_FILE
    duplicate_reports_collection = MongoClient(Settings.MONGO_CONNECTION_STRING)[Settings.DOC2VEC_REPORTS_DATABASE][
    Settings.DUPLICATE_REPORTS_COLLECTION]
    reports_collection = MongoClient(Settings.MONGO_CONNECTION_STRING)[Settings.DOC2VEC_REPORTS_DATABASE][
    Settings.REPORTS_COLLECTION]

    with open(dataset_file) as dataset:
        data = json.loads(dataset.read())
        for i, (report_num, updates) in enumerate(data["short_desc"].items()):
            try:
                dups = []
                for update in updates:
                    txt = normalize_text(update["what"])
                    
                    # add to db of all reports
                    reports_collection.insert({
                        "reId": i,
                        "text": txt
                        })
                    # add to list of duplcates
                    dups.append(txt)

                # add to db of duplicate if more than one update
                if len(dups) > 1:
                    duplicate_reports_collection.insert({
                        "reId": i,
                        "dups": dups
                        })
            except:
                print "Error: %i" %i
 

if __name__ == '__main__':
    main()