from langgraph.graph import StateGraph
from rag import query_rag
from tools import search_tool
from llm import generate


# -------- ROUTER NODE --------
def router_node(state):
    query = state["query"].lower()

    if "debales" in query:
        state["route"] = "rag"
    else:
        state["route"] = "search"

    return state


# -------- RAG NODE --------
def rag_node(state):
    context = query_rag(state["db"], state["query"])
    state["context"] = context
    return state


# -------- SEARCH NODE --------
def search_node(state):
    context = search_tool(state["query"])
    state["context"] = context
    return state


# -------- GENERATE NODE --------
def generate_node(state):
    context = state.get("context", "")
    query = state["query"]

    if not context.strip():
        state["answer"] = "I don’t have enough information to answer that."
        return state

    prompt = f"""
    Answer ONLY using the context below.
    If unsure, say you don't know.

    Context:
    {context}

    Question:
    {query}
    """

    state["answer"] = generate(prompt)
    return state


# -------- BUILD GRAPH --------
def build_graph():
    builder = StateGraph(dict)

    builder.add_node("router", router_node)
    builder.add_node("rag", rag_node)
    builder.add_node("search", search_node)
    builder.add_node("generate", generate_node)

    builder.set_entry_point("router")

    # ✅ stable routing using state key
    builder.add_conditional_edges(
        "router",
        lambda state: state["route"],
        {
            "rag": "rag",
            "search": "search",
        },
    )

    builder.add_edge("rag", "generate")
    builder.add_edge("search", "generate")

    return builder.compile()