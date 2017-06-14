import gensim
from gensim.models.doc2vec import Doc2Vec

def test_similarity(arr, model):
    for pair in arr:
        w1 = pair[0]
        w2 = pair[1]
        print w1, w2, model.similarity(w1, w2)


def main():

    model = Doc2Vec.load("doc2vec.model")

    test_similarity([("history", "tradition"),
                     ("king", "man"),
                     ("queen", "woman"),
                     ("king", "peasant"),
                     ("peasant", "rich"),
                     ("king", "rich"),
                     ("king", "queen"),
                     ("man", "woman"),
                     ("husband", "wife"),
                     ("love", "hate"),
                     ("tyrant", "ruler"),
                     ("food", "drink"),
                     ("food", "servant"),
                     ("cow", "food"),
                     ("right", "wrong"),
                     ("king", "woman")], model)

    #print model["king"]

if __name__ == '__main__':
      main()