# AI Text Humanizer & Enhancer

A streamlined web application and API designed for text humanization. Convert AI-generated text into natural, human-like writing while preserving academic integrity and citations.

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white)

## 🚀 Features

### ✍️ AI Text Humanization
- **Smart Citation Protection**: Automatically detects and protects academic citations (e.g. APA format) from being altered.
- **Rule-based Enhancements**: Expands contractions, replaces repetitive words with context-appropriate synonyms, and inserts professional transitions.
- **Customizable Intensity**: User-controlled sliders for synonym replacement rate and transition frequency.
- **Line Break Preservation**: Keeps paragraphs and line breaks formatted exactly like the input.
- **Fast & Private**: Runs completely locally (on your machine or private server) with no external API calls required.

### 🌐 Dual Interfaces
- **Streamlit Web UI**: Simple, user-friendly interactive interface.
- **FastAPI Endpoint**: Production-ready API for programmatic integration.

---

## 🛠️ Technologies Used

### Core Frameworks
- **Streamlit** - Web UI frontend
- **FastAPI & Uvicorn** - API server framework
- **Python 3.8+** - Core language

### Natural Language Processing
- **spaCy** - Part-Of-Speech (POS) tagging and lemmatization
- **NLTK** - Sentence tokenization and WordNet synonyms

---

## 💻 Local Setup

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd AI-content-detector-Humanizer
   ```

2. **Run setup script (installs dependencies, downloads NLTK and spaCy models):**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Run Streamlit Web UI:**
   ```bash
   streamlit run main.py
   ```

4. **Run FastAPI Server:**
   ```bash
   uvicorn api.humanize_api:app --reload
   ```
