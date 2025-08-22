# lean

## Features

- **Simple Workflow**: Take a screenshot, get an answer
- **Rich Output**: Rendered Markdown with LaTeX equations and highlighted code blocks

## Requirements

- A Google Gemini API key
- Nix package manager (for installation)

## Usage

1. **Launch lean**: Run the app and enter your Gemini API key when prompted
2. **Select mode**: Choose "Short" for quick answers or "Long" for detailed explanations
3. **Take screenshot**: Click the ask button to select a screen region containing your question
4. **View results**: Get your AI-generated answer

## Run

### Run from GitHub

```bash
nix run github:vipulog/lean
```

### Run locally

```bash
nix run .
```
