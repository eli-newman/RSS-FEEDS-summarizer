# AI Technology News Digest

An intelligent RSS feed processor that fetches, filters, ranks, summarizes, and distributes AI technology news.

## Features

- Fetches articles from multiple tech news sources
- Uses keyword filtering and LLM-based categorization
- Ranks articles by importance within each category
- Generates concise, informative summaries using GPT-4
- Distributes beautifully formatted email digests
- Implements caching to reduce API costs
- Supports multiple recipients with privacy (BCC)

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file from the example:
```bash
cp .env.example .env
```

3. Configure your environment variables in `.env`:
- Add your OpenAI API key
- Set your email sender address
- Add recipient email addresses
- Optionally adjust other settings

## Usage

Run the pipeline:
```bash
python pipeline.py
```

This will:
1. Fetch recent articles from configured RSS feeds
2. Filter and categorize articles using keywords and LLM
3. Select top 5 articles per category
4. Generate summaries for selected articles
5. Send a formatted digest to configured recipients

## Configuration

Edit `config.py` to customize:
- RSS feed sources
- Time window for article freshness
- Article categories and keywords
- Model settings (GPT-4 vs GPT-3.5-turbo)

## Cost Optimization

The pipeline implements several cost-saving measures:
- Caches LLM responses to avoid duplicate API calls
- Uses keyword pre-filtering before LLM processing
- Limits articles per category
- Supports GPT-3.5-turbo for lower costs

## Contributing

Feel free to submit issues and pull requests! 