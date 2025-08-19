import json
import faiss
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.docstore import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from uuid import uuid4
import os
import openai
from dotenv import load_dotenv

load_dotenv(".env")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def similarity_search(preferred_environment,query_text,max_price, min_price,capacity):
    with open(os.path.abspath("../data/vacation_rentals_final.json"), "r", encoding="utf-8") as f:
        property_data = json.load(f)

    combined_query = f"{preferred_environment} {query_text}"
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

    dim = len(embeddings.embed_query(combined_query))
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
            f"group size: {property_item["capacity"]}\n"
            f"Price per night: {property_item.get('price_per_night', 'N/A')}\n"
        )

        client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )

        response = client.chat.completions.create(
            extra_body={},
            model="meta-llama/llama-3.3-70b-instruct:free",
            messages=[
                {"role": "system",
                        "content": "You are a helpful assistant that summarizes property listings."},
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=120,
            temperature=0.5,
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
                "group size": prop["capacity"],
                "price per night": prop["price_per_night"]
            }
        )
        for prop in property_data
    ]
    uuids = [str(uuid4()) for _ in range(len(documents))]

    vector_store.add_documents(documents=documents, ids=uuids)
    vector_store.save_local("faiss_index")
    initial_results = vector_store.similarity_search_with_score(combined_query, k=50)  # Similarity search function




    found = False
    for res in initial_results:  # since similarity_search_with_score returns (doc, score)
        price = res.metadata.get("price_per_night", 0)
        group_size = res.metadata.get("group_size", 0)

        if (min_price <= price <= max_price) and (group_size <= capacity):
            found = True
            # print summary + some metadata fields
            print(f"{res.page_content}\n{dict(list(res.metadata.items())[:3])}\n")

    if not found:
         print("Not Found")


similarity_search(preferred_environment="beach",query_text="I want to go to toronto",max_price=200, min_price=100, capacity=5)








