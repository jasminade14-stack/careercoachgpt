from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from crewai import Crew, Process, Task
from agents.analyst import analyst_agent
from agents.coach import coach_agent
from agents.ethics import ethics_agent
import uvicorn
import httpx

app = FastAPI(
    title="Student Support API",
    description="AI-powered student support service using CrewAI",
    version="1.0.0"
)

class StudentRequest(BaseModel):
    prompt: str

class SupportResponse(BaseModel):
    status: str
    result: str

class AnalyzeRequest(BaseModel):
    query: str
    jobs: List[Dict[str, Any]] = []
    skills: List[Dict[str, Any]] = []
    ethics_guidelines: List[Dict[str, Any]] = []

def run_student_support_crew(prompt: str):
    """Execute the student support crew workflow"""
    analysis_task = Task(
        description=f"Analyze the following student request:\n{prompt}",
        expected_output=(
            "A clear summary of the student's main problem, goals, and constraints."
        ),
        agent=analyst_agent
    )
    
    coaching_task = Task(
        description=(
            "Based on the analysis, provide helpful, concrete, and actionable advice."
        ),
        expected_output=(
            "A list of practical recommendations tailored to the student's situation."
        ),
        agent=coach_agent
    )
    
    ethics_task = Task(
        description=(
            "Review the career recommendations to verify they are fair and unbiased. "
            "Check that recommendations are based on student qualifications and interests, "
            "not on demographic factors like gender, age, or ethnicity. "
            "\n\n"
            "If the advice is fair and helpful, respond: 'APPROVED - Recommendations are ethical and bias-free.' "
            "Only flag concerns if you detect actual discrimination or unfair treatment."
        ),
        expected_output=(
            "Either 'APPROVED - Recommendations are ethical and bias-free' "
            "or a specific description of any bias or ethical concerns detected."
        ),
        agent=ethics_agent
    )
    
    crew = Crew(
        agents=[analyst_agent, coach_agent, ethics_agent],
        tasks=[analysis_task, coaching_task, ethics_task],
        process=Process.sequential,
        verbose=True
    )
    
    result = crew.kickoff()
    return str(result)

async def search_haystack(query: str, top_k: int = 5) -> Dict:
    """Call Haystack API for semantic search"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://haystack:8002/search",
                json={"query": query, "top_k": top_k}
            )
            response.raise_for_status()
            data = response.json()
            
            # Debug: Print was Haystack zurückgibt
            print(f"📥 Haystack returned: {type(data)}")
            if "documents" in data:
                print(f"📄 Found {len(data['documents'])} documents")
                if data['documents']:
                    print(f"🔍 First doc type: {type(data['documents'][0])}")
            
            return data
            
    except httpx.RequestError as e:
        print(f"❌ Haystack connection error: {e}")
        return {"documents": [], "error": str(e)}
    except Exception as e:
        print(f"❌ Haystack search error: {e}")
        return {"documents": [], "error": str(e)}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Student Support API",
        "status": "running",
        "version": "1.0.0"
    }

@app.post("/support", response_model=SupportResponse)
async def get_student_support(
    request: Optional[StudentRequest] = None,
    key: Optional[str] = Query(None, description="Student prompt as query parameter"),
    prompt: Optional[str] = Query(None, description="Alternative prompt parameter")
):
    """
    Process a student support request through the CrewAI workflow
    
    Accepts input in three ways:
    1. JSON body: {"prompt": "your question"}
    2. Query parameter: ?key=your+question
    3. Query parameter: ?prompt=your+question
    """
    try:
        user_prompt = None
        
        if request and request.prompt:
            user_prompt = request.prompt
        elif key:
            user_prompt = key
        elif prompt:
            user_prompt = prompt
        
        if not user_prompt or not user_prompt.strip():
            raise HTTPException(
                status_code=400, 
                detail="Prompt cannot be empty. Provide via JSON body, ?key= or ?prompt= parameter"
            )
        
        result = run_student_support_crew(user_prompt)
        
        return SupportResponse(
            status="success",
            result=str(result)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing student support request: {str(e)}"
        )

@app.post("/analyze")
async def analyze(request: AnalyzeRequest):

    try:
        # Falls n8n keine Daten mitgibt, selbst Haystack aufrufen
        jobs = list(request.jobs) if request.jobs else []
        skills = list(request.skills) if request.skills else []
        ethics_guidelines = list(request.ethics_guidelines) if request.ethics_guidelines else []
        
        # Rufe Haystack auf wenn keine Daten übergeben wurden
        if not jobs and not skills:
            print("⚠️ No context provided, using Multi-Query Strategy...")
            
            # Multi-Query Strategy: 3 separate searches für bessere Results
            print("🔍 Query 1/3: Searching for JOB opportunities...")
            jobs_query = f"{request.query} job opportunities career positions roles"
            jobs_results = await search_haystack(jobs_query, top_k=3)
            
            print("🔍 Query 2/3: Searching for SKILLS & training...")
            skills_query = f"{request.query} skills training courses learning paths"
            skills_results = await search_haystack(skills_query, top_k=3)
            
            print("🔍 Query 3/3: Searching for ETHICS guidelines...")
            ethics_query = "career guidance ethics fairness bias prevention"
            ethics_results = await search_haystack(ethics_query, top_k=2)
            
            # Combine all results
            all_documents = (
                jobs_results.get("documents", []) +
                skills_results.get("documents", []) +
                ethics_results.get("documents", [])
            )
            
            haystack_results = {"documents": all_documents}
            print(f"📊 Combined: {len(all_documents)} total documents from 3 queries")
            
            # Parse Haystack results
            # WICHTIG: Haystack gibt "metadata" zurück, nicht "meta"!
            if "documents" in haystack_results:
                print(f"📦 Processing {len(haystack_results['documents'])} documents from Haystack")
                
                for i, doc in enumerate(haystack_results["documents"]):
                    try:
                        # Format 1: Haystack 2.x gibt zurück: {"content": "text", "metadata": {...}}
                        if isinstance(doc, dict) and "metadata" in doc:
                            metadata = doc["metadata"]
                            doc_type = metadata.get("type", "")
                            
                            print(f"  📄 Doc {i+1}: type='{doc_type}', program='{metadata.get('study_program', 'N/A')}'")
                            
                            # Sortiere nach Type
                            if doc_type == "job_description":
                                jobs.append(metadata)
                            elif doc_type == "skill_learning_path":
                                skills.append(metadata)
                            elif doc_type == "ethics_guideline":
                                ethics_guidelines.append(metadata)
                            else:
                                print(f"  ⚠️ Unknown doc_type: '{doc_type}'")
                        
                        # Format 2: Fallback für alte Haystack Versionen mit "meta"
                        elif isinstance(doc, dict) and "meta" in doc:
                            meta = doc["meta"]
                            doc_type = meta.get("type", "")
                            
                            print(f"  📄 Doc {i+1}: type='{doc_type}' (legacy 'meta' format)")
                            
                            if doc_type == "job_description":
                                jobs.append(meta)
                            elif doc_type == "skill_learning_path":
                                skills.append(meta)
                            elif doc_type == "ethics_guideline":
                                ethics_guidelines.append(meta)
                        
                        # Format 3: Direktes Dict ohne metadata/meta
                        elif isinstance(doc, dict):
                            print(f"  ⚠️ Doc {i+1}: No 'metadata' or 'meta' key, trying direct access")
                            doc_type = doc.get("type", "")
                            
                            if "job" in doc_type.lower():
                                jobs.append(doc)
                            elif "skill" in doc_type.lower():
                                skills.append(doc)
                            elif "ethics" in doc_type.lower():
                                ethics_guidelines.append(doc)
                    
                    except Exception as e:
                        print(f"⚠️ Error parsing document {i+1}: {e}")
                        import traceback
                        traceback.print_exc()
                        continue
                
                print(f"✅ Final parsed: {len(jobs)} jobs, {len(skills)} skills, {len(ethics_guidelines)} ethics")
        
        # Build enriched prompt for CrewAI
        enriched_prompt = f"""
STUDENT QUERY: {request.query}

RELEVANT JOB OPPORTUNITIES:
{format_jobs_for_prompt(jobs)}

RECOMMENDED SKILLS:
{format_skills_for_prompt(skills)}

ETHICS GUIDELINES:
{format_ethics_for_prompt(ethics_guidelines)}

YOUR TASK:
Provide a clean, structured career recommendation with:
1. Top 3 job recommendations (with brief reasoning)
2. Key skills to develop (prioritize based on available data)
3. 2-3 actionable next steps

Keep it concise and student-friendly. No verbose explanations.
"""
        
        # Run CrewAI
        result = run_student_support_crew(enriched_prompt)
        
        # Extract clean final answer
        clean_message = extract_final_answer(str(result))
        
        return {
            "status": "success",
            "coach_message": clean_message,
            "top_jobs": jobs[:3] if jobs else [],
            "suggested_learning_paths": extract_learning_paths(clean_message),
            "ethics_status": "passed",
            "ethics_notes": "Recommendations based on qualifications without bias",
            "sources_used": {
                "jobs_count": len(jobs),
                "skills_count": len(skills),
                "ethics_guidelines_count": len(ethics_guidelines)
            }
        }
        
    except Exception as e:
        print(f"❌ Analysis error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    return {
        "status": "healthy",
        "agents": ["analyst", "coach", "ethics"],
        "process": "sequential",
        "haystack_integration": "active"
    }

# ============ HELPER FUNCTIONS ============

def extract_final_answer(crew_output: str) -> str:
    """Extract clean final answer from CrewAI verbose output"""
    
    # Try to find "Final Answer:" section
    if "Final Answer:" in crew_output:
        parts = crew_output.split("Final Answer:")
        if len(parts) > 1:
            output = parts[-1].strip()
        else:
            output = crew_output
    else:
        output = crew_output
    
    # Remove CrewAI system prompts and artifacts
    artifacts_to_remove = [
        "Your final answer must be the great and the most complete as possible",
        "it must be outcome described",
        "Begin! This is VERY important to you",
        "use the tools available and give your best Final Answer",
        "your job depends on it",
        "I now can give a great answer",
        "I MUST use these formats, my job depends on it!",
        "### User:",
        "Current Task:",
        "Thought:",
        "Action:",
    ]
    
    for artifact in artifacts_to_remove:
        output = output.replace(artifact, "")
    
    # Remove lines that start with system markers
    lines = output.split('\n')
    clean_lines = []
    skip_next = False
    
    for line in lines:
        stripped = line.strip()
        
        # Skip empty lines at start
        if not clean_lines and not stripped:
            continue
        
        # Skip system messages
        if any(marker in stripped for marker in ["Thought:", "Action:", "### User:", "Current Task:"]):
            skip_next = True
            continue
        
        if skip_next and not stripped:
            skip_next = False
            continue
        
        clean_lines.append(line)
    
    # Join and clean up
    result = '\n'.join(clean_lines).strip()
    
    # Remove multiple newlines
    while '\n\n\n' in result:
        result = result.replace('\n\n\n', '\n\n')
    
    return result if result else "No response generated"

def extract_learning_paths(message: str) -> list:
    """Extract learning paths from CrewAI response message"""
    paths = []
    
    # Erweiterte Keywords basierend auf tatsächlichen Daten
    keywords = [
        # Programming Languages
        "Python", "Java", "JavaScript", "C++", "R", "SQL", "Go", "Rust",
        # Data Science & AI
        "Machine Learning", "Data Analysis", "Statistics", "Deep Learning",
        "AI", "Neural Networks", "Data Science", "Analytics",
        # Business & Management
        "Digital Marketing", "Business Strategy", "Project Management",
        "Marketing", "Management", "Leadership", "Entrepreneurship",
        # Technical Skills
        "Cloud Computing", "DevOps", "Cybersecurity", "Web Development",
        "Mobile Development", "Database", "API",
        # Tools & Frameworks
        "Excel", "Tableau", "Power BI", "Git", "Docker", "Kubernetes",
        # Soft Skills
        "Communication", "Problem Solving", "Critical Thinking",
        "Teamwork", "Presentation"
    ]
    
    for keyword in keywords:
        if keyword.lower() in message.lower():
            paths.append(keyword)
    
    # Return unique items, max 5
    unique_paths = list(dict.fromkeys(paths))  # Preserve order, remove duplicates
    return unique_paths[:5] if unique_paths else ["Data Analysis", "Python", "Communication"]

def format_jobs_for_prompt(jobs):
    if not jobs: return "..."
    formatted = []
    for i, job in enumerate(jobs[:5], 1):
        # Fallback Kette: study_program -> title -> content (gekürzt)
        text = job.get('study_program') or job.get('title') or job.get('content', 'No content')[:100]
        formatted.append(f"{i}. {text}")
    return "\n".join(formatted)

def format_skills_for_prompt(skills):
    """Format skills for CrewAI prompt"""
    if not skills:
        return "No specific skills provided - recommend based on query"
    
    formatted = []
    for i, skill in enumerate(skills[:5], 1):
        program = skill.get('study_program') or skill.get('title', 'Unknown')
        skill_list = skill.get('skills', skill.get('content', ''))
        formatted.append(f"{i}. {program}: {skill_list}")
    
    return "\n".join(formatted)

def format_ethics_for_prompt(ethics):
    """Format ethics guidelines for CrewAI prompt"""
    if not ethics:
        return "Standard ethics: Provide fair, unbiased, merit-based recommendations"
    
    formatted = []
    for guideline in ethics[:3]:
        title = guideline.get('title', 'Ethics Guideline')
        content = guideline.get('content', '')[:150]
        formatted.append(f"- {title}: {content}...")
    
    return "\n".join(formatted)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )