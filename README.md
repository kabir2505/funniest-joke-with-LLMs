# funniest-joke-with-LLMs
Plansearch and LLM as a Judge Implementation

`User provides a topic → Generate N candidate jokes about that topic → LLM ranks them → Output top-k jokes about that topic`


`Topic (e.g., "penguins", "VM") ➝ Premises / Observations ➝ Derived Punchline Ideas ➝ Joke Setup ➝ Full Joke`


## Overview
![Plan Search for Jokes](pleansearch.png)
![High Level Overview](overview.png)

### Example Run 
Refer to `output_eg.md`
---

### Report
Refer to `Report.md`


### Runs
use `uv`

```
uv venv           # Create a virtual environment
uv pip install -r requirements.txt  # Or use uv pip if you have a requirements file
uv run python main.py               # Replace with your entry point
```

### Outputs for a joke context/word
The above code runs the main file and generates an output based on the given context word
Refer to `output_eg.md`