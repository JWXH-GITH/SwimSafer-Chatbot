import os
from dotenv import load_dotenv
from app.services.groq_client import GroqClient

load_dotenv()

client = GroqClient(api_key=os.getenv("GROQ_API_KEY"))

def generate_response(state):
    query = state["query"]
    raw_context = state.get("context", "")

    system_prompt = (
        "You are a helpful assistant knowledgeable about the SwimSafer program in Singapore. "
        "Use *only* the provided context to answer the question. "
        "Do not fabricate or assume information beyond the context. "
        "If the context does not contain the answer, politely inform the user you don't have enough information. "
        "Keep the answer concise and relevant."
    )

    user_prompt = f"Context:\n{raw_context}\n\nQuestion:\n{query}"

    response = client.chat_complete(
        model="llama3-8b-8192",  # your Groq chat model name here
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        max_tokens=300,
    )

    answer = response["choices"][0]["message"]["content"].strip()

    print(f"\n📝 Query: {query}\n💬 Answer: {answer}\n")

    return {
        **state,
        "response": answer
    }
