import os
import json
import time
import faiss
import requests
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.docstore import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from uuid import uuid4



"""
Takes in the property details and has Llama 4 generate a summary for the listing.
"""
def create_page_content(property_item):
    time.sleep(3)
    # Initialize prompt and details for building the summary
    prompt = (
        f"Summarize the following property for a vacation rental listing:\n"
        f"Location: {property_item['location']}\n"
        f"Type: {property_item['type']}\n"
        f"Features: {', '.join(property_item['features'])}\n"
        f"Tags: {', '.join(property_item['tags'])}\n"
        f"group size: {property_item['capacity']}\n"
        f"Price per night: {property_item.get('price_per_night', 'N/A')}\n"
    )
    # URL information and data payload for the request
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
     }
    # Base model name and message is all that is needed
    data = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    # Makes the post request and retrieves the summary
    response = requests.post(url, headers=headers, json=data)
    summary = response.json()["choices"].pop()["message"]["content"]
    return summary



"""
Creates the FAISS index and saves it locally.
"""
def create_embeddings():
    # Read in the listings 
    with open(os.path.abspath("../data/vacation_rentals_final.json"), "r", encoding="utf-8") as f:
        property_data = json.load(f)
    # Initialize embedding model
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2",
                                        model_kwargs={"device": "cpu"})
    # Get index size 
    dim = len(embeddings.embed_query("test"))
    index = faiss.IndexFlatL2(dim)
    # Create FAISS object
    vector_store = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={},
    )
    # Create list of documents to embedd with appropriate metadata
    documents = [
        Document(
            page_content=create_page_content(prop),
            metadata={
                "property_id": prop["property_id"],
                "location": prop["location"],
                "type": prop["type"],
                "features": prop["features"],
                "tags": prop["tags"],
                "group size": prop["capacity"],
                "price per night": prop["price_per_night"]
            }
        )
        for prop in property_data
    ]
    uuids = [str(uuid4()) for _ in range(len(documents))]
    # Embed and save
    vector_store.add_documents(documents=documents, ids=uuids)
    vector_store.save_local("faiss_index")



def similarity_search(pref_env="Tropical", query_text="Beach House", max_price=500, min_price=100, capacity=4):
    # Listings retrieved
    top_n = []
    # Combine users query alongside their preferences
    combined_query = f"{pref_env} {query_text}"
    # Initialize embedding model
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    # Get reference length
    dim = len(embeddings.embed_query(combined_query))
    index = faiss.IndexFlatL2(dim)
    # Check if vector store
    if not os.path.exists("../data/faiss_index"):
        create_embeddings() 
    # Load in local vector stor
    vector_store = FAISS.load_local(
        "../data/faiss_index", 
        embeddings, 
        allow_dangerous_deserialization=True
    )
    # Get the initial 50 matches and filter based on price and capacity
    initial_results = vector_store.similarity_search_with_score(combined_query, k=50)
    for item in initial_results:
        res = item[0]
        price = res.metadata.get("price per night", 0)
        group_size = res.metadata.get("group size", 0)
        if (min_price <= price <= max_price) and (capacity <= group_size):
            top_n.append(res)
    return top_n
