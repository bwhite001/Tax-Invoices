# Changelog - Invoice Cataloger

## [2.0.0] - Multi-Provider API Support - 2024

### 🎉 Major Features Added

#### Multi-Provider API Support
- **LM Studio (Local AI)** - Continue using local models for privacy and offline processing
- **OpenAI** - Access to GPT-4, GPT-3.5-turbo for cloud-based processing
- **OpenRouter** - Access to Claude, Gemini, Llama, and many other models

#### Configurable Prompts
- Custom prompt support via environment variables
- Optimized default prompt for Australian tax invoices
- Placeholder system for easy customization

#### Environment-Based Configuration
- Secure API key management via `.env` files
- Easy switching between providers
- No code changes needed to switch providers

### 📝 Changes by File

#### New Files
- **`.env.example`** - Comprehensive configuration template
- **`API_SETUP_GUIDE.md`** - Detailed setup instructions for all providers
- **`CHANGELOG.md`** - This file

#### Modified Files

##### `requirements.txt`
- Added `python-dotenv>=1.0.0` for environment variable management

##### `config.py`
- Added `api_provider` field (lmstudio/openai/openrouter)
- Added OpenAI configuration fields:
  - `openai_api_key`
  - `openai_model`
  - `openai_api_base`
- Added OpenRouter configuration fields:
  - `openrouter_api_key`
  - `openrouter_model`
  - `openrouter_api_base`
  - `openrouter_app_name`
- Added custom prompt configuration:
  - `use_custom_prompt`
  - `custom_extraction_prompt`
- All configuration now loaded from `.env` file
- Added `validate_api_config()` method
- Updated `to_dict()` to include new fields

##### `processors/llm_processor.py`
- Refactored to support multiple API providers
- Added `_call_openai()` method using official OpenAI SDK
- Added `_call_openrouter()` method using OpenAI-compatible SDK
- Renamed `_call_llm()` to `_call_lmstudio()` for clarity
- Updated `_call_llm()` to route to appropriate provider
- Enhanced `_build_extraction_prompt()`:
  - New optimized default prompt for Australian invoices
  - Support for custom prompts via configuration
  - Better structured extraction rules
- Updated `test_connection()` to support all providers
- Improved error handling for each provider

##### `invoice_cataloger.py`
- Updated `LLMProcessor` initialization with all provider parameters
- Enhanced `check_prerequisites()`:
  - Validates API configuration based on provider
  - Provider-specific connection testing
  - Provider-specific error messages
  - Shows custom prompt status
- Added logging for API provider selection

### 🔧 Configuration

#### Environment Variables (`.env`)

**API Provider Selection:**
```env
API_PROVIDER=lmstudio  # or openai, openrouter
```

**LM Studio (Local):**
```env
LM_STUDIO_ENDPOINT=http://localhost:1234/v1/chat/completions
LM_STUDIO_MODELS_ENDPOINT=http://localhost:1234/v1/models
LM_STUDIO_MODEL=local-model
```

**OpenAI:**
```env
OPENAI_API_KEY=sk-proj-xxxxx
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_API_BASE=https://api.openai.com/v1
```

**OpenRouter:**
```env
OPENROUTER_API_KEY=sk-or-xxxxx
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
OPENROUTER_API_BASE=https://openrouter.ai/api/v1
OPENROUTER_APP_NAME=Invoice-Cataloger
```

**Custom Prompts:**
```env
USE_CUSTOM_PROMPT=false
CUSTOM_EXTRACTION_PROMPT=
```

**LLM Parameters:**
```env
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=3000
LLM_TIMEOUT_SECONDS=120
LLM_RETRY_ATTEMPTS=3
LLM_RETRY_DELAY_SECONDS=2
```

### 🔄 Migration Guide

#### From Version 1.x to 2.0

1. **Install new dependency:**
   ```bash
   pip install python-dotenv
   ```

2. **Create `.env` file:**
   ```bash
   cp .env.example .env
   ```

3. **Configure your provider:**
   - For LM Studio users: No changes needed! Default is `API_PROVIDER=lmstudio`
   - For OpenAI: Set `API_PROVIDER=openai` and add your API key
   - For OpenRouter: Set `API_PROVIDER=openrouter` and add your API key

4. **Test configuration:**
   ```bash
   python invoice_cataloger.py --check-only
   ```

### ✨ Benefits

#### For Existing Users (LM Studio)
- ✅ **Backward compatible** - No changes required
- ✅ **Same functionality** - All existing features work as before
- ✅ **Optional upgrade** - Switch to cloud APIs when needed

#### For New Users
- ✅ **More choices** - Pick the provider that fits your needs
- ✅ **Easy setup** - Simple `.env` configuration
- ✅ **Better accuracy** - Access to state-of-the-art models
- ✅ **Flexible** - Switch providers without code changes

### 🎯 Use Cases

**Use LM Studio when:**
- Privacy is critical
- Processing sensitive financial data
- Want to work offline
- No API costs desired

**Use OpenAI when:**
- Need highest accuracy
- Processing complex invoices
- Want reliable cloud service
- Budget allows pay-per-use

**Use OpenRouter when:**
- Want access to multiple models
- Need Claude or Gemini
- Want competitive pricing
- Flexibility is important

### 📊 Performance Comparison

| Provider | Speed | Accuracy | Cost | Privacy |
|----------|-------|----------|------|---------|
| LM Studio | Medium | Good | Free | High |
| OpenAI GPT-4 | Fast | Excellent | $0.01-0.03/invoice | Low |
| OpenAI GPT-3.5 | Very Fast | Good | $0.001-0.003/invoice | Low |
| OpenRouter Claude | Fast | Excellent | Varies | Low |

### 🔒 Security Improvements

- API keys stored in `.env` file (not in code)
- `.env` file excluded from version control
- Secure credential management
- No hardcoded secrets

### 📚 Documentation

New documentation added:
- **API_SETUP_GUIDE.md** - Complete setup guide for all providers
- **CHANGELOG.md** - This changelog
- Updated **README.md** - References to new features
- Enhanced **.env.example** - Comprehensive configuration template

### 🐛 Bug Fixes

- Improved error handling for API failures
- Better timeout management
- More informative error messages
- Graceful fallback on connection issues

### 🚀 Future Enhancements

Potential future additions:
- Azure OpenAI support
- Google Vertex AI support
- Anthropic direct API support
- Prompt templates library
- Model performance benchmarking
- Cost tracking and reporting

### 🙏 Acknowledgments

This update maintains backward compatibility while adding powerful new features. Special thanks to the open-source community for the excellent libraries that made this possible.

---

## How to Use This Version

1. **Quick Start:**
   ```bash
   cp .env.example .env
   # Edit .env with your preferred provider
   python invoice_cataloger.py --check-only
   python invoice_cataloger.py
   ```

2. **Read the guides:**
   - [API Setup Guide](API_SETUP_GUIDE.md) - Detailed provider setup
   - [README](README.md) - General usage
   - [Quick Start](../QUICK_START.md) - Fast setup

3. **Get help:**
   - Check logs in `Processed/Logs/`
   - Review [TESTING_STATUS.md](../TESTING_STATUS.md)
   - See troubleshooting in API_SETUP_GUIDE.md

---

**Version:** 2.0.0  
**Release Date:** 2024  
**Compatibility:** Python 3.8+  
**License:** Same as project license
