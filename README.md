# 🥔 AskPOTATO - AI-Powered QA Test Management System

A modern, intelligent QA test management system with natural language AI assistant powered by local LLMs.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Features

- **🎯 Test Scenario Management** - Create and organize test scenarios with steps
- **🐞 Defect Tracking** - Log and manage defects linked to specific test steps
- **📎 Evidence Management** - Upload and organize proof files (images, PDFs, documents)
- **🤖 AI Assistant** - Ask questions in natural language using RAG (Retrieval Augmented Generation)
- **📊 Smart Insights** - Get AI-powered answers about your test data
- **🔒 Secure** - Input validation, secure file uploads, parameterized SQL queries
- **📱 Responsive** - Modern, mobile-friendly UI


### Prerequisites

- Python 3.8 or higher
- [Ollama](https://ollama.ai/) installed and running (for AI features)
- `llama3` model pulled in Ollama: `ollama pull llama3`

### Installation

1. **Clone or download this project**

2. **Create virtual environment** (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Initialize database**
```bash
python init_db.py
```

6. **Run the application**
```bash
python app.py
```

7. **Open browser**
```
http://localhost:5000
```

## 📁 Project Structure

```
askpotato/
├── app.py                 # Main Flask application
├── config.py             # Configuration management
├── init_db.py            # Database initialization script
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── askpotato/           # AI module package
│   ├── __init__.py
│   ├── detector.py      # Intent detection
│   ├── explainer.py     # AI explanation generation
│   ├── intents.py       # Supported question types
│   ├── normalizer.py    # Question normalization
│   └── retrieval.py     # Data retrieval functions
├── static/
│   └── style.css        # Modern CSS styling
├── templates/           # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── projects.html
│   ├── scenario_details.html
│   ├── ask.html
│   ├── 404.html
│   └── 500.html
└── uploads/            # Uploaded proof files (created automatically)
```


### Creating a Test Scenario

1. Go to **Projects** page
2. Click **Add New Scenario**
3. Fill in scenario details
4. Click **Create Scenario**
5. 10 steps are automatically created

### Managing Test Steps

1. Click on a scenario name
2. Expand any step to see details
3. Update step status and assignee
4. Add defects or upload proof files
5. Click **Save** to persist changes

### Using the AI Assistant

1. Go to **Ask AI** page
2. Type a natural language question:
   - "List all scenarios"
   - "Which scenario has the most defects?"
   - "Show me all failed steps"
   - "What steps are missing proof?"
3. Get instant AI-powered answers

## 🛠️ Configuration

Edit `.env` file or set environment variables:

```bash
# Flask
SECRET_KEY=your-secret-key          
DEBUG=False                          # Set to False in production

# Database
DATABASE_PATH=potato.db              # SQLite database file

# Uploads
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=5242880           # 5MB in bytes

# Ollama
OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=llama3
OLLAMA_TIMEOUT=120
```

## 🧪 Testing

The application includes error handling and logging. To test:

```bash
# Check database
sqlite3 potato.db ".tables"

# View logs
# Logs are printed to console with INFO level

# Test API endpoint
curl http://localhost:5000/api/scenarios
```

## 📝 Supported Question Types

The AI assistant understands these intent categories:

| Intent | Example Questions |
|--------|------------------|
| **LIST_SCENARIOS** | "List all scenarios", "Show me scenarios" |
| **MOST_DEFECTS_SCENARIO** | "Which scenario has most defects?", "Most buggy scenario" |
| **OPEN_DEFECTS** | "Show open defects", "Pending issues" |
| **FAILED_STEPS** | "What steps failed?", "Show failing steps" |
| **NO_PROOF_STEPS** | "Steps without proof", "Missing evidence" |



### Ollama Connection Error
```
Cannot connect to AI service. Make sure Ollama is running.
```
**Solution:** 
- Install Ollama from https://ollama.ai/
- Run `ollama serve`
- Pull the model: `ollama pull llama3`

### Database Locked
```
database is locked
```
**Solution:** Close any other connections to the database file

### Import Errors
```
ModuleNotFoundError: No module named 'flask'
```
**Solution:** `pip install -r requirements.txt`

**Note:** This project uses local LLMs via Ollama for privacy and offline capability.
