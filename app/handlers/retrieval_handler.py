import os
import re
from qdrant_client import QdrantClient
from app.utils.embedding import get_query_embedding
from openai import OpenAI
import tiktoken

# Initialize Qdrant client
qdrant = QdrantClient(url=os.getenv("QDRANT_URL"))

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def normalize_query(query: str) -> str:
    synonym_map = {
        # Results related
        "get results": "check results",
        "retrieve results": "check results",
        "view results": "check results",
        "how to get results": "check results",
        "where to get results": "check results",
        "assessment results": "check results",
        "result appeal": "appeal results",
        "appeal results": "appeal results",
        "check certificate": "get certificate",
        "get certificate": "get certificate",
        "retrieve certificate": "get certificate",
        "download certificate": "get certificate",
        "certificate request": "get certificate",
        "how to get certificate": "get certificate",
        "check expiry": "check expiry",
        "certificate expiry": "check expiry",

        # Registration related
        "register": "register",
        "sign up": "register",
        "how to register": "register",
        "assessment registration": "register",
        "submit registration": "register",
        "enroll": "register",
        "enrollment": "register",
        "register participant": "register",
        "participant registration": "register",

        # Assessment related
        "assessment": "assessment",
        "test": "assessment",
        "exam": "assessment",
        "swimsafer assessment": "assessment",
        "swimsafer test": "assessment",
        "assessment schedule": "assessment schedule",
        "when is the assessment": "assessment schedule",
        "next assessment": "assessment schedule",
        "assessment fee": "assessment cost",
        "assessment cost": "assessment cost",
        "assessment duration": "assessment duration",
        "assessment time": "assessment duration",
        "assessment length": "assessment duration",
        "assessment venue": "assessment locations",
        "assessment location": "assessment locations",
        "where is the assessment": "assessment locations",
        "assessment centres": "assessment locations",
        "assessment centers": "assessment locations",
        "group size limits": "group size limits",

        # Remediation related
        "remediation": "remediation",
        "retest": "remediation",
        "remediation registration": "remediation",
        "remediation retest": "remediation",
        "swimsafer remediation": "remediation",

        # Program Info
        "swimsafer 2.0": "swimsafer 2.0",
        "stages in swimsafer": "stages",
        "swimsafer stages": "stages",
        "how many stages": "stages",
        "stage info": "stages",
        "swimsafer program": "swimsafer 2.0",
        "swimsafer program info": "swimsafer 2.0",
        "swimsafer program details": "swimsafer 2.0",

        # Instructor / Coach / Usage Permit
        "swimsafer instructor": "instructor",
        "become instructor": "instructor",
        "how to become instructor": "instructor",
        "instructor course": "instructor course",
        "instructor certification": "instructor certification",
        "usage permit": "usage permit",
        "usage permit renewal": "usage permit renewal",
        "apply usage permit": "usage permit",
        "renew usage permit": "usage permit renewal",

        # Refund and Medical
        "refund": "refund",
        "refund policy": "refund",
        "medical exemption": "medical exemption",
        "medical certificate": "medical exemption",
        "refund due to medical reason": "medical exemption",
        "medical certificate submission": "medical exemption",
        "medical condition refund": "medical exemption",

        # Rain / Rescheduling / Weather policy
        "what if it rains": "rain policy",
        "rain policy": "rain policy",
        "rain-off": "rain policy",
        "rebook due to rain": "rain policy",
        "reschedule due to rain": "rain policy",
        "rain rescheduling": "rain policy",
        "assessment cancelled rain": "rain policy",

        # Appeal
        "appeal": "appeal",
        "file appeal": "appeal",
        "appeal results": "appeal",
        "not competent": "appeal",
        "reassess": "appeal",
        "re-evaluate": "appeal",
        "assessment appeal": "appeal",

        # Theory Quiz
        "theory quiz": "theory quiz",
        "where to do theory quiz": "theory quiz",
        "attempt theory quiz": "theory quiz",
        "complete theory quiz": "theory quiz",

        # General questions
        "who can join swimsafer": "eligibility",
        "eligibility": "eligibility",
        "prerequisites for stages": "prerequisites",
        "stage prerequisites": "prerequisites",
        "how to check expiry": "check expiry",
        "check expiry date": "check expiry",
    }

    query = query.lower()
    sorted_keys = sorted(synonym_map.keys(), key=len, reverse=True)

    for phrase in sorted_keys:
        pattern = r'\b' + re.escape(phrase) + r'\b'
        if re.search(pattern, query):
            query = re.sub(pattern, synonym_map[phrase], query)

    # Optional: log normalized query for debugging
    print(f"Normalized query: {query}")

    return query


def classify_query_topic(query):
    topic_keywords = {
        "results": ["result", "certificate", "check", "pass", "fail"],
        "registration": ["register", "signup", "sign up", "account", "login"],
        "assessment": ["assessment", "book", "slot", "reschedule", "schedule"],
        "appeal": ["appeal", "not competent", "reassess", "re-evaluate"],
        # You can expand topics if needed
    }
    for topic, keywords in topic_keywords.items():
        if any(k in query for k in keywords):
            return topic
    return "general"


def retrieve_context(state):
    original_query = state["query"]
    normalized_query = normalize_query(original_query)

    topic = classify_query_topic(normalized_query)

    score_threshold = 0.25 if topic == "results" else 0.20
    limit = 40

    query_vector = get_query_embedding(normalized_query)

    search_results = qdrant.search(
        collection_name="chatbot_docs",
        query_vector=query_vector,
        limit=limit,
        score_threshold=score_threshold
    )

    if not search_results:
        return {**state, "context": ""}

    print("\n🔍 All retrieved chunks:")
    for hit in search_results:
        print(f"Score: {hit.score:.3f} | Category: {hit.payload.get('category')} | Topic: {hit.payload.get('topic')} | Text snippet: {hit.payload.get('text','')[:100]}...")

    # Combine topic hits, supplemental hits, and main hits
    topic_hits = [hit for hit in search_results if hit.payload.get("topic") == topic]
    supplemental_hits = [hit for hit in search_results if hit.payload.get("category") != "main"]
    main_hits = [hit for hit in search_results if hit.payload.get("category") == "main"]

    hits_to_use = topic_hits + supplemental_hits + main_hits

    # Sort hits by descending score to get top results first
    hits_to_use = sorted(hits_to_use, key=lambda h: h.score, reverse=True)[:limit]

    context = "\n---\n".join([hit.payload.get("text", "") for hit in hits_to_use])

    print(f"\n🔍 Used chunks for query: '{original_query}' (normalized: '{normalized_query}') [topic: {topic}]")
    for hit in hits_to_use:
        print("→", hit.payload.get("text", "")[:300].replace("\n", " ") + "...\n")

    return {
        **state,
        "context": context
    }


    topic_hits = [hit for hit in search_results if hit.payload.get("topic") == topic]
    main_hits = [hit for hit in search_results if hit.payload.get("category") == "main"]
    hits_to_use = topic_hits or main_hits or search_results

    context = "\n---\n".join([hit.payload.get("text", "") for hit in hits_to_use])

    print(f"\n🔍 Retrieved chunks for query: '{original_query}' (normalized: '{normalized_query}') [topic: {topic}]")
    for hit in hits_to_use:
        print("→", hit.payload.get("text", "")[:300].replace("\n", " ") + "...\n")

    return {
        **state,
        "context": context
    }


def count_tokens(text, model="gpt-3.5-turbo"):
    import tiktoken
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def truncate_to_token_limit(text, max_tokens, model="gpt-3.5-turbo"):
    import tiktoken
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(text)
    truncated = tokens[:max_tokens]
    return encoding.decode(truncated)


def generate_response(state):
    query = state["query"]
    raw_context = state.get("context", "")

    system_prompt = (
        "You are a knowledgeable assistant specialized in the SwimSafer program in Singapore. "
        "Answer user questions only using the provided context. "
        "If the context does not contain enough information to answer,assume it is within the context of SwimSafer or politely ask the user for more details or clarification. "
        "Provide clear, concise, and user-friendly answers relevant to SwimSafer. Avoid guessing or making up information. Keep answers brief and focused."
    )

    # Leave token budget for answer generation; keep max total ~16385 tokens
    token_budget = 15800
    context = truncate_to_token_limit(raw_context, token_budget)

    user_prompt = f"Context:\n{context}\n\nQuestion:\n{query}"

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.5,
        max_tokens=300,
    )

    answer = response.choices[0].message.content.strip()

    return {
        **state,
        "response": answer
    }
