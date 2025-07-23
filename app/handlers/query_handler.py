def handle_query(state):
    """
    Preprocesses the user query and passes it to the next node.
    """
    query = state["query"]

    # Optional: Clean or normalize query
    cleaned_query = query.strip()

    # Update state
    return {
        **state,
        "query": cleaned_query
    }
