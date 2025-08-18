import faiss
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from uuid import uuid4
import json, hashlib

user_prompt = input("Please enter: ")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

index = faiss.IndexFlatL2(len(embeddings.embed_query(user_prompt)))

vector_store = FAISS(
    embedding_function=embeddings,
    index=index,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={},
)


# Path to your JSON file
json_path = "Canadian_properties_50.json"

# Load the JSON
with open(json_path, "r", encoding="utf-8") as f:
    properties = json.load(f)

# Convert to LongChain Document objects
documents = []

for prop in properties:
    # 'page_content' is what embedding will be generated from
    page_content = prop['description']

    # "metadata" holds structured info for filtering
    metadata = {
        "location": prop["location"],
        "type": prop["type"],
        "nightly_price": prop["nightly_price"],
        "features": prop["features"],
        "tags": prop["tags"]
    }
    documents.append(Document(page_content=page_content, metadata=metadata))

uuids =[str(uuid4()) for _ in range(len(documents))]
vector_store.add_documents(documents=documents, ids=uuids)

retriever = vector_store.as_retriever(search_type="mmr", search_kmargs={"k": 5})
results = retriever.invoke(user_prompt, filter={})
for res in results:
    print(f"* [{res.metadata}]\n {res.page_content} ")