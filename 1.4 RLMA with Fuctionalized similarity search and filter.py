from uuid import uuid4
import faiss
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
import tkinter as tk
from tkinter import simpledialog
from tabulate import tabulate


# 1. Input data (dictionary format)

users = [
    {"user_id": 1, "username": "ethan123", "password": "password", "name": "Ethan",
     "group_size": 5, "preferred_env": "Tropical", "min_price": 100.0, "max_price": 1000.0,
     "created_at": "2025-08-15 18:06:10"},
    {"user_id": 2, "username": "sophia2", "password": "password", "name": "Sophia",
     "group_size": 2, "preferred_env": "Mountain", "min_price": 50.0, "max_price": 500.0,
     "created_at": "2025-08-16 10:12:00"}
]

property_data = [
    {"property_id": 900, "location": "Victoria Gardens", "type": "chalet", "price_per_night": 198,
     "capacity": 4, "features": ["pool", "ski-in", "pet-friendly"],
     "tags": ["historic", "adventure", "summer escape", "nightlife", "family-friendly"],
     "description": "Built with comfort in mind. Whether for work or rest, it meets your needs."},
    {"property_id": 901, "location": "Banff Village", "type": "loft", "price_per_night": 119,
     "capacity": 3, "features": ["sauna", "balcony", "parking", "fireplace"],
     "tags": ["budget", "luxury", "nature", "family-friendly"],
     "description": "Calm spot with easy access to nature. Simple, serene, and special."}
]


# 2. Vector store setup
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
dim = len(embeddings.embed_query("hello world"))
index = faiss.IndexFlatL2(dim)

vector_store = FAISS(
    embedding_function=embeddings,
    index=index,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={},
)


def create_page_content(property_item):
    location = property_item["location"]
    types = property_item["type"]
    features_text = ", ".join(property_item["features"])
    tags_text = ", ".join(property_item["tags"])
    return f"Our top {tags_text} {location} {types} with {features_text} experiences."


documents = [
    Document(
        page_content=create_page_content(prop),
        metadata={
            "property_id": prop["property_id"],
            "location": prop["location"],
            "type": prop["type"],
            "features": prop["features"],
            "tags": prop["tags"],
            "price_per_night": prop["price_per_night"],
            "capacity": prop["capacity"]
        }
    ) for prop in property_data
]

uuids = [str(uuid4()) for _ in range(len(documents))]
vector_store.add_documents(documents=documents, ids=uuids)



# 3. Functionalized search + filter

# Functionalized Similarity Search with appended user preferred_env and group_size & budget filter
def search_properties(query_text, user, vector_store, top_k=50):
    """Search properties using similarity and filter by user budget and group size."""
    combined_query = f"{user['preferred_env']} {query_text}"
    initial_results = vector_store.similarity_search_with_score(combined_query, k=top_k)

    def filter_property(prop):
        price = prop.metadata.get("price_per_night", 0)
        capacity = prop.metadata.get("capacity", 0)
        return user["min_price"] <= price <= user["max_price"] and capacity >= user["group_size"]

    filtered_results = [(res, score) for res, score in initial_results if filter_property(res)]
    filtered_results.sort(key=lambda x: x[1])  # sort by similarity score
    return filtered_results

#4. Print table for display
def format_tabulate_for_display(filtered_results, top_n=10):
    #Convert filtered results to tabulate-ready table.
    table_data = []
    for rank, (res, score) in enumerate(filtered_results[:top_n], start=1):
        table_data.append([
            res.metadata["property_id"],
            res.metadata["location"],
            res.metadata.get("type", ""),
            res.metadata["price_per_night"],
            res.metadata.get("capacity", ""),
            ", ".join(res.metadata.get("features", [])),
            ", ".join(res.metadata.get("tags", [])),
            rank
        ])
    return table_data

# Pick a user programmatically (no popup)
current_user = users[0]  # for example, Ethan

# The only input is query_text
query_text = "beachfront adventure"

filtered_results = search_properties(query_text, current_user, vector_store)
table_data = format_tabulate_for_display(filtered_results)

print(tabulate(
    table_data,
    headers=["ID", "Location", "Type", "Price", "Capacity", "Features", "Tags", "Recommendation"],
    tablefmt="grid"
))
for res, score in filtered_results[:10]:
    print(f"* [SIM={score:.3f}] {res.page_content}")