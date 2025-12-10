# Teachable AI

An AI learning system where students teach  concepts to an AI agent instead of the other way around. The AI acts as a confused learner, asking questions and making mistakes for students to correct. In general deeper understanding is promoted through teaching.

## Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key
- Pinecone account

### Installation

```bash
git clone https://github.com/sdragonslayer/teachable-ai-agent
cd teachable-ai
pip install -r requirements.txt
```
### Configuration

Edit `config.py`:

```python
OPENAI_API_KEY = "your-openai-key"
PINECONE_API_KEY = "your-pinecone-key"
```

Create a Pinecone index:
- **Name**: `teachable-ai`
- **Dimensions**: 1536
- **Metric**: cosine

### Run

```bash
python app.py
```

## How To Use

1. **Upload Course Materials** - Add PDFs or text files of lecture notes
2. **Create a Session** - Start teaching a new topic
3. **Teach the AI** - Explain concepts in your own words
4. **Respond to Questions** - Answer the AI's questions and correct its mistakes
5. **Review History** - See past teaching sessions

## Fundamental Components

- **RAG System**: Your uploaded materials are embedded and stored in Pinecone
- **Context Retrieval**: When you teach, relevant materials are retrieved to ground the AI's responses
- **AI Learner**: GPT-5 acts as a confused student, using course materials to ask relevant questions and make realistic mistakes
- **Conversation Storage**: All conversations are stored for instructor review