import json
import requests, getpass
import faiss
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.docstore import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from uuid import uuid4
import os
import openai
from dotenv import load_dotenv

file_path = r"C:\Users\vicky\Rotman-MMA-Team-4-Airbnb\api\data\vacation_rentals_final.json"


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# print(os.getenv("OPENAI_API_KEY"))

def similarity_search(preferred_environment,query_text,max_price, min_price):
    with open(file_path, "r", encoding="utf-8") as f:
        property_data = json.load(f)


    combined_query = f"{preferred_environment} {query_text}"
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
        # Use OpenAI's API to summarize the property details
        prompt = (
            f"Summarize the following property for a vacation rental listing:\n"
            f"Location: {property_item['location']}\n"
            f"Type: {property_item['type']}\n"
            f"Features: {', '.join(property_item['features'])}\n"
            f"Tags: {', '.join(property_item['tags'])}\n"
            f"Price per night: {property_item.get('price_per_night', 'N/A')}\n"
        )

        client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENAI_API_KEY,
        )

        response = client.chat.completions.create(
            extra_body={},
            model="nousresearch/deephermes-3-llama-3-8b-preview:free",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that summarizes property listings. Provide concise and engaging summaries that highlight key features and appeal to potential renters."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        summary = response.choices[0].message.content.strip()
        return summary

    documents = [
        Document(
            page_content=create_page_content(prop),  
            metadata={
                "property_id": prop["property_id"],
                "location": prop["location"],
                "type": prop["type"],
                "features": prop["features"],
                "tags": prop["tags"],
                "price_per_night": prop["price_per_night"]
            }
        )
        for prop in property_data
    ]
    uuids = [str(uuid4()) for _ in range(len(documents))]
    vector_store.add_documents(documents=documents, ids=uuids)

    initial_results = vector_store.similarity_search_with_score(combined_query, k=50)  # Similarity search function


    def filter_properties_by_user(prop):
        price = prop.metadata.get("price_per_night", 0)
        return min_price <= price <= max_price

    filtered_results = [(res, score) for res, score in initial_results if
                                filter_properties_by_user(res)]
    filtered_results = filtered_results[:10]  # Display top 10 results

    for res, score in filtered_results:
        print(f"* [SIM={score:.3f}] {res.page_content}")
        print()
    pass



similarity_search("beach","I want go to toronto",200,100)

