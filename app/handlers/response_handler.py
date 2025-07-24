import os
from openai import OpenAI
import tiktoken

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def count_tokens(text, model="gpt-3.5-turbo"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def truncate_to_token_limit(text, max_tokens, model="gpt-3.5-turbo"):
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    truncated = tokens[:max_tokens]
    return encoding.decode(truncated)

def generate_response(state):
    query = state["query"]
    raw_context = state.get("context", "")

    model_name = "gpt-4o-mini"  # or "gpt-3.5-turbo" if you prefer
    max_context_tokens = 16000
    max_response_tokens = 300
    # Leave some buffer tokens for system+user prompts overhead
    buffer_tokens = 200

    # Calculate tokens available for context after accounting for response + buffer
    max_context_budget = max_context_tokens - max_response_tokens - buffer_tokens

    truncated_context = truncate_to_token_limit(raw_context, max_context_budget, model=model_name)

    system_prompt = (
        "You are a helpful assistant knowledgeable about the SwimSafer program in Singapore. "
        "Use *only* the provided context to answer the question. "
        "Do not fabricate or assume information beyond the context. "
        "If the context does not contain the answer, politely inform the user you don't have enough information. "
        "Keep the answer concise and relevant."
    )

    user_prompt = f"Context:\n{truncated_context}\n\nQuestion:\n{query}"

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,  # Lower temp for more precise answers
        max_tokens=max_response_tokens,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    answer = response.choices[0].message.content.strip()

    # Debug print - can be toggled or sent to a logger
    print(f"\n📝 Query: {query}\n🗂️ Context tokens used: {count_tokens(truncated_context, model_name)}\n💬 Answer: {answer}\n")

    return {
        **state,
        "response": answer
    }
