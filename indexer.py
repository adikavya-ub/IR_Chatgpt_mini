from collections import OrderedDict, Counter
from linkedlist import LinkedList


class Indexer:
    def __init__(self):
        self.inverted_index = OrderedDict({})
        self.tf_counter = {}
        self.nterms_doc_map = {}

    def get_index(self):
        return self.inverted_index

    def generate_inverted_index(self, doc_id, tokenized_document):
        self.tf_counter[doc_id] = Counter(tokenized_document)
        self.nterms_doc_map[doc_id] = len(tokenized_document)
        for t in tokenized_document:
            self.add_to_index(t, doc_id)

    def add_to_index(self, term_, doc_id_):
        if term_ not in self.inverted_index:
            self.inverted_index[term_] = LinkedList()
            
        node = self.inverted_index[term_].insert_at_end(doc_id_)
      
    def calculate_tf_idf(self, total_doc):
        for term, ll in self.inverted_index.items():
          temp = ll.start_node
          while temp:
            posting_list_count = ll.length
            idf = total_doc/posting_list_count
            temp.tfidf = idf * (self.tf_counter[temp.value][term]/self.nterms_doc_map[temp.value])
            temp = temp.next

    def sort_terms(self):
        sorted_index = OrderedDict({})
        for k in sorted(self.inverted_index.keys()):
            sorted_index[k] = self.inverted_index[k]
        self.inverted_index = sorted_index

    def add_skip_connections(self):
        for value in self.inverted_index.values():
            value.add_skip_connections()
