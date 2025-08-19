import json
import requests, getpass
import faiss
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from uuid import uuid4


def similarity_search(preferened_environment,query_text,max_price, min_price):
    with open("../data/vacation_rentals_final.json", "r", encoding="utf-8") as f:
        property_data = json.load(f)

    combined_query = f"{preferened_environment} {query_text}"
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
        # Airbnb 的风格，简洁描述
        return f"Our top {tags_text} {location} {types} with {features_text} experiences."

    documents = [
        Document(
            page_content=create_page_content(prop),  # 将整个属性数据作为 page_content
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

    top_results = []
    for doc, score in filtered_results:
        item = dict(doc.metadata)
        item["description"] = doc.page_content
        item["similarity"] = float(score)
        top_results.append(item)
    print(top_results)

    return top_results

