# 🧠 HumorNet  
**Multistage Humor Generation + Evaluation with LLMs, Personality Judges, and Novelty Metrics**

---

## 🔍 Overview

![High Level Overview](overview.png)

**HumorNet** is a research prototype exploring the generative and evaluative boundaries of humor using LLMs. It tackles three hard problems in computational humor:

1. **Creative Joke Generation** using structured observations and LLM planning  
2. **Humanlike Humor Judging** through diverse LLM judge personas  
3. **Novelty Measurement** using structure-aware and semantic-aware scoring  

An experimental pipeline where jokes are *planned*, *generated*, *judged*, and *ranked*.

## 🧩 Core Modules

### 🧪 1. Plan-Based Joke Generation
![Plan Search for Jokes](pleansearch.png)
> _"Structured observation → Multi-step planning → LLM joke creation"_

- Accepts **contextual observations** (e.g., personality quirks, stereotypes)
- Uses a **multi-stage plan search** to draft and refine setups and punchlines
- Future plan: Replace brittle stepwise prompting with **beam search** or **MCTS**

---

### ⚖️ 2. LLM-as-a-Judge
> _"What if every joke had 21 judges with wildly different tastes?"_

- Evaluates jokes using **3 LLM families** × **7 personality archetypes**:
  - *Aggressive, Absurdist, Affiliative, Self-Enhancing*, etc.
- Judges score jokes across multiple axes:
  - `score`, `originality`, `setup_quality`, `confidence`, `humor_type`, etc.
- Scores aggregated via **Bayesian smoothing**
- Final ranking weighted using configurable `composite_score`

---

### 🌱 3. Novelty Scoring (NovaScore)
> _"Originality beyond surface-level variation"_

- Computes **semantic novelty** via SentenceTransformer + FAISS
- Computes **structural novelty** via POS-tag pattern similarity
- Computes **acu-level (setup/punchline)** novelty from vector distance
- Outputs:

```json
{
  "semantic": 0.71,
  "structural": 0.62,
  "nova_score": 0.65,
  "is_novel": true
}
```
Plansearch and LLM as a Judge Implementation

`User provides a topic → Generate N candidate jokes about that topic → LLM ranks them → Output top-k jokes about that topic`


`Topic (e.g., "penguins", "VM") ➝ Premises / Observations ➝ Derived Punchline Ideas ➝ Joke Setup ➝ Full Joke`


### Overview



### Detailed Report on methodology, experiments, learnings 
Report link : https://docs.google.com/document/d/1K7TKCjaMitwuCzfkGIjF7hbwhZbpvKwfVJLiNF3JQiQ/edit?usp=sharing

#### Output of the input context word is saved in `output_report.md` !

#### Example Run 
 #### Refer to `output_eg.md`
---



### Runs
use `uv`  
Generate a `Groq api key` from `https://console.groq.com/keys`

```
uv venv           
uv pip install -r pyproject.toml  
uv run src/main.py            
```

#### Output example run of the whole pipeline
Refer to `output_eg.md`

#### Outputs for a joke context/word
The above code runs the main file and generates an output based on the given context word
Refer to `output_report.md`


---
`llm_judge` few shot prompts referred from https://github.com/RajeshThevar/Joke-Classification-using-Machine-Learning-model/blob/master/JokeNonJokecollection/Collection