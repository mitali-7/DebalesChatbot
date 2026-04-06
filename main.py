from rag import create_vector_store
from graph import build_graph

def main():
    print("🔄 Loading...")
    db = create_vector_store()
    graph = build_graph()

    while True:
        query = input("\nYou: ")

        if query.lower() == "exit":
            break

        result = graph.invoke({
            "query": query,
            "db": db
        })

        print("\nBot:", result["answer"])


if __name__ == "__main__":
    main()