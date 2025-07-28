import os
import time
from dotenv import load_dotenv
from app.services.groq_client import GroqClient
from app.handlers.retrieval_handler import retrieve_similar

load_dotenv()
client = GroqClient(api_key=os.getenv("GROQ_API_KEY"))

# Optional: In-memory cache
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_response(query):
    return generate_response_core(query)

# Detect greetings/smalltalk
def is_greeting_or_smalltalk(text):
    greetings = [
        "hi", "hello", "hey", "good morning", "good afternoon", "good evening",
        "how are you", "what's up", "yo", "sup", "howdy"
    ]
    text_lower = text.strip().lower()
    return any(text_lower.startswith(greet) for greet in greetings)

def generate_response(state):
    query = state["query"]

    # Handle greetings directly
    if is_greeting_or_smalltalk(query):
        return {
            **state,
            "response": "Hello! 👋 How can I assist you with the SwimSafer program today?"
        }

    # Use cached or fresh response
    answer = cached_response(query)
    return {
        **state,
        "response": answer
    }

def generate_response_core(query):
    start_time = time.time()

    # Retrieve relevant context
    results = retrieve_similar(query, top_k=5, min_score=0.8)

    # Compact context, clamp size
    MAX_CONTEXT_CHARS = 1500
    context_chunks = []
    char_count = 0

    for hit in results:
        chunk = hit.payload.get("text", "").strip()
        if not chunk:
            continue
        if char_count + len(chunk) > MAX_CONTEXT_CHARS:
            break
        context_chunks.append(chunk)
        char_count += len(chunk)

    raw_context = "\n\n".join(context_chunks)

    system_prompt = (
        "You are a helpful assistant knowledgeable about the SwimSafer program in Singapore. "
        "Only answer using the information given. Do not speculate or add extra information. "
        "If the answer is not in the provided information, say: 'Sorry, I don't have that information.' "
        "Do not mention any context or documents. Keep responses short and user-friendly."
    )

    user_prompt = f"{raw_context}\n\nQuestion:\n{query}"

    # Time LLM call
    before_llm = time.time()
    response = client.chat_complete(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        max_tokens=200,
    )
    llm_time = time.time()

    # Clean output
    answer = response["choices"][0]["message"]["content"].strip()

    # Remove LLM fluff
    unwanted_phrases = [
        "According to the provided context,",
        "Based on the context,",
        "From the context,",
        "As per the context,",
        "It seems like you're interested in",
        "However, I noticed that",
        "Please feel free to ask",
        "I'd be happy to help",
        "Let me know if"
    ]
    for phrase in unwanted_phrases:
        if answer.lower().startswith(phrase.lower()):
            answer = answer[len(phrase):].lstrip().capitalize()

    print(f"\n📝 Query: {query}")
    print(f"⏱ Retrieval Time: {before_llm - start_time:.2f}s")
    print(f"⏱ LLM Time: {llm_time - before_llm:.2f}s")
    print(f"💬 Answer: {answer}\n")

    return answer
