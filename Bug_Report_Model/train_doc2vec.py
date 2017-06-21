import gensim
import logging
from gensim.models.doc2vec import TaggedDocument
from pymongo import MongoClient

from settings import Settings

class LabeledLineSentence(object):
    def __init__(self, doc_cursor):
        self.doc_cursor = doc_cursor
    def __iter__(self):
        for idx, doc in enumerate(self.doc_cursor):
            yield TaggedDocument(words=doc["text"].split(),tags=[doc["reId"]])

def main():
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

    model_path = Settings.MODEL_PATH
    dictionary_path = model_path + "dictionary.dict"
    corpus_path = model_path + "corpus.lda-c"
    lda_num_topics = Settings.NUM_OF_MODELS
    lda_model_path = model_path + "lda_model_100_topics.lda"

    reports_collection = MongoClient(Settings.MONGO_CONNECTION_STRING)[Settings.DOC2VEC_REPORTS_DATABASE][
        Settings.REPORTS_COLLECTION]
    reports_cursor = reports_collection.find()

    it = LabeledLineSentence(reports_cursor)
    model = gensim.models.Doc2Vec(size=300, window=7, min_count=5, workers=11,alpha=0.025, min_alpha=0.025)
      
    num_epochs = 15

    model.build_vocab(it)
    for epoch in range(num_epochs):
        model.train(it, total_examples=model.corpus_count, epochs=num_epochs)
        model.alpha -= 0.002
        model.min_alpha = model.alpha
        model.save(Settings.MODEL_PATH + 'doc2vec.model')
        print "Epoch %i done" %(epoch + 1)


if __name__ == '__main__':
    main()
