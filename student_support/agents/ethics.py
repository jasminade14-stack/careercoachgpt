from crewai import Agent
from crewai.llm import LLM

llm = LLM(
    model="ollama/llama3.2:3b",
    api_base="http://ollama:11434"   
)


ethics_agent = Agent(
    role="Ethics Guidance Support",
    goal="Ensure recommendations are constructive and helpful for the student",
    backstory=(
        "You are a supportive career mentor. Your job is to verify that the "
        "advice provided is encouraging and focuses on student strengths. "
        "Simply confirm that the advice is helpful and provides positive direction."
    ),
    llm=llm,
    verbose=False,
    max_iter=1
)
   