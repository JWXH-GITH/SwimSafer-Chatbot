import os
from dotenv import load_dotenv
from app.services.groq_client import GroqClient

load_dotenv()

client = GroqClient(api_key=os.getenv("GROQ_API_KEY"))


def generate_response(state):
    query = state["query"]
    raw_context = state.get("context", "")

    system_prompt = (
        "You are a friendly and helpful assistant knowledgeable about the SwimSafer program in Singapore. "
        "Answer questions based only on the information provided. "
        "If you don't have enough information, politely say so. "
        "Do not mention or refer to any 'context' or 'documents'. "
        "Keep answers concise, natural, and user-friendly."
    )

    user_prompt = f"{raw_context}\n\nQuestion:\n{query}"

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

    # Optional: clean robotic lead-ins (if any slip through)
    unwanted_phrases = [
        "According to the provided context, ",
        "Based on the context, ",
        "From the context, ",
        "As per the context, "
    ]
    for phrase in unwanted_phrases:
        if answer.startswith(phrase):
            answer = answer[len(phrase):].lstrip().capitalize()

    print(f"\n📝 Query: {query}\n💬 Answer: {answer}\n")

    return {
        **state,
        "response": answer
    }
