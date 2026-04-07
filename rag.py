from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


# use HuggingFace embeddings (clean integration)
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


def create_vector_store():
    with open("data.txt", "r", encoding="utf-8") as f:
        text = f.read()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    chunks = splitter.split_text(text)

    # FAISS handles embeddings internally
    db = FAISS.from_texts(chunks, embedding_model)

    return db

def get_top_k_with_scores(db, query, k=5):
    results = db.similarity_search_with_score(query, k=k)
    return results

def get_similarity_score(db, query):
    docs_and_scores = db.similarity_search_with_score(query, k=1)

    if not docs_and_scores:
        return 999  # high distance = bad match

    _, score = docs_and_scores[0]
    return score


def query_rag(db, query):
    docs = db.similarity_search(query, k=3)
    return "\n".join([doc.page_content for doc in docs])