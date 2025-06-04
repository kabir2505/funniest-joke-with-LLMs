from typing import List, Tuple
import logging


logger=logging.getLogger(__name__)
class PlanSearch:
    def __init__(self, system_prompt:str,client,model:str):
        """
        Initializes the PlanSearch object with the given system prompt, client, and model.

        Args:
            system_prompt (str): The prompt to guide the system behavior.
            client: The client instance used to interact with the model.
            model (str): The model identifier for generating completions.

        Attributes:
            system_prompt (str): Stores the prompt for system guidance.
            client: Holds the client instance for model interaction.
            model (str): Keeps the model identifier for completions.
            plansearch_completion_tokens (int): Counter for the completion tokens used.
        """

        self.system_prompt = system_prompt
        self.client=client
        self.model = model
        self.plansearch_completion_tokens=0
    
    
    def generate_observations(self,context:str,num_observations: int=3) -> List[str]:

        """
        Generates a list of unique, funny, or surprising observations based on the given context.

        This method interacts with a language model to brainstorm several creative and humorous
        observations or associations related to the provided context, avoiding clichés. These
        observations are intended as seeds to inspire future joke generation.

        Args:
            context (str): The context or word to base the observations on.
            num_observations (int): The number of unique observations to generate. Defaults to 3.

        Returns:
            List[str]: A list of observations as strings, each containing a unique, funny, or 
            surprising observation related to the context.
        """

        prompt = f"""You are a world-class comedy writer. You will be given a word or context (e.g. "penguins", "nodejs locked in a VM").
Your job is to brainstorm several non-obvious, creative, and potentially hilarious observations or associations related to this context.
Avoid clichés. These are the seeds that could inspire the funniest jokes ever. You will NOT write any actual jokes yet.

Here is the context:
{context}

Please provide {num_observations} unique, funny, or surprising observations."""

        response=self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role":"system","content":self.system_prompt},
                {"role":"user","content":prompt}
            ]
        )
        
        self.plansearch_completion_tokens+=response.usage.completion_tokens
        observations=response.choices[0].message.content.strip().split('\n')
        print([obs.strip() for obs in observations])
        return [obs.strip() for obs in observations]


    def generate_derived_observations(self,context:str, observations:List[str],num_new_observations:int=2) -> List[str]:
        """
        Generates new, humorous observations derived from given observations and context.

        This method enhances the creativity of initial observations by developing new, 
        funny angles and ideas based on the provided context. It utilizes a language 
        model to generate observations that riff on or expand the original ones, 
        pushing them to more absurd or extreme directions while avoiding actual joke 
        writing.

        Args:
            context (str): The context or theme related to the observations.
            observations (List[str]): A list of initial humorous observations.
            num_new_observations (int): The number of new derived observations to generate.

        Returns:
            List[str]: A list of new, funny observations derived from the input observations.
        """

        
        prompt = f"""You are a professional comedy writer. You will be given a context and a few humorous observations about it.
            Your task is to build on those and come up with new, even more twisted or funny angles. These derived observations
            should riff on the original ones or take them to absurd/extreme directions. Do NOT write any jokes.

            Context:
            {context}

            Original Observations:
            {chr(10).join(f"{i+1}. {obs}" for i, obs in enumerate(observations))}

            Please provide {num_new_observations} new funny observations derived from the above."""

        
        response=self.client.chat.completions.create(
            model=self.model,
            max_tokens=4096,
            messages=[
                {"role":"system","content":self.system_prompt},
                {"role":"user","content":prompt}
            ]
        )
        
        self.plansearch_completion_tokens+=response.usage.completion_tokens
        observations=response.choices[0].message.content.strip().split('\n')
        print([obs.strip() for obs in observations])
        return [obs.strip() for obs in observations]

    
    def generate_solution_nl(self,context:str,observations:List[str]) -> str:
        """
        Generates a structured joke idea in natural language based on a set of creative observations about a context.

        This method takes the context and a list of observations as input and prompts the model to generate a clear, structured joke idea in natural language. The joke idea should quote relevant observations exactly before each punchline idea or twist. The model should focus on misdirection, absurdity, irony, and surprise while generating the joke idea. The output is not a final joke, but rather the structured joke logic with quoting.

        Args:
            context (str): The context or theme related to the observations.
            observations (List[str]): A list of humorous observations.

        Returns:
            str: A structured joke idea in natural language based on the input observations.
        """
        prompt = f"""You are writing a hilarious joke based on a set of creative observations about a context.

            Context:
            {context}

            Observations:
            {chr(10).join(f"Observation {i+1}: {obs}" for i, obs in enumerate(observations))}

            Now, use these ideas to brainstorm a clear, structured joke idea in natural language.
            Quote relevant observations exactly before each punchline idea or twist.
            Focus on misdirection, absurdity, irony, and surprise. You are NOT writing final code here, just the structured joke logic with quoting."""
        
         
        response=self.client.chat.completions.create(
            model=self.model,
            max_tokens=4096,
            messages=[
                {"role":"system","content":self.system_prompt},
                {"role":"user","content":prompt}
            ]
        )                  
        
        self.plansearch_completion_tokens+=response.usage.completion_tokens
        print(response.choices[0].message.content.strip())
        return response.choices[0].message.content.strip()

    
    
    def implement_solution(self,context:str,solution:str) -> str:
        """
        Generates a final joke based on a given context and structured joke idea.

        This method utilizes a language model to transform a structured joke plan 
        into a finalized joke format. The joke can be a one-liner, tweet-style, or 
        a short monologue, reflecting the humor encapsulated in the provided 
        structured joke idea.

        Args:
            context (str): The context or theme for the joke.
            solution (str): The structured joke plan that guides the joke creation.

        Returns:
            str: The finalized joke in markdown codeblocks.
        """

        prompt=prompt = f"""You are a world-class stand-up comedian. You will be given a context and a structured joke idea (solution).
Write a short, hilarious joke that reflects the idea. One-liner, tweet-style, or short monologue is fine.

Context:
{context}

Structured Joke Plan:
{solution}

Now write the final joke. You will NOT return anything except for the joke inside markdown codeblocks"""

        response=self.client.chat.completions.create(
            model=self.model,
            max_tokens=4096,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        
        self.plansearch_completion_tokens +=response.usage.completion_tokens
        print(response.choices[0].message.content.strip())
        
        return response.choices[0].message.content.strip()

    
    def solve(self,context:str, num_initial_observations:int=3,num_derived_observations:int=2) -> Tuple[str,str]:
        """
        Solves the joke generation problem for a given context.

        This method first generates some initial funny observations about the context,
        then derives new observations from those, and finally uses all of them to generate
        a structured joke idea and a final joke.

        Args:
            context (str): The context or theme for the joke.
            num_initial_observations (int): The number of initial observations to generate.
            num_derived_observations (int): The number of derived observations to generate.

        Returns:
            Tuple[str,str]: A tuple of the structured joke idea and the final joke.
        """
        logger.info("Generating initial funny observatuons")
        initial_observations=self.generate_observations(context,num_initial_observations)
        
        logger.info("Generating derived observations")
        derived_observations=self.generate_derived_observations(context,initial_observations,num_derived_observations)
        
        all_observations=initial_observations+derived_observations
        
        logger.info("Generating joke structure from observations")
        joke_idea=self.generate_solution_nl(context,all_observations)
        
        logger.info("Writing final joke")
        final_joke=self.implement_solution(context,joke_idea)
        
        print('joke_idea,final_joke',joke_idea,final_joke)
        
        return joke_idea,final_joke

    
    def solve_multiple(self,context:str,n:int,num_initial_observations:int=3, num_derived_observations:int=2) -> List[str]:
        """
        Solves the joke generation problem for a given context multiple times.

        This method wraps the solve method to generate multiple jokes for a given context.

        Args:
            context (str): The context or theme for the jokes.
            n (int): The number of jokes to generate.
            num_initial_observations (int): The number of initial observations to generate each time.
            num_derived_observations (int): The number of derived observations to generate each time.

        Returns:
            List[str]: A list of jokes as strings.
        """
        jokes=[]
        for _ in range(n):
            _,joke=self.solve(context=context,num_initial_observations=num_initial_observations,num_derived_observations=num_derived_observations)
            jokes.append(joke)
        
        return jokes


def plansearch(system_prompt:str,context:str,client,model:str,n:int=1) -> List[str]:
    """
    Executes the plansearch process to generate multiple jokes for a given context.

    This function initializes a PlanSearch object with the given system prompt, client, and model, 
    then uses it to solve the joke generation problem multiple times.

    Args:
        system_prompt (str): The prompt to guide the system behavior.
        context (str): The context or theme for the jokes.
        client: The client instance used to interact with the model.
        model (str): The model identifier for generating completions.
        n (int): The number of jokes to generate. Defaults to 1.

    Returns:
        List[str]: A list of generated jokes.
    """

    planner=PlanSearch(system_prompt=system_prompt,client=client,model=model)
    
    return planner.solve_multiple(context,n), planner.plansearch_completion_tokens

        



