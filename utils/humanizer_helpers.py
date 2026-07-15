# utils/humanizer_helpers.py
import random
import re
import ssl
import warnings
import nltk
import spacy
from nltk.corpus import wordnet
from nltk.tokenize import sent_tokenize, word_tokenize

warnings.filterwarnings("ignore", category=FutureWarning)

########################################
# Download needed NLTK resources
########################################
def download_nltk_resources():
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

    resources = ['punkt', 'averaged_perceptron_tagger',
                 'punkt_tab', 'wordnet', 'averaged_perceptron_tagger_eng']
    for r in resources:
        nltk.download(r, quiet=True)

download_nltk_resources()

########################################
# Prepare spaCy pipeline
########################################
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    warnings.warn("spaCy en_core_web_sm model not found. Run: python -m spacy download en_core_web_sm")
    nlp = None

########################################
# Citation Regex
########################################
CITATION_REGEX = re.compile(
    r"\(\s*[A-Za-z&\-,\.\s]+(?:et al\.\s*)?,\s*\d{4}(?:,\s*(?:pp?\.\s*\d+(?:-\d+)?))?\s*\)"
)

########################################
# Helper: Word & Sentence Counts
########################################
def count_words(text):
    return len(word_tokenize(text))

def count_sentences(text):
    return len(sent_tokenize(text))

########################################
# Step 1: Extract & Restore Citations
########################################
def extract_citations(text):
    refs = CITATION_REGEX.findall(text)
    placeholder_map = {}
    replaced_text = text
    for i, r in enumerate(refs, start=1):
        placeholder = f"[[REF_{i}]]"
        placeholder_map[placeholder] = r
        replaced_text = replaced_text.replace(r, placeholder, 1)
    return replaced_text, placeholder_map

PLACEHOLDER_REGEX = re.compile(r"\[\s*\[\s*REF_(\d+)\s*\]\s*\]")

def restore_citations(text, placeholder_map):
    def replace_placeholder(match):
        idx = match.group(1)
        key = f"[[REF_{idx}]]"
        return placeholder_map.get(key, match.group(0))

    restored = PLACEHOLDER_REGEX.sub(replace_placeholder, text)
    return restored

########################################
# Step 2: Expansions, Synonyms, & Transitions
########################################
WHOLE_CONTRACTIONS = {
    "can't": "cannot",
    "won't": "will not",
    "shan't": "shall not",
    "ain't": "is not",
    "i'm": "i am",
    "it's": "it is",
    "we're": "we are",
    "they're": "they are",
    "you're": "you are",
    "he's": "he is",
    "she's": "she is",
    "that's": "that is",
    "there's": "there is",
    "what's": "what is",
    "who's": "who is",
    "let's": "let us",
    "didn't": "did not",
    "doesn't": "does not",
    "don't": "do not",
    "couldn't": "could not",
    "shouldn't": "should not",
    "wouldn't": "would not",
    "isn't": "is not",
    "aren't": "are not",
    "weren't": "were not",
    "hasn't": "has not",
    "haven't": "have not",
    "hadn't": "had not",
}

SUFFIX_CONTRACTIONS = {
    "n't": " not",
    "'re": " are",
    "'s": " is",
    "'ll": " will",
    "'ve": " have",
    "'d": " would",
    "'m": " am"
}

ACADEMIC_TRANSITIONS = [
    "Moreover,",
    "Additionally,",
    "Furthermore,",
    "Hence,",
    "Therefore,",
    "Consequently,",
    "Nonetheless,",
    "Nevertheless,",
    "In contrast,",
    "On the other hand,",
    "In addition,",
    "As a result,",
]

def expand_contractions(sentence):
    def _replace_whole_with_quotes(match):
        open_tok = match.group(1) or ""
        word = match.group('word')
        close_tok = match.group(3) or ""
        key = word.lower()
        repl = WHOLE_CONTRACTIONS.get(key, word)
        if word and word[0].isupper():
            repl = repl.capitalize()
        return f"{open_tok}{repl}{close_tok}"

    alt = "|".join(re.escape(k) for k in WHOLE_CONTRACTIONS.keys())
    whole_pattern = rf"(?:(``)\s*)?(?P<word>(?:{alt}))(?:\s*(''))?"

    sentence = re.sub(whole_pattern, _replace_whole_with_quotes,
                      sentence, flags=re.IGNORECASE)

    tokens = word_tokenize(sentence)
    out_tokens = []
    for t in tokens:
        lower_t = t.lower()
        replaced = False
        for contr, expansion in SUFFIX_CONTRACTIONS.items():
            if lower_t.endswith(contr):
                base = lower_t[: -len(contr)]
                new_t = base + expansion
                if t and t[0].isupper():
                    new_t = new_t.capitalize()
                out_tokens.append(new_t)
                replaced = True
                break
        if not replaced:
            out_tokens.append(t)
    return " ".join(out_tokens)

def replace_synonyms(sentence, p_syn=0.2):
    if not nlp:
        return sentence

    doc = nlp(sentence)
    new_tokens = []
    for token in doc:
        if "[[REF_" in token.text:
            new_tokens.append(token.text)
            continue
        if token.pos_ in ["ADJ", "NOUN", "VERB", "ADV"] and wordnet.synsets(token.text):
            if random.random() < p_syn:
                synonyms = get_synonyms(token.text, token.pos_)
                if synonyms:
                    new_tokens.append(random.choice(synonyms))
                else:
                    new_tokens.append(token.text)
            else:
                new_tokens.append(token.text)
        else:
            new_tokens.append(token.text)
    return " ".join(new_tokens)

def add_academic_transition(sentence, p_transition=0.2):
    if random.random() < p_transition:
        transition = random.choice(ACADEMIC_TRANSITIONS)
        return f"{transition} {sentence}"
    return sentence

def get_synonyms(word, pos):
    wn_pos = None
    if pos.startswith("ADJ"):
        wn_pos = wordnet.ADJ
    elif pos.startswith("NOUN"):
        wn_pos = wordnet.NOUN
    elif pos.startswith("ADV"):
        wn_pos = wordnet.ADV
    elif pos.startswith("VERB"):
        wn_pos = wordnet.VERB

    synonyms = set()
    if wn_pos:
        for syn in wordnet.synsets(word, pos=wn_pos):
            for lemma in syn.lemmas():
                lemma_name = lemma.name().replace("_", " ")
                if lemma_name.lower() != word.lower():
                    synonyms.add(lemma_name)
    return list(synonyms)

########################################
# Step 3: Minimal "Humanize" line-by-line
########################################
def minimal_humanize_line(line, p_syn=0.2, p_trans=0.2):
    line = expand_contractions(line)
    line = replace_synonyms(line, p_syn=p_syn)
    line = add_academic_transition(line, p_transition=p_trans)
    return line

def minimal_rewriting(text, p_syn=0.2, p_trans=0.2):
    lines = sent_tokenize(text)
    out_lines = [
        minimal_humanize_line(ln, p_syn=p_syn, p_trans=p_trans) for ln in lines
    ]
    return " ".join(out_lines)

def preserve_linebreaks_rewrite(text, p_syn=0.2, p_trans=0.2):
    """Rewrite text while preserving original line breaks.

    Splits the input on newline characters and rewrites each non-empty line
    independently, keeping blank lines and original line structure.
    """
    lines = text.splitlines()
    out_lines = []
    for ln in lines:
        if not ln.strip():
            out_lines.append("")
        else:
            out_lines.append(minimal_rewriting(
                ln, p_syn=p_syn, p_trans=p_trans))
    return "\n".join(out_lines)
