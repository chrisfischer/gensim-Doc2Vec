import gensim
import numpy as np
import os

from matplotlib import pyplot as plt
from gensim.models.doc2vec import Doc2Vec
from pymongo import MongoClient

from sklearn import decomposition
from sklearn.utils import shuffle
from scipy import spatial

from settings import Settings

def combinations(iterable, r):
    # combinations('ABCD', 2) --> AB AC AD BC BD CD
    # combinations(range(4), 3) --> 012 013 023 123
    pool = tuple(iterable)
    n = len(pool)
    if r > n:
        return
    indices = list(range(r))
    yield tuple(pool[i] for i in indices)
    while True:
        for i in reversed(range(r)):
            if indices[i] != i + n - r:
                break
        else:
            return
        indices[i] += 1
        for j in range(i+1, r):
            indices[j] = indices[j-1] + 1
        yield tuple(pool[i] for i in indices)

def calculate_duplicate_errors(reports_cursor, model):
    errors = []
    count = reports_cursor.count()
    for i, doc in enumerate(reports_cursor):
        duplicate_list = doc["dups"]
        # calculate the feature vector for each document
        vec_list = [model.infer_vector(report) for report in duplicate_list]
        # get all combinations of size 2
        comb_iter = combinations(vec_list, 2)
        for pair in comb_iter:
            v1 = pair[0]
            v2 = pair[1]
            # compute the squared error
            error = 1 - spatial.distance.cosine(v1, v2)
            errors.append(error)
        if i % 1000 == 0:
            print "Done %i of %i" %(i, count)
    print "Finished duplicate errors"
    return errors

def calculate_nonduplicate_errors(reports_cursor1, reports_cursor2, model):
    errors = []
    count = reports_cursor1.count()
    for i, doc1 in enumerate(reports_cursor1):
        doc2 = next(reports_cursor2)
        report1 = doc1["text"]
        report2 = doc2["text"]
        v1 = model.infer_vector(report1)
        v2 = model.infer_vector(report2)
        # compute the squared error
        error = 1 - spatial.distance.cosine(v1, v2)
        errors.append(error)
        if i % 1000 == 0:
            print "Done %i of %i" %(i, count)
    print "Finished non-duplicate errors"
    return errors

def load_saved_errors():
    errors_dup = np.load(Settings.MODEL_PATH + "dup_errors_cosine.npy")
    errors_non_dup = np.load(Settings.MODEL_PATH + "non_dup_errors_cosine.npy")
    return errors_dup, errors_non_dup

def calculate_errors():
    model = Doc2Vec.load(Settings.MODEL_PATH + "doc2vec.model")

    # calculate duplicate errors
    dup_reports_collection = MongoClient(Settings.MONGO_CONNECTION_STRING)[Settings.DOC2VEC_REPORTS_DATABASE][
        Settings.DUPLICATE_REPORTS_COLLECTION_SUBSET]
    dup_reports_cursor = dup_reports_collection.find()
    errors_dup = calculate_duplicate_errors(dup_reports_cursor, model)
    np.save(Settings.MODEL_PATH + "dup_errors_cosine.npy", errors_dup)

    # calculate non-duplicate errors
    reports_collection1 = MongoClient(Settings.MONGO_CONNECTION_STRING)[Settings.DOC2VEC_REPORTS_DATABASE][
        Settings.REPORTS_COLLECTION_SUBSET_1]
    reports_collection2 = MongoClient(Settings.MONGO_CONNECTION_STRING)[Settings.DOC2VEC_REPORTS_DATABASE][
        Settings.REPORTS_COLLECTION_SUBSET_2]
    reports_cursor1 = reports_collection1.find()
    reports_cursor2 = reports_collection2.find()
    errors_non_dup = calculate_nonduplicate_errors(reports_cursor1, reports_cursor2, model)
    np.save(Settings.MODEL_PATH + "non_dup_errors_cosine.npy", errors_non_dup)
    return errors_dup, errors_non_dup

def main():
    # calculate errors
    #errors_dup, errors_non_dup = calculate_errors()

    # load saved vec form errors
    errors_dup, errors_non_dup  = load_saved_errors()

    # plot errors overlayed
    plt.hist(errors_dup, bins=40, alpha=0.5, label='Duplicate')
    plt.hist(errors_non_dup, bins=40, alpha=0.5, label='Non-duplicate')
    plt.legend(loc='upper right')
    plt.ylabel("Frequency");
    plt.xlabel("Cosine Error")
    plt.show()

if __name__ == '__main__':
      main()