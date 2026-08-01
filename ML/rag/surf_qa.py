import os
import json
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Direct imports from same folder
from retriever import load_vectorstore, retrieve_context
from generator import generate_answer
# Paths
RAG_PATH = "ml/rag/"
FINAL_PATH = "data/final/"

print("✓ Surf Q&A initialized")


def surf_qa(question, vectorstore, k=3):
    """Answer a surf related question using RAG."""

    # Retrieve relevant context
    context = retrieve_context(question, vectorstore, k=k)

    # Generate answer
    answer = generate_answer(question, context)

    return {
        "question": question,
        "context": context,
        "answer": answer
    }


def load_predictions_context():
    """Load latest surf predictions as additional context."""

    try:
        with open(f"{FINAL_PATH}surf_predictions.json", "r") as f:
            predictions = json.load(f)

        context = "Latest Surf Predictions:\n"
        for pred in predictions["predictions"]:
            context += f"{pred['location']}: predicted wave {pred['predicted_wave_ft']}ft "
            context += f"({pred['predicted_wave_m']}m) — surfable: {pred['surfable']}\n"

        return context
    except FileNotFoundError:
        return None


def run_interactive_qa():
    """Run interactive Q&A session."""

    print("\n" + "=" * 60)
    print("🌊 SURF PIPELINE — Natural Language Q&A")
    print("=" * 60)
    print("Ask anything about surf locations, wave records,")
    print("benchmarks, or predictions.")
    print("Type 'quit' to exit.\n")

    # Load vector store
    vectorstore = load_vectorstore()

    # Load predictions as extra context
    predictions_context = load_predictions_context()
    if predictions_context:
        print("✓ Latest predictions loaded\n")

    # Predefined questions for demo
    demo_questions = [
        "What caused the biggest wave ever recorded?",
        "Which location is best for experienced surfers?",
        "Which location is best for beginners?",
        "How does Huntington Beach compare to Waikiki?",
        "What is the Nazare benchmark and why does it matter?",
        "Which location has the most seismic activity?"
    ]

    print("--- Demo Q&A Session ---\n")

    results = []
    for question in demo_questions:
        print(f"Q: {question}")
        print("-" * 50)

        result = surf_qa(question, vectorstore)
        print(result["answer"])
        print()

        results.append(result)

    # Save results
    output_path = f"{RAG_PATH}surf_qa_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=4)

    print(f"✓ Q&A results saved to {output_path}")
    return results


def answer_single_question(question):
    """Answer a single question and return result."""

    vectorstore = load_vectorstore()
    result = surf_qa(question, vectorstore)

    print(f"\nQ: {result['question']}")
    print("-" * 50)
    print(result["answer"])

    return result


if __name__ == "__main__":
    print("Starting Surf Q&A...\n")
    results = run_interactive_qa()
    print(f"\n✓ Answered {len(results)} questions")
    print("\n✓ Surf Q&A complete!")