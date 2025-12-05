Comparative Analysis of Open-Source LLMs on RAG Tasks

📄 Abstract

This project evaluates the performance of three prominent open-source Large Language Models (LLMs)—Meta's Llama-3 8B, Mistral 7B, and Microsoft's Phi-3 Mini—within a Retrieval-Augmented Generation (RAG) pipeline. The primary objective is to assess their suitability for financial reasoning and retrieval tasks in resource-constrained environments.

We benchmarked the models on a dataset of queries derived from 10-K financial reports (e.g., NVIDIA, Amazon, Google), focusing on Accuracy, Latency, and Hallucination Rate.

📊 Key Findings

Model

Avg Accuracy (1-5)

Avg Latency (s)

Hallucinations

Recommendation

llama3:8b

3.0

5.86

1

Best All-Rounder (Fast & Accurate)

mistral

3.0

23.60

1

Good accuracy, but significantly slower

phi3:mini

2.6

55.53

0

Best for Safety (Zero Hallucinations)

🛠️ Project Architecture

The system utilizes a RAG workflow to answer user queries based on ingested financial documents.

graph TD
    UserQuery[User Query] --> Embed[Embedding Model]
    Embed --> VectorDB[(Vector DB)]
    VectorDB --> Context[Retrieved Context]
    Context --> LLM{LLM Inference}
    LLM --> Response[Generated Answer]
    
    subgraph Models
    L[Llama-3 8B]
    M[Mistral 7B]
    P[Phi-3 Mini]
    end


📂 Repository Structure

├── Final_Project_Data.csv        # The dataset containing model responses and metrics
├── genrate_table_results.py      # Script to analyze data and generate summary tables
├── Project_Report.md             # Detailed comparative analysis report
├── README.md                     # Project documentation
└── requirements.txt              # Python dependencies


🚀 Getting Started

Prerequisites

Python 3.8 or higher

pandas

tabulate (optional, for pretty printing tables)

Installation

Clone the repository

git clone [https://github.com/yourusername/llm-comparative-analysis.git](https://github.com/yourusername/llm-comparative-analysis.git)
cd llm-comparative-analysis


Install dependencies

pip install pandas tabulate


Usage

To reproduce the analysis table and view the failure cases, run the analysis script:

python genrate_table_results.py


This will:

Read the Final_Project_Data.csv.

Calculate aggregate metrics (Mean Accuracy, Total Hallucinations, etc.).

Generate a model_comparison_summary.csv file.

Print a comparative table and a breakdown of failure cases to the console.

📚 References

This project builds upon foundational research in scaling laws and efficient language modeling:

Abdin, M., et al. (2024). Phi-3 Technical Report: A Highly Capable Language Model Locally on Your Phone. arXiv preprint arXiv:2404.14219.

Gunasekar, S., et al. (2023). Textbooks are all you need. arXiv preprint arXiv:2306.11644.

Jiang, A. Q., et al. (2023). Mistral 7B. arXiv preprint arXiv:2310.06825.

Kaplan, J., et al. (2020). Scaling laws for neural language models. arXiv preprint arXiv:2001.08361.

Meta AI. (2024). The Llama 3 Herd of Models. arXiv preprint arXiv:2407.21783.

Touvron, H., et al. (2023). Llama: Open and efficient foundation language models. arXiv preprint arXiv:2302.13971.

📝 License

This project is licensed under the MIT License - see the LICENSE file for details.
