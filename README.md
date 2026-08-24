# ResumeIQ — AI-Powered Resume Analyser

> Upload your resume, get actionable AI insights, ATS compatibility scores, and a tailored version matched to any job description — all processed in-memory, never stored.

---

## Features

| Feature | Description |
|---|---|
| **Deep Analysis** | Overall resume score (0–100), strengths, weaknesses, missing sections, and a written summary |
| **High-Impact Improvements** | Top 3 prioritised action items to immediately improve your resume |
| **Detailed Issues** | Flags weak action verbs, bullets missing quantifiable metrics, and formatting problems |
| **ATS Scoring** | Hybrid ATS score combining LLM semantic analysis + deterministic keyword overlap |
| **Keyword Analysis** | Visual breakdown of matched vs. missing keywords against the job description |
| **Smart Rewriting** | AI-tailored resume rewrite optimised for a specific role (no fabricated experience) |
| **Download** | Export the tailored resume as a `.txt` file |
| **Privacy-First** | All processing is in-memory — files are deleted immediately after analysis |

---

## Project Structure

```
Resume-Analyser/
├── app.py                  # Streamlit UI — entry point
├── core/
│   ├── analyzer.py         # LLM chains: analyze_resume, score_ats, tailor_resume
│   ├── ats_scorer.py       # Deterministic keyword-overlap ATS scorer
│   └── parser.py           # PDF (pdfplumber) & DOCX (python-docx) text extractor
├── prompts/
│   ├── analyze.txt         # Prompt template for general resume analysis
│   ├── ats_score.txt       # Prompt template for ATS scoring
│   └── tailor.txt          # Prompt template for resume rewriting
├── utils/
│   └── helpers.py          # Token counting (tiktoken) and text truncation
├── .env.example            # Environment variable template
└── requirements.txt        # Python dependencies
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Amandsvv/Resume-Analyser.git
cd Resume-Analyser
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and add your [Groq API key](https://console.groq.com/):

```env
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Run the app

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## How It Works

### Analysis Pipeline

1. **Parse** — `core/parser.py` extracts plain text from the uploaded PDF or DOCX file.
2. **Truncate** — `utils/helpers.py` counts tokens via `tiktoken` and truncates to 4,000 tokens if needed.
3. **Analyse** — `core/analyzer.py` sends the resume text to **Llama 3.3 70B** (via Groq) using a structured prompt, returning a JSON payload with score, summary, strengths, weaknesses, skills, and improvement tips.
4. **ATS Score** *(optional)* — A hybrid score is calculated:
   - **LLM Score**: Groq analyses semantic alignment between resume and JD.
   - **Keyword Score**: `core/ats_scorer.py` performs deterministic keyword-overlap scoring, weighting high-frequency JD terms (mentioned 2+ times) as core requirements.
   - **Combined ATS Score**: Average of the two scores.
5. **Tailor** *(optional)* — A higher-temperature LLM instance rewrites the resume to optimise language, phrasing, and keyword density for the target role.

### Score Reference

| Range | Rating |
|---|---|
| 85 – 100 | ✅ Excellent |
| 70 – 84 | 🟡 Good |
| 50 – 69 | 🟠 Fair |
| 0 – 49  | 🔴 Needs Work |

---

## Tech Stack

| Layer | Technology |
|---|---|
| **UI** | [Streamlit](https://streamlit.io/) with custom CSS (glassmorphism dark theme) |
| **LLM** | [Llama 3.3 70B Versatile](https://groq.com/) via Groq API |
| **LLM Orchestration** | [LangChain](https://python.langchain.com/) (`langchain`, `langchain-groq`) |
| **PDF Parsing** | [pdfplumber](https://github.com/jsvine/pdfplumber) |
| **DOCX Parsing** | [python-docx](https://python-docx.readthedocs.io/) |
| **Tokenisation** | [tiktoken](https://github.com/openai/tiktoken) |
| **Config** | [python-dotenv](https://pypi.org/project/python-dotenv/) |

---

## Dependencies

```
streamlit
langchain
langchain-groq
jsonpatch
jsonpointer
pdfplumber
python-docx
python-dotenv
tiktoken
```

---

## Analysis Modes

Switch between modes in the sidebar:

- **Analyze Only** — General resume feedback with score, strengths, weaknesses, skill tags, and improvement tips.
- **ATS Score + Tailor** — Everything in Analyze Only *plus* ATS compatibility scoring against a pasted job description and an AI-rewritten tailored resume.

---

## Privacy

- Resume files are written to a temporary file, processed, and **immediately deleted** via Python's `tempfile` module.
- No resume data is persisted to disk or any external service beyond the Groq API call.

---

## License

This project is open source. Feel free to fork, improve, and submit pull requests.
