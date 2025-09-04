def generate_response(state):
    query = state["query"]

    # Early return for empty query
    if not query.strip():
        return {**state, "response": "Please type your question so I can assist you."}

    # Early return for greetings
    if is_greeting_or_smalltalk(query):
        return {**state, "response": "Hello! 👋 How can I assist you with the SwimSafer program today?"}

    # Retrieve relevant context
    from app.handlers.retrieval_handler import retrieve_similar
    results = retrieve_similar(query, top_k=5)
    retrieved_chunks = [hit.payload.get("text", "") for hit in results if "text" in hit.payload]
    raw_context = "\n\n".join(retrieved_chunks)

    # Prompts
    system_prompt = (
        "You are a friendly and helpful assistant knowledgeable about the SwimSafer program in Singapore. "
        "Answer questions based only on the information provided. "
        "If you don't have enough information, politely say so. "
        "Do not mention or refer to any 'context' or 'documents'. "
        "Keep answers concise, natural, and user-friendly."
    )
    user_prompt = f"{raw_context}\n\nQuestion:\n{query}"

    # Lazy-load client
    client = get_client()
    response = client.chat_complete(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        max_tokens=150,
    )

    answer = response["choices"][0]["message"]["content"].strip()

    # Clean robotic phrases
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

    return {**state, "response": answer}
