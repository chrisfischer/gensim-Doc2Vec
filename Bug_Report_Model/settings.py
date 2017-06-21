class Settings:
    def __init__(self):
        pass

    DATASET_FILE = "data/mozilla_data.json"
    MONGO_CONNECTION_STRING = "mongodb://localhost:27017/"
    DOC2VEC_REPORTS_DATABASE = "doc2vec_mozilla_test"
    DUPLICATE_REPORTS_COLLECTION = "duplicate_reports"
    DUPLICATE_REPORTS_COLLECTION_SUBSET = "duplicates_half"
    REPORTS_COLLECTION = "all_reports"
    REPORTS_COLLECTION_SUBSET_1 = "all_results1"
    REPORTS_COLLECTION_SUBSET_2 = "all_results2"
    MODEL_PATH = 'model/'
    NUM_OF_MODELS = 100