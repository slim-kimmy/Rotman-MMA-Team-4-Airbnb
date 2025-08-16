import json

# 打开并读取 JSON 文件
with open("Canadian_properties_50.json", "r", encoding="utf-8") as file:
    properties = json.load(file)
    
import json
from uuid import uuid4
import faiss
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

with open("Canadian_properties_50.json", "r", encoding="utf-8") as f:
    property_data = json.load(f)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

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
    nightly_prices = property_item["nightly_price"]
    # 拼接 features 和 tags
    features_text = ", ".join(property_item["features"])
    tags_text = ", ".join(property_item["tags"])
    # Airbnb 的风格，简洁描述
    return f"Our top {tags_text} {location} {types} with {features_text} experiences. Price:{nightly_prices} CAD/night."

documents = [
    Document(
        page_content=create_page_content(prop),  # 将整个属性数据作为 page_content
        metadata={
            "property_id": prop["property_id"],
            "location": prop["location"],
            "tags": prop["tags"],
            "nightly_price": prop["nightly_price"]
        }
    )
    for prop in property_data
]
uuids = [str(uuid4()) for _ in range(len(documents))]
vector_store.add_documents(documents=documents, ids=uuids)

print(f"成功将 {len(documents)} 个房产数据加入向量数据库！")

import tkinter as tk
from tkinter import simpledialog
root = tk.Tk()
root.withdraw()  # 隐藏主窗口

###################### 加载用户数据 弹窗搜索 ###########################
with open("canadian_users_50.json", "r", encoding="utf-8") as f:
    users = json.load(f)

# 弹窗让用户输入 user_id
user_id_input = simpledialog.askstring("用户登录", "请输入你的用户ID：")

# 查找对应的用户
current_user = next((u for u in users if u["user_id"] == user_id_input), None)

if not current_user:
    print("未找到该用户！")
else:
    # 弹窗获取查询文本
    query_text = simpledialog.askstring("请输入", "请输入查询内容：")

    if query_text:
        # 相似度搜索
        initial_results = vector_store.similarity_search_with_score(query_text, k=20)
################### 未过滤结果 ###################
        # 按价格过滤
        def filter_properties_by_user(prop, user):
            price = prop.metadata.get("nightly_price", 0)
            return user["budget_min"] <= price <= user["budget_max"]

        filtered_results = [(res, score) for res, score in initial_results if filter_properties_by_user(res, current_user)]
        filtered_results = filtered_results[:5]

        print(f"\n用户 {current_user['name']} 的搜索结果：")
        for res, score in filtered_results:
            print(f"* [SIM={score:.3f}] {res.page_content}")
#U1000000001
