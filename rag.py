from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


# use HuggingFace embeddings (clean integration)
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


def create_vector_store():
    with open("data.txt", "r", encoding="utf-8") as f:
        text = f.read()

    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(text)

    # FAISS handles embeddings internally
    db = FAISS.from_texts(chunks, embedding_model)

    return db


def query_rag(db, query):
    docs = db.similarity_search(query, k=3)
    return "\n".join([doc.page_content for doc in docs])