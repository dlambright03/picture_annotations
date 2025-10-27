# ADA Annotator - Setup Guide

This guide will help you get the ADA Annotator project up and running on your local machine.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

### Required
- **Python 3.11 or higher** - [Download Python](https://www.python.org/downloads/)
- **uv** - Fast Python package manager
- **Git** - For version control

### Optional but Recommended
- **Visual Studio Code** - [Download VS Code](https://code.visualstudio.com/)
- **Azure OpenAI access** or **OpenAI API key**

## 🚀 Quick Start

### Step 1: Install UV

UV is a fast Python package manager that we use for dependency management.

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Step 2: Clone and Setup (Automated)

We have an automated setup script that will handle everything:

```powershell
# Run the setup script
.\scripts\setup.ps1
```

This script will:
- ✅ Check for required tools
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Create `.env` file from template
- ✅ Create temporary directories

### Step 3: Configure API Keys

Edit the `.env` file and add your API credentials:

**For Azure OpenAI (Recommended):**
```bash
# AI Service Configuration
AI_SERVICE_TYPE=azure_openai

# Azure OpenAI Settings
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Optional: Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/ada-annotator.log

# Optional: Processing Configuration
DEFAULT_MAX_IMAGES=0  # 0 = process all images
CONTINUE_ON_ERROR=true
```

**Finding Your Azure OpenAI Credentials:**

1. **Endpoint:**
   - Go to [Azure Portal](https://portal.azure.com)
   - Navigate to your Azure OpenAI resource
   - Copy "Endpoint" from "Keys and Endpoint" section
   - Format: `https://your-resource.openai.azure.com/`

2. **API Key:**
   - Same location as endpoint
   - Click "Show Keys" and copy KEY 1 or KEY 2

3. **Deployment Name:**
   - In Azure OpenAI resource, click "Model deployments"
   - Copy the exact deployment name (e.g., `gpt-4o`)
   - Must have vision capabilities (GPT-4o or GPT-4V)

4. **API Version:**
   - Use `2024-02-15-preview` for vision capabilities
   - Check [Azure OpenAI versions](https://learn.microsoft.com/en-us/azure/ai-services/openai/reference) for latest

**Configuration Validation:**

After configuring, test your setup:
```powershell
# Activate virtual environment first
.\.venv\Scripts\Activate.ps1

# Test configuration
python -c "from ada_annotator.config import Settings; s = Settings(); print(f'Service: {s.ai_service_type}'); print(f'Endpoint: {s.azure_openai_endpoint}')"
```

You should see output like:
```
Service: azure_openai
Endpoint: https://your-resource.openai.azure.com/
```

### Step 4: Activate Virtual Environment

```powershell
# Windows
.\.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate
```

### Step 5: Run the Application

```powershell
streamlit run src/ada_annotator/app.py
```

The application will open in your browser at `http://localhost:8501`

## 🔧 Manual Setup (Alternative)

If you prefer to set up manually:

### 1. Create Virtual Environment
```powershell
uv venv
```

### 2. Activate Virtual Environment
```powershell
# Windows
.\.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies
```powershell
# Install all dependencies including dev tools
uv pip install -e ".[dev]"

# Or install minimal dependencies only
uv pip install -e .
```

### 4. Configure Environment
```powershell
# Copy example environment file
cp .env.example .env

# Edit .env and add your API keys
code .env  # or use your preferred editor
```

### 5. Create Temporary Directories
```powershell
mkdir temp
```

## 🧪 Running Tests

```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=ada_annotator --cov-report=html

# Run specific test file
pytest tests/unit/test_config.py

# Run in verbose mode
pytest -v
```

## 🎨 Code Quality

### Format Code
```powershell
black src/ tests/
```

### Lint Code
```powershell
ruff check src/ tests/
```

### Type Check
```powershell
mypy src/
```

### Run All Quality Checks
```powershell
black src/ tests/
ruff check src/ tests/
mypy src/
pytest
```

## 📦 UV Commands Reference

### Installing Packages
```powershell
# Install package
uv pip install package-name

# Install with specific version
uv pip install package-name==1.2.3

# Install from requirements
uv pip install -r requirements.txt

# Install project in editable mode
uv pip install -e .
```

### Managing Dependencies
```powershell
# List installed packages
uv pip list

# Show package info
uv pip show package-name

# Freeze dependencies
uv pip freeze > requirements.txt

# Update all packages
uv pip install --upgrade -e ".[dev]"
```

### Virtual Environments
```powershell
# Create virtual environment
uv venv

# Create with specific Python version
uv venv --python 3.11

# Remove virtual environment
rm -r .venv
```

## 🐛 Troubleshooting

### Common Issues and Solutions

#### Import Errors

**Problem:** `ModuleNotFoundError` or import errors when running the CLI

**Solution:**
```powershell
# Reinstall dependencies in editable mode
uv pip install -e ".[dev]"

# Verify installation
python -c "import ada_annotator; print(ada_annotator.__file__)"
```

#### UV Not Found

**Problem:** `uv: command not found` or `uv` not recognized

**Solution (Windows):**
```powershell
# Add to PATH temporarily
$env:Path += ";$env:USERPROFILE\.local\bin"

# Or reinstall UV
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Restart terminal after installation
```

**Solution (macOS/Linux):**
```bash
# Add to PATH
export PATH="$HOME/.local/bin:$PATH"

# Add to shell profile for persistence
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

#### Python Version Issues

**Problem:** `Python 3.11 or higher required` error

**Solution:**
```powershell
# Check Python version
python --version

# If version < 3.11, install Python 3.11+
# Download from: https://www.python.org/downloads/

# Create venv with specific Python version
uv venv --python 3.11
```

#### Port Already in Use (Streamlit)

**Problem:** `Address already in use` when running Streamlit

**Solution:**
```powershell
# Use different port
streamlit run src/ada_annotator/app.py --server.port 8502

# Or kill process using port 8501 (Windows)
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Or kill process (macOS/Linux)
lsof -ti:8501 | xargs kill
```

### API Configuration Issues

#### Azure OpenAI Connection Errors

**Problem:** `APIError: Connection failed` or authentication errors

**Checklist:**
1. ✅ Verify `.env` file exists in project root
2. ✅ Check for extra spaces in `.env` values
3. ✅ Ensure endpoint URL ends with `/`
4. ✅ Verify deployment name matches Azure portal
5. ✅ Confirm API version is supported (use `2024-02-15-preview`)
6. ✅ Test API key with curl:

```powershell
# Test Azure OpenAI connection
$headers = @{
    "api-key" = "your-api-key"
    "Content-Type" = "application/json"
}

$body = @{
    messages = @(
        @{
            role = "user"
            content = "Hello"
        }
    )
    max_tokens = 10
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://your-resource.openai.azure.com/openai/deployments/your-deployment/chat/completions?api-version=2024-02-15-preview" -Method Post -Headers $headers -Body $body
```

#### Rate Limiting Issues

**Problem:** `APIError: Rate limit exceeded (429)`

**Solutions:**
1. **Reduce batch size:** Use `--max-images` flag
   ```powershell
   python -m ada_annotator.cli --input doc.docx --output out.docx --max-images 5
   ```

2. **Check quota in Azure Portal:**
   - Navigate to your Azure OpenAI resource
   - Check "Quota" section
   - Increase TPM (Tokens Per Minute) if needed

3. **Retry with backoff:** Built-in retry logic will handle transient rate limits automatically

#### Invalid Deployment Name

**Problem:** `DeploymentNotFound` error

**Solution:**
```powershell
# List your deployments in Azure Portal:
# 1. Go to Azure OpenAI resource
# 2. Click "Model deployments"
# 3. Copy exact deployment name

# Update .env with exact name
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o  # Match deployment name exactly
```

### Document Processing Issues

#### No Images Found

**Problem:** `No images found in document` message

**Possible Causes:**
1. Document has no embedded images (only text)
2. Images are linked externally (not embedded)
3. Document is corrupted

**Solution:**
```powershell
# Test with sample document
python -m ada_annotator.cli \
    --input tests/fixtures/documents/sample.docx \
    --dry-run

# Check document in Word/PowerPoint:
# - Are images actually embedded?
# - Try "Save As" to create fresh copy
# - Re-embed external images
```

#### Corrupted Document Errors

**Problem:** `ProcessingError: Failed to open document`

**Solution:**
1. **Open and re-save** in Microsoft Word/PowerPoint
2. **Check file extension** matches content (.docx for Word, .pptx for PowerPoint)
3. **Try different document** to isolate issue
4. **Check file permissions** (read access required)

#### Position Preservation Issues

**Problem:** Images in wrong positions in output document

**Notes:**
- **DOCX:** Position is paragraph-based (flow layout). Images stay in same paragraphs.
- **PPTX:** Position preserved with EMU precision (pixel-perfect).
- **Floating images:** May appear different in different Word views (Print Layout vs Web Layout)

**Verify:**
```powershell
# Enable debug logging to see position metadata
python -m ada_annotator.cli \
    --input document.docx \
    --output output.docx \
    --log-level DEBUG
```

### Performance Issues

#### Slow Processing

**Problem:** Document processing takes too long

**Solutions:**
1. **Limit images for testing:**
   ```powershell
   python -m ada_annotator.cli --input doc.docx --output out.docx --max-images 10
   ```

2. **Check network latency:** Azure OpenAI API calls are network-dependent
   ```powershell
   # Test latency (Windows)
   Test-NetConnection your-resource.openai.azure.com -Port 443
   ```

3. **Use dry-run to test extraction:**
   ```powershell
   python -m ada_annotator.cli --input doc.docx --dry-run
   ```

4. **Check logs for retry attempts:**
   - Excessive retries indicate API issues
   - Review `logs/ada-annotator.log`

#### High Token Usage/Costs

**Problem:** Unexpected high costs for processing

**Analysis:**
```powershell
# Check report for token usage
# Look for: {output}_report.md
# Section: "Resource Usage"

# Typical costs:
# - Small images: ~100-300 tokens ($0.001-0.003)
# - Complex images: ~500-1000 tokens ($0.005-0.010)
# - With context: +50-200 tokens
```

**Optimization tips:**
1. **Limit context file size** (< 2000 chars recommended)
2. **Process fewer images** for testing
3. **Use simpler images** when possible
4. **Monitor Azure OpenAI quota**

### Testing Issues

#### Tests Failing

**Problem:** `pytest` tests fail after code changes

**Solution:**
```powershell
# Run specific failing test with verbose output
pytest tests/unit/test_failing.py -v -s

# Check for missing dependencies
uv pip install -e ".[dev]"

# Clear pytest cache
pytest --cache-clear

# Re-run only failed tests
pytest --lf -v
```

#### Coverage Below 80%

**Problem:** Test coverage drops below threshold

**Solution:**
```powershell
# Generate detailed coverage report
pytest --cov=src/ada_annotator --cov-report=html

# Open htmlcov/index.html to see uncovered lines

# Run coverage for specific module
pytest tests/unit/test_module.py --cov=src/ada_annotator/module.py --cov-report=term-missing
```

### Logging Issues

#### No Log File Created

**Problem:** `logs/ada-annotator.log` not created

**Solution:**
```powershell
# Create logs directory manually
mkdir logs

# Run with explicit log level
python -m ada_annotator.cli --input doc.docx --output out.docx --log-level DEBUG

# Check console for errors
```

#### Too Much Log Output

**Problem:** Excessive console logging

**Solution:**
```powershell
# Use INFO level (default)
python -m ada_annotator.cli --input doc.docx --output out.docx --log-level INFO

# Or WARNING for minimal output
python -m ada_annotator.cli --input doc.docx --output out.docx --log-level WARNING
```

## ❓ FAQ

### General Questions

**Q: What document formats are supported?**
A: Phase 1 supports DOCX (Word) and PPTX (PowerPoint). PDF support is planned for Phase 2.

**Q: Can I use OpenAI instead of Azure OpenAI?**
A: The code is designed for Azure OpenAI. OpenAI support would require modifying the `SemanticKernelService` class.

**Q: How accurate is the alt-text generation?**
A: Accuracy depends on GPT-4o's vision capabilities (~85-95%). Always review generated alt-text for critical documents.

**Q: Does this work offline?**
A: No, internet connection required for Azure OpenAI API calls.

**Q: Can I customize the alt-text generation prompt?**
A: Yes, modify the system message in `src/ada_annotator/ai_services/semantic_kernel_service.py`.

### Technical Questions

**Q: What's the maximum image size?**
A: Azure OpenAI supports images up to 20MB. Larger images are automatically rejected.

**Q: How many images can I process at once?**
A: No hard limit, but consider:
- API rate limits (TPM quota in Azure)
- Processing time (~2-5 seconds per image)
- Cost implications

**Q: Can I process multiple documents in parallel?**
A: Not built-in. Use PowerShell/bash loops for batch processing (see README examples).

**Q: How is context extracted from documents?**
A: 5-level hierarchy:
1. External context file (highest priority)
2. Document metadata (title, author)
3. Section headings (nearest heading above image)
4. Page context (slide title for PPTX)
5. Local context (surrounding paragraphs/text)

**Q: What happens if alt-text generation fails for one image?**
A: Processing continues for remaining images. Failed images are logged in the report with error reasons.

**Q: How accurate is position preservation?**
A:
- **PPTX:** Exact (EMU precision, pixel-perfect)
- **DOCX:** Paragraph-based (images stay in same paragraphs)

### Cost and Performance

**Q: How much does it cost to process documents?**
A: Azure OpenAI GPT-4o pricing (as of 2024):
- Input: $2.50 per 1M tokens
- Output: $10.00 per 1M tokens
- **Typical cost:** $0.004-0.008 per image
- **Example:** 100-image document ≈ $0.40-0.80

**Q: How long does processing take?**
A: Approximately:
- Image extraction: <1 second per image
- Alt-text generation: 2-5 seconds per image
- Document assembly: <1 second total
- **Total:** ~2-5 seconds per image + overhead

**Q: Can I reduce costs?**
A: Yes:
1. Use shorter context files
2. Process fewer images (--max-images flag)
3. Reuse alt-text for similar images (manual process)
4. Use lower-cost models (requires code changes)

### Development Questions

**Q: How do I add support for a new document format?**
A:
1. Create new extractor class extending `DocumentExtractor`
2. Create new assembler class extending `DocumentAssembler`
3. Implement required abstract methods
4. Add tests
5. Update CLI to recognize new format

**Q: Can I use a different AI service?**
A: Yes, implement a new service class with same interface as `SemanticKernelService`. Update dependency injection in `AltTextGenerator`.

**Q: How do I contribute?**
A: See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines (planned).

## 📚 Additional Resources

- **Project Requirements:** [docs/requirements.md](docs/requirements.md)
- **Phase Summaries:** [docs/phase_summaries/](docs/phase_summaries/)
- **Python Standards:** [.github/instructions/python.instructions.md](.github/instructions/python.instructions.md)
- **Azure OpenAI Docs:** https://learn.microsoft.com/en-us/azure/ai-services/openai/
- **Semantic Kernel Docs:** https://learn.microsoft.com/en-us/semantic-kernel/
- **python-docx Docs:** https://python-docx.readthedocs.io/
- **python-pptx Docs:** https://python-pptx.readthedocs.io/

## 🆘 Getting Help

If you're still stuck after trying the troubleshooting steps:

1. **Check Logs:**
   ```powershell
   # View structured logs
   cat logs/ada-annotator.log | ConvertFrom-Json | Format-List
   ```

2. **Run with Debug Logging:**
   ```powershell
   python -m ada_annotator.cli --input doc.docx --output out.docx --log-level DEBUG
   ```

3. **Review Test Suite:**
   ```powershell
   # Run tests to verify installation
   pytest -v
   ```

4. **GitHub Issues:** Report bugs or request features
5. **Documentation:** Review [docs/](docs/) folder for detailed specifications

**Ready to start processing documents!** 🚀

## 🏗️ Project Structure

```
ada-annotator/
├── src/ada_annotator/          # Main application code
│   ├── __init__.py             # Package initialization
│   ├── config.py               # Configuration management
│   ├── app.py                  # Streamlit web app
│   ├── cli.py                  # Command-line interface
│   ├── document_processors/    # DOCX, PDF, PPTX processing
│   ├── ai_services/            # AI service integrations
│   ├── plugins/                # Semantic Kernel plugins
│   ├── models/                 # Data models
│   └── utils/                  # Utility functions
├── tests/                      # Test suite
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── fixtures/               # Test data
├── docs/                       # Documentation
│   ├── requirements.md         # Project requirements
│   └── adr/                    # Architecture decisions
├── scripts/                    # Helper scripts
├── .vscode/                    # VS Code settings
├── pyproject.toml              # Project configuration
├── .env.example                # Environment template
└── README.md                   # Project overview
```

## 📚 Next Steps

1. **Review Requirements**: Read `docs/requirements.md` for detailed project requirements
2. **Explore Code**: Check out the skeleton code in `src/ada_annotator/`
3. **Start Development**: Begin implementing features from Phase 1
4. **Write Tests**: Add tests in `tests/` directory
5. **Check Documentation**: Update README.md as you add features

## 🆘 Getting Help

- 📖 **Documentation**: `docs/requirements.md`
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/ada-annotator/issues)
- 💬 **Discussions**: Project discussion board
- 📧 **Email**: your.email@example.com

## 🎯 Local Prototype Features

See `docs/requirements.md` Section 12.1.0 for detailed feature list.

**Essential Features for Local Prototype:**
- ✅ Document upload & validation (DOCX)
- ✅ Image extraction from DOCX
- ✅ AI-powered alt-text generation
- ✅ Document output with annotations
- ✅ Simple Streamlit UI

**Ready to start coding!** 🚀
