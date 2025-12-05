import pandas as pd
from rag_pipeline import get_rag_engine
from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
import time

# --- 1. DEFINE YOUR QUESTIONS ---
# Tailored for: INTC, META, NVDA, AMZN, GOOG (2024 10-Ks)
QUESTIONS = [
    # 1. Numerical Retrieval (Nvidia - Growth)
    "What was Nvidia's total revenue for the fiscal year 2024?",
    
    # 2. Segment Reporting (Amazon - Specific Segment)
    "What was the net sales revenue specifically for Amazon Web Services (AWS) in 2024?",
    
    # 3. Financial Reasoning (Intel - Turnaround Context)
    "Did Intel's total revenue increase or decrease in 2024 compared to 2023, and by how much?",
    
    # 4. Specific Fact (Meta - Loss/Investment)
    "What was the operating loss reported for Meta's Reality Labs segment in 2024?",
    
    # 5. Strategic Analysis (Google - AI Risks)
    "What specific risk factors does Alphabet (Google) list regarding Generative AI and Large Language Models?",
    
    # 6. Competition (Nvidia - Market Position)
    "Who does Nvidia identify as its main competitors in the Data Center market?",
    
    # 7. Expense Analysis (Meta - R&D)
    "How much did Meta spend on Research and Development (R&D) in 2024?",
    
    # 8. Operational Risks (Amazon - Logistics)
    "What factors does Amazon list as affecting its shipping and fulfillment costs?",
    
    # 9. Legal/Regulatory (Google - Antitrust)
    "What are the key antitrust legal proceedings mentioned by Alphabet (Google) in the 10-K?",
    
    # 10. Strategy (Intel - IDM 2.0)
    "Describe Intel's 'IDM 2.0' strategy and the risks associated with it."
]

# --- 2. DEFINE MODELS TO COMPARE [cite: 13] ---
# Make sure you have pulled these: 'ollama pull mistral', 'ollama pull phi3:mini'
MODELS = ["phi3:mini"]

def run_evaluation():
    results = []
    
    print("🚀 Starting Comparative Evaluation...")
    
    for model_name in MODELS:
        print(f"\n🤖 Loading Model: {model_name}...")
        try:
            # Initialize the RAG engine with the specific model
            engine = get_rag_engine(model_name)
            
            for i, question in enumerate(QUESTIONS):
                print(f"   ❓ Q{i+1}: {question[:40]}...")
                
                start_time = time.time()
                try:
                    # Run the query
                    response = engine.query(question)
                    answer_text = str(response)
                    
                    # Capture source nodes (citations)
                    sources = [node.node.metadata.get('file_name', 'Unknown') for node in response.source_nodes]
                    source_str = ", ".join(set(sources))
                    
                except Exception as e:
                    answer_text = f"ERROR: {str(e)}"
                    source_str = "N/A"
                
                elapsed = time.time() - start_time
                
                # Save data
                results.append({
                    "Model": model_name,
                    "Question": question,
                    "Answer": answer_text,
                    "Sources": source_str,
                    "Time_Sec": round(elapsed, 2)
                })
                
        except Exception as e:
            print(f"❌ Failed to load {model_name}: {e}")

    # --- 3. SAVE RESULTS TO CSV ---
    df = pd.DataFrame(results)
    output_file = "results/experiment_results.csv"
    
    # Ensure results folder exists
    import os
    os.makedirs("results", exist_ok=True)
    
    df.to_csv(output_file, index=False)
    print(f"\n✅ Evaluation Complete! Results saved to {output_file}")
    print("👉 You can now open this CSV in Excel to build your comparison tables.")

if __name__ == "__main__":
    run_evaluation()