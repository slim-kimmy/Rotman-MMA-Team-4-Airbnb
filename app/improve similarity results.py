import os
os.chdir(r"C:\Users\wkq02\OneDrive - University of Toronto\桌面\你该死了")
import json
from uuid import uuid4
import faiss
import numpy as np
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
import tkinter as tk
from tkinter import simpledialog
import nltk
from nltk.corpus import wordnet

nltk.download('wordnet')  # 如果没下载过，取消注释运行一次

# -------------------- 加载数据 --------------------
with open("Canadian_properties_50.json", "r", encoding="utf-8") as f:
    property_data = json.load(f)
with open("canadian_users_50.json", "r", encoding="utf-8") as f:
    users = json.load(f)

# -------------------- Embeddings --------------------
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
dim = len(embeddings.embed_query("hello world"))

# -------------------- FAISS + 归一化 --------------------
index = faiss.IndexFlatIP(dim)


def normalize_vectors(vectors):
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / norms


# -------------------- 创建文档 --------------------
def create_page_content(prop):
    features_text = ", ".join(prop["features"])
    tags_text = ", ".join(prop["tags"])
    return f"Our top {tags_text} {prop['location']} {prop['type']} with {features_text} experiences. Price:{prop['nightly_price']} CAD/night."


documents = [
    Document(
        page_content=create_page_content(prop),
        metadata={
            "property_id": prop["property_id"],
            "location": prop["location"],
            "tags": prop["tags"],
            "features": prop["features"],
            "nightly_price": prop["nightly_price"]
        }
    )
    for prop in property_data
]

doc_vectors = normalize_vectors(
    np.array([embeddings.embed_query(doc.page_content) for doc in documents], dtype='float32'))
index.add(doc_vectors)

vector_store = FAISS(
    embedding_function=embeddings,
    index=index,
    docstore=InMemoryDocstore({doc.metadata["property_id"]: doc for doc in documents}),
    index_to_docstore_id={i: doc.metadata["property_id"] for i, doc in enumerate(documents)},
)

# -------------------- 用户交互 --------------------
root = tk.Tk()
root.withdraw()

user_id_input = simpledialog.askstring("用户登录", "请输入你的用户ID：")
current_user = next((u for u in users if u["user_id"] == user_id_input), None)

if not current_user:
    print("未找到该用户！")
else:
    query_text = simpledialog.askstring("请输入", "请输入查询内容：")
    if query_text:
        # 同义词扩展
        def expand_query(query):
            return list({lemma.name().replace("_", " ")
                         for word in query.split()
                         for syn in wordnet.synsets(word)
                         for lemma in syn.lemmas()} | set(query.split()))


        query_vecs = normalize_vectors(
            np.array([embeddings.embed_query(w) for w in expand_query(query_text)], dtype='float32'))

        # 累积搜索结果
        results = {}
        for qv in query_vecs:
            D, I = index.search(np.array([qv]), k=20)
            for score, i in zip(D[0], I[0]):
                doc = documents[i]
                pid = doc.metadata["property_id"]
                if pid not in results or score > results[pid][0]:
                    results[pid] = (score, doc)

        # 价格过滤 + 排序 + 前5
        filtered = sorted([(doc, s) for s, doc in results.values()
                           if
                           current_user["budget_min"] <= doc.metadata["nightly_price"] <= current_user["budget_max"]],
                          key=lambda x: x[1], reverse=True)[:5]

        # 输出
        print(f"\n用户 {current_user['name']} 的搜索结果：")
        for doc, score in filtered:
            print(f"* [SIM={score:.3f}] {doc.page_content}")
