# 📄 Transition Triplet Extractor (Streamlit App)

This Streamlit app extracts structured `(paragraph_a, transition, paragraph_b)` triplets from `.docx` documents, using a custom rule-based approach.

## 🔧 Features

- Upload `.docx` files with press articles
- Detect and extract transitions from footers
- Outputs:
  - `fewshot_examples.json`
  - `transitions_only.txt`
  - `repetitions.json`
  - `transitions_only_rejected.txt`
  - `fewshot_examples.jsonl` (for fine-tuning)

## 🚀 Live App

👉 [Visit Streamlit Cloud App](https://your-streamlit-link)

## 🛠 How to Run Locally

1. Clone the repo:
   ```bash
   git clone https://github.com/your-username/transition-triplet-extractor.git
   cd transition-triplet-extractor
