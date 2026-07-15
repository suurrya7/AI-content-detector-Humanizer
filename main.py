# main.py
import re
import streamlit as st
from utils.humanizer_helpers import (
    count_words,
    count_sentences,
    extract_citations,
    preserve_linebreaks_rewrite,
    restore_citations,
)

def main():
    st.set_page_config(
        page_title="Academic Wizard",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    st.title("🧙‍♂️ Academic Wizard")
    st.markdown("---")

    st.subheader("🎛️ Customize Your Settings")

    col1, col2 = st.columns(2)
    
    with col1:
        p_syn = st.slider(
            "**Synonym Replacement Intensity**", 
            0.0, 1.0, 0.2, 0.05,
            help="Higher values replace more words with synonyms for greater variation"
        )
    
    with col2:
        p_trans = st.slider(
            "**Academic Transition Frequency**", 
            0.0, 1.0, 0.2, 0.05,
            help="Higher values add more transitional phrases for better flow"
        )

    st.subheader("📝 Enter Your Text to Enhance")
    
    input_text = st.text_area(
        "Paste your AI-generated text below:", 
        height=200,
        placeholder="Paste your text here... We'll automatically protect your citations and enhance the writing style.",
        label_visibility="collapsed"
    )

    if st.button("🚀 Run Academic Wizard", type="primary", use_container_width=True):
        if not input_text.strip():
            st.warning("📝 Please enter some text first.")
            return

        # Show original stats
        orig_wc = count_words(input_text)
        orig_sc = count_sentences(input_text)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Original Word Count", orig_wc)
        with col2:
            st.metric("Original Sentence Count", orig_sc)

        with st.spinner("🔍 Analyzing text and protecting citations..."):
            # Extract and protect citations
            no_refs_text, placeholders = extract_citations(input_text)
            
        with st.spinner("✍️ Enhancing writing style and flow..."):
            # Apply humanization while preserving line breaks
            partially_rewritten = preserve_linebreaks_rewrite(
                no_refs_text, p_syn=p_syn, p_trans=p_trans
            )
            
        with st.spinner("✅ Restoring citations and finalizing..."):
            # Restore citations
            final_text = restore_citations(partially_rewritten, placeholders)

            # Normalize spaces around punctuation but do not remove newlines
            final_text = re.sub(r"[ \t]+([.,;:!?])", r"\1", final_text)
            final_text = re.sub(r"(\()[ \t]+", r"\1", final_text)
            final_text = re.sub(r"[ \t]+(\))", r"\1", final_text)
            # Collapse multiple spaces/tabs (but keep newlines)
            final_text = re.sub(r"[ \t]{2,}", " ", final_text)
            # Normalize paired tokenized quotes: `` ... '' -> "..." (remove stray spaces)
            final_text = re.sub(r"``\s*(.+?)\s*''", r'"\1"', final_text)

        # Calculate new stats
        new_wc = count_words(final_text)
        new_sc = count_sentences(final_text)

        st.subheader("🎉 Your Enhanced Text")

        st.success(f"✅ Successfully enhanced your text! Added **{new_wc - orig_wc} words** and **{new_sc - orig_sc} sentences** for better flow.")

        # Single editable output box that preserves original line breaks and paragraphs
        st.text_area(
            "Enhanced Result",
            final_text,
            height=300,
            label_visibility="collapsed"
        )

        # Copy to clipboard functionality
        st.download_button(
            "📋 Download Enhanced Text",
            data=final_text,
            file_name="enhanced_text.txt",
            mime="text/plain",
            use_container_width=True
        )

        st.markdown("""
        ### 📊 Enhancement Summary
        """)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Words Added", new_wc - orig_wc, delta="Enhancement")
        with col2:
            st.metric("Sentences Added", new_sc - orig_sc, delta="Flow")
        with col3:
            st.metric("Final Word Count", new_wc)
        with col4:
            st.metric("Final Sentence Count", new_sc)

if __name__ == "__main__":
    main()
