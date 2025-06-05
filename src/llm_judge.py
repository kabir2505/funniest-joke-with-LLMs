#llm as a judge implemnetation to score jokes

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
Joke: Why don't scientists trust atoms? Because they make up everything.
Score: 8

Joke: I told my wife she was drawing her eyebrows too high. She looked surprised.
Score: 7

Joke: A horse walks into a bar. Bartender says, "Why the long face?"
Score: 5

Joke: What did the existential nihilist say? "Nothing matters. Especially this joke."
Score: 4

Joke: What's brown and sticky? A stick.
Score: 6

Joke: Knock knock. Who's there? Interrupting cow. Interrupting co—MOO!
Score: 3

Joke: My life is like a software update... always asking for more time.
Score: 2
"""

class JokeJudge:
    def __init__(self,client):
        self.client=client
    
    def call_llm(self,model_name:str,prompt:str) -> int | None:
        response = self.client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=10,
        )
        
        answer = response.choices[0].message.content.strip()
        
        try:
            return int(answer)
        except ValueError:
            return None
        
    
    
    def rate_jokes(self,model_name:str, personality:str, joke:str) -> int | None:
        prompt = f"""
    You are a comedy judge with the following personality: 
    {personality}

    Read the joke below and respond exactly as this judge would. Let your unique personality fully shape how funny you find the joke.
    Rate the joke on a scale from 1 (not funny) to 10 (hilarious).

    Here are some examples:
    {few_shot_examples}

    Joke:
    {joke}

    ONLY reply with the score as a single integer number between 1 and 10. No explanations, no extra text.
    """
        return self.call_llm(model_name=model_name, prompt=prompt)
    
    
    def evaluate_joke_across_judges(self, joke: str) -> dict[str, int | None]:
        all_scores = {}
        for model_name in llm_clients:
            for personality_key, personality_desc in judge_personalities.items():
                score = self.rate_jokes(
                    model_name=model_name,
                    personality=personality_desc,
                    joke=joke
                )
                key = f"{model_name}_{personality_key}"
                all_scores[key] = score
        return all_scores

    @staticmethod
    def aggregate_scores(scores_dict: dict[str, int | None]) -> float | None:
        """
        Aggregate scores by averaging only valid scores.
        """
        valid_scores = [score for score in scores_dict.values() if score is not None]
        if not valid_scores:
            return None
        return sum(valid_scores) / len(valid_scores)


    def evaluate_multiple_jokes(self, jokes: list[str], top_k: int = 2) -> list[tuple[str, float]]:
        """
        Evaluate multiple jokes and return top_k jokes sorted by aggregate score.
        """
        joke_scores = []
        for joke in jokes:
            scores = self.evaluate_joke_across_judges(joke=joke)
            crowd_score = self.aggregate_scores(scores)
            joke_scores.append((joke, crowd_score))

        # Filter and sort
        joke_scores = [js for js in joke_scores if js[1] is not None]
        joke_scores.sort(key=lambda x: x[1], reverse=True)
        return joke_scores[:top_k]



