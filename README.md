# RSS Feed Summarizer 🤖📰

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-green.svg)](https://openai.com/)

An intelligent RSS feed processor that uses a **6-agent AI pipeline** to fetch, filter, rank, summarize, and distribute AI technology news.

## ✨ What It Does

- Fetches articles from 20+ AI/tech RSS feeds
- Uses AI to filter for relevant content
- Categorizes articles into Tools, Models, Enterprise, and Market
- Ranks articles by importance
- Generates concise summaries
- Sends beautiful email digests or saves markdown files

## 🚀 Quick Start

### 1. Install

```bash
git clone https://github.com/yourusername/rss-feed-summarizer.git
cd rss-feed-summarizer
pip install -r requirements.txt
```

### 2. Configure

```bash
# Create your config file
cp .env.example .env

# Edit with your settings
nano .env
```

**Required:**
```env
OPENAIAPIKEY=your_openai_api_key_here
```

**Optional (for email):**
```env
SMTP_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_gmail_app_password
EMAIL_RECIPIENTS=recipient1@example.com,recipient2@example.com
```

### 3. Run

```bash
# Run the summarizer
python pipeline.py

# Or use the CLI
rss-summarizer run
```

## 📊 Example Output

The summarizer creates beautiful markdown files in the `output/` directory:

```markdown
# AI News Digest - 2024-01-15

## 📊 Daily Overview
Today's AI landscape shows significant developments in enterprise adoption...

## 🛠️ Tools And Frameworks (3)
**[LangChain 0.1.0 Released](https://blog.langchain.dev/...)**
*Source: LangChain Blog*
LangChain 0.1.0 introduces new agent capabilities and improved memory...

## ⚡ Models And Infrastructure (4)
**[GPT-4 Turbo Performance Analysis](https://openai.com/blog/...)**
*Source: OpenAI Blog*
New benchmarks show GPT-4 Turbo achieving 95% accuracy on...
```

## 💰 Cost

- **Daily digest**: ~$0.50-2.00 (depending on article volume)
- **With caching**: 50-80% cost reduction on subsequent runs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Commit: `git commit -m 'Add amazing feature'`
5. Push: `git push origin feature/amazing-feature`
6. Open a Pull Request

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Made with ❤️ for the AI community** 