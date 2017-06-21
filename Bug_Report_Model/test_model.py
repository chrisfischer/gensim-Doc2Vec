import random

from gensim.models.doc2vec import Doc2Vec
from pymongo import MongoClient

from settings import Settings
from report2mongo import normalize_text

def test_similarity(arr, model):
    for pair in arr:
        w1 = pair[0]
        w2 = pair[1]
        print w1, w2, model.similarity(w1, w2)

def main():
    model = Doc2Vec.load(Settings.MODEL_PATH + "doc2vec.model")

    """test_similarity([("right", "wrong"),
                     ("refresh", "cache")], model)"""

    reports_collection = MongoClient(Settings.MONGO_CONNECTION_STRING)[Settings.DOC2VEC_REPORTS_DATABASE][
    Settings.REPORTS_COLLECTION]
    duplicate_reports_collection = MongoClient(Settings.MONGO_CONNECTION_STRING)[Settings.DOC2VEC_REPORTS_DATABASE][
    Settings.DUPLICATE_REPORTS_COLLECTION]
    
    # get random target text that has a duplciate
    index = random.randint(0, duplicate_reports_collection.count()-1)
    txt = duplicate_reports_collection.find_one({"reId": index})["dups"][0]
    txt = normalize_text(txt)
    print "Target Text: %s" %txt

    vec = model.infer_vector(txt)
    
    # print most similar documents
    for reId, p in model.docvecs.most_similar([vec], topn=10):
        print "%0.3f: \"%s\"" %(p, reports_collection.find_one({"reId": reId})["text"])

if __name__ == '__main__':
      main()