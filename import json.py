import json

# 打开并读取 JSON 文件

import os
print(os.getcwd())
with open("C:\Users\wkq02\OneDrive - University of Toronto\桌面\你该死了\Canadian_properties_50.json", "r", encoding="utf-8") as file:
    properties = json.load(file)

with open("Canadian_properties_50.json", "r", encoding="utf-8") as file:
    properties = json.load(file)

with open("Canadian_properties_50.json", "r", encoding="utf-8") as file:
    properties = json.load(file)


for prop in properties[:5]:
    print(f"ID: {prop['property_id']}, Location: {prop['location']}, Price: {prop['nightly_price']}")
from uuid import uuid4

import faiss
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

with open("Canadian_properties_50.json", "r", encoding="utf-8") as f:
    property_data = json.load(f)

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
            "nightly_price": prop["nightly_price"]
        }
    )
    for prop in property_data
]
uuids = [str(uuid4()) for _ in range(len(documents))]
vector_store.add_documents(documents=documents, ids=uuids)

import json
import tkinter as tk
from tkinter import simpledialog
from tkinter import scrolledtext
from tabulate import tabulate

root = tk.Tk()
root.withdraw()  # 隐藏主窗口

# 加载用户数据
with open("canadian_users_50.json", "r", encoding="utf-8") as f:
    users = json.load(f)

# 弹窗让用户输入 user_id
user_id_input = simpledialog.askstring("用户登录", "请输入你的用户ID：")

# 查找对应的用户
current_user = next((u for u in users if u["user_id"] == user_id_input), None)

if not current_user:
    print("未找到该用户！")
else:
    while True:
        # 弹窗获取查询文本
        query_text = simpledialog.askstring("搜索", "请输入查询内容（取消或空文本退出）：")
        if not query_text:
            print("用户取消搜索，程序结束。")
            break  # 用户取消或输入空文本则退出循环

        # 相似度搜索
        initial_results = vector_store.similarity_search_with_score(query_text, k=50) # Similarity search function

        # 按用户预算过滤
        def filter_properties_by_user(prop, user):
            price = prop.metadata.get("nightly_price", 0)
            return user["budget_min"] <= price <= user["budget_max"]

        filtered_results = [(res, score) for res, score in initial_results if filter_properties_by_user(res, current_user)]
        filtered_results = filtered_results[:10] # Display top 10 results
        filtered_results.sort(key=lambda x: x[1])
        # 打印搜索结果
        for res, score in filtered_results:
            print(f"* [SIM={score:.3f}] {res.page_content}")
        print()



import requests, getpass

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "deepseek/deepseek-chat"  # try alternatives if needed

# Safely input your key (won't echo in Colab)
API_KEY = getpass.getpass("Enter your OpenRouter API key (input is hidden): ").strip()
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

SYSTEM_PROMPT = (
    "You are a helpful assistant for an Airbnb-like vacation property search. "
    "Given PROPERTIES (JSON) and a USER REQUEST, return JSON with keys: "
    "'tags' (list[str]) and optionally 'property_ids' (list[int]). Return ONLY valid JSON."
)

def llm_search(properties, user_prompt, model, temperature):
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "PROPERTIES:\n" + json.dumps(properties) +
                    "\n\nUSER REQUEST:\n" + user_prompt +
                    "\n\nRespond ONLY with JSON: {\"tags\": [...], \"property_ids\": [...]}"
                ),
            },
        ],
        "temperature": temperature,
    }
    r = requests.post(OPENROUTER_URL, headers=HEADERS, json=payload, timeout=60)
    if r.status_code != 200:
        return {"error": f"HTTP {r.status_code}", "details": r.text}
    data = r.json()
    content = (data.get("choices") or [{}])[0].get("message", {}).get("content")
    if not content:
        return {"error": "Empty response", "raw": data}
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Fallback: try to extract JSON substring
        s, e = content.find("{"), content.rfind("}")
        if s != -1 and e != -1 and e > s:
            try:
                return json.loads(content[s:e+1])
            except json.JSONDecodeError:
                return {"error": "Non-JSON content", "raw": content}
        return {"error": "Non-JSON content", "raw": content}

# Example single-turn usage (optional quick test)
example_request = "Cozy place by the lake with a fireplace under $220"
subset = properties[:12]  # send fewer for cheaper tokens
print("Querying model... (uses your API key)")
resp = llm_search(subset, example_request, model = MODEL, temperature=0.7)
print(resp)