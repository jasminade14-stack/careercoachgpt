import json
import os
from haystack import Document
from haystack_integrations.document_stores.weaviate import WeaviateDocumentStore

# Base path für Daten
DATA_DIR = '/app/haystack/data'

# Weaviate Configuration für Haystack 2.x
print("🔗 Connecting to Weaviate...")

document_store = WeaviateDocumentStore(
    url="http://weaviate:8080"
)

print("✅ Connected to Weaviate")

# Load JSON files
print("\n📂 Loading JSON files...")

with open(os.path.join(DATA_DIR, 'job_descriptions_all_programs.json'), 'r', encoding='utf-8') as f:
    job_descriptions = json.load(f)

with open(os.path.join(DATA_DIR, 'skills_learning_paths.json'), 'r', encoding='utf-8') as f:
    skills_learning = json.load(f)

with open(os.path.join(DATA_DIR, 'ethics_fairness_guidelines.json'), 'r', encoding='utf-8') as f:
    ethics_guidelines = json.load(f)

print(f"✅ Loaded {len(job_descriptions)} job descriptions")
print(f"✅ Loaded {len(skills_learning)} skills & learning paths")
print(f"✅ Loaded {len(ethics_guidelines)} ethics guidelines")

# Convert to Haystack Documents
print("\n📄 Converting to Haystack documents...")

documents = []

# Job Descriptions
for job in job_descriptions:
    doc = Document(
        content=f"Study Program: {job['study_program']} ({job['degree']})\nRoles: {job['roles']}\nResponsibilities: {job['responsibilities']}\nRequirements: {job['requirements']}",
        meta={
            "type": "job_description",
            "id": job["id"],
            "study_program": job["study_program"],
            "degree": job["degree"],
            "roles": job["roles"],
            "domain": job["domain"],
            "source": job["source"]
        }
    )
    documents.append(doc)

print(f"  ✅ Converted {len(job_descriptions)} job descriptions")

# Skills & Learning Paths
for skill in skills_learning:
    doc = Document(
        content=f"Study Program: {skill['study_program']} ({skill['degree']})\nSkills: {skill['skills']}\nLearning Paths: {skill['learning_paths']}",
        meta={
            "type": "skill_learning_path",
            "id": skill["id"],
            "study_program": skill["study_program"],
            "degree": skill["degree"],
            "skills": skill["skills"],
            "domain": skill["domain"],
            "source": skill["source"]
        }
    )
    documents.append(doc)

print(f"  ✅ Converted {len(skills_learning)} skills & learning paths")

# Ethics Guidelines
for ethics in ethics_guidelines:
    doc = Document(
        content=f"Title: {ethics['title']}\nContent: {ethics['content']}\nCategory: {ethics['category']}",
        meta={
            "type": "ethics_guideline",
            "id": ethics["id"],
            "title": ethics["title"],
            "category": ethics["category"],
            "domain": ethics["domain"],
            "source": ethics["source"]
        }
    )
    documents.append(doc)

print(f"  ✅ Converted {len(ethics_guidelines)} ethics guidelines")
print(f"\n✅ Total documents created: {len(documents)}")

# Write to Weaviate
print("\n📥 Writing documents to Weaviate...")

try:
    document_store.write_documents(documents)
    print(f"✅ Successfully imported {len(documents)} documents to Weaviate!")
except Exception as e:
    print(f"❌ Error writing documents: {e}")
    import traceback
    traceback.print_exc()

# Verify
print("\n🔍 Verifying import...")
try:
    count = document_store.count_documents()
    print(f"✅ Total documents in Weaviate: {count}")
except Exception as e:
    print(f"⚠️  Could not verify count: {e}")

print("\n🎉 Import completed!")
print("\nDocument breakdown:")
print(f"  - Job Descriptions: {len(job_descriptions)}")
print(f"  - Skills & Learning Paths: {len(skills_learning)}")
print(f"  - Ethics Guidelines: {len(ethics_guidelines)}")
print(f"  - Total: {len(documents)}")
print("\nNext steps:")
print("1. Test semantic search via Haystack pipeline")
print("2. Integrate with n8n workflow")
print("3. Connect to CrewAI agents")