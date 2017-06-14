import os
import urllib

DOWNLOADS_DIR = '/Users/chrisfischer/Desktop/doc2vec_test/Texts'

# For every line in the file
for url in open('/Users/chrisfischer/Desktop/doc2vec_test/urls.txt'):
    # Split on the rightmost / and take everything on the right side of that
    name = url.rsplit('/', 1)[-1]

    # Combine the name and the downloads directory to get the local filename
    filename = os.path.join(DOWNLOADS_DIR, name) + ".txt"

    # Download the file if it does not exist
    if not os.path.isfile(filename):
        urllib.urlretrieve(url, filename)