from dotenv import load_dotenv, find_dotenv, set_key, unset_key, get_key
import os
print( 'file path currently',os.path.abspath(__file__))
from pathlib import Path
from plansearch import plansearch
from groq import Groq
from typing import List
from llm_judge import JokeJudge
from novelty_measure import Novelty_Detect


env_file_path=".env"

from typing import List, Tuple
import logging


def set_api_key():
    api_key=input("🔑 Please enter your groq api key: ")
    if api_key:
        set_key(str(env_file_path),"Groq_key",api_key)
        print("✅ API key set successfully!")
    
    else:
        print("❌ API Key not set!")


def get_api_key():
    return get_key(str(env_file_path),"Groq_key")

def update_api_key():
    api_key=input("🔑 Please enter your api key: ")
    if api_key:
        set_key(str(env_file_path),"Groq_key",api_key)
        print("✅ API key set successfully!")
    else:
        print("❌ API Key not set!")


def run_plansearch(api_key:str,context:str,model:str="gemma2-9b-it",n:int=3):
    """
    n: number of jokes to generate
    """
    generated_jokes=[]
    client=Groq(api_key=api_key)
    system_prompt="You are a brilliant and extremely funny stand-up comedian."
    context=context
    jokes,tokens=plansearch(system_prompt=system_prompt,context=context,client=client,model=model,n=n)
    
    print("\n===== Generated Jokes =====\n")
    for i, joke in enumerate(jokes, start=1):
        print(f"Joke {i}:\n{joke}\n")
        generated_jokes.append(joke)

    # print(f"Total completion tokens used: {tokens}")
    
    return generated_jokes




def clean_joke_text(joke: str) -> str:
    joke = joke.replace("```", "")        # Remove backticks
    joke = joke.strip()                    # Trim whitespace
    # Remove leading > and any leading/trailing quotes
    if joke.startswith(">"):
        joke = joke.lstrip(">").strip()
    joke = joke.strip('"').strip("'")     # Strip quotes from start/end
    # Replace multiple newlines with a single newline
    import re
    joke = re.sub(r'\n+', '\n', joke)
    return joke

topic=["elevator","node js locked in a VM"]



n=6 #number of jokes 


input_context=str(input("Please enter a context/idea to generate jokes from: "))
set_api_key()
print(f"{get_api_key()}")

client=Groq(api_key=get_api_key())

generated_jokes=run_plansearch(api_key=get_api_key(),context=input_context,model="gemma2-9b-it",n=n)
clean_jokes = [clean_joke_text(j) for j in generated_jokes]

judge=JokeJudge(client)

top_jokes=judge.evaluate_multiple_jokes(generated_jokes)





nd=Novelty_Detect(client,create_joke_embed=False,create_acu_embed=False)
baseline_nov=nd.baseline_novelty(generated_jokes)
novelty_scores=nd.novascore(generated_jokes)




def write_markdown_report(jokes,top_jokes,baseline_nov,novelty_scores,file_path="output_report.md"):
    md_lines = []
    md_lines.append(f"# 📝 Joke Generation, Judgement and Novelty Report\n")

    # md_lines.append(f"**Total Completion Tokens Used**: `{token_count}`\n")
    md_lines.append("---\n")

    # Generated Jokes
    md_lines.append("## Generated Jokes\n")
    for idx, joke in enumerate(jokes, 1):
        md_lines.append(f"### Joke {idx}\n")
        if joke.startswith(">"):
            md_lines.append(f"> {joke.strip()}\n")
        else:
            md_lines.append("```text\n" + joke.strip() + "\n```\n")

    md_lines.append("---\n")
    md_lines.append("## Top Jokes\n")
    for idx, (joke, score) in enumerate(top_jokes, 1):
        # Clean joke text (remove backticks and strip)
        clean_joke = joke.replace("```", "").strip()
        md_lines.append(f"### Joke {idx}\n")
        md_lines.append("```text\n" + clean_joke + "\n```\n")
        md_lines.append(f"**Score**: `{score:.2f}`\n")
    md_lines.append("---\n")
    
    
    md_lines.append("## Baseline Novelty Scores\n")
    for idx, (joke, scores) in enumerate(baseline_nov.items(), 1):
        clean_joke = joke.replace("```", "").strip()
        md_lines.append(f"### Joke {idx}\n")
        if joke.startswith(">"):
            md_lines.append(f"> {clean_joke}\n")
        else:
            md_lines.append("```text\n" + clean_joke + "\n```\n")

        # Score details
        md_lines.append(f"- Semantic Score: `{scores['semantic']:.4f}`")
        md_lines.append(f"- Structural Score: `{scores['structural']:.4f}`")
        md_lines.append(f"- Combined Score: `{scores['combined']:.4f}`")
        md_lines.append(f"- Is Novel: `{'Yes' if scores['is_novel'] else 'No'}`")
        md_lines.append("\n---\n")
    
    md_lines.append("## ✨ Joke NovAScore \n")
    for joke, details in novelty_scores.items():
        clean_joke = joke.replace("```", "").strip()
        md_lines.append("```text\n" + clean_joke + "\n```\n")
        md_lines.append(f"- Novelty Score: `{float(details['nova_score']):.4f}`\n")
        md_lines.append(f"- Is Novel: `{bool(details['is_novel'])}`\n")
    md_lines.append("---\n")


    # Write to file
    Path(file_path).write_text("\n".join(md_lines), encoding="utf-8")
    print(f"[✓] Markdown report written to `{file_path}`.")
    

write_markdown_report(clean_jokes,top_jokes=top_jokes,baseline_nov=baseline_nov,novelty_scores=novelty_scores)