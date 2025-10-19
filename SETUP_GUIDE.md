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
AI_SERVICE_TYPE=azure_openai
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

**For OpenAI:**
```bash
AI_SERVICE_TYPE=openai
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4o
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

### Import Errors
If you see import errors:
```powershell
# Reinstall dependencies
uv pip install -e ".[dev]"
```

### UV Not Found
```powershell
# Add to PATH (Windows)
$env:Path += ";$env:USERPROFILE\.local\bin"

# Or reinstall UV
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Python Version Issues
```powershell
# Check Python version
python --version

# UV can create venv with specific Python
uv venv --python 3.11
```

### Port Already in Use
If port 8501 is already in use:
```powershell
# Use different port
streamlit run src/ada_annotator/app.py --server.port 8502
```

### API Key Issues
- Ensure no extra spaces in `.env` file
- Check that API endpoint URL ends with `/`
- Verify deployment name matches Azure portal
- Test API key with a simple curl command

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
