import os
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_response(state):
    query = state["query"]
    context = state.get("context", "")

    if not context.strip():
        return {
            **state,
            "response": "I couldn't find relevant information in the documents."
        }

    prompt = f"""Use the following context to answer the question. 
Only use the context provided. If the answer is not in the context, say "I don't know based on the documents provided."

Context:
{context}

Question:
{query}
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Only use the provided context."},
            {"role": "user", "content": prompt}
        ],
        temperature=0  # More factual and deterministic
    )

    answer = response.choices[0].message.content

    return {
        **state,
        "response": answer
    }
