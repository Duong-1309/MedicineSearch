
import sqlite3
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from gemini_helper import parse_query_dimensions, summarize_results, translate_results

DB_PATH = './medicine.db'
model = SentenceTransformer('all-MiniLM-L6-v2')

class MedicineSearchEngine:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self._load_data()

    def _load_data(self):
        self.cursor.execute("SELECT id, embedding FROM medicines_detail")
        rows = self.cursor.fetchall()
        self.data = []
        self.embeddings = []
        for _id, embedding in rows:
            self.data.append(_id)
            self.embeddings.append(pickle.loads(embedding))
        self.embeddings = np.array(self.embeddings)

    def search(self, query, top_k=10) -> list[dict]:
        query_embedding = model.encode(query)
        similarities = cosine_similarity([query_embedding], self.embeddings)[0]
        print(f"🔍 Similarities: {similarities[0]}")
        top_indices = similarities.argsort()[-top_k:][::-1]
        top_ids = [self.data[idx] for idx in top_indices]
        print(top_ids)
        # name, composition, uses, side_effects, image_url, manufacturer, excellent_review, average_review, poor_review
        columns = ['id', 'name', 'composition', 'uses', 'side_effects', 'image_url', 'manufacturer', 'excellent_review', 'average_review', 'poor_review']
        query = f"""
        SELECT {', '.join(columns)}
        FROM medicines_detail
        WHERE id IN {tuple([int(id) for id in top_ids])}
        ORDER BY average_review DESC
        """
        print(f"🔍 SQL Query: {query}")
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        results = []
        for row in rows:
            result = {col: row[i] for i, col in enumerate(columns)}
            results.append(result)
        return results

    # process results before returning
    def process_results(self, results: list[dict]) -> list[dict]:
        # select only fields uses and side_effects
        _results_trans = []
        for result in results:
            _results_trans.append({
                'id': result['id'],
                'uses': result['uses'],
                'side_effects': result['side_effects']
            })
        # translate results
        _results_af_trans = translate_results(_results_trans)
        # merge translate results to original results
        for result in results:
            for _result_trans in _results_af_trans:
                if result['id'] == _result_trans['id']:
                    result['uses'] = _result_trans['uses']
                    result['side_effects'] = _result_trans['side_effects']
        return results   
        

    def search_with_llm(self, question, top_k=6):
        parsed_query = parse_query_dimensions(question)
        print(f"🔍 Parsed Query: {parsed_query}")
        results = self.search(parsed_query, top_k)
        print(f"🔍 Search Results: {results}")
        # process results
        results = self.process_results(results)
        print(f"🔍 Processed Results: {results}")
        # docs_id = [doc[0] for doc in results]
        # final_answer = summarize_results(question, texts)
        return results
