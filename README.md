# AI Scientist Challenge Code Scanner

Automated code review tool for AI Scientist Challenge submissions using Claude Agent SDK.

> **Important Notice:** This tool is provided for participants' self-review only and is NOT the official code scanner used by the organizing committee. Passing this tool's checks does not guarantee approval by the official review process. All submissions are subject to the official competition rules.

## Requirements

- Node.js and npm (for Claude Code CLI)
- Python 3.8+
- DeepSeek API key from [DeepSeek Platform](https://platform.deepseek.com/)

## Installation

```bash
# 1. Install Claude Code CLI (required by claude-agent-sdk)
npm install -g @anthropic-ai/claude-code

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Set DeepSeek API configuration
export ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
export ANTHROPIC_API_KEY='your-deepseek-api-key'
export ANTHROPIC_MODEL=deepseek-chat
```

## Usage

### Scan submission code

```bash
python scan.py /path/to/submission <track> -o report.json

# Available tracks: literature_review | paper_qa | ideation | paper_review
```

### Format JSON report

```bash
python format_report.py report.json
```

## What it checks

- File structure (Dockerfile, docker-compose.yml)
- API endpoint implementation
- Model usage compliance
- Network access (whitelisted academic APIs only)
- Environment variable usage
