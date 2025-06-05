# from llm_judge import JokeJudge
# from groq import Groq

# def test_joke_judge():
#     client = Groq(api_key="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")

#     jokes = [
#         "Why did the chicken cross the road? To get to the other side!",
#         "I told my computer I needed a break, and it said 'No problem, I'll go to sleep.'"
#     ]

#     judge = JokeJudge(client)

#     top_jokes = judge.evaluate_multiple_jokes(jokes)
#     print(top_jokes)

#     assert len(top_jokes) > 0
#     # Optionally assert more about the scores or jokes