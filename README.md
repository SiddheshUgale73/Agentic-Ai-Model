# Institute AI Assistant (RAG & Agentic)

A sophisticated AI-powered enquiry system designed for educational institutes. It combines **Retrieval-Augmented Generation (RAG)** for factual knowledge with an **Agentic Counselor** for personalized student guidance, course enrollments, and fee calculations.

## 🚀 Features

- **Intellectual RAG Engine**: Instantly answers questions based on uploaded documents (PDF, Word, Excel).
- **Lead AI Counselor**: An autonomous agent that handles:
  - **Course Discovery**: Searches and recommends courses based on student interest.
  - **Dynamic Fee Calculation**: Estimates total fees based on course duration and base rates.
  - **Automated Enrollments**: Directly registers students into the system and sends email confirmations.
  - **Roadmap Generation**: Provides 6-month learning paths for various technologies.
- **Unified Frontend**: Includes both a student-facing chatbot interface and an admin dashboard for document indexing.

---

## 🏗️ Project Structure

```text
Institute chat bot/
├── app/
│   ├── main.py             # FastAPI entry point
│   ├── agent.py            # Agentic AI counselor logic (ReAct loop)
│   ├── services.py         # RAG pipeline & LLM Integration
│   ├── schemas.py          # Pydantic data models
│   └── db/                 # Vector database management
├── data/
│   ├── courses.csv         # Course catalog
│   ├── enrollments.json    # Student registration records
│   ├── uploads/            # Indexed documents
│   └── vectors/            # FAISS index and text chunks
├── static/
│   ├── index.html          # Student Chat UI
│   ├── admin.html          # Admin Document Upload UI
│   ├── css/ & js/          # Frontend assets
└── requirements.txt        # Backend dependencies
```

---

## 🛠️ Getting Started

### 1. Requirements
- Python 3.8+
- [Groq API Key](https://console.groq.com/keys) (for Llama 3 models)

### 2. Installation
```powershell
# Clone the repository
git clone <repository-url>
cd "Institute chat bot"

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory (use `.env.example` as a template):
```env
GROQ_API_KEY=your_api_key_here
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
```

### 4. Running the Application
```powershell
python -m app.main
```
The server will start at `http://127.0.0.1:8000`. 
- Open `http://127.0.0.1:8000/` for the Chatbot.
- Open `http://127.0.0.1:8000/admin.html` for the Admin Dashboard.

---

## 🧪 Technology Stack
- **Backend**: FastAPI
- **LLM**: Groq (Llama-3.1-8b)
- **Embeddings**: Sentence-Transformers (all-MiniLM-L6-v2)
- **Vector DB**: FAISS (Meta AI)
- **Frontend**: Vanilla JS, HTML, CSS
