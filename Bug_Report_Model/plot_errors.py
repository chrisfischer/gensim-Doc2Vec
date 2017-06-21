import gensim
import numpy as np
import os

from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from gensim.models.doc2vec import Doc2Vec
from pymongo import MongoClient

from sklearn import decomposition
from sklearn.utils import shuffle

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
    summed_errors = []
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
            vec = np.square(np.add(v1, -1*v2))
            errors.append(vec)
            summed_errors.append(np.sum(vec))
        if i % 1000 == 0:
            print "Done %i of %i" %(i, count)
    print "Finished duplicate errors"
    return errors, summed_errors

def calculate_nonduplicate_errors(reports_cursor1, reports_cursor2, model):
    errors = []
    summed_errors = []
    count = reports_cursor1.count()
    for i, doc1 in enumerate(reports_cursor1):
        doc2 = next(reports_cursor2)
        report1 = doc1["text"]
        report2 = doc2["text"]
        v1 = model.infer_vector(report1)
        v2 = model.infer_vector(report2)
        # compute the squared error
        vec = np.square(np.add(v1, -1*v2))
        errors.append(vec)
        summed_errors.append(np.sum(vec))
        if i % 1000 == 0:
            print "Done %i of %i" %(i, count)
    print "Finished non-duplicate errors"
    return errors, summed_errors

def apply_PCA(X, y):
    pca = decomposition.PCA(n_components=3)
    pca.fit(X)
    X = pca.transform(X)
    print "Finished PCA"
    # y == 1 inidcates duplicate, plot first 2000
    count = 1000
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(X[0:count,0], X[0:count,1], zs=X[0:count,1], c=y[0:count])
    ax.autoscale(True)
    plt.show()

def load_saved_errors():
    errors_dup = np.load(Settings.MODEL_PATH + "dup_errors.npy")
    errors_non_dup = np.load(Settings.MODEL_PATH + "non_dup_errors.npy")
    errors_dup_summed = np.load(Settings.MODEL_PATH + "dup_errors_summed.npy")
    errors_non_dup_summed = np.load(Settings.MODEL_PATH + "non_dup_errors_summed.npy")
    return errors_dup, errors_non_dup, errors_dup_summed, errors_non_dup_summed

def calculate_errors():
    model = Doc2Vec.load(Settings.MODEL_PATH + "doc2vec.model")

    # calculate duplicate errors
    dup_reports_collection = MongoClient(Settings.MONGO_CONNECTION_STRING)[Settings.DOC2VEC_REPORTS_DATABASE][
        Settings.DUPLICATE_REPORTS_COLLECTION_SUBSET]
    dup_reports_cursor = dup_reports_collection.find()
    errors_dup, errors_dup_summed = calculate_duplicate_errors(dup_reports_cursor, model)
    np.save(Settings.MODEL_PATH + "dup_errors.npy", errors_dup)
    np.save(Settings.MODEL_PATH + "dup_errors_summed.npy", errors_dup_summed)

    # calculate non-duplicate errors
    reports_collection1 = MongoClient(Settings.MONGO_CONNECTION_STRING)[Settings.DOC2VEC_REPORTS_DATABASE][
        Settings.REPORTS_COLLECTION_SUBSET_1]
    reports_collection2 = MongoClient(Settings.MONGO_CONNECTION_STRING)[Settings.DOC2VEC_REPORTS_DATABASE][
        Settings.REPORTS_COLLECTION_SUBSET_2]
    reports_cursor1 = reports_collection1.find()
    reports_cursor2 = reports_collection2.find()
    errors_non_dup, errors_non_dup_summed = calculate_nonduplicate_errors(reports_cursor1, reports_cursor2, model)
    np.save(Settings.MODEL_PATH + "non_dup_errors.npy", errors_non_dup)
    np.save(Settings.MODEL_PATH + "non_dup_errors_summed.npy", errors_non_dup_summed)

    return errors_dup, errors_non_dup, errors_dup_summed, errors_non_dup_summed

def main():
    # calculate errors
    # errors_dup, errors_non_dup, errors_dup_summed, errors_non_dup_summed = calculate_errors()

    # load saved vec form errors
    errors_dup, errors_non_dup, errors_dup_summed, errors_non_dup_summed  = load_saved_errors()

    # plot errors overlayed
    plt.hist(errors_dup_summed, bins=40, alpha=0.5, label='Duplicate')
    plt.hist(errors_non_dup_summed, bins=40, alpha=0.5, label='Non-duplicate')
    plt.legend(loc='upper right')
    plt.ylabel("Frequency");
    plt.xlabel("Squared Error")
    plt.draw()

    # PCA
    errors_dup = np.array(errors_dup)
    errors_non_dup = np.array(errors_non_dup)

    X = np.concatenate((errors_dup[0:50000,:], errors_non_dup[0:50000,:]), axis=0)
    y = np.concatenate((np.ones(50000), np.zeros(50000)), axis=0)
    X, y = shuffle(X, y)
    apply_PCA(X, y)


if __name__ == '__main__':
      main()