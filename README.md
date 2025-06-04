# funniest-joke-with-LLMs
Plansearch and LLM as a Judge Implementation

`User provides a topic → Generate N candidate jokes about that topic → LLM ranks them → Output top-k jokes about that topic`


`Topic (e.g., "penguins", "VM") ➝ Premises / Observations ➝ Derived Punchline Ideas ➝ Joke Setup ➝ Full Joke`


### solve vs solve_multiple

`solve`  
- gives you one full pipeline result:
    -  a unique joke idea (based on new observations)
    - a joke written from that idea
- The joke is based on freshly generated content every time it's called


- `solve_multiple()` is just a convinient, reusable helper to say:
> Give me 5 different jokes about AI
- it internally calls solve() n times
- each time, it generates a *new idea* and joke from scratch
- returns a list of only *final jokes*, not the joke ideas
- Returns 3 unique jokes, each generated independently — not different versions of the same idea.



### Running tests
`uv run pytest -s`