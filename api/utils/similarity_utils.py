def similarity_search():
    pass
from openai import OpenAI

BASE_URL = "https://openrouter.ai/api/v1"
MODEL =  "deepseek/deepseek-chat-v3-0324:free"

client = OpenAI(base_url=BASE_URL, api_key="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")

def extract_text(resp) -> str | None:
    """Safely pull assistant text from a ChatCompletion response."""
    if resp is None:
        return None
    choices = getattr(resp, "choices", None)
    if not choices:  # None or empty
        # helpful debug dump so you can see what actually came back
        try:
            print("[debug] raw response:", resp.model_dump_json(indent=2))
        except Exception:
            print("[debug] raw response (repr):", repr(resp))
        return None

    ch0 = choices[0]
    # Normal Chat Completions
    msg = getattr(ch0, "message", None)
    if msg and getattr(msg, "content", None):
        return msg.content

    # Some providers/SDKs expose text on `text`
    if getattr(ch0, "text", None):
        return ch0.text

    return None

def chat_loop():
    system_prompt = "You are a helpful, concise assistant. Always answer in Markdown."
    messages = [{"role": "system", "content": system_prompt}]

    print("Chat started. Type exit to quit, or new to reset.\n")
    while True:
        try:
            user_text = input("Enter Your Request > ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\nBye!")
            break

        if not user_text:
            continue
        cmd = user_text.lower()
        if cmd in {"exit", "quit", "q"}:
            print("See ya!")
            break
        if cmd in {"/new", "/reset"}:
            messages = [{"role": "system", "content": system_prompt}]
            print("(Started a new chat)\n")
            continue

        messages.append({"role": "user", "content": user_text})

        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                max_tokens=200,
            )
        except Exception as e:
            print(f"[Error] {e}\n")
            messages.pop()  # remove the last user turn on failure
            continue

        answer = extract_text(resp)
        if not answer:
            print("[Warn] No text returned by the model. Try again or switch models.\n")
            messages.pop()  # don’t keep the user turn if we got no answer
            continue

        print(f"Bot > {answer}\n")
        messages.append({"role": "assistant", "content": answer})

chat_loop()
