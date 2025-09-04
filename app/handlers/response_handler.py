from app.handlers.retrieval_handler import retrieve_similar

# 👇 Add this greeting detector
def is_greeting_or_smalltalk(text):
    greetings = [
        "hi", "hello", "hey", "good morning", "good afternoon", "good evening",
        "how are you", "what's up", "yo", "sup", "howdy"
    ]
    text_lower = text.strip().lower()
    return any(text_lower.startswith(greet) for greet in greetings)

# 👇 Main response generator
def generate_response(state):
    query = state["query"]

    # Early return for greetings / smalltalk
    if is_greeting_or_smalltalk(query):
        return {
            **state,
            "response": "Hello! 👋 How can I assist you with the SwimSafer program today?"
        }

    # Retrieve top 5 relevant documents from Qdrant
    results = retrieve_similar(query, top_k=5)
    retrieved_chunks = [hit.payload.get("text", "") for hit in results if "text" in hit.payload]
    raw_context = "\n\n".join(retrieved_chunks)

    # Prompt for LLM (can be any lightweight model; llama3 or similar)
    system_prompt = (
        "You are a friendly and helpful assistant knowledgeable about the SwimSafer program in Singapore. "
        "Answer questions based only on the information provided. "
        "If you don't have enough information, politely say so. "
        "Keep answers concise, natural, and user-friendly."
    )
    
    user_prompt = f"{raw_context}\n\nQuestion:\n{query}"

    # Use a small local LLM or llama3 API if available
    try:
        from app.services.llm_client import llm_complete  # <-- lightweight LLM wrapper
        answer = llm_complete(system_prompt=system_prompt, user_prompt=user_prompt)
    except ImportError:
        # Fallback if no LLM: just echo the query
        answer = "Sorry, I cannot answer that right now."

    # Optional: clean unwanted phrasing
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
