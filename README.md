# ADA Annotator - Image Accessibility Automation

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Automatically generate ADA-compliant alt-text descriptions for images in documents using AI-powered analysis through Microsoft Semantic Kernel.

## 🎯 Purpose

Help college professors and educators make their educational documents ADA-compliant by automatically generating descriptive alternative text for images embedded in Word documents, PDFs, and PowerPoint presentations.

## ✨ Features (Local Prototype)

- 📄 **DOCX Processing**: Extract images from Microsoft Word documents
- 🤖 **AI-Powered Alt-Text**: Generate descriptions using GPT-4o/GPT-4 Vision
- 🔄 **Semantic Kernel Integration**: Robust AI orchestration and plugin architecture
- 🖼️ **Image Preview**: View extracted images with generated descriptions
- 📥 **Easy Output**: Download annotated documents with alt-text applied
- 🎨 **Simple UI**: Streamlit-based interface for non-technical users

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager
- Azure OpenAI account (or OpenAI API key)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/ada-annotator.git
cd ada-annotator
```

2. **Install uv** (if not already installed):
```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. **Create virtual environment and install dependencies:**
```bash
uv venv
uv pip install -e ".[dev]"
```

4. **Configure environment variables:**
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys
# For Azure OpenAI:
#   - AZURE_OPENAI_ENDPOINT
#   - AZURE_OPENAI_API_KEY
#   - AZURE_OPENAI_DEPLOYMENT_NAME
# OR for OpenAI:
#   - OPENAI_API_KEY
```

5. **Run the application:**
```bash
# Activate virtual environment
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# Run Streamlit app
streamlit run src/ada_annotator/app.py
```

6. **Open your browser:**
Navigate to `http://localhost:8501`

## 📖 Usage

1. **Upload Document**: Drag and drop a DOCX file or click to browse
2. **Extract Images**: System automatically extracts all images
3. **Generate Alt-Text**: AI analyzes each image and creates descriptions
4. **Review**: Preview generated alt-text for each image
5. **Download**: Get your annotated document with alt-text applied

## 🏗️ Project Structure

```
ada-annotator/
├── src/
│   └── ada_annotator/
│       ├── __init__.py
│       ├── config.py              # Configuration and settings
│       ├── app.py                 # Streamlit web application
│       ├── cli.py                 # Command-line interface
│       ├── document_processors/   # DOCX, PDF, PPTX processors
│       ├── ai_services/           # AI service integrations
│       ├── plugins/               # Semantic Kernel plugins
│       ├── models/                # Data models (Pydantic)
│       └── utils/                 # Utility functions
├── tests/
│   ├── unit/                      # Unit tests
│   ├── integration/               # Integration tests
│   └── fixtures/                  # Test data
├── docs/
│   ├── requirements.md            # Project requirements
│   └── adr/                       # Architecture Decision Records
├── scripts/                       # Helper scripts
├── pyproject.toml                 # Project configuration (uv/pip)
├── .env.example                   # Example environment variables
├── .gitignore
└── README.md
```

## 🔧 Development

### Running Tests

```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/unit/test_document_processor.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code with black
black src/ tests/

# Lint with ruff
ruff check src/ tests/

# Type check with mypy
mypy src/
```

### Using UV Commands

```bash
# Install dependencies
uv pip install -e ".[dev]"

# Add a new package
uv pip install package-name

# Update all dependencies
uv pip install --upgrade -e ".[dev]"

# Sync dependencies from pyproject.toml
uv pip sync
```

## 📋 Requirements

See [docs/requirements.md](docs/requirements.md) for detailed project requirements.

### Core Dependencies

- **Document Processing**: python-docx, pypdf, python-pptx, Pillow
- **AI/ML**: semantic-kernel, openai, azure-identity
- **Web Framework**: streamlit
- **Configuration**: python-dotenv, pydantic

## 🗺️ Roadmap

### Phase 1: Local Prototype (Current - Week 1-2)
- [x] Project setup with uv
- [ ] DOCX image extraction
- [ ] Semantic Kernel integration
- [ ] Basic alt-text generation
- [ ] Streamlit UI

### Phase 2: Cloud MVP (Week 3-4)
- [ ] Deploy to Azure App Service
- [ ] PDF support
- [ ] PowerPoint support
- [ ] Manual review interface

### Phase 3: Production (Future)
- [ ] Azure Functions deployment
- [ ] Batch processing
- [ ] Context-aware annotations
- [ ] User authentication

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Microsoft Semantic Kernel team for the excellent AI orchestration framework
- OpenAI/Azure OpenAI for powerful vision capabilities
- python-docx, python-pptx, pypdf maintainers for document processing libraries

## 📞 Support

- 📧 Email: your.email@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/ada-annotator/issues)
- 📖 Documentation: [Project Docs](https://github.com/yourusername/ada-annotator/docs)

## 🔒 Security

- Never commit `.env` files
- Store API keys securely in environment variables
- Use Azure Key Vault for production deployments
- Follow FERPA guidelines for educational records

---

**Made with ❤️ for accessibility in education**
