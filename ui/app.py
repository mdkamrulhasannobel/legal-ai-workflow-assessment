import os
import tempfile
from pathlib import Path

import streamlit as st

from src.pipeline import LegalWorkflowPipeline
from src.feedback.diff_engine import DiffEngine
from src.feedback.pattern_store import PatternStore

st.set_page_config(page_title="Legal AI Workflow", layout="wide")
st.title("⚖️ Pearson Specter Litt — AI Legal Workflow")

pipeline = LegalWorkflowPipeline()
diff_engine = DiffEngine()
pattern_store = PatternStore()

tab1, tab2, tab3 = st.tabs(["Upload & Process", "Generate Draft", "Edit & Improve"])

with tab1:
    st.header("Upload a Legal Document")
    uploaded_file = st.file_uploader(
        "Choose a PDF or image file",
        type=["pdf", "png", "jpg", "jpeg", "tiff", "bmp"],
    )

    if uploaded_file and st.button("Process Document"):
        with st.spinner("Processing document..."):
            suffix = Path(uploaded_file.name).suffix
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name

            try:
                result = pipeline.process_document(tmp_path)
                st.session_state["doc_result"] = result
                st.success(f"Processed {result['file_name']}")
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Structured Fields")
                    st.json(result["structured_fields"])
                with col2:
                    st.subheader("Raw Text Preview")
                    st.text_area("Extracted Text", result["raw_text"][:2000], height=300)
                st.info(f"OCR used: {result['used_ocr']} | Chunks indexed: {result['num_indexed']}")
            finally:
                Path(tmp_path).unlink(missing_ok=True)

with tab2:
    st.header("Generate Draft")
    if "doc_result" not in st.session_state:
        st.warning("Please process a document first (Upload & Process tab)")
    else:
        query = st.text_input(
            "Draft query (optional)",
            placeholder="Draft a case fact summary...",
        )
        if st.button("Generate Draft"):
            with st.spinner("Generating draft..."):
                doc_result = st.session_state["doc_result"]
                draft = pipeline.generate_draft(doc_result, query or None)
                st.session_state["current_draft"] = draft
                st.markdown(draft)
                st.download_button("Download Draft", draft, file_name="draft.txt")

with tab3:
    st.header("Edit & Improve")
    if "current_draft" not in st.session_state:
        st.warning("Please generate a draft first (Generate Draft tab)")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Original Draft")
            original = st.text_area(
                "Original",
                st.session_state["current_draft"],
                height=400,
                key="original_draft",
            )
        with col2:
            st.subheader("Your Edited Version")
            edited = st.text_area(
                "Edited",
                st.session_state["current_draft"],
                height=400,
                key="edited_draft",
            )

        if st.button("Submit Edit & Extract Pattern"):
            if original != edited:
                with st.spinner("Analyzing changes..."):
                    diff_result = diff_engine.compute_diff(original, edited)
                    st.subheader("Diff Summary")
                    st.caption(diff_result["summary"])

                    if diff_result["additions"]:
                        st.write("**Additions:**")
                        for a in diff_result["additions"]:
                            st.text(f"+ {a}")

                    if diff_result["deletions"]:
                        st.write("**Deletions:**")
                        for d in diff_result["deletions"]:
                            st.text(f"- {d}")

                    st.subheader("Learned Pattern")
                    pattern = pipeline.drafter.extract_pattern(diff_result["diff_text"])
                    pattern_store.add_pattern({
                        "rule": pattern,
                        "category": "style",
                        "examples": diff_result["additions"][:3],
                        "active": True,
                    })
                    st.success(f"Pattern learned: {pattern}")

        with st.expander("View Learned Patterns"):
            patterns = pattern_store.load_patterns()
            if patterns:
                for p in patterns:
                    st.text(f"- {p['rule']}")
            else:
                st.text("No patterns learned yet.")
