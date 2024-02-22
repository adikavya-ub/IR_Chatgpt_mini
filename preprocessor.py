
import collections
from nltk.stem import PorterStemmer
import re
from nltk.corpus import stopwords
import nltk
import pandas as pd
nltk.download('stopwords')


class Preprocessor:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.ps = PorterStemmer()

    def read_docs_pocess(self, file_name):
        df = pd.read_csv(file_name, sep='\t', index_col=0, names=['doc_id', 'text'])
        df['stemmed_tokens'] = df['text'].apply(self.preprocessing)
        df['doc_id'] = df.index
        return df        

    def preprocessing(self, text):
        text = text.lower()
        query = re.sub(r'[^0-9a-zA-Z]+', ' ', text)
        query_tokens = [self.ps.stem(q.strip()) for q in query.split() if q not in self.stop_words]
        return query_tokens