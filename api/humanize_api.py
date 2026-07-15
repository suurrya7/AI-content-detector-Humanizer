from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import re

# Import processing helpers from the shared module
from utils.humanizer_helpers import (
    extract_citations,
    restore_citations,
    minimal_rewriting,
    preserve_linebreaks_rewrite,
    count_words,
    count_sentences,
)

DESCRIPTION = (
    """
Academic Wizard API

This API provides server-side access to the text rewriting and enhancement pipeline. It accepts
AI-generated or draft text and returns an enhanced, more natural, academic version while preserving
citations and structure. The endpoint exposes options to control synonym replacement
intensity and the frequency of added academic transitions.
"""
)

tags_metadata = [
    {
        "name": "enhance",
        "description": "Endpoints for transforming draft/AI text into refined academic prose.",
    }
]

app = FastAPI(
    title="Academic Wizard API",
    version="0.2",
    description=DESCRIPTION,
    openapi_tags=tags_metadata,
)


class EnhanceRequest(BaseModel):
    text: str = Field(..., description="The input text to enhance. Must be non-empty.")
    p_syn: Optional[float] = Field(0.2, ge=0.0, le=1.0, description="Synonym replacement intensity (0.0-1.0)")
    p_trans: Optional[float] = Field(0.2, ge=0.0, le=1.0, description="Academic transition insertion probability (0.0-1.0)")
    preserve_linebreaks: Optional[bool] = Field(True, description="Whether to preserve original line breaks")

    class Config:
        schema_extra = {
            "example": {
                "text": "Recent studies (Smith et al., 2020) show promising results. It can't be ignored.",
                "p_syn": 0.3,
                "p_trans": 0.2,
                "preserve_linebreaks": True,
            }
        }


class EnhanceResponse(BaseModel):
    enhanced_text: str = Field(..., description="The transformed academic text result")
    orig_word_count: int
    orig_sentence_count: int
    new_word_count: int
    new_sentence_count: int
    words_added: int
    sentences_added: int

    class Config:
        schema_extra = {
            "example": {
                "enhanced_text": "Moreover, Recent studies (Smith et al., 2020) show promising results. It cannot be ignored.",
                "orig_word_count": 11,
                "orig_sentence_count": 2,
                "new_word_count": 13,
                "new_sentence_count": 3,
                "words_added": 2,
                "sentences_added": 1,
            }
        }


@app.get("/health", tags=["enhance"], summary="Health check")
def health():
    """Returns OK when the service is healthy.

    Useful for simple uptime checks.
    """
    return {"status": "ok"}


@app.post(
    "/enhance",
    response_model=EnhanceResponse,
    tags=["enhance"],
    summary="Enhance input text academically",
    response_description="The transformed text and basic metrics",
)
def enhance(req: EnhanceRequest):
    """Transform draft or AI-generated text into refined academic prose.

    The endpoint will:
    - Preserve and protect citation strings (e.g., APA style) while rewriting
    - Optionally preserve original line breaks
    - Expand contractions, replace synonyms, and optionally add academic transitions

    Provide `p_syn` and `p_trans` to tune intensity of synonym replacement and
    transition insertion respectively (values between 0.0 and 1.0).
    """
    text = req.text or ""
    if not text.strip():
        raise HTTPException(status_code=400, detail="`text` must be a non-empty string")

    # Original stats
    orig_wc = count_words(text)
    orig_sc = count_sentences(text)

    # Protect citations
    no_refs_text, placeholders = extract_citations(text)

    # Choose rewrite mode
    if req.preserve_linebreaks:
        rewritten = preserve_linebreaks_rewrite(no_refs_text, p_syn=req.p_syn, p_trans=req.p_trans)
    else:
        rewritten = minimal_rewriting(no_refs_text, p_syn=req.p_syn, p_trans=req.p_trans)

    # Restore citations and normalize spacing similar to Streamlit page
    final_text = restore_citations(rewritten, placeholders)
    final_text = re.sub(r"[ \t]+([.,;:!?])", r"\1", final_text)
    final_text = re.sub(r"(\()[ \t]+", r"\1", final_text)
    final_text = re.sub(r"[ \t]+(\))", r"\1", final_text)
    final_text = re.sub(r"[ \t]{2,}", " ", final_text)
    final_text = re.sub(r"``\s*(.+?)\s*''", r'"\1"', final_text)

    new_wc = count_words(final_text)
    new_sc = count_sentences(final_text)

    return {
        "enhanced_text": final_text,
        "orig_word_count": orig_wc,
        "orig_sentence_count": orig_sc,
        "new_word_count": new_wc,
        "new_sentence_count": new_sc,
        "words_added": new_wc - orig_wc,
        "sentences_added": new_sc - orig_sc,
    }


# if __name__ == "__main__":
#     # Quick developer run: python api/humanize_api.py
#     import uvicorn

#     uvicorn.run("api.humanize_api:app", host="127.0.0.1", port=8000, reload=True)
