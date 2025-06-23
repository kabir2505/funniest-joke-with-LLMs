#llm as a judge implemnetation to score jokes
from groq import Groq
from dotenv import load_dotenv, find_dotenv, set_key, unset_key, get_key
from pydantic import BaseModel
import json
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

#llm clients
llm_clients=["gemma2-9b-it","llama-3.1-8b-instant","deepseek-r1-distill-llama-70b"]

# 7 judge personalities
judge_personalities={
    "affiliative": "You are a friendly and warm comediy judge who loves jokes that bring people together",
    "self_enhancing":"You are a witty judge who appreciates jokes that build confidence and optimism",
    "aggressive":"You are a sarcastic and edgy judge who enjoys dark or biting humor",
    "self_defeating":"You are a humble judge who likes hokes making fun of oneself",
    "brutal":"You are a brutally honest judge who rarely laughs and only appreciates jokes that are genuinely funny and celever. You have a dry sense of humor and don't tolerate mediocre jokes.",
    "absurdist": "You are a judge who loves surreal, bizarre, and nonsensical humor that twists reality in unexpected ways.",
    "philosophical": "You are a thoughtful judge who enjoys jokes that make people think deeply or challenge their perspectives.",
    
}


few_shot_examples = """
Joke: Today a man knocked on my door and asked for a small donation towards the local swimming pool. I gave him a glass of water.
{
    "score": 8,
    "isFunny": true,
    "confidence": 9,
    "humor_type": "wordplay",
    "reason_code": "clever_misdirection",
    "originality": 7,
    "would_tell_again": true,
    "understood_punchline": true,
    "setup_quality": 9
}
"""

class Joke(BaseModel):
    score: int
    isFunny: bool
    confidence: int
    humor_type: str
    reason_code: str
    originality: int
    would_tell_again: bool
    understood_punchline: bool
    setup_quality: int

class JokeJudge:
    def __init__(self, client):
        self.client = client
    
    def call_llm(self, model_name: str, prompt: str) -> str | None:
        try:
            response = self.client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content":prompt}],
                temperature=0.3, 
                max_tokens=1000,  
                response_format={"type": "json_object"}
            )
            
            answer = response.choices[0].message.content.strip()
            return answer
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return None
    
    def rate_jokes(self, model_name: str, personality: str, joke: str) -> str | None:
        # Simplified and more focused prompt
        prompt = f"""You are a comedy judge with this personality: {personality}

Rate this joke on a 1-10 scale where:
1-2: Not funny, 3-4: Mildly amusing, 5-6: Decent, 7-8: Funny, 9-10: Hilarious

Example response format:
{few_shot_examples}

Joke: {joke}

Respond with ONLY valid JSON matching this exact format. Be concise in string values.

Required JSON structure:
{{
    "score": <1-10 integer>,
    "isFunny": <true/false>,
    "confidence": <1-10 integer>,
    "humor_type": "<brief description>",
    "reason_code": "<brief reason>",
    "originality": <1-10 integer>,
    "would_tell_again": <true/false>,
    "understood_punchline": <true/false>,
    "setup_quality": <1-10 integer>
}}

Dont output any other explanations or strings except the json.
"""

        return self.call_llm(model_name=model_name, prompt=prompt)
    
    
    def evaluate_joke_across_judges(self, joke: str):
        all_scores = {}
        for model_name in llm_clients:
            for personality_key, personality_desc in judge_personalities.items():
                score = self.rate_jokes(
                    model_name=model_name,
                    personality=personality_desc,
                    joke=joke
                )
                try:
                    score = json.loads(score)
                except TypeError:
                    print(f"Skipping joke due to TypeError in response: {joke}")
                    continue
                # score=json.loads(score) # {'score': 6, 'isFunny': True, 'confidence': 8, 'humor_type': 'pun', 'reason_code': 'animal_based_pun', 'originality': 5, 'would_tell_again': True, 'understood_punchline': True, 'setup_quality': 7}
                key = f"{model_name}_{personality_key}"
                all_scores[key] = score # {"gemma_affiliative":{"score": 6, "isFunny": True, "confidence": 8, "humor_type": "pun", "reason_code": "animal_based_pun", "originality": 5, "would_tell_again": True, "understood_punchline": True, "setup_quality": 7}}
        
        #all_scores=21 variants for one joke
        return all_scores

    
    def aggregate_scores(self,judge_output: dict, plot: bool = True) -> pd.Series:
        df = pd.DataFrame(judge_output).T.copy()

        bool_cols = ["isFunny", "would_tell_again", "understood_punchline"]
        for col in bool_cols:
            df[col] = df[col].astype(int)

        numeric_cols = df.select_dtypes(include='number').columns
        categorical_cols = df.select_dtypes(exclude='number').columns

        bayesian_cols = ["score", "originality", "setup_quality"]
        bayesian_result = {}
        m = 5  # prior weight 
        C = 7  # global mean

        for col in bayesian_cols:
            v = len(df)
            R = df[col].mean()
            bayesian_score = (v / (v + m)) * R + (m / (v + m)) * C
            bayesian_result[col] = bayesian_score

        #  mean for confidence
        bayesian_result["confidence"] = df["confidence"].mean()

        # binary (boolean) columns mean
        for col in bool_cols:
            bayesian_result[col] = df[col].mean()

        # mode for categorical modes
        categorical_modes = df[categorical_cols].mode().iloc[0]
        for col in categorical_modes.index:
            bayesian_result[col] = categorical_modes[col]

        if plot and 'score' in df.columns:
            plt.figure(figsize=(10, 5))
            plt.scatter(df.index, df["score"], color="blue", alpha=0.8)
            plt.title("Raw Score by Model")
            plt.xlabel("Model")
            plt.ylabel("Score")
            plt.xticks(rotation=90)
            plt.grid(True, linestyle='--', alpha=0.5)
            plt.tight_layout()
            plt.show()
            

        return pd.Series(bayesian_result)
    
    def get_top_2_jokes(self,joke_score_tuples, weights=None):
        
        jokes, scores = zip(*joke_score_tuples)
        df = pd.DataFrame(scores)
        df["joke"] = jokes

       
        if weights is None:
            weights = {
                "score": 0.4,
                "originality": 0.2,
                "setup_quality": 0.2,
                "confidence": 0.1,
                "would_tell_again": 0.05,
                "isFunny": 0.05
            }

       
        numeric_cols = list(weights.keys())
        scaler = MinMaxScaler()
        df[numeric_cols] = scaler.fit_transform(df[numeric_cols])

        # Compute weighted composite score
        df["composite_score"] = sum(df[col] * weight for col, weight in weights.items())

        # Sort and select top 2
        top_2 = df.sort_values("composite_score", ascending=False).head(2)

        return top_2[["joke", "composite_score"]]
    
    def filter_and_convert_to_df(self,judge_output: dict, selected_keys: list) -> pd.DataFrame:
        selected_data = {}

        for model_name, scores in judge_output.items():
            for selected_key in selected_keys:
                if selected_key in model_name:
                    selected_data[model_name] = scores
                    break  

        df = pd.DataFrame.from_dict(selected_data, orient="index")
        return df

    def evaluate_multiple_jokes(self, jokes: list[str], top_k: int = 2) -> list[tuple[str, float]]:
        
        """
        Evaluate multiple jokes and return top_k jokes sorted by aggregate score.
        """
        
        selected_keys = [
        "llama-3.1-8b-instant_absurdist",
        "gemma2-9b-it_self_defeating",
        "deepseek-r1-distill-llama-70b_philosophical",
        "gemma2-9b-it_aggressive"
    ]

        joke_scores = []
        for joke in jokes:
            print(f"Joke output for joke :{joke}")
            scores = self.evaluate_joke_across_judges(joke=joke)
            df = self.filter_and_convert_to_df(scores, selected_keys)
            print(df.to_string())
            crowd_score = self.aggregate_scores(scores) #plots a graph and returns aggregate score dict #{"isFunny":1.0,"would_tell_again":0.8571428571,"understood_punchline":1.0,"score":6,"confidence":9,"humor_type":"pun","reason_code":"animal_based","originality":6,"setup_quality":9}
            print(crowd_score)
            crowd_score=crowd_score
            joke_scores.append((joke, crowd_score.to_dict()))

        # Filter and sort
        top_2_jokes = self.get_top_2_jokes(joke_score_tuples=joke_scores, weights={"score": 0.4, "originality": 0.2, "setup_quality": 0.2, "confidence": 0.1, "would_tell_again": 0.05, "isFunny": 0.05})
        print(top_2_jokes)
        return joke_scores[:top_k]





    

