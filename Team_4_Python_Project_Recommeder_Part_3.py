# -*- coding: utf-8 -*-

!pip install -qU langchain faiss-cpu langchain-openai

import getpass
import os
from uuid import uuid4

from langchain.embeddings import AzureOpenAIEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain.schema import Document  # updated import for Document

# Azure API Setup
if not os.environ.get("AZURE_OPENAI_API_KEY"):
    os.environ["AZURE_OPENAI_API_KEY"] = getpass.getpass("Enter Azure API key: ")

embeddings = AzureOpenAIEmbeddings(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    openai_api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2023-03-15-preview")
)

# Generate FAISS index
index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world")))

vector_store = FAISS(
    embedding_function=embeddings,
    index=index,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={}
)
# Sample property data (replace with your actual data)
property_data = [
    {
        "location": "Toronto",
        "type": "Apartment",
        "features": ["wifi", "kitchen", "balcony"],
        "tags": ["cozy", "central"],
        "nightly_price": 120,
    },
    {
        "location": "Montreal",
        "type": "Condo",
        "features": ["parking", "pool"],
        "tags": ["modern", "bright"],
        "nightly_price": 200,
    },
 
]


def gen_page_content(prop):
    location = prop["location"]
    prop_type = prop["type"]
    features_text = ", ".join(prop["features"])
    tags_text = ", ".join(prop["tags"])
    return f"{tags_text} {location} {prop_type} with {features_text} experiences."

documents = [
    Document(
        page_content=gen_page_content(prop),
        metadata={
            "prop_type": prop["type"]
            "feature": prop["features"],
            "location": prop["location"],
            "tags": prop["tags"]
        }
    )
    #how would metadata affect fit score, what is user preference 
    for prop in property_data
]

uuids = [str(uuid4()) for _ in range(len(documents))]
vector_store.add_documents(documents=documents, ids=uuids)

# User input (example)
user = {
    "user_id": "U01",
    "name": "Keqing",
    "group_size": 2,
    "preferred_environment": "urban",
    "budget_min": 100,
    "budget_max": 150,
    "travel_dates":{
        "start":"2025-09-24",
        "end": "2025-09-25"
    }
}

query_text = "Looking for a cozy apartment with wifi and balcony"

# Similarity search
raw_results = vector_store.similarity_search_with_score(query_text, k=10)

# Filter by environment
filtered_results = [
    (doc, score) for doc, score in raw_results
    if doc.metadata.get("tags") == user["preferred_environment"]
]

# Apply budget filter
final_results = [
    (doc, score) for doc, score in filtered_results
    if user["budget_min"] <= doc.metadata.get("nightly_price", 0) <= user["budget_max"]
]

# Print results
print("Recommended properties:")
for doc, score in final_results:
    print(f"* [SIM={score:.3f}] {doc.page_content} | Price: {doc.metadata['nightly_price']}")
