# API Setup Guide - Invoice Cataloger

This guide explains how to configure the Invoice Cataloger to work with different AI providers: LM Studio (local), OpenAI, or OpenRouter.

## Table of Contents
- [Quick Start](#quick-start)
- [LM Studio Setup (Local AI)](#lm-studio-setup-local-ai)
- [OpenAI Setup](#openai-setup)
- [OpenRouter Setup](#openrouter-setup)
- [Custom Prompts](#custom-prompts)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file** and configure your preferred API provider

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Test your configuration:**
   ```bash
   python invoice_cataloger.py --check-only
   ```

---

## LM Studio Setup (Local AI)

**Best for:** Privacy-conscious users, offline processing, no API costs

### Prerequisites
- Download and install [LM Studio](https://lmstudio.ai/)
- Download a model (recommended: Mistral 7B, Llama 2, or similar)

### Configuration

1. **Start LM Studio:**
   - Open LM Studio
   - Load your preferred model
   - Go to "Developer" tab
   - Click "Start Server"
   - Note the server address (usually `http://localhost:1234`)

2. **Configure `.env` file:**
   ```env
   API_PROVIDER=lmstudio
   LM_STUDIO_ENDPOINT=http://localhost:1234/v1/chat/completions
   LM_STUDIO_MODELS_ENDPOINT=http://localhost:1234/v1/models
   LM_STUDIO_MODEL=local-model
   ```

3. **Adjust for network access** (if LM Studio is on another machine):
   ```env
   LM_STUDIO_ENDPOINT=http://192.168.0.100:1234/v1/chat/completions
   LM_STUDIO_MODELS_ENDPOINT=http://192.168.0.100:1234/v1/models
   ```

### Recommended Models
- **Mistral 7B Instruct** - Good balance of speed and accuracy
- **Llama 2 13B** - Better accuracy, slower
- **Phi-2** - Fast, good for simple invoices

---

## OpenAI Setup

**Best for:** Highest accuracy, cloud-based, pay-per-use

### Prerequisites
- OpenAI account with API access
- Valid API key with credits

### Configuration

1. **Get your API key:**
   - Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
   - Click "Create new secret key"
   - Copy the key (you won't see it again!)

2. **Configure `.env` file:**
   ```env
   API_PROVIDER=openai
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
   OPENAI_MODEL=gpt-4-turbo-preview
   OPENAI_API_BASE=https://api.openai.com/v1
   ```

### Model Options
- **gpt-4-turbo-preview** - Best accuracy (recommended)
- **gpt-4** - High accuracy, more expensive
- **gpt-3.5-turbo** - Faster, cheaper, good accuracy

### Cost Estimates (as of 2024)
- **GPT-4 Turbo:** ~$0.01-0.03 per invoice
- **GPT-3.5 Turbo:** ~$0.001-0.003 per invoice

---

## OpenRouter Setup

**Best for:** Access to multiple models, competitive pricing, Claude support

### Prerequisites
- OpenRouter account
- Valid API key with credits

### Configuration

1. **Get your API key:**
   - Go to [OpenRouter Keys](https://openrouter.ai/keys)
   - Create a new API key
   - Add credits to your account

2. **Configure `.env` file:**
   ```env
   API_PROVIDER=openrouter
   OPENROUTER_API_KEY=sk-or-xxxxxxxxxxxxxxxxxxxxx
   OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
   OPENROUTER_API_BASE=https://openrouter.ai/api/v1
   OPENROUTER_APP_NAME=Invoice-Cataloger
   ```

### Recommended Models

#### High Accuracy (Premium)
- **anthropic/claude-3.5-sonnet** - Excellent for complex invoices
- **openai/gpt-4-turbo** - Very accurate
- **google/gemini-pro-1.5** - Good balance

#### Good Accuracy (Budget)
- **anthropic/claude-3-haiku** - Fast and accurate
- **openai/gpt-3.5-turbo** - Reliable and cheap
- **meta-llama/llama-3-70b-instruct** - Open source, good quality

#### See all models at: https://openrouter.ai/models

---

## Custom Prompts

You can customize the extraction prompt to better suit your specific invoice formats.

### Enable Custom Prompt

1. **In `.env` file:**
   ```env
   USE_CUSTOM_PROMPT=true
   CUSTOM_EXTRACTION_PROMPT=Your custom prompt here...
   ```

2. **Use `{invoice_text}` as placeholder** for where the invoice content should be inserted

### Example Custom Prompt

```env
CUSTOM_EXTRACTION_PROMPT=You are an expert at extracting data from Australian tax invoices.

Analyze this invoice text:
{invoice_text}

Extract and return ONLY a JSON object with these fields:
{
  "vendor_name": "Business name",
  "vendor_abn": "ABN number",
  "invoice_number": "Invoice number",
  "invoice_date": "Date in YYYY-MM-DD format",
  "total": 0.00,
  "tax": 0.00,
  "description": "Brief description"
}

Rules:
- Return ONLY valid JSON
- No markdown formatting
- Use 0.00 for missing amounts
- Use empty string "" for missing text
```

### Tips for Custom Prompts
- Be specific about the output format
- Include examples if needed
- Specify how to handle missing data
- Keep it concise but clear
- Test with a few invoices first

---

## LLM Parameters

Fine-tune the AI behavior in your `.env` file:

```env
# Temperature: 0.0 = deterministic, 1.0 = creative
# For invoices, keep it low (0.1-0.3)
LLM_TEMPERATURE=0.1

# Maximum tokens in response
LLM_MAX_TOKENS=3000

# Request timeout in seconds
LLM_TIMEOUT_SECONDS=120

# Number of retry attempts on failure
LLM_RETRY_ATTEMPTS=3

# Delay between retries in seconds
LLM_RETRY_DELAY_SECONDS=2
```

---

## Troubleshooting

### LM Studio Issues

**Problem:** "Cannot connect to LM Studio"
- **Solution:** Ensure LM Studio is running and server is started
- Check the endpoint URL matches your LM Studio settings
- Try `http://localhost:1234` instead of `http://127.0.0.1:1234`

**Problem:** "No model loaded in LM Studio"
- **Solution:** Load a model in LM Studio before starting the server

### OpenAI Issues

**Problem:** "OpenAI API key not configured"
- **Solution:** Check your `.env` file has `OPENAI_API_KEY` set
- Ensure the key starts with `sk-`

**Problem:** "OpenAI connection failed: 401"
- **Solution:** Your API key is invalid or expired
- Generate a new key at https://platform.openai.com/api-keys

**Problem:** "OpenAI connection failed: 429"
- **Solution:** Rate limit exceeded or no credits
- Check your usage at https://platform.openai.com/usage
- Add credits or wait for rate limit reset

### OpenRouter Issues

**Problem:** "OpenRouter API key not configured"
- **Solution:** Check your `.env` file has `OPENROUTER_API_KEY` set

**Problem:** "OpenRouter connection failed: 402"
- **Solution:** Insufficient credits
- Add credits at https://openrouter.ai/credits

**Problem:** "Model not found"
- **Solution:** Check the model name is correct
- See available models at https://openrouter.ai/models

### General Issues

**Problem:** "Failed to extract data with LLM"
- **Solution:** 
  - Try increasing `LLM_MAX_TOKENS`
  - Check if the invoice text was extracted correctly
  - Try a different model
  - Enable verbose logging: `--verbose`

**Problem:** Extraction is slow
- **Solution:**
  - Use a faster model (e.g., GPT-3.5 instead of GPT-4)
  - Reduce `LLM_MAX_TOKENS`
  - For LM Studio, use a smaller model

**Problem:** Extraction is inaccurate
- **Solution:**
  - Use a more powerful model
  - Increase `LLM_TEMPERATURE` slightly (0.2-0.3)
  - Create a custom prompt with specific instructions
  - Ensure OCR is working correctly

---

## Testing Your Setup

Run the prerequisite check:
```bash
python invoice_cataloger.py --check-only
```

Expected output:
```
✓ Invoice folder exists
✓ Output folder ready
✓ [Provider] configured with model: [model-name]
✓ [Provider] connected. Using model: [model-name]
✓ Using default optimized extraction prompt
✓ All prerequisites met
```

---

## Security Best Practices

1. **Never commit `.env` file** to version control
2. **Keep API keys secret** - don't share them
3. **Rotate keys regularly** if using cloud APIs
4. **Use environment-specific keys** for development/production
5. **Monitor API usage** to detect unauthorized access
6. **For sensitive data**, consider using LM Studio (local processing)

---

## Support

For issues or questions:
- Check the [main README](README.md)
- Review [TESTING_STATUS.md](../TESTING_STATUS.md)
- Check the logs in `Processed/Logs/`

---

## Quick Reference

| Provider | Best For | Cost | Privacy | Setup Difficulty |
|----------|----------|------|---------|------------------|
| **LM Studio** | Privacy, Offline | Free | High | Medium |
| **OpenAI** | Accuracy | Pay-per-use | Low | Easy |
| **OpenRouter** | Flexibility | Pay-per-use | Low | Easy |

Choose based on your priorities! 🚀
