import os
import json
from retriever import load_vectorstore, retrieve_context

# Paths
RAG_PATH = "ml/rag/"

print("✓ Generator script initialized")


def generate_answer(query, context):
    """Generate answer from retrieved context."""

    # Simple extractive answer generation
    # In production this would call Bedrock or OpenAI
    answer = f"""
Based on the surf pipeline research data:

Query: {query}

Context Retrieved:
{context}

Summary:
This answer was generated using RAG — retrieving relevant chunks 
from the surf pipeline knowledge base and synthesizing a response.
In production this would use AWS Bedrock to generate a more 
natural language response using the retrieved context.
    """
    return answer.strip()


def run_qa_session(questions):
    """Run a Q&A session against the knowledge base."""

    print("Loading knowledge base...")
    vectorstore = load_vectorstore()

    print("\n--- Surf Pipeline Q&A ---\n")

    results = []

    for question in questions:
        print(f"Q: {question}")
        print("-" * 60)

        # Retrieve relevant context
        context = retrieve_context(question, vectorstore, k=3)

        # Generate answer
        answer = generate_answer(question, context)
        print(answer)
        print()

        results.append({
            "question": question,
            "context": context,
            "answer": answer
        })

    return results


if __name__ == "__main__":
    questions = [
    "What caused the biggest wave ever recorded?",
    "Which location has the best surf potential and why?",
    "How does Huntington Beach compare to Nazare benchmark?",
    "What is the surfable frequency at Waikiki?",
    "How often do seismic events occur near Huntington Beach?",
    "Which surf location is good for beginners?"
]

    results = run_qa_session(questions)

    # Save results
    output_path = f"{RAG_PATH}qa_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=4)

    print(f"✓ Q&A results saved to {output_path}")
    print("\n✓ Generator complete!")