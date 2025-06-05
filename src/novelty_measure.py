from sentence_transformers import SentenceTransformer
from datasets import load_dataset
import os
import numpy as np
import faiss
from typing import List
from nltk import word_tokenize, pos_tag
import nltk
from difflib import SequenceMatcher
from nltk.tokenize import word_tokenize
from nltk.tag.perceptron import PerceptronTagger
import json


nltk.download('punkt')
nltk.download('averaged_perceptron_tagger_eng')
def get_pos_pattern(text):
    tokens=word_tokenize(text)
    pos = tagger.tag(tokens)  
    return [tag for _, tag in pos]

tagger = PerceptronTagger()  

def structure_diversity_score(joke, reference_jokes):
    joke_pattern = get_pos_pattern(joke)
    similarities = []

    for ref_joke in reference_jokes:
        ref_pattern = get_pos_pattern(ref_joke)
        sm = SequenceMatcher(None, joke_pattern, ref_pattern)
        similarities.append(sm.ratio())

    max_similarity = max(similarities) if similarities else 0
    return 1 - max_similarity  # Higher = more novel structurally

def files_missing_or_empty():
    files = ["src/punchline_list.json", "src/setup_list.json"]
    for file in files:
        if not os.path.exists(file):
            return True 
        try:
            with open(file, "r") as f:
                data = json.load(f)
                if not data: 
                    return True
        except Exception:
            return True  
    return False


class Novelty_Detect:
    def __init__(self,client,create_joke_embed=False,create_acu_embed=False):
        self.client=client
        self.senty=SentenceTransformer('all-MiniLM-L6-v2')
        self.joke_ds=load_dataset("corbt/reddit_jokes",split="train[:400]")

        self.create_joke_embed=create_joke_embed
        self.create_acu_embed=create_acu_embed
        
        if self.create_joke_embed:
            self.embed_index_joke()
        if self.create_acu_embed:
            if files_missing_or_empty():
                self.acu_bank()
            
            self.embed_index_acu()


    
    def embed_index_joke(self):
        reference_embeddings=self.senty.encode(self.joke_ds['selftext'],convert_to_numpy=True)
        #Normalize for cosine similarity
        reference_embeddings=reference_embeddings / np.linalg.norm(reference_embeddings, axis=1, keepdims=True)

        dim=reference_embeddings.shape[1]
        index=faiss.IndexFlatIP(dim) #Inner product
        index.add(reference_embeddings)
        
        faiss.write_index(index,"src/embeddings/joke_level/joke_index.faiss")
        np.save("src/embeddings/joke_level/reference_embeddings.npy",reference_embeddings)


    def extract_acus_via_prompt(self,joke:str) -> dict:
        prompt = f"""
You're a humor analyst.
Given the following joke, identify and separate:
- The **setup** : Background or context
- The **punchline**: The twist or funny part

Joke:
{joke}

Respond ONLY with valid JSON. Do not add any extra explanation, markdown, or commentary.
Return exactly:
{{
    "setup": "<setup>",
    "punchline": "<punchline>"
}}
"""
        
        response=self.client.chat.completions.create(
            model="gemma2-9b-it",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
            
        )
        
        return response.choices[0].message.content

    def acu_bank(self):
        setup_list=[]
        punchline_list=[]
        
        for i,joke in enumerate(self.joke_ds['selftext']):
            if i==100:
                break
            try:
                result_str = self.extract_acus_via_prompt(joke)
                #print(f"Raw model output for joke {i}:\n{result_str}\n")
                result = json.loads(result_str)
                setup = result.get("setup", "").strip()
                punchline = result.get("punchline", "").strip()
                
                if setup and punchline:
                    setup_list.append(setup)
                    punchline_list.append(punchline)
            except Exception as e:
                print(f"Error processing joke {i}: {str(e)}")
        
        with open("src/setup_list.json", "w") as f:
            json.dump(setup_list, f)

        with open("src/punchline_list.json", "w") as f:
            json.dump(punchline_list, f)
    
    def embed_index_acu(self):
        setup_list=json.load(open("src/setup_list.json"))
        punchline_list=json.load(open("src/punchline_list.json"))
        setup_embeddings=self.senty.encode(setup_list,convert_to_numpy=True)
        punchline_embeddings=self.senty.encode(punchline_list,convert_to_numpy=True)
        #Normalize for cosine similarity
        setup_embeddings=setup_embeddings / np.linalg.norm(setup_embeddings, axis=1, keepdims=True)
        punchline_embeddings=punchline_embeddings / np.linalg.norm(punchline_embeddings, axis=1, keepdims=True)
        
        setup_index = faiss.IndexFlatIP(setup_embeddings.shape[1])
        punchline_index = faiss.IndexFlatIP(punchline_embeddings.shape[1])
        
        setup_index.add(setup_embeddings)
        punchline_index.add(punchline_embeddings)

        
        faiss.write_index(setup_index, "src/embeddings/acu_level/setup_index.faiss")
        faiss.write_index(punchline_index, "src/embeddings/acu_level/punchline_index.faiss")
        
      

    
    def baseline_novelty(self, jokes: List[str], threshold: float = 0.7):

        """
        Computes the baseline novelty scores for a given list of jokes.

        This method combines semantic novelty (measured using FAISS) and structural novelty (measured using POS patterns)
        to generate an overall novelty score. The scores are then compared to a specified threshold to determine if the joke
        is novel or not.

        Args:
            jokes (List[str]): A list of joke texts to evaluate

            threshold (float, optional): The threshold for determining novelty. Defaults to 0.65.

        Returns:
            dict: A dictionary mapping each joke to its corresponding novelty scores and a boolean indicating whether it is novel.
        """
        baseline_novelty_score = {}

        # Load FAISS index and ref joke dataset
        index = faiss.read_index("src/embeddings/joke_level/joke_index.faiss")
        reference_jokes = self.joke_ds['selftext']  # Assuming this is a list of texts

        for joke in jokes:
            # --- Semantic Novelty ---
            joke_embedding = self.senty.encode(joke, convert_to_numpy=True)
            joke_embedding = joke_embedding.reshape(1, -1)
            normed_embedding = joke_embedding / np.linalg.norm(joke_embedding, axis=1, keepdims=True)

            distances, _ = index.search(normed_embedding, k=1)
            semantic_score = 1 - distances.squeeze()

            # --- Structural Novelty ---
            structural_score = structure_diversity_score(joke, reference_jokes)

            # --- Combine Both ---
            combined_score = 0.45 * semantic_score + 0.55 * structural_score  # weight as needed
            if combined_score >= threshold:
                is_novel = True
            else:
                is_novel = False
            baseline_novelty_score[joke] = {
                "semantic": semantic_score,
                "structural": structural_score,
                "combined": combined_score,
                "is_novel": is_novel
            }

        return baseline_novelty_score
            
    def novascore(self, jokes: List[str], threshold=0.65):
        nova_results = {}  # Store both score and novelty flag here

        def get_weights(saliences):
            sal_count = sum(saliences.values())
            total = len(saliences)
            sal_ratio = sal_count / total
            if sal_ratio < 0.3:
                return 1.0, 0.1
            elif sal_ratio > 0.7:
                return 0.9, 0.4
            else:
                return 1.0, 0.3

        setup_index = faiss.read_index("src/embeddings/acu_level/setup_index.faiss")
        punchline_index = faiss.read_index("src/embeddings/acu_level/punchline_index.faiss")

        for new_joke in jokes:
            acus = self.extract_acus_via_prompt(new_joke)
            
            if acus is not None:
                acus = json.loads(acus)
                print('acus here', acus)
                setup = acus["setup"]
                punchline = acus["punchline"]

                setup_embedding = self.senty.encode(setup, convert_to_numpy=True).reshape(1, -1)
                punchline_embedding = self.senty.encode(punchline, convert_to_numpy=True).reshape(1, -1)

               
                setup_embedding /= np.linalg.norm(setup_embedding, axis=1, keepdims=True)
                punchline_embedding /= np.linalg.norm(punchline_embedding, axis=1, keepdims=True)

                setup_sim, _ = setup_index.search(setup_embedding, k=1)
                punchline_sim, _ = punchline_index.search(punchline_embedding, k=1)

                setup_novelty = 1 - setup_sim.squeeze()
                punchline_novelty = 1 - punchline_sim.squeeze()

                novelty_scores = {"setup": setup_novelty, "punchline": punchline_novelty}
                saliences = {"setup": 1, "punchline": 1}  # hardcoded salience for now

                ws, wns = get_weights(saliences)

                nova_score = 0
                for acu in novelty_scores:
                    N = novelty_scores[acu]
                    S = saliences[acu]
                    nova_score += N * (ws * S + wns * (1 - S))

                nova_score /= len(novelty_scores)

                is_novel = nova_score >= threshold

                nova_results[new_joke] = {"nova_score": nova_score, "is_novel": is_novel}
            else:
                nova_results[new_joke] = {"nova_score": None, "is_novel": False}

        return nova_results