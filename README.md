# ADA Annotator - Image Accessibility Automation

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Automatically generate ADA-compliant alt-text descriptions for images in documents using AI-powered analysis through Microsoft Semantic Kernel.

## 🎯 Purpose

Help college professors and educators make their educational documents ADA-compliant by automatically generating descriptive alternative text for images embedded in Word documents, PDFs, and PowerPoint presentations.

## ✨ Features (Phase 1 Complete)

- 📄 **DOCX & PPTX Processing**: Extract images from Microsoft Word and PowerPoint files
- 📋 **PDF Support**: Extract images from PDFs (debug/extract mode only)
- 🤖 **AI-Powered Alt-Text**: Generate ADA-compliant descriptions using GPT-4o Vision
- 🔄 **Two-Step Workflow**: Separate generation from application for manual review
- 📊 **Context-Aware Generation**: 5-level hierarchical context extraction for accurate descriptions
- 🎯 **Dynamic Confidence Scoring**: Quality-based scores (0.1-1.0) considering validation, warnings, and length
- 🖼️ **Image Embedding**: JSON includes base64-encoded images for human review
- ✅ **ADA Compliance Validation**: Automatic validation of length, content, and formatting
- 💾 **Reusable Alt-Text**: Generate once, apply to multiple document versions
- 🎯 **Position Preservation**: Images remain in exact original positions
- 📝 **Comprehensive Reporting**: Markdown reports with statistics, costs, and error tracking
- ⚡ **Batch Processing**: Process multiple images with progress tracking
- 🛡️ **Error Resilience**: Continue processing on individual failures
- 📝 **Structured Logging**: JSON logs with correlation IDs for debugging
- 🔄 **Semantic Kernel Integration**: Robust AI orchestration with retry logic and error handling

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager
- Azure OpenAI account with GPT-4o deployment

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/ada-annotator.git
cd ada-annotator
```

2. **Run automated setup** (recommended):
```powershell
# Windows PowerShell
.\scripts\setup.ps1
```

This script will:
- Install uv if not already installed
- Create virtual environment
- Install all dependencies
- Create `.env` file from template
- Verify installation

3. **Configure Azure OpenAI** (edit `.env`):
```bash
AI_SERVICE_TYPE=azure_openai
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

4. **Process your first document:**
```bash
# Using uv with the annotate command (simplest - note: input is positional, not --input)
uv run annotate tests/fixtures/documents/sample.docx --output output.docx --log-level INFO

# Or using the full module path
uv run python -m ada_annotator.cli tests/fixtures/documents/sample.docx --output output.docx --log-level INFO

# Or activate virtual environment first, then use the command directly
# Windows
.\.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate

annotate tests/fixtures/documents/sample.docx --output output.docx --log-level INFO
```

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed setup instructions and troubleshooting.

## 📖 Usage

### Command Line Interface (CLI)

The primary interface offers two workflow options:

#### **Two-Step Workflow (Recommended)**

The two-step workflow separates alt-text generation from document modification, allowing manual review:

```bash
# Step 1: Extract images and generate alt-text (saves to JSON + HTML)
uv run annotate extract document.docx -o alttext.json

# Step 2: Review the HTML file - open in your browser to see images!
# - Open document_alttext.html in any browser
# - See images displayed alongside their alt-text
# - Beautiful, interactive report with metadata
# (JSON file is also created for programmatic access)

# Step 3: Apply reviewed alt-text to document
uv run annotate apply document.docx alttext.json -o annotated.docx
```

**Benefits of Two-Step Workflow:**
- 💰 **Cost Savings**: Generate once, apply to multiple output formats
- 👁️ **Manual Review**: Beautiful HTML report showing images with their alt-text
- ✏️ **Editable**: Modify alt-text in JSON before applying
- 🔄 **Reusable**: Apply same alt-text to updated document versions
- 📊 **Traceable**: Both HTML (human-readable) and JSON (machine-readable) formats

**Extract Command Options:**
```bash
# Basic extraction
uv run annotate extract document.docx

# Specify output JSON path
uv run annotate extract document.docx -o my_alttext.json

# Include external context for better descriptions
uv run annotate extract document.docx -o alttext.json -c course_context.txt

# Limit to first 5 images (for testing)
uv run annotate extract document.docx --max-images 5

# Works with DOCX, PPTX, and PDF
uv run annotate extract presentation.pptx -o alttext.json
```

**Apply Command Options:**
```bash
# Basic application
uv run annotate apply document.docx alttext.json

# Specify output path
uv run annotate apply document.docx alttext.json -o final.docx

# Create backup before applying
uv run annotate apply document.docx alttext.json --backup
```

**JSON Format:**
The intermediate JSON file includes:
- Base64-encoded images (for programmatic access)
- Generated alt-text for each image
- Confidence scores and validation results
- Image metadata (dimensions, position, format)
- Processing statistics and timestamps

**HTML Report:**
A beautiful, interactive HTML file is also generated showing:
- 🖼️ **Visual Display**: Images shown directly (no base64 decoding needed)
- 📊 **Statistics Dashboard**: Overview of processing results
- ✅ **Validation Status**: Color-coded badges for each image
- 📏 **Metadata**: Dimensions, file size, confidence scores
- ⚠️ **Warnings**: Highlighted validation issues
- 🎨 **Modern Design**: Responsive, gradient UI with smooth animations

Simply open the HTML file in any browser to review your images and their alt-text!

#### **Single-Step Workflow (Legacy)**

For backward compatibility, the original single-step workflow is still supported:

```bash
# Process a DOCX file directly (using uv) - INPUT IS POSITIONAL
uv run annotate document.docx --output annotated.docx

# Process a PowerPoint presentation
uv run annotate presentation.pptx --output annotated.pptx

# Use external context file for better descriptions
uv run annotate document.docx \
    --output annotated.docx \
    --context course_syllabus.txt

# Dry-run mode (extract images and preview without generating alt-text)
uv run annotate document.docx --dry-run

# Debug mode (create debug document with images and annotations)
uv run annotate document.docx --debug

# Limit processing to first 5 images (for testing)
uv run annotate document.docx \
    --output annotated.docx \
    --max-images 5

# Enable verbose logging
uv run annotate document.docx \
    --output annotated.docx \
    --log-level DEBUG
```

**Note:** `uv run annotate` automatically uses the project's virtual environment. You can also activate the virtual environment and use `annotate` directly.

### Common Workflows

**1. Two-Step Review Workflow (Recommended):**
```bash
# Extract and generate alt-text
uv run annotate extract lecture_notes.docx -o alttext.json

# Open the HTML file in your browser to review
# lecture_notes_alttext.html shows all images with their alt-text
# Edit JSON file if you need to modify any alt-text

# Apply to original document
uv run annotate apply lecture_notes.docx alttext.json -o final_lecture.docx

# Or apply to different format/version
uv run annotate apply lecture_notes_v2.docx alttext.json -o final_v2.docx
```

**2. Quick Single-Step Processing:**
```bash
# Process sample document with debug logging
uv run annotate tests/fixtures/documents/sample.docx \
    --output output/annotated.docx \
    --log-level DEBUG
```

**3. Batch Processing Multiple Documents:**
```bash
# Extract alt-text for all DOCX files (using PowerShell)
Get-ChildItem *.docx | ForEach-Object {
    uv run annotate extract $_.Name -o "json/$($_.BaseName)_alttext.json"
}

# Review JSON files, then apply
Get-ChildItem json/*.json | ForEach-Object {
    $docName = $_.BaseName -replace '_alttext$','.docx'
    uv run annotate apply $docName $_.FullName -o "output/$docName"
}
```

**4. Educational Content with Context:**
```bash
# Include course context for better descriptions
uv run annotate extract lecture_notes.docx \
    -o alttext.json \
    -c course_context.md \
    --log-level INFO

# Review and apply
uv run annotate apply lecture_notes.docx alttext.json -o annotated_lecture.docx
```

### Output Files

#### Two-Step Workflow Output:
After extraction:
- **JSON File**: `{input_name}_alttext.json` containing:
  - Base64-encoded images for programmatic access
  - AI-generated alt-text for each image
  - Confidence scores (0.1-1.0) based on quality factors
  - Validation results and warnings
  - Image metadata (dimensions, position, format)
  - Processing statistics
- **HTML Report**: `{input_name}_alttext.html` - beautiful interactive report showing:
  - Images displayed directly in the browser
  - Alt-text alongside each image
  - Statistics dashboard with processing metrics
  - Color-coded validation badges
  - Metadata and warnings clearly highlighted
  - Modern, responsive design

After application:
- **Annotated Document**: Original document with alt-text applied
- **JSON Log File**: `logs/ada-annotator.log` with structured logs

#### Single-Step Workflow Output:
After processing:
- **Annotated Document**: Your original document with AI-generated alt-text applied
- **Markdown Report**: `{output_name}_report.md` with:
  - Processing statistics (success rate, duration)
  - List of processed images with alt-text previews
  - Failed images with error messages
  - Token usage and estimated costs
- **JSON Log File**: `logs/ada-annotator.log` with structured processing logs

### Streamlit Web Interface (Future)

A web interface is planned for Phase 2:

1. **Upload Document**: Drag and drop a DOCX file or click to browse
2. **Extract Images**: System automatically extracts all images
3. **Generate Alt-Text**: AI analyzes each image and creates descriptions
4. **Review**: Preview generated alt-text for each image
5. **Download**: Get your annotated document with alt-text applied

## 🏗️ Project Structure

```
ada-annotator/
├── src/ada_annotator/
│   ├── __init__.py
│   ├── config.py              # Pydantic settings and configuration
│   ├── exceptions.py          # Custom exception hierarchy
│   ├── cli.py                 # Command-line interface (Phase 1)
│   ├── app.py                 # Streamlit web app (Phase 2 - planned)
│   │
│   ├── models/                # Pydantic data models
│   │   ├── image_metadata.py  # Image extraction results
│   │   ├── context_data.py    # Hierarchical context
│   │   ├── alt_text_result.py # AI generation results
│   │   └── processing_result.py # Document processing summary
│   │
│   ├── document_processors/   # DOCX & PPTX handling
│   │   ├── base_extractor.py  # Abstract extractor base
│   │   ├── docx_extractor.py  # DOCX image extraction
│   │   ├── pptx_extractor.py  # PPTX image extraction
│   │   ├── base_assembler.py  # Abstract assembler base
│   │   ├── docx_assembler.py  # DOCX alt-text application
│   │   └── pptx_assembler.py  # PPTX alt-text application
│   │
│   ├── ai_services/           # AI integration
│   │   └── semantic_kernel_service.py # SK + Azure OpenAI
│   │
│   ├── generators/            # Alt-text generation
│   │   └── alt_text_generator.py # Orchestrator with validation
│   │
│   └── utils/                 # Utility modules
│       ├── logging.py         # Structured logging (structlog)
│       ├── error_handler.py   # Error handling framework
│       ├── error_tracker.py   # Error tracking and categorization
│       ├── context_extractor.py # 5-level context extraction
│       ├── image_utils.py     # Image processing utilities
│       ├── retry_handler.py   # Exponential backoff retry logic
│       └── report_generator.py # Markdown report generation
│
├── tests/
│   ├── unit/                  # Unit tests (271 tests, 100% pass)
│   ├── integration/           # Integration tests (planned)
│   └── fixtures/              # Test documents and data
│       ├── documents/         # Sample DOCX/PPTX files
│       └── context/           # Sample context files
│
├── docs/
│   ├── requirements.md        # Project requirements
│   ├── phase_summaries/       # Phase implementation summaries
│   └── adr/                   # Architecture Decision Records
│
├── scripts/
│   └── setup.ps1              # Automated setup script (Windows)
│
├── .copilot-tracking/         # Implementation tracking (internal)
│   ├── plans/                 # Task plans and checklists
│   ├── details/               # Detailed specifications
│   ├── research/              # Research and references
│   └── changes/               # Implementation change logs
│
├── pyproject.toml             # Project config (dependencies, tools)
├── .env.example               # Environment variable template
├── SETUP_GUIDE.md             # Detailed setup instructions
└── README.md                  # This file
```

## 🔧 Development

### Running Tests

```bash
# Run all tests with coverage report
pytest --cov=src/ada_annotator --cov-report=term-missing

# Run specific test file
pytest tests/unit/test_alt_text_generator.py -v

# Run tests for a specific module
pytest tests/unit/test_docx_extractor.py tests/unit/test_pptx_extractor.py -v

# Generate HTML coverage report
pytest --cov=src/ada_annotator --cov-report=html
# Open htmlcov/index.html in browser

# Run with verbose output and show print statements
pytest -v -s

# Run only failed tests from last run
pytest --lf
```

**Current Test Status:**
- **271 tests passing (100%)**
- **87% code coverage** (exceeds 80% target)
- All modules tested (unit tests)
- Integration tests planned for Phase 2

### Code Quality

```bash
# Format code with black (79-char line limit)
black src/ tests/ --line-length 79

# Lint with ruff
ruff check src/ tests/

# Fix auto-fixable issues
ruff check src/ tests/ --fix

# Type check with mypy
mypy src/ada_annotator

# Run all quality checks
black src/ tests/ --line-length 79 --check
ruff check src/ tests/
mypy src/ada_annotator
pytest --cov=src/ada_annotator --cov-fail-under=80
```

### Project Standards

All code follows:
- **PEP 8**: Python style guide
- **PEP 257**: Docstring conventions
- **Type hints**: On all function signatures
- **79-character line limit**: For readability
- **4-space indentation**: Standard Python
- **Comprehensive error handling**: All edge cases covered
- **Structured logging**: JSON logs with correlation IDs

See [.github/instructions/python.instructions.md](.github/instructions/python.instructions.md) for full coding standards.

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

### Phase 1: CLI Implementation ✅ COMPLETE
- [x] Project infrastructure (logging, models, error handling)
- [x] CLI argument parsing and validation
- [x] DOCX image extraction with position metadata
- [x] PPTX image extraction with EMU precision
- [x] 5-level hierarchical context extraction
- [x] Semantic Kernel + Azure OpenAI integration
- [x] Alt-text generation with validation
- [x] DOCX output with position preservation
- [x] PPTX output with property preservation
- [x] Markdown reports and error tracking
- [x] Comprehensive test suite (87% coverage)
- [x] Complete documentation

**Status:** Phase 1 is production-ready with >80% test coverage

### Phase 2: Web Interface (Planned - Week 3-4)
- [ ] Streamlit web application
- [ ] File upload interface
- [ ] Real-time processing progress
- [ ] Manual alt-text review/editing
- [ ] Batch document processing
- [ ] Deploy to Azure App Service

### Phase 3: Enhanced Features (Future)
- [ ] PDF support with OCR integration
- [ ] Multi-language support
- [ ] Custom validation rules
- [ ] Alt-text quality scoring
- [ ] A/B testing for prompt optimization
- [ ] Integration with LMS platforms

### Phase 4: Enterprise Features (Future)
- [ ] Azure Functions deployment
- [ ] Queue-based batch processing
- [ ] User authentication and authorization
- [ ] Document version history
- [ ] Audit logging and compliance reporting
- [ ] RESTful API for integrations

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
