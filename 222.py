import json
from uuid import uuid4
import faiss
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
import requests
from tabulate import tabulate
import getpass

# -----------------------
# 1. 加载房源和用户数据
with open("Canadian_properties_50.json", "r", encoding="utf-8") as f:
    property_data = json.load(f)

with open("canadian_users_50.json", "r", encoding="utf-8") as f:
    users = json.load(f)

# -----------------------
# 2. 初始化向量存储
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
            "nightly_price": prop["nightly_price"]
        }
    )
    for prop in property_data
]
uuids = [str(uuid4()) for _ in range(len(documents))]
vector_store.add_documents(documents=documents, ids=uuids)

# -----------------------
# 3. LLM 初始化（一次）
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "deepseek/deepseek-chat"
API_KEY = getpass.getpass("Enter your OpenRouter API key (input hidden): ").strip()
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

SYSTEM_PROMPT = (
    "You are a helpful assistant for an Airbnb-like vacation property search. "
    "Given a user's query, generate a list of related tags that capture the user's intent. "
    "Return ONLY a JSON array of strings. Example: ['sunny', 'lakefront', 'outdoor']"
)

def llm_generate_tags(user_query, model=MODEL, temperature=0.7):
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_query}
        ],
        "temperature": temperature
    }
    r = requests.post(OPENROUTER_URL, headers=HEADERS, json=payload, timeout=60)
    if r.status_code != 200:
        return {"error": f"HTTP {r.status_code}", "details": r.text}

    data = r.json()
    content = (data.get("choices") or [{}])[0].get("message", {}).get("content")
    print("原始 LLM 响应:", content)

    if not content:
        return {"error": "Empty response", "raw": data}

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # 尝试提取 JSON 子串
        s, e = content.find("["), content.rfind("]")
        if s != -1 and e != -1 and e > s:
            try:
                return json.loads(content[s:e+1])
            except json.JSONDecodeError:
                return {"error": "Non-JSON content", "raw": content}
        return {"error": "Non-JSON content", "raw": content}

# -----------------------
# 4. 用户登录
user_id_input = input("请输入你的用户ID：")
current_user = next((u for u in users if u["user_id"] == user_id_input), None)

if not current_user:
    print("未找到该用户！")
    exit()

# -----------------------
# 5. 主搜索循环
while True:
    query_text = input("请输入查询内容（直接回车退出）：")
    if not query_text:
        print("用户取消搜索，程序结束。")
        break

    # 生成标签
    tags = llm_generate_tags(query_text)
    if isinstance(tags, dict) and "error" in tags:
        print("LLM 生成标签出错:", tags)
        continue

    print("LLM 扩展的标签:", tags)
    tag_query = ", ".join(tags)

    # 向量搜索
    initial_results = vector_store.similarity_search_with_score(tag_query, k=50)

    # 按用户预算过滤
    def filter_properties_by_user(prop, user):
        price = prop.metadata.get("nightly_price", 0)
        return user["budget_min"] <= price <= user["budget_max"]

    filtered_results = [(res, score) for res, score in initial_results if filter_properties_by_user(res, current_user)]
    filtered_results = filtered_results[:10]  # top 10
    filtered_results.sort(key=lambda x: x[1])

    # 打印结果
    for res, score in filtered_results:
        print(f"* [SIM={score:.3f}] {res.page_content}")
    print()
