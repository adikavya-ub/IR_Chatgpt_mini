from re import L
from symbol import comparison
from tqdm import tqdm
from preprocessor import Preprocessor
from indexer import Indexer
from collections import OrderedDict
from linkedlist import LinkedList
import inspect as inspector
import sys
import argparse
import json
import time
import random
import flask
from flask import Flask
from flask import request
import hashlib

app = Flask(__name__)


class ProjectRunner:
    def __init__(self):
        self.preprocessor = Preprocessor()
        self.indexer = Indexer()

    def _daat_and(self, query_tokens):
        list_of_posting = [self.indexer.inverted_index[t] for t in query_tokens]
        list_of_posting.sort(key=lambda x: x.length)
        i = 1
        comparisons = 0
        temp_ll = list_of_posting[0]
        while i < len(list_of_posting) and len(list_of_posting) > 1:
            pl_1 = temp_ll.start_node
            pl_2 = list_of_posting[i].start_node
            temp = LinkedList()
            while pl_1 and pl_2:
                if pl_1.value == pl_2.value:
                    comparisons += 1
                    temp.insert_at_end(pl_1.value, tfidf=max(pl_1.tfidf, pl_2.tfidf))
                    print(pl_1.tfidf)
                    pl_1 = pl_1.next
                    pl_2 = pl_2.next
                elif pl_1.value > pl_2.value:
                    comparisons += 1
                    pl_2 = pl_2.next
                else:
                    comparisons += 1
                    pl_1 = pl_1.next
            temp_ll = temp
            i += 1
        return temp_ll, comparisons
    
    def _daat_and_skips(self, query_tokens):
        list_of_posting = [self.indexer.inverted_index[t] for t in query_tokens]
        list_of_posting.sort(key=lambda x: x.length)
        i = 1
        comparisons = 0
        temp_ll = list_of_posting[0]
        while i < len(list_of_posting) and len(list_of_posting) > 1:
            pl_1 = temp_ll.start_node
            pl_2 = list_of_posting[i].start_node
            temp = LinkedList()
            while pl_1 is not None and pl_2 is not None:
                if pl_1.value == pl_2.value:
                    temp.insert_at_end(pl_1.value, tfidf=pl_1.tfidf)
                    print(pl_1.tfidf)
                    pl_2 = pl_2.next
                    pl_1 = pl_1.next
                    comparisons += 1
                elif pl_1.value < pl_2.value:
                    if pl_1.skip_pointer and pl_1.skip_pointer.value < pl_2.value:
                        while pl_1.skip_pointer and pl_1.skip_pointer.value < pl_2.value:
                            comparisons += 1
                            pl_1 = pl_1.skip_pointer
                    else:
                        comparisons += 1
                        pl_1 = pl_1.next
                else:
                    if pl_2.skip_pointer and pl_2.skip_pointer.value < pl_1.value:
                        while pl_2.skip_pointer and pl_2.skip_pointer.value < pl_1.value:
                            comparisons += 1
                            pl_2 = pl_2.skip_pointer
                    else:
                        comparisons += 1
                        pl_2 = pl_2.next
            temp_ll = temp
            i += 1
        return temp_ll, comparisons
    
    def tfidf(self, query_tokens, skips=False):
        if skips:
            ll, comparison = self._daat_and_skips(query_tokens=query_tokens)
        else:
            ll, comparison = self._daat_and(query_tokens=query_tokens)
            
        current = ll.start_node;  
        index = None;  
        
        if ll.start_node == None:  
            return; 
        else:  
            while current != None:   
                index = current.next;  
                
                while(index != None):  
                    if(current.tfidf > index.tfidf):  
                        temp = (current.value, current.tfidf)
                        current.value, current.tfidf = index.value, index.tfidf
                        index.value, index.tfidf = temp[0], temp[1]
                    index = index.next  
                current = current.next
        return ll, comparison

    def _output_formatter(self, op):
        if op is None or len(op) == 0:
            return [], 0
        op_no_score = [int(i) for i in op]
        results_cnt = len(op_no_score)
        return op_no_score, results_cnt

    def run_indexer(self, corpus):
        df = self.preprocessor.read_docs_pocess(corpus)
        df[['doc_id', 'stemmed_tokens']].apply(lambda x: self.indexer.generate_inverted_index(x[0], x[1]), axis=1)
        self.indexer.sort_terms()
        self.indexer.add_skip_connections()
        self.indexer.calculate_tf_idf(df.shape[0])

    def run_queries(self, query_list, random_command):
        output_dict = {'postingsList': {},
                       'postingsListSkip': {},
                       'daatAnd': {},
                       'daatAndSkip': {},
                       'daatAndTfIdf': {},
                       'daatAndSkipTfIdf': {},
                       'sanity': self.sanity_checker(random_command)}

        for query in tqdm(query_list):
            input_term_arr = self.preprocessor.preprocessing(query)

            for term in input_term_arr:
                ll = self.indexer.inverted_index[term]
                postings, skip_postings = ll.traverse_list(), ll.traverse_skips()
                output_dict['postingsList'][term] = postings
                output_dict['postingsListSkip'][term] = skip_postings

            and_op_no_skip, and_comparisons_no_skip = self._daat_and(input_term_arr)
            and_op_skip, and_comparisons_skip = self._daat_and_skips(input_term_arr)
            and_op_no_skip_sorted, and_comparisons_no_skip_sorted = self.tfidf(input_term_arr)
            and_op_skip_sorted, and_comparisons_skip_sorted = self.tfidf(input_term_arr, skips=True)

            and_op_no_score_no_skip, and_results_cnt_no_skip = self._output_formatter(and_op_no_skip.traverse_list())
            and_op_no_score_skip, and_results_cnt_skip = self._output_formatter(and_op_skip.traverse_list())
            and_op_no_score_no_skip_sorted, and_results_cnt_no_skip_sorted = self._output_formatter(and_op_no_skip_sorted.traverse_list())
            and_op_no_score_skip_sorted, and_results_cnt_skip_sorted = self._output_formatter(and_op_skip_sorted.traverse_list())

            output_dict['daatAnd'][query.strip()] = {}
            output_dict['daatAnd'][query.strip()]['results'] = and_op_no_score_no_skip
            output_dict['daatAnd'][query.strip()]['num_docs'] = and_results_cnt_no_skip
            output_dict['daatAnd'][query.strip()]['num_comparisons'] = and_comparisons_no_skip

            output_dict['daatAndSkip'][query.strip()] = {}
            output_dict['daatAndSkip'][query.strip()]['results'] = and_op_no_score_skip
            output_dict['daatAndSkip'][query.strip()]['num_docs'] = and_results_cnt_skip
            output_dict['daatAndSkip'][query.strip()]['num_comparisons'] = and_comparisons_skip

            output_dict['daatAndTfIdf'][query.strip()] = {}
            output_dict['daatAndTfIdf'][query.strip()]['results'] = and_op_no_score_no_skip_sorted
            output_dict['daatAndTfIdf'][query.strip()]['num_docs'] = and_results_cnt_no_skip_sorted
            output_dict['daatAndTfIdf'][query.strip()]['num_comparisons'] = and_comparisons_no_skip_sorted

            output_dict['daatAndSkipTfIdf'][query.strip()] = {}
            output_dict['daatAndSkipTfIdf'][query.strip()]['results'] = and_op_no_score_skip_sorted
            output_dict['daatAndSkipTfIdf'][query.strip()]['num_docs'] = and_results_cnt_skip_sorted
            output_dict['daatAndSkipTfIdf'][query.strip()]['num_comparisons'] = and_comparisons_skip_sorted

        return output_dict


@app.route("/execute_query", methods=['POST'])
def execute_query():
    start_time = time.time()

    queries = request.json["queries"]
    random_command = request.json["random_command"]
    output_dict = runner.run_queries(queries, random_command)
    with open(output_location, 'w') as fp:
        json.dump(output_dict, fp)

    response = {
        "Response": output_dict,
        "time_taken": str(time.time() - start_time),
        "username_hash": username_hash
    }
    return flask.jsonify(response)

@app.route("/execute_query", methods=['POST'])
def execute_quer():
    start_time = time.time()

    queries = request.json["queries"]
    random_command = request.json["random_command"]
    output_dict = runner.run_queries(queries, random_command)
    with open(output_location, 'w') as fp:
        json.dump(output_dict, fp)

    response = {
        "Response": output_dict,
        "time_taken": str(time.time() - start_time),
        "username_hash": username_hash
    }
    return flask.jsonify(response)

if __name__ == "__main__":
    output_location = "project2_output.json"
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--corpus", type=str, help="Corpus File name, with path.")
    parser.add_argument("--output_location", type=str, help="Output file name.", default=output_location)
    parser.add_argument("--username", type=str,
                        help="Your UB username. It's the part of your UB email id before the @buffalo.edu. "
                             "DO NOT pass incorrect value here")

    argv = parser.parse_args()
    corpus = argv.corpus
    output_location = argv.output_location
    username_hash = hashlib.md5(argv.username.encode()).hexdigest()
    runner = ProjectRunner()
    runner.run_indexer(corpus)
    app.run(host="0.0.0.0", port=9999)
