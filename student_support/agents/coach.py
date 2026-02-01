from crewai import Agent
from crewai.llm import LLM

llm = LLM(
    model="ollama/llama3.2:3b",   # Prefix für Provider
    api_base="http://ollama:11434"
)


coach_agent = Agent(
    role="Career Coach",
    goal="Provide specific job and learning path recommendations based on student interests and retrieved job data",
    backstory=(
        "You are a career counselor. Use provided job matches to suggest: "
        "1. Specific job roles. 2. Skills to develop. 3. Next steps. "
        "Keep it extremely concise."
    ),
    llm=llm,
    verbose=False,
    max_iter=1
)                                                                                            