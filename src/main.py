from dotenv import load_dotenv, find_dotenv, set_key, unset_key, get_key
import os
print( 'file path currently',os.path.abspath(__file__))
from pathlib import Path
from plansearch import plansearch
from groq import Groq
from typing import List

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

    print(f"Total completion tokens used: {tokens}")
    
    return generated_jokes




topic=["elevator","node js locked in a VM"]

n=5 #number of jokes to genrate for each topic

def llm_judge(generated_jokes:List):
    pass



def measure_novelty(generated_jokes:List):
    pass




set_api_key()
print(f"{get_api_key()}")

run_plansearch(api_key=get_api_key(),context=topic[1],model="gemma2-9b-it",n=n)