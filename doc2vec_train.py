from os import listdir
from os.path import isfile, join

import gensim

from gensim.models.doc2vec import TaggedDocument

def normalize_text(text):
    norm_text = text.lower()

    # Replace breaks with spaces
    norm_text = norm_text.replace('<br />', ' ')

    # Pad punctuation with spaces on both sides
    for char in ['.', '"', ',', '(', ')', '!', '?', ';', ':', '|']:
        norm_text = norm_text.replace(char, ' ' + char + ' ')

    return norm_text

class LabeledLineSentence(object):
    def __init__(self, doc_list, labels_list):
        self.labels_list = labels_list
        self.doc_list = doc_list
    def __iter__(self):
        for idx, doc in enumerate(self.doc_list):
            yield TaggedDocument(words=doc.split(),tags=[self.labels_list[idx]])


def main():
    path = "Texts/"

    docLabels = [f for f in listdir(path) if f.endswith('.txt')]
    data = []
    for docLabel in docLabels:
        with open(path + docLabel, 'r') as f:
            #normalize_text
            doc = f.read()
            normalize_text(doc)
            data.append(doc)

    it = LabeledLineSentence(data, docLabels)
    model = gensim.models.Doc2Vec(size=300, window=7, min_count=5, workers=11,alpha=0.025, min_alpha=0.025)
      
    num_epochs = 10

    model.build_vocab(it)
    for epoch in range(num_epochs):
        model.train(it, total_examples=model.corpus_count, epochs=num_epochs)
        model.alpha -= 0.002
        model.min_alpha = model.alpha
        print "epoch %i complete." %epoch
    model.save('doc2vec.model')


if __name__ == '__main__':
      main()
