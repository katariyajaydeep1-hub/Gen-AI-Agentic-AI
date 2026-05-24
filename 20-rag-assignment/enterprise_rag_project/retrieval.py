from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# ==========================================
# Load embeddings
# ==========================================
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# ==========================================
# Load FAISS index
# ==========================================
vectorstore = FAISS.load_local(
    "faiss_index",
    embedding_model,
    allow_dangerous_deserialization=True
)

# ==========================================
# Search function
# ==========================================
def search(query):

    docs = vectorstore.similarity_search(query, k=3)

    results = []

    for doc in docs:
        results.append(doc.page_content)

    return results
