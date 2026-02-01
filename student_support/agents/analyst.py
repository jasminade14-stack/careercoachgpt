from crewai import Agent
from crewai.llm import LLM

llm = LLM(
    model="ollama/llama3.2:3b",   # Prefix für Provider
    api_base="http://ollama:11434" 
)


analyst_agent = Agent(
    role="Analyst Agent",
    goal="Extract key student interests and skills from the input",
    backstory=(
        "You are a precise data analyst. Your only task is to extract "
        "facts, skills, and interests from the student's request and "
        "list them clearly for the next agent."
    ),
    llm=llm,
    verbose=False,        # Disable logging to speed up execution 
    max_iter=1
)
