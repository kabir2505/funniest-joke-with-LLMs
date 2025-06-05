

### Why Did You Pick This Project?

I’ve always been fascinated by how people laugh at the unexpected — how a shift in perspective, a sudden incongruity, or even a playful misuse of logic can trigger something as human as laughter. Humor is one of the few areas where LLMs still struggle — not due to grammar or syntax, but because of **intentional misdirection**, the “twist” that turns a statement into a joke.

This project was my way of asking:

> Can we teach a model not just to be fluent, but to be funny on purpose?

I focused on three core challenges:

1. **Incongruity modeling** — Generating setups and punchlines that deliberately play off a shared context without collapsing into bland templates.
2. **Subjective evaluation** — Using personality-driven LLM judges to score humor along diverse human tastes instead of relying on BLEU or token overlap.
3. **Novelty detection** — Designing both embedding-based and structural (POS-based) metrics to test whether generated jokes were genuinely new or recycled from existing patterns.

Humor is **culturally grounded, often ambiguous**, and prone to surface-level mimicry. But that’s exactly what made it worth trying: if a model can handle something this fuzzy, it’s a strong testbed for general creative alignment.

---
###  If You Had More Compute/Time, What Would You Have Done?

Given the tight schedule, including travel to campus and participation in a 2-day hackathon mid-project, I focused on building end-to-end prototypes of each module (generation, judging, novelty detection), prioritizing iteration speed over scale.

If I had access to more compute and time, I would have deepened and expanded each of the three modules — not just in scale, but in **depth of experimentation** and **granularity of feedback**.

#### Novelty Detection

Currently, the novelty detector uses FAISS indexing for semantic distance and POS sequence comparisons for structural variation. These are lightweight but shallow.

- Fine-tune LLMs as style critics to flag derivative humor based on subtle trope reuse — beyond token-level overlap.
- Incorporate mutual information metrics between setup and punchline embeddings to quantify unexpectedness (e.g., how “orthogonal” the punchline is to the setup).

#### LLM-as-Judge

The LLM judge module currently uses 3 base models and 7 judge personalities. With more resources, I would:

- Expand personality coverage — include regional/cultural judges, age-specific personas (e.g., Gen Z vs. Boomer humor), or satire vs. slapstick preferences.
- Calibrate judges using human-aligned rating benchmarks — measure how well LLM-judge scores correlate with human annotator ratings across joke types.
- Introduce multi-turn evaluations where judges could ask clarifying questions or suggest rewrites — emulating how real comedians refine material.
- Run A/B tests of LLM-written jokes in real environments (e.g., Reddit, Discord bots, meme subreddits) to collect real-time crowd-laugh data.

#### Controlled Joke Generation at Scale

Right now, the Plan-and-Search joke generation module uses a simple template for first-order and second-order observations. With more compute/memory:

- Train a dedicated **observation extractor**, fine-tuned to identify primitive ideas from real-world concepts using visual grounding or structured knowledge bases.
- Diversify combinatorial logic — go beyond “AND” logic (A + B) to include temporal, causal, or analogical reasoning (“like A but for B”).
- Introduce **persona-driven joke writers** (e.g., “write this as if Seinfeld noticed it,” or “make it sound like a stoner Twitter post”) to test humor-style transfer.


### Explore and Experiment multiple different thresholds for novelty score calculations
Due to time constraints, I was only able to experiment with a limited range of thresholds. In future iterations, I’d like to explore a wider variety, systematically evaluate their impact, and identify the most effective threshold for capturing meaningful novelty.



## Learnings
This project taught me a lot about the *hidden complexity* of evaluating creative generation — especially humor — in LLMs. While generation itself is relatively straightforward with current models, **measuring quality, originality, and alignment** turned out to be the harder and more intellectually rich challenge.

####  Evaluation is not just a final step — it shapes the system.
Designing the LLM judge module made me realize that how you evaluate generation directly influences how you prompt, fine-tune, or even define “success.” Constructing judging personas forced me to think clearly about what kinds of humor I wanted to encourage (e.g., clever vs. crude, surprising vs. derivative). I came to appreciate evaluation as an *active part of the creative loop*, not a passive afterthought.


#### Novelty isn’t just distance — it’s context-aware and structural.
Building the novelty detection module showed me how easy it is to over-rely on semantic similarity via embeddings. Two jokes can be lexically different but structurally identical — or vice versa. By mixing syntactic analysis with semantic distance, I gained a deeper understanding of how novelty must be defined *relative to form, content, and timing*. It also showed the value of hybrid heuristics before diving into full model training.


 #### Humor exposes the limits of current LLM reasoning.
While models can imitate the surface form of jokes, they often lack deeper incongruity modeling — especially when required to link real-world facts, analogies, or metaphors. This made me more sensitive to the difference between **coherence** and **cleverness**. Models are good at being coherent — but cleverness requires structured surprises, and that remains difficult.



#### Judging humor is as hard as generating it.
Finally, I learned that aligning LLMs as humor critics is both a subjective and technical challenge. It raised questions about **whose laughter matters**, how cultural priors shape humor, and what fairness means when evaluating creative outputs. Humor evaluation isn’t just a matter of metrics — it’s a matter of perspective.

---

### What Surprised You the Most?

What surprised me most was **how brittle “funny” is for large language models**, despite their surface-level fluency. LLMs can easily generate text that *looks* like a joke: punchy, setup–punchline format, maybe even a pun, but whether it’s actually funny is another matter entirely.

#### 1. LLMs Often Confuse Randomness with Wit

I expected models to struggle with deep humor, but I underestimated how often they would equate absurdity or noise with cleverness. Many outputs felt like they *learned the form* of jokes, but not the cognitive *mechanics* behind incongruity, misdirection, or irony. It made me realize that humor isn’t just about surprising the reader — it’s about surprising them in *just the right way*.

---

#### 2. Evaluating Humor Is Harder Than Generating It

I assumed building the judge module would be relatively straightforward , just fine-tune or prompt a model to score jokes. But the real challenge was in **modeling taste**. Humor is personal, cultural, and contextual. The idea of having seven distinct judge “personalities” started as a design hack — but evolved into a key insight: **humor evaluation is a values problem**, not just a metrics one.

---

#### 3. Structural Novelty ≠ Conceptual Novelty

In the novelty detection module, I was surprised by how often jokes could be structurally unique (different grammar, POS patterns) but semantically stale — and vice versa. Some reused old tropes in new formats, others felt fresh despite familiar patterns. This taught me that detecting novelty requires **multi-dimensional reasoning**, not just vector distance.

---

#### 4. LLMs Could Decompose Jokes Surprisingly Well

Another pleasant surprise was how well models handled joke decomposition into setup and punchline using zero-shot prompting. Despite no explicit training for that task, the model often understood *where the twist happens*. It gave me hope that we might eventually be able to fine-tune models not just to write jokes, but to *understand why they’re funny*.

---

In short, the biggest surprise was that **humor lies at the intersection of language, logic, and psychology** — and LLMs can navigate the first two reasonably well, but still fumble the third. That gap is where the real research lies.

### If You Had to Write a Paper on the Project, What Else Needs to Be Done?

If this were to evolve into a full research paper, several directions stand out as necessary to rigorously validate and extend the work:

### 1. Ground the Evaluation Framework with Human Ratings

While the LLM-as-judge module offers a scalable, personality-aligned evaluation mechanism, we would need to **validate its judgments against real human annotators**. A core missing component is a human benchmark: collecting ratings across humor types (affiliative, aggressive, absurd, etc.) and **measuring agreement** between human judgments and LLM-simulated judges (e.g., Krippendorff’s alpha or Kendall’s tau).

- **Goal**: Establish whether LLM-based evaluation can serve as a reliable proxy for subjective human taste.
- **Open question**: Can LLMs generalize cultural, emotional, or subcultural humor preferences?

---
### 2. Fine-Grained Taxonomy of Joke Failures

Many jokes “almost” work — but break down in subtle ways (timing, tone, logic, cultural mismatches). To better understand this, we’d need to **annotate failure modes** across generated jokes:

- Formally categorize issues: logical incoherence, misfired puns, overused tropes, etc.
- Align these error types with model generation stages (e.g., setup–punchline disconnect).

This could lead to a **diagnostic benchmark for LLM humor generation**, filling a current gap in evaluation.

---

### 3. Incorporate Cross-Cultural and Multilingual Humor

Humor is deeply contextual — and culturally specific. Right now, our system is **monolingual and culturally narrow** (mostly trained on Reddit/Western jokes). Future work should:

- Include multilingual joke corpora and translation-based evaluation.
- Analyze if “funny” persists after translation — a true test of structural and conceptual novelty.

This opens the door to **cultural robustness** in humor models — a vital step for generalizable AI.

---

### 4. More Sophisticated Novelty Modeling

Our novelty detection system is a mix of embedding-based and POS-pattern heuristics. This could be extended by:

- Training a contrastive or variational model to explicitly learn **humor style embeddings**.
- Using **causal language modeling scores** to detect low-probability twists (potentially funnier ones).

This could help differentiate between “safe” jokes that models have seen a lot of, and truly **novel cognitive leaps** — the essence of creativity.

--
### 5. Longitudinal Joke Evolution

An underexplored but rich avenue is to model how jokes **change over time** — across memes, events, or internet subcultures. If we had temporal embeddings, we could:

- Measure how novelty decays
- Study when recontextualization makes old jokes funny again

It would be a way to study **memetic dynamics** through the lens of LLMs.

---

