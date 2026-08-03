import os
import json
import pickle
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import pandas as pd

# Paths
RAG_PATH = "ml/rag/"
KNOWLEDGE_BASE_PATH = "ml/rag/knowledge_base/"
FINAL_PATH = "data/final/"

print("✓ Embeddings script initialized")


def load_knowledge_base():
    """Load all documents from knowledge base folders."""

    print("Loading knowledge base documents...")

    documents = []

    # Load all text files from knowledge base subfolders
    knowledge_base_path = "ml/rag/knowledge_base"
    subfolders = ["benchmark_docs", "location_reports", "noaa_documentation"]

    for subfolder in subfolders:
        folder_path = os.path.join(knowledge_base_path, subfolder)
        if os.path.exists(folder_path):
            for filename in os.listdir(folder_path):
                if filename.endswith(".txt"):
                    file_path = os.path.join(folder_path, filename)
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    documents.append({
                        "source": f"{subfolder}/{filename}",
                        "content": content
                    })
                    print(f"  ✓ Loaded {subfolder}/{filename}")

    # Also load hardcoded context documents
    benchmark_summary = {
        "source": "benchmark_research",
        "content": """
        Lituya Bay Megatsunami 1958:
        The largest wave ever recorded occurred on July 9 1958 in Lituya Bay Alaska.
        The wave reached a height of 1720 feet (524 meters). It was caused by a massive
        rockslide triggered by a magnitude 7.8 earthquake along the Fairweather Fault.
        The rockslide displaced approximately 90 million tons of rock into the bay
        generating a megatsunami. The wave was not surfable and represents the absolute
        scientific upper bound for wave height measurement.

        Nazare Big Wave Record 2020:
        The largest wave ever surfed was ridden by Sebastian Steudtner at Nazare Portugal
        on October 29 2020. The wave measured 86 feet (26.2 meters). Nazare is famous for
        its underwater canyon called the Nazare Canyon which extends 170 kilometers into
        the Atlantic Ocean. The canyon funnels and amplifies Atlantic swells creating
        consistently giant waves. This represents the human surfability ceiling and is
        used as the primary benchmark for scoring surf locations in this project.
        """
    }
    documents.append(benchmark_summary)

    # Load beginner research
    beginner_data = {
        "source": "beginner_research",
        "content": """
        Beginner Surf Locations:
        Pensacola Beach is considered the most beginner friendly location
        due to its low average wave height of 0.97 meters and only 17.60
        percent surfable frequency meaning waves are generally small and
        manageable for beginners.

        Cocoa Beach has the lowest surfable frequency at 2 percent and
        smallest average wave height of 0.62 meters making it very calm
        and suitable for beginners most of the time.

        Waikiki and Huntington Beach have higher wave frequencies and
        are better suited for intermediate to advanced surfers.
        """
    }
    documents.append(beginner_data)

    # Load surf scores
    try:
        import pandas as pd
        scores_df = pd.read_csv("data/processed/surf_scores.csv")
        scores_content = "Surf Potential Rankings:\n"
        for _, row in scores_df.iterrows():
            scores_content += f"{row['location_name']}: score {row['surf_potential_score']} rank {row['rank']}\n"
        documents.append({
            "source": "surf_scores",
            "content": scores_content
        })
    except FileNotFoundError:
        print("✗ Surf scores not found — skipping")

    print(f"\n✓ Loaded {len(documents)} knowledge base documents")
    return documents


def create_embeddings(documents):
    """Chunk documents and create vector embeddings."""

    print("\nCreating embeddings...")

    # Initialize text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len
    )

    # Split documents into chunks
    all_chunks = []
    for doc in documents:
        chunks = text_splitter.split_text(doc["content"])
        for chunk in chunks:
            all_chunks.append({
                "text": chunk,
                "source": doc["source"]
            })

    print(f"✓ Created {len(all_chunks)} text chunks")

    # Initialize HuggingFace embeddings
    print("Loading HuggingFace embedding model...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Create FAISS vector store
    texts = [chunk["text"] for chunk in all_chunks]
    metadatas = [{"source": chunk["source"]} for chunk in all_chunks]

    print("Building FAISS vector store...")
    vectorstore = FAISS.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas
    )

    print(f"✓ Vector store created with {len(texts)} embeddings")
    return vectorstore, embeddings


def save_vectorstore(vectorstore):
    """Save FAISS vector store to disk."""

    save_path = f"{RAG_PATH}vectorstore"
    vectorstore.save_local(save_path)
    print(f"✓ Vector store saved to {save_path}")


if __name__ == "__main__":
    print("Starting embeddings pipeline...\n")

    # Load knowledge base
    documents = load_knowledge_base()

    # Create embeddings and vector store
    vectorstore, embeddings = create_embeddings(documents)

    # Save vector store
    save_vectorstore(vectorstore)

    print("\n✓ Embeddings pipeline complete!")

