import streamlit as st
from docx import Document
import re
from collections import defaultdict
import json

st.title("📄 Transition Triplet Extractor")
st.write("Upload a .docx file to extract structured (paragraph_a, transition, paragraph_b) triplets.")

uploaded_file = st.file_uploader("Upload a DOCX file", type="docx")

# Helper functions
def extract_articles(paragraphs):
    articles = []
    article = []
    for para in paragraphs:
        if re.match(r"^\d{2,3} du \d{2}/\d{2}", para):
            if article:
                articles.append(article)
                article = []
        article.append(para)
    if article:
        articles.append(article)
    return articles

def extract_transitions_from_footer(article, max_lines=5):
    footer_candidates = article[-max_lines:]
    return [line.strip() for line in footer_candidates if 5 < len(line.strip()) < 100]

def extract_triplets_fuzzy(paragraph_text, transitions_list):
    triplets = []
    matches = []
    for transition in transitions_list:
        transition_clean = transition.strip()
        if not transition_clean:
            continue
        for match in re.finditer(re.escape(transition_clean[:10]), paragraph_text, re.IGNORECASE):
            start_idx = match.start()
            context_window = paragraph_text[start_idx:start_idx+len(transition_clean)+30]
            if transition_clean.lower() in context_window.lower():
                real_start = paragraph_text.lower().find(transition_clean.lower(), start_idx)
                if real_start != -1:
                    matches.append((real_start, real_start + len(transition_clean), transition_clean))
    matches.sort()
    for idx, (start, end, transition) in enumerate(matches):
        prev_end = matches[idx - 1][1] if idx > 0 else 0
        next_start = matches[idx + 1][0] if idx + 1 < len(matches) else len(paragraph_text)
        paragraph_a = paragraph_text[prev_end:start].strip()
        paragraph_b = paragraph_text[end:next_start].strip()
        if paragraph_a and paragraph_b:
            triplets.append({
                "paragraph_a": paragraph_a[:200],
                "transition": transition,
                "paragraph_b": paragraph_b[:200]
            })
    return triplets

if uploaded_file:
    doc = Document(uploaded_file)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip() != ""]
    articles = extract_articles(paragraphs)

    triplets_final = []
    transition_usage = defaultdict(int)
    repetitions = defaultdict(int)
    rejected_transitions = set()
    transition_set = set()

    for article in articles:
        transitions = extract_transitions_from_footer(article)
        transition_set.update(transitions)
        large_para_index = next((i for i, line in enumerate(article) if line.startswith("À savoir ")), None)
        if large_para_index is not None and large_para_index + 1 < len(article):
            long_paragraph = " ".join(article[large_para_index + 1:-len(transitions)])
            extracted = extract_triplets_fuzzy(long_paragraph, transitions)
            for triplet in extracted:
                tran = triplet["transition"]
                transition_usage[tran] += 1
                if transition_usage[tran] <= 3:
                    triplets_final.append(triplet)
                else:
                    repetitions[tran] += 1
                    rejected_transitions.add(tran)

    transitions_only = sorted(set(transition_usage.keys()) - rejected_transitions)
    transitions_only_rejected = sorted(rejected_transitions)

    st.success(f"Extracted {len(triplets_final)} structured triplets from {len(articles)} articles.")
    st.write("### Preview (first 5 entries):")
    st.json(triplets_final[:5])

    st.download_button("Download fewshot_examples.json", json.dumps(triplets_final, ensure_ascii=False, indent=2), "fewshot_examples.json")
    st.download_button("Download transitions_only.txt", "\n".join(transitions_only), "transitions_only.txt")
    st.download_button("Download repetitions.json", json.dumps(repetitions, ensure_ascii=False, indent=2), "repetitions.json")
    st.download_button("Download transitions_only_rejected.txt", "\n".join(transitions_only_rejected), "transitions_only_rejected.txt")

    jsonl_lines = []
    for triplet in triplets_final:
        jsonl_obj = {
            "messages": [
                {"role": "system", "content": "Insère une courte transition naturelle entre deux paragraphes de presse."},
                {"role": "user", "content": f"Paragraphe A : {triplet['paragraph_a']}\nParagraphe B : {triplet['paragraph_b']}"},
                {"role": "assistant", "content": triplet['transition']}
            ]
        }
        jsonl_lines.append(json.dumps(jsonl_obj, ensure_ascii=False))

    st.download_button("Download fewshot_examples.jsonl", "\n".join(jsonl_lines), "fewshot_examples.jsonl")
