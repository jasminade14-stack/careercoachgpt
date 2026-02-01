import json
import requests

# Weaviate Configuration
WEAVIATE_URL = "http://localhost:8080"

# Step 1: Create Schemas
print("📝 Creating schemas...")

schemas = [
    {
        "class": "JobDescription",
        "vectorizer": "text2vec-openai",
        "moduleConfig": {
            "text2vec-openai": {
                "model": "text-embedding-3-small",
                "vectorizeClassName": False
            }
        },
        "properties": [
            {"name": "jobId", "dataType": ["text"]},
            {"name": "studyProgram", "dataType": ["text"]},
            {"name": "degree", "dataType": ["text"]},
            {"name": "roles", "dataType": ["text"]},
            {"name": "responsibilities", "dataType": ["text"]},
            {"name": "requirements", "dataType": ["text"]},
            {"name": "domain", "dataType": ["text"]},
            {"name": "source", "dataType": ["text"]}
        ]
    },
    {
        "class": "SkillLearningPath",
        "vectorizer": "text2vec-openai",
        "moduleConfig": {
            "text2vec-openai": {
                "model": "text-embedding-3-small",
                "vectorizeClassName": False
            }
        },
        "properties": [
            {"name": "skillId", "dataType": ["text"]},
            {"name": "studyProgram", "dataType": ["text"]},
            {"name": "degree", "dataType": ["text"]},
            {"name": "skills", "dataType": ["text"]},
            {"name": "learningPaths", "dataType": ["text"]},
            {"name": "domain", "dataType": ["text"]},
            {"name": "source", "dataType": ["text"]}
        ]
    },
    {
        "class": "EthicsGuideline",
        "vectorizer": "text2vec-openai",
        "moduleConfig": {
            "text2vec-openai": {
                "model": "text-embedding-3-small",
                "vectorizeClassName": False
            }
        },
        "properties": [
            {"name": "ethicsId", "dataType": ["text"]},
            {"name": "title", "dataType": ["text"]},
            {"name": "content", "dataType": ["text"]},
            {"name": "category", "dataType": ["text"]},
            {"name": "domain", "dataType": ["text"]},
            {"name": "source", "dataType": ["text"]}
        ]
    }
]

for schema in schemas:
    try:
        response = requests.post(f"{WEAVIATE_URL}/v1/schema", json=schema)
        if response.status_code == 200:
            print(f"✅ Created schema: {schema['class']}")
        else:
            print(f"⚠️  Schema {schema['class']} might already exist")
    except Exception as e:
        print(f"❌ Error creating schema {schema['class']}: {e}")

# Step 2: Import Data
print("\n📦 Importing data...")

# Load JSON files
with open('job_descriptions_all_programs.json', 'r', encoding='utf-8') as f:
    job_descriptions = json.load(f)

with open('skills_learning_paths.json', 'r', encoding='utf-8') as f:
    skills_learning = json.load(f)

with open('ethics_fairness_guidelines.json', 'r', encoding='utf-8') as f:
    ethics_guidelines = json.load(f)

# Import Job Descriptions
print(f"\n📄 Importing {len(job_descriptions)} job descriptions...")
for job in job_descriptions:
    try:
        obj = {
            "class": "JobDescription",
            "properties": {
                "jobId": job["id"],
                "studyProgram": job["study_program"],
                "degree": job["degree"],
                "roles": job["roles"],
                "responsibilities": job["responsibilities"],
                "requirements": job["requirements"],
                "domain": job["domain"],
                "source": job["source"]
            }
        }
        response = requests.post(f"{WEAVIATE_URL}/v1/objects", json=obj)
        if response.status_code == 200:
            print(f"✅ Imported job: {job['id']}")
        else:
            print(f"❌ Failed to import {job['id']}: {response.text}")
    except Exception as e:
        print(f"❌ Error importing {job['id']}: {e}")

# Import Skills & Learning Paths
print(f"\n📚 Importing {len(skills_learning)} skills & learning paths...")
for skill in skills_learning:
    try:
        obj = {
            "class": "SkillLearningPath",
            "properties": {
                "skillId": skill["id"],
                "studyProgram": skill["study_program"],
                "degree": skill["degree"],
                "skills": skill["skills"],
                "learningPaths": skill["learning_paths"],
                "domain": skill["domain"],
                "source": skill["source"]
            }
        }
        response = requests.post(f"{WEAVIATE_URL}/v1/objects", json=obj)
        if response.status_code == 200:
            print(f"✅ Imported skill: {skill['id']}")
        else:
            print(f"❌ Failed to import {skill['id']}: {response.text}")
    except Exception as e:
        print(f"❌ Error importing {skill['id']}: {e}")

# Import Ethics Guidelines
print(f"\n⚖️  Importing {len(ethics_guidelines)} ethics guidelines...")
for ethics in ethics_guidelines:
    try:
        obj = {
            "class": "EthicsGuideline",
            "properties": {
                "ethicsId": ethics["id"],
                "title": ethics["title"],
                "content": ethics["content"],
                "category": ethics["category"],
                "domain": ethics["domain"],
                "source": ethics["source"]
            }
        }
        response = requests.post(f"{WEAVIATE_URL}/v1/objects", json=obj)
        if response.status_code == 200:
            print(f"✅ Imported ethics: {ethics['id']}")
        else:
            print(f"❌ Failed to import {ethics['id']}: {response.text}")
    except Exception as e:
        print(f"❌ Error importing {ethics['id']}: {e}")

# Step 3: Verify Import
print("\n🔍 Verifying import...")

classes = ["JobDescription", "SkillLearningPath", "EthicsGuideline"]
for class_name in classes:
    try:
        response = requests.get(f"{WEAVIATE_URL}/v1/objects?class={class_name}&limit=1")
        if response.status_code == 200:
            count = len(response.json().get("objects", []))
            print(f"✅ {class_name}: Objects found")
        else:
            print(f"⚠️  {class_name}: Could not verify")
    except Exception as e:
        print(f"❌ Error verifying {class_name}: {e}")

print("\n🎉 Import completed!")
print("\nNext steps:")
print("1. Verify in browser: http://localhost:8080/v1/schema")
print("2. Test semantic search via Haystack")
print("3. Integrate with CrewAI agents")