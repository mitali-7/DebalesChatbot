from langgraph.graph import StateGraph
from rag import get_similarity_score, query_rag, get_top_k_with_scores
from tools import search_tool
from llm import generate


# -------- ROUTER NODE --------
# -------- ROUTER NODE --------
def router_node(state):
    query = state["query"].lower()
    db = state["db"]

    # --- NEW: Identity Check ---
    # If the user says 'you' or 'your', they are likely talking to the bot about Debales
    identity_keywords = ["you", "your", "this company", "this app", "the company"]
    is_identity_query = any(k in query for k in identity_keywords)

    # Augment the query for the vector search if it's vague
    search_query = f"Debales AI {query}" if is_identity_query else query
    
    results = get_top_k_with_scores(db, search_query, k=1)
    # ---------------------------

    if not results:
        state["route"] = "search"
        return state

    _, score = results[0]
    # print(f"Distance score for '{search_query}': {score}")

    # Use a stricter threshold for RAG to ensure high quality
    if is_identity_query or score < 0.6: 
        state["route"] = "rag"
    elif score < 1.1:
        state["route"] = "both"
    else:
        state["route"] = "search"

    return state

# -------- RAG NODE --------
def rag_node(state):
    query = state["query"]
    db = state["db"]

    docs = db.similarity_search(query, k=5)

    context = "\n".join([doc.page_content for doc in docs])

    state["context"] = context
    return state


# -------- SEARCH NODE --------
def search_node(state):
    context = search_tool(state["query"])
    state["context"] = context
    return state


# -------- GENERATE NODE --------
def generate_node(state):
    query = state["query"]
    context = state.get("context", "")

    prompt = f"""
    You are the official Debales AI Assistant. 
    Your job is to provide accurate information about Debales AI services and products.

    Rules:
    1. If the user refers to "you" or "this company", they mean Debales AI.
    2. Answer ONLY using the provided context below.
    3. If the context doesn't contain the answer, say "I don’t have enough information."
    4. Do not use outside knowledge.

    Context:
    {context}

    Question:
    {query}
    """
    state["answer"] = generate(prompt)
    return state

def both_node(state):
    query = state["query"]
    db = state["db"]

    rag_docs = db.similarity_search(query, k=5)
    rag_context = "\n".join([doc.page_content for doc in rag_docs])

    search_context = search_tool(query)

    state["context"] = rag_context + "\n" + search_context
    return state


# -------- BUILD GRAPH --------
def build_graph():
    builder = StateGraph(dict)

    builder.add_node("router", router_node)
    builder.add_node("rag", rag_node)
    builder.add_node("search", search_node)
    builder.add_node("both", both_node)
    builder.add_node("generate", generate_node)

    builder.set_entry_point("router")

    builder.add_conditional_edges(
        "router",
        lambda state: state["route"],
        {
            "rag": "rag",
            "search": "search",
            "both": "both",
        }
    )

    builder.add_edge("rag", "generate")
    builder.add_edge("search", "generate")
    builder.add_edge("both", "generate")

    return builder.compile()