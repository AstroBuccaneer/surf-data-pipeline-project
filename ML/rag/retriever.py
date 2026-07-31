import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Paths
RAG_PATH = "ml/rag/"

print("✓ Retriever script initialized")


def load_vectorstore():
    """Load saved FAISS vector store."""

    print("Loading vector store...")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = FAISS.load_local(
        f"{RAG_PATH}vectorstore",
        embeddings,
        allow_dangerous_deserialization=True
    )

    print("✓ Vector store loaded")
    return vectorstore


def retrieve_context(query, vectorstore, k=3):
    """Retrieve most relevant chunks for a query."""

    docs = vectorstore.similarity_search(query, k=k)
    context = "\n\n".join([doc.page_content for doc in docs])
    return context


if __name__ == "__main__":
    vectorstore = load_vectorstore()

    # Test retrieval
    test_queries = [
        "What caused the biggest wave ever recorded?",
        "Which location has the best surf potential?",
        "How does Huntington Beach compare to Nazare?",
        "Which surf location is good for beginners?"
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 50)
        context = retrieve_context(query, vectorstore)
        print(context[:300])


