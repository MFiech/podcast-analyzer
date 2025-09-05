# 🎙️ Podcast Summarizer with Langfuse Integration

A powerful, AI-driven podcast analysis tool that downloads, transcribes, cleans, and summarizes podcast episodes using OpenAI GPT-4o-mini. Features advanced observability with **Langfuse integration** for prompt management, sessions tracking, and detailed LLM observability.

## ✨ Features

### 🎯 Core Functionality
- **📥 Download**: Automatic podcast episode downloading from URLs
- **🎵 Transcription**: Audio-to-text conversion using Whisper
- **🧹 Cleaning**: Intelligent transcript cleaning and processing
- **🤖 AI Summarization**: Structured summaries using OpenAI GPT-4o-mini
- **💾 Database**: MongoDB storage for episodes and metadata
- **🌐 Web Interface**: Browse and manage your podcast library

### 📊 Advanced Observability (Langfuse Integration)
- **🔗 Sessions**: Group related podcast episodes together
- **📋 Prompt Management**: Centralized, versioned prompts with A/B testing
- **📈 Rich Tracing**: Detailed input/output capture for every operation
- **💰 Cost Tracking**: Monitor OpenAI token usage and costs
- **⚡ Performance**: Processing time analysis and optimization insights

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MongoDB
- Redis (for Celery task queue)
- FFmpeg (for audio processing)
- OpenAI API key
- Langfuse instance (optional but recommended)

### 1. Installation

```bash
# Clone the repository
git clone git@github.com:MFiech/podcast-analyzer.git
cd podcast-analyzer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file in the root directory:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-your-openai-api-key

# Langfuse Configuration (Optional - for advanced observability)
LANGFUSE_SECRET_KEY=sk-lf-your-secret-key
LANGFUSE_PUBLIC_KEY=pk-lf-your-public-key
LANGFUSE_HOST=http://localhost:4000
LANGFUSE_ENABLED=true

# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017/podcast_db

# Redis Configuration (for Celery)
CELERY_BROKER_URL=redis://localhost:6379/0
```

### 3. Set Up Langfuse Prompts (Recommended)

```bash
# Initialize Langfuse prompts for better prompt management
python setup_prompts.py
```

### 4. Start Services

```bash
# Start Celery worker (in one terminal)
celery -A celery_app worker --loglevel=info

# Start the web interface (in another terminal)
python -m http.server 8000 --directory web
```

### 5. Analyze a Podcast

```bash
# Analyze a single episode
python podcast_analyzer.py analyze "https://www.youtube.com/watch?v=EPISODE_ID"

# Or use the web interface at http://localhost:8000
```

## 📖 Usage Examples

### Basic Analysis
```bash
# Analyze a podcast episode
python podcast_analyzer.py analyze "https://podcast-url.com/episode"

# Force re-analysis of existing episode
python podcast_analyzer.py analyze "https://podcast-url.com/episode" --force
```

### Advanced Features with Langfuse

```python
from summarizer import PodcastSummarizer
from tasks import analyze_episode

# The summarizer automatically uses Langfuse for:
# - Prompt management (centralized prompts)
# - Session tracking (groups related episodes)
# - Rich observability (detailed traces)

# Analyze with full observability
result = analyze_episode("https://podcast-url.com/episode")
```

## 🏗️ Architecture

### Core Components

```
📦 Podcast Summarizer
├── 🎵 downloader.py     # YouTube/podcast downloading
├── 📝 transcriber.py    # Whisper audio transcription  
├── 🧹 cleaner.py        # Transcript cleaning & processing
├── 🤖 summarizer.py     # AI summarization with Langfuse
├── 💾 database.py       # MongoDB operations
├── ⚡ tasks.py          # Celery background tasks
└── 🌐 web/              # Web interface
```

### Langfuse Integration Flow

```
Episode URL → Download → Transcribe → Clean → Summarize
     ↓            ↓          ↓         ↓         ↓
Session Tracking → Span → Span → Span → Generation (LLM)
     ↓
Langfuse Dashboard (Sessions, Prompts, Traces, Costs)
```

## 🎛️ Configuration Options

### Summarization Prompts

The app uses **Langfuse Prompt Management** for intelligent, versioned prompts:

- **`podcast-analyzer-system`**: System instructions for the AI
- **`podcast-summarization-user`**: Main template with variables (`{{title}}`, `{{transcript}}`)
- **`podcast-chat-template`**: Chat-format prompts
- **`podcast-quick-summary`**: Shorter summary format

Edit prompts in your Langfuse dashboard at `http://localhost:4000/prompts`

### Processing Settings

```python
# In summarizer.py - customize these settings:
MODEL = "gpt-4o-mini"        # OpenAI model
TEMPERATURE = 0.7            # Creativity (0.0-1.0)
MAX_TOKENS = 2000           # Maximum response length
```

## 📊 Observability & Analytics

### Langfuse Dashboard Features

1. **Sessions**: `http://localhost:4000/sessions`
   - View grouped podcast episodes
   - Track processing workflows
   - Analyze user journeys

2. **Prompts**: `http://localhost:4000/prompts` 
   - Manage prompt versions
   - A/B test different approaches
   - Collaborate on prompt improvements

3. **Traces**: `http://localhost:4000/traces`
   - Detailed processing breakdowns
   - Input/output inspection
   - Performance optimization

4. **Generations**: `http://localhost:4000/generations`
   - LLM call monitoring
   - Token usage & costs
   - Quality assessment

### Sample Analytics

```bash
# View session analytics
Session: podcast_analyzer_session
├── Episode 1: "AI in Product Management" (7.04s, 1076 tokens)
├── Episode 2: "Startup Funding 2024" (5.92s, 1101 tokens)  
└── Episode 3: "Developer Tools" (6.23s, 987 tokens)

Total Cost: $0.048
Avg Speed: 167 tokens/second
Success Rate: 100%
```

## 🧪 Testing

```bash
# Test basic functionality
python test_langfuse_simple.py

# Test Sessions + Prompt Management integration  
python test_full_integration.py

# Test session concepts
python test_sessions.py
```

## 📁 Project Structure

```
podcast-analyzer/
├── 📄 README.md                    # This file
├── ⚙️ requirements.txt             # Python dependencies
├── 🐳 docker-compose.yml           # Docker setup
├── 📋 .env.example                 # Environment template
├── 🎵 Core Processing/
│   ├── downloader.py               # Audio downloading
│   ├── transcriber.py              # Speech-to-text
│   ├── cleaner.py                  # Transcript processing
│   └── summarizer.py               # AI summarization
├── 🗄️ Data Management/
│   ├── database.py                 # MongoDB operations
│   ├── tasks.py                    # Background jobs
│   └── celery_app.py              # Task queue config
├── 🌐 Interface/
│   ├── podcast_analyzer.py        # CLI interface
│   └── web/                       # Web dashboard
├── 🧪 Testing & Setup/
│   ├── setup_prompts.py           # Initialize Langfuse prompts
│   ├── test_langfuse_simple.py    # Basic integration tests
│   ├── test_full_integration.py   # Advanced feature tests
│   └── test_sessions.py           # Session concept demos
└── 📊 Observability/
    ├── LANGFUSE_INTEGRATION.md     # Detailed Langfuse guide
    └── demo_sessions.py            # Session usage examples
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **OpenAI** for GPT-4o-mini API
- **Langfuse** for LLM observability platform  
- **Whisper** for speech-to-text capabilities
- **Celery** for distributed task processing
- **MongoDB** for document storage

## 📞 Support

- 🐛 [Report Issues](https://github.com/MFiech/podcast-analyzer/issues)
- 💬 [Discussions](https://github.com/MFiech/podcast-analyzer/discussions)
- 📚 [Documentation](./LANGFUSE_INTEGRATION.md)

---

Built with ❤️ using OpenAI, Langfuse, and modern Python tools.