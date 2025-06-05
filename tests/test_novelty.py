from novelty_measure import Novelty_Detect
from groq import Groq

def test_novelty_detect():
    client = Groq(api_key="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")

    nd=Novelty_Detect(client,create_joke_embed=False,create_acu_embed=False)
    jokes=[
        "Why did the chicken cross the road? To get to the other side!",
        "I told my computer I needed a break, and it said 'No problem, I'll go to sleep.'",
        "Did you hear about the mathematician who's afraid of negative numbers? He'll stop at nothing."
    ]

    # print(nd.baseline_novelty(jokes))
    print(nd.novascore(jokes))
    
    #print(nd.create_joke_embed)
    #print(nd.create_acu_embed)