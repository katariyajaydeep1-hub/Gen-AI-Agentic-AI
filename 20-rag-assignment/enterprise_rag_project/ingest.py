from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
import os
import shutil

# ==========================================
# Delete old FAISS index if exists
# ==========================================
if os.path.exists("faiss_index"):
    shutil.rmtree("faiss_index")

# ==========================================
# Load markdown file
# ==========================================
with open("../enterprise_500_policy_dataset.md", "r", encoding="utf-8") as file:
    text = file.read()

# ==========================================
# Split into chunks
# ==========================================
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

chunks = splitter.split_text(text)

print(f"Total chunks created: {len(chunks)}")

# ==========================================
# Create embeddings
# ==========================================
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# ==========================================
# Create FAISS vector database
# ==========================================
vectorstore = FAISS.from_texts(
    texts=chunks,
    embedding=embedding_model
)

# ==========================================
# Save locally
# ==========================================
vectorstore.save_local("faiss_index")

print("\nFAISS index saved successfully")