# ADA Compliance Image Annotation System - Requirements Document

**Project Name:** Picture Annotations for ADA Compliance
**Version:** 1.0
**Date:** October 18, 2025
**Author:** System Requirements Team

---

## 1. Executive Summary

### 1.1 Purpose
Develop an automated system that processes document files (DOCX, PDF, PowerPoint) to extract images and generate ADA-compliant alternative text descriptions using AI-powered analysis through Microsoft Semantic Kernel.

### 1.2 Target Users
- College professors and educators
- Educational content creators
- Academic institutions requiring ADA compliance
- Document accessibility coordinators

### 1.3 Primary Goal
Simplify the process of making educational documents ADA-compliant by automatically generating descriptive alternative text for images embedded in common document formats.

---

## 2. Functional Requirements

### 2.1 Document Processing

#### FR-2.1.1: Multi-Format Document Support
- **Priority:** High
- **Description:** System must accept and process the following document formats:
  - Microsoft Word (.docx)
  - PDF (.pdf)
  - Microsoft PowerPoint (.pptx)
- **Acceptance Criteria:**
  - System successfully extracts images from all supported formats
  - Maintains image quality during extraction
  - Handles encrypted/password-protected documents gracefully with clear error messages

#### FR-2.1.2: Image Extraction
- **Priority:** High
- **Description:** Extract all embedded images from uploaded documents
- **Acceptance Criteria:**
  - Extracts images from document body, headers, footers, and slide notes
  - Preserves image metadata (position, size, context)
  - Handles various image formats (JPEG, PNG, GIF, BMP, SVG)
  - Processes both inline and floating images
  - Extracts images from complex layouts (tables, text boxes, grouped objects)

#### FR-2.1.3: Document Context Analysis
- **Priority:** High (elevated for Phase 1)
- **Description:** Extract surrounding text context for each image to improve annotation quality
- **Acceptance Criteria:**
  - Captures text within proximity of images (before/after paragraphs)
  - Identifies image captions and figure labels
  - Preserves document structure context (section headings, slide titles)
  - Accepts optional external context file for additional information
  - Merges multiple context sources (file, document, local) intelligently
  - Configurable context window size (e.g., 2 paragraphs before/after)

### 2.2 AI-Powered Image Annotation

#### FR-2.2.1: Semantic Kernel Integration
- **Priority:** High
- **Description:** Utilize Microsoft Semantic Kernel to orchestrate AI-powered image analysis
- **Acceptance Criteria:**
  - Successfully integrates Semantic Kernel Python SDK
  - Implements proper plugin architecture for extensibility
  - Supports multiple AI service connectors (Azure OpenAI, OpenAI)
  - Handles API rate limiting and retries gracefully

#### FR-2.2.2: Image Description Generation
- **Priority:** High
- **Description:** Generate descriptive alternative text that meets ADA compliance standards
- **Acceptance Criteria:**
  - Descriptions are concise (100-150 characters preferred, max 250 characters)
  - Descriptions convey the purpose and content of images
  - Handles different image types: photographs, diagrams, charts, graphs, screenshots, illustrations
  - Avoids redundant phrases like "image of" or "picture of"
  - Includes relevant data for charts/graphs (trends, key values)
  - Identifies text within images (OCR capability)

#### FR-2.2.3: Context-Aware Annotations
- **Priority:** Medium
- **Description:** Enhance annotations using document context
- **Acceptance Criteria:**
  - Uses surrounding text to inform image descriptions
  - References document subject matter in annotations
  - Adjusts technical level based on document type (academic, instructional, presentation)

#### FR-2.2.4: Long Description Support
- **Priority:** Medium
- **Description:** Generate detailed long descriptions for complex images
- **Acceptance Criteria:**
  - Identifies complex images requiring extended descriptions
  - Generates comprehensive long descriptions (no length limit)
  - Links short alt-text to long descriptions appropriately

### 2.3 Document Output

#### FR-2.3.1: Annotated Document Generation
- **Priority:** High
- **Description:** Produce modified documents with AI-generated alt-text applied
- **Acceptance Criteria:**
  - Maintains original document formatting and layout
  - Preserves all non-image content unchanged
  - Applies alt-text to all images in format-appropriate manner
  - Generates output in same format as input

#### FR-2.3.2: Annotation Report
- **Priority:** Medium
- **Description:** Provide summary report of annotation process
- **Acceptance Criteria:**
  - Lists all images processed with before/after preview
  - Includes confidence scores for AI-generated descriptions
  - Highlights any images that failed processing
  - Provides edit interface for manual review/correction

#### FR-2.3.3: Batch Processing
- **Priority:** Medium (Phase 2 feature)
- **Description:** Support processing multiple documents in a single operation
- **Acceptance Criteria:**
  - CLI: Process all files in a directory (Phase 5)
  - Web UI: Accept multiple file uploads simultaneously (Phase 2)
  - Provides progress tracking for batch operations
  - Generates combined report for all processed documents
  - Option to use same context file for entire batch

---

## 3. Non-Functional Requirements

### 3.1 Performance

#### NFR-3.1.1: Processing Speed
- **Priority:** High
- **Description:** System must process documents efficiently
- **Acceptance Criteria:**
  - Process documents with <10 images in under 60 seconds
  - Process documents with 10-50 images in under 5 minutes
  - Handle documents with 50+ images with progress indication

#### NFR-3.1.2: Scalability
- **Priority:** Medium
- **Description:** System should handle concurrent users
- **Acceptance Criteria:**
  - Support at least 10 concurrent users for web deployment
  - Queue mechanism for high-load scenarios
  - Horizontal scaling capability for cloud deployment

### 3.2 Usability

#### NFR-3.2.1: User Interface
- **Priority:** High
- **Description:** Interface must be intuitive for non-technical users
- **Acceptance Criteria:**
  - Simple file upload with drag-and-drop support
  - Clear progress indicators during processing
  - Easy download of processed documents
  - Responsive design for desktop and tablet devices

#### NFR-3.2.2: Error Handling
- **Priority:** High
- **Description:** Provide clear error messages and recovery options
- **Acceptance Criteria:**
  - User-friendly error messages (no technical jargon)
  - Suggestions for resolving common errors
  - Partial processing support (process successful images even if some fail)
  - Logging for troubleshooting

### 3.3 Security

#### NFR-3.3.1: Data Privacy (Phase 1 - Local)
- **Priority:** High
- **Description:** Protect user document content and privacy
- **Acceptance Criteria (Phase 1):**
  - Temporary files deleted immediately after processing
  - No transmission of document content except to AI service
  - UTF-8 encoding with proper escaping to prevent injection
  - **Note:** Full security implementation deferred to Phase 3 (cloud deployment)
  - **Future Requirements:**
    - HTTPS for all file uploads (Phase 3)
    - Encryption at rest for temporary storage (Phase 3)
    - FERPA compliance audit (Phase 3)
    - Data retention policies and automatic purging (Phase 3)

#### NFR-3.3.2: API Key Management
- **Priority:** High
- **Description:** Secure handling of AI service credentials
- **Acceptance Criteria:**
  - API keys stored in `.env` file (never in config.json or code)
  - `.env` file in `.gitignore` to prevent accidental commit
  - No hardcoded credentials in source code
  - API keys loaded via `python-dotenv` at runtime
  - Validation of API key format at startup (fail fast)
  - **Future:** Azure Key Vault integration (Phase 3)

#### NFR-3.3.3: Input Validation
- **Priority:** High
- **Description:** Validate all user inputs to prevent attacks
- **Acceptance Criteria:**
  - File path validation (prevent directory traversal)
  - File size limits enforced (max 50MB)
  - File format validation (magic bytes, not just extension)
  - Context file size limits (max 1MB)
  - Sanitize file paths in logs (no PII exposure)
  - Command injection prevention in CLI arguments

### 3.4 Reliability

#### NFR-3.4.1: Availability
- **Priority:** Medium
- **Description:** System should be available during typical usage hours
- **Acceptance Criteria:**
  - 99% uptime during business hours (8 AM - 8 PM local time)
  - Graceful degradation if AI service unavailable
  - Automatic retry mechanisms for transient failures

#### NFR-3.4.2: Data Integrity
- **Priority:** High
- **Description:** Ensure original documents are never corrupted
- **Acceptance Criteria:**
  - Original documents remain unmodified
  - Output generation failures don't affect source files
  - Validation of document integrity before and after processing

### 3.5 Maintainability

#### NFR-3.5.1: Code Quality
- **Priority:** High
- **Description:** Follow Python coding best practices
- **Acceptance Criteria:**
  - PEP 8 compliant code
  - Comprehensive docstrings for all functions
  - Type hints for function signatures
  - Unit test coverage >80%

#### NFR-3.5.2: Documentation
- **Priority:** High
- **Description:** Comprehensive technical and user documentation
- **Acceptance Criteria:**
  - README with setup and usage instructions
  - API documentation for developers
  - User guide for professors
  - Architecture decision records (ADRs)

---

## 4. Technical Requirements

### 4.1 Core Technologies

#### TR-4.1.1: Programming Language
- **Technology:** Python 3.11+
- **Rationale:**
  - **Best-in-class document processing libraries:** `python-docx`, `python-pptx`, `PyPDF2` are mature and actively maintained
  - **Excellent AI/ML ecosystem:** First-class support for OpenAI, Azure OpenAI, and Semantic Kernel
  - **Rapid prototyping:** Streamlit enables quick UI development for local→cloud progression
  - **Local-to-cloud flexibility:** Same codebase runs locally and on Azure (App Service, Functions, Container Apps)
  - **Strong typing support:** Type hints and `mypy` for production-grade code quality

- **Alternative Considered - C#/.NET:**
  - ✅ Native Office Interop for desktop apps
  - ✅ Excellent Semantic Kernel support
  - ❌ Less mature PDF processing
  - ❌ Steeper learning curve for document manipulation
  - **Verdict:** Python preferred for this use case

- **Alternative Considered - Node.js/TypeScript:**
  - ✅ Excellent for web-first applications
  - ❌ Immature document processing libraries
  - ❌ Limited image processing ecosystem compared to Python
  - **Verdict:** Not recommended for document-heavy workflows

#### TR-4.1.2: AI Orchestration
- **Technology:** Microsoft Semantic Kernel (Python SDK)
- **Rationale:** Requirement specified; provides robust AI orchestration and plugin architecture

#### TR-4.1.3: Document Processing Libraries (Windows-Optimized)
- **Required Libraries:**
  - `python-docx`: For DOCX file processing (best-in-class, cross-platform)
  - `python-pptx`: For PowerPoint processing (native Office Open XML support)
  - `Pillow (PIL)`: For image manipulation
  - **Note:** PDF support deferred to Phase 2 (library TBD: pypdf, pdfplumber, or PyMuPDF)
  - **Note:** OCR capabilities (pytesseract) deferred to Phase 2
  - **Note:** Legacy DOC format not supported (Office Interop too complex)

#### TR-4.1.4: AI Services
- **Technology:** Azure OpenAI Service or OpenAI API
- **Rationale:** Required for GPT-4 Vision or similar multimodal model support

### 4.2 Development Tools

#### TR-4.2.1: Version Control
- **Technology:** Git + GitHub
- **Rationale:** Standard industry practice

#### TR-4.2.2: Testing Framework
- **Technology:** pytest
- **Rationale:** Comprehensive Python testing framework

#### TR-4.2.3: Code Quality Tools
- **Technologies:**
  - `black`: Code formatting
  - `pylint` or `ruff`: Linting
  - `mypy`: Type checking

---

## 5. Deployment Options

### 5.1 Recommended Deployment Architectures

#### 5.1.1: Option A - Azure Web App + Azure Functions (Recommended)
- **Components:**
  - **Frontend:** Azure Static Web Apps or Azure App Service
  - **Backend:** Azure Functions (Python) for processing
  - **Storage:** Azure Blob Storage for temporary file storage
  - **AI Service:** Azure OpenAI Service
  - **Secrets:** Azure Key Vault

- **Advantages:**
  - Serverless scaling for cost efficiency
  - Pay-per-use model ideal for academic usage patterns
  - Integrated with Azure services ecosystem
  - Built-in security and compliance features

- **Use Case:** Best for institutional deployment with multiple professors

#### 5.1.2: Option B - Streamlit Web Application
- **Components:**
  - **Framework:** Streamlit for rapid UI development
  - **Hosting:** Azure App Service or Azure Container Apps
  - **AI Service:** Azure OpenAI or OpenAI API

- **Advantages:**
  - Rapid development and deployment
  - Minimal frontend development required
  - Easy to prototype and iterate
  - Built-in file upload and download widgets

- **Use Case:** Quick deployment for single professor or small department

#### 5.1.3: Option C - Flask/FastAPI Web Application
- **Components:**
  - **Backend:** Flask or FastAPI
  - **Frontend:** Simple HTML/JavaScript or React
  - **Hosting:** Azure App Service, Azure Container Apps, or Docker
  - **AI Service:** Azure OpenAI or OpenAI API

- **Advantages:**
  - Full control over application architecture
  - RESTful API for future integrations
  - Professional web application structure

- **Use Case:** Production-grade deployment with future extensibility

#### 5.1.4: Option D - Desktop Application (Low Priority)
- **Components:**
  - **Framework:** PyQt or Tkinter
  - **Distribution:** Executable via PyInstaller

- **Advantages:**
  - No hosting costs
  - Works offline (with local AI models)
  - Full privacy (documents never leave user's machine)

- **Disadvantages:**
  - Requires software installation
  - Limited to local computing resources
  - More complex distribution and updates

### 5.2 Deployment Recommendation

**Primary Recommendation: Progressive Deployment Strategy (Local → Cloud MVP → Cloud Scale)**

**Tier 1 - Local CLI:**
- **Deployment:** Command-line application run locally
- **Purpose:** Core functionality development and validation
- **Benefits:**
  - Zero hosting costs during development
  - Fast iteration cycles
  - Easy debugging with breakpoints
  - Works offline for sensitive documents
  - Scriptable and automatable
  - Processes all document formats (DOCX, DOC, PDF, PPTX)
  - Supports context files for enhanced processing
- **Limitations:** Single document at a time, command-line interface only

**Tier 2 - Local Web UI:**
- **Deployment:** Streamlit web app on `localhost`
- **Purpose:** User-friendly interface for non-technical users
- **Benefits:**
  - Wrap CLI with intuitive UI
  - File upload instead of command-line
  - Visual preview of images and alt-text
  - Batch processing support
  - Review and edit interface
  - Still runs locally (no hosting needed)
- **Cost:** $0 (still local development)

**Tier 3 - Cloud Deployment:**
- **Deployment:** Streamlit on Azure App Service
- **Purpose:** Make accessible to professors across institution
- **Benefits:**
  - Public URL for easy access
  - 5-10 concurrent users supported
  - Managed hosting (no server maintenance)
  - Automatic backups and monitoring
- **Cost:** ~$50-100/month for App Service Basic tier

**Tier 4 - Enterprise Scale (Phase 4+):**
- **Deployment:** Azure Functions with Azure Blob Storage and Queue
- **Purpose:** Production deployment for multi-institution use
- **Benefits:**
  - Serverless autoscaling (20+ concurrent users)
  - Pay-per-execution model (cost-effective for bursty workloads)
  - Enterprise-grade reliability and security
  - Integration with Azure ecosystem
  - API endpoints for LMS integration
- **Cost:** Pay-per-use, typically $100-300/month depending on usage

---

## 6. System Architecture

### 6.1 High-Level Architecture

```
┌─────────────────┐
│   User (Web)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Web Interface  │ (Streamlit/Flask/FastAPI)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Document        │
│ Processor       │ (python-docx, pypdf, python-pptx)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Image Extractor │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│   Semantic Kernel Engine    │
│  ┌─────────────────────┐    │
│  │  AI Plugins         │    │
│  │  - Image Analyzer   │    │
│  │  - Context Analyzer │    │
│  │  - ADA Validator    │    │
│  └─────────────────────┘    │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│   Azure OpenAI / OpenAI     │
│   (GPT-4 Vision API)        │
└─────────────────────────────┘
           │
           ▼
┌─────────────────┐
│ Document        │
│ Assembler       │ (Generates annotated document)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Output File    │
└─────────────────┘
```

### 6.2 Component Breakdown

#### 6.2.1 CLI Interface Layer
- Argument parsing and validation
- Progress display (console)
- Error messaging
- Exit code management

#### 6.2.2 Document Processing Layer
- Format detection (DOCX, PPTX)
- Image extraction with position metadata
- Multi-level context analysis
- Configuration management (JSON + .env)

#### 6.2.3 AI Processing Layer (Semantic Kernel)
- Image analysis plugin (vision-capable model)
- Alt-text generation with prompt template
- Context integration (4-level hierarchy)
- Alt-text validation and quality gates
- AI service availability checking

#### 6.2.4 Output Generation Layer
- Document reconstruction with position preservation
- Alt-text injection without layout reflow
- Format-specific rendering (DOCX, PPTX)
- Report generation (markdown)
- Failed images tracking

#### 6.2.5 Logging & Monitoring Layer
- Structured JSON logging (local file)
- Cost tracking (tokens, API calls)
- Performance metrics collection
- Error tracking with correlation IDs
- Abstracted logger interface (future Azure App Insights migration)

### 6.3 Data Models (Pydantic Schemas)

```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Literal
from datetime import datetime
from pathlib import Path

class ImageMetadata(BaseModel):
    """Metadata for extracted image."""
    image_id: str = Field(..., description="Unique identifier for image")
    filename: str = Field(..., description="Temporary filename for extracted image")
    format: Literal["JPEG", "PNG", "GIF", "BMP"] = Field(..., description="Image format")
    size_bytes: int = Field(..., description="Image file size in bytes")
    width_pixels: int = Field(..., description="Image width")
    height_pixels: int = Field(..., description="Image height")
    page_number: Optional[int] = Field(None, description="Page number (DOCX) or slide number (PPTX)")
    position: dict = Field(..., description="Position metadata: {x, y, anchor_type}")
    existing_alt_text: Optional[str] = Field(None, description="Existing alt-text if any")

class ContextData(BaseModel):
    """Hierarchical context for image."""
    external_context: Optional[str] = Field(None, description="Content from --context file")
    document_context: str = Field(..., description="Document title, subject, metadata")
    section_context: Optional[str] = Field(None, description="Current section/chapter heading")
    page_context: Optional[str] = Field(None, description="Page/slide title or header")
    local_context: str = Field(..., description="Surrounding paragraphs and captions")

    @validator('local_context', 'document_context')
    def validate_utf8(cls, v):
        """Ensure UTF-8 encoding compatibility."""
        if v:
            v.encode('utf-8')  # Raises UnicodeEncodeError if invalid
        return v

    def get_merged_context(self, max_tokens: int = 3000) -> str:
        """Merge contexts with truncation if needed."""
        parts = []
        if self.external_context:
            parts.append(f"[External Context] {self.external_context}")
        parts.append(f"[Document: {self.document_context}]")
        if self.section_context:
            parts.append(f"[Section: {self.section_context}]")
        if self.page_context:
            parts.append(f"[Page: {self.page_context}]")
        parts.append(f"[Local: {self.local_context}]")

        merged = " | ".join(parts)
        # Truncate if exceeds token limit (rough estimate: 4 chars per token)
        if len(merged) > max_tokens * 4:
            merged = merged[:max_tokens * 4] + "..."
        return merged

class AltTextResult(BaseModel):
    """Generated alt-text with validation."""
    image_id: str = Field(..., description="Reference to ImageMetadata.image_id")
    alt_text: str = Field(..., description="Generated alt-text description")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="AI confidence")
    validation_passed: bool = Field(..., description="Passed quality gates")
    validation_warnings: List[str] = Field(default_factory=list, description="Quality warnings")
    tokens_used: int = Field(..., description="AI tokens consumed")
    processing_time_seconds: float = Field(..., description="Generation time")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    @validator('alt_text')
    def validate_alt_text(cls, v):
        """Apply alt-text validation rules."""
        if len(v) < 10:
            raise ValueError("Alt-text too short (min 10 characters)")
        if len(v) > 250:
            raise ValueError("Alt-text too long (max 250 characters)")
        if not v[0].isupper():
            raise ValueError("Alt-text must start with capital letter")
        if not v.endswith('.'):
            v += '.'  # Auto-correct missing period
        forbidden = ["image of", "picture of", "graphic showing"]
        if any(phrase in v.lower() for phrase in forbidden):
            raise ValueError(f"Alt-text contains forbidden phrase: {forbidden}")
        return v

class ProcessingError(BaseModel):
    """Failed image processing record."""
    image_id: str
    page_number: Optional[int]
    error_type: str = Field(..., description="Error category: extraction, ai_service, validation")
    error_message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class DocumentProcessingResult(BaseModel):
    """Complete processing result for document."""
    input_file: Path
    output_file: Path
    document_type: Literal["DOCX", "PPTX"]
    total_images: int
    successful_images: int
    failed_images: int
    images_processed: List[AltTextResult]
    errors: List[ProcessingError]
    total_tokens_used: int
    estimated_cost_usd: float
    processing_duration_seconds: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AppConfig(BaseModel):
    """Application configuration (from config.json)."""
    ai: dict = Field(..., description="AI service configuration")
    alt_text: dict = Field(..., description="Alt-text generation settings")
    processing: dict = Field(..., description="Document processing limits")
    output: dict = Field(..., description="Output generation settings")
    logging: dict = Field(..., description="Logging configuration")

    @validator('ai')
    def validate_ai_config(cls, v):
        """Ensure required AI fields present."""
        required = ['service_type', 'model']
        if not all(k in v for k in required):
            raise ValueError(f"AI config missing required fields: {required}")
        return v
```

---

## 7. ADA Compliance Standards

### 7.1 WCAG 2.1 Guidelines

#### 7.1.1 Level A Requirements (Must Have)
- **1.1.1 Non-text Content:** All images must have text alternatives
- **1.4.5 Images of Text:** Minimize use of text in images; extract and describe

#### 7.1.2 Level AA Requirements (Should Have)
- Descriptions should be meaningful and context-appropriate
- Complex images should have long descriptions
- Decorative images should be marked as such (empty alt text)

### 7.2 Alt-Text Best Practices

#### 7.2.1 Content Guidelines
- **Informative Images:** Describe what the image conveys
- **Functional Images:** Describe the action/purpose
- **Complex Images:** Provide structured long descriptions
- **Decorative Images:** Use empty alt attribute (alt="")

#### 7.2.2 Writing Style
- Be concise but descriptive
- Avoid "image of" or "picture of"
- Include relevant text from image
- Describe charts/graphs with key data points
- Use objective, factual language

---

## 8. Data Flow

### 8.1 Processing Pipeline

```
1. Upload Document
   ↓
2. Validate Format & Extract Images
   ↓
3. For Each Image:
   a. Extract surrounding context
   b. Send to Semantic Kernel
   c. Semantic Kernel calls AI service
   d. Generate alt-text description
   e. Optional: Generate long description
   ↓
4. Apply Annotations to Document
   ↓
5. Generate Output Document
   ↓
6. Create Processing Report
   ↓
7. Return Results to User
```

### 8.2 Error Handling Flow

```
Error Detected
   ↓
Log Error Details
   ↓
Determine Severity
   ├── Critical: Stop processing
   │   ↓
   │   Notify user with recovery options
   │
   └── Non-Critical: Continue processing
       ↓
       Mark failed items in report
       ↓
       Process remaining items
```

---

## 9. Integration Requirements

### 9.1 Semantic Kernel Integration

#### 9.1.1 Plugin Architecture
- **Image Analysis Plugin:**
  - Function: `analyze_image(image: bytes, context: str) -> str`
  - Purpose: Analyze image and generate description

- **ADA Validator Plugin:**
  - Function: `validate_ada_compliance(alt_text: str, image_type: str) -> bool`
  - Purpose: Ensure descriptions meet ADA standards

#### 9.1.2 AI Service Configuration
- Support for multiple AI backends
- Configurable model selection (GPT-4V, GPT-4, etc.)
- Prompt engineering for optimal descriptions
- Temperature and token limit configuration

### 9.2 External Service Dependencies

#### 9.2.1 Azure OpenAI Service
- **API:** Vision API for image analysis
- **Authentication:** API key or Azure AD
- **Rate Limits:** Handle throttling gracefully

#### 9.2.2 Optional: OCR Service
- **Azure Computer Vision:** For text extraction from images
- **Tesseract OCR:** Open-source alternative

---

## 10. Testing Requirements

### 10.1 Unit Testing (TDD Approach)

#### UT-10.1.1: Document Processing (Target: >80% coverage)
- **DOCX Extraction:**
  - Test image extraction from body, headers, footers
  - Test position metadata capture (x, y, anchor type)
  - Test with various image formats (JPEG, PNG, GIF, BMP)
  - Test with inline, floating, and anchored images
  - Test with corrupted images (expect graceful failure)
- **PPTX Extraction:**
  - Test image extraction from slides and slide notes
  - Test slide number and title capture
  - Test with grouped objects and layered images
- **Context Extraction:**
  - Test 4-level hierarchy (external, document, section, page, local)
  - Test context merging algorithm with deduplication
  - Test paragraph extraction (2 before, 2 after)
  - Test caption and figure label identification
  - Test UTF-8 encoding handling
  - Test context truncation when exceeding token limits

#### UT-10.1.2: AI Integration (Use mocks)
- **Semantic Kernel Service:**
  - Mock Azure OpenAI API responses
  - Test AI service availability check (success and failure)
  - Test prompt template rendering with context
  - Test response parsing and error handling
  - Test token counting and cost calculation
  - Test rate limiting and retry logic
- **Alt-Text Validation:**
  - Test length requirements (10-250 chars)
  - Test forbidden phrase detection
  - Test capitalization and punctuation rules
  - Test validation warnings (length, quality)
  - Test auto-correction (missing periods)

#### UT-10.1.3: Output Generation
- **Document Assembly:**
  - Test alt-text injection without layout changes
  - Test image position preservation (exact x, y coordinates)
  - Test with various document structures (simple, complex)
  - Test format preservation (fonts, styles, spacing)
  - Test backup file creation
- **Report Generation:**
  - Test markdown report structure
  - Test failed images section formatting
  - Test cost and token summary
  - Test timestamp formatting

#### UT-10.1.4: Configuration & Logging
- **Config Management:**
  - Test JSON config parsing
  - Test .env file loading
  - Test configuration precedence (CLI > env > config > defaults)
  - Test validation of required fields
  - Test sensitive data exclusion from logs
- **Logging:**
  - Test structured JSON log format
  - Test log rotation (size and count limits)
  - Test PII redaction
  - Test correlation ID generation and tracking
  - Test console vs file output separation

### 10.2 Integration Testing

#### IT-10.2.1: End-to-End Pipeline (Use real test documents)
- **Happy Path Testing:**
  - DOCX with 5 images → annotated DOCX output
  - PPTX with 10 slides, 3 images → annotated PPTX output
  - With context file → verify improved alt-text quality
  - Dry-run mode → verify no file modification
  - Backup mode → verify original preserved
- **Edge Cases:**
  - Document with no images → graceful completion
  - Document with 50+ images → progress tracking, completion
  - Corrupted image in document → skip and continue
  - Very large document (40MB) → successful processing
  - Context file with UTF-8 special characters → proper encoding
- **Error Scenarios:**
  - Invalid file path → exit code 2
  - Unsupported format → exit code 1
  - AI service unavailable → exit code 4
  - Output write permission denied → exit code 5

#### IT-10.2.2: AI Service Integration (Live API calls)
- **Azure OpenAI:**
  - Test with GPT-4o vision API
  - Test with various image types (photo, chart, diagram, screenshot)
  - Test context integration in prompt
  - Measure token usage accuracy
  - Test timeout handling (30 second limit)
- **Error Handling:**
  - Invalid API key → fail fast with exit code 4
  - Rate limiting (429) → exponential backoff retry
  - Service timeout → retry with logging
  - Invalid model name → exit code 4 with message

#### IT-10.2.3: Cross-Module Integration
- Config loading → AI service initialization → document processing
- Context extraction → prompt generation → AI call → validation
- Image extraction → alt-text generation → document assembly
- Error tracking → logging → report generation

### 10.3 User Acceptance Testing

#### UAT-10.3.1: Professor User Testing
- **Test Scenarios:**
  - Process lecture slides (PPTX) with diagrams and charts
  - Process handout document (DOCX) with screenshots
  - Use context file (lecture notes) to enhance descriptions
  - Review generated alt-text for accuracy and usefulness
- **Evaluation Criteria:**
  - Alt-text quality: 4/5+ rating from professors
  - Ease of use: Can run CLI following SETUP_GUIDE without assistance
  - Processing speed: Acceptable for 10-20 image document (<5 minutes)
  - Error clarity: Error messages understandable and actionable
  - ADA compliance: Output passes screen reader testing

### 10.4 Accessibility Testing

#### AT-10.4.1: Output Validation
- Screen reader compatibility
- WCAG 2.1 compliance verification
- Accessibility audit tools (aXe, WAVE)

---

## 11. Success Metrics

### 11.1 Performance Metrics (**Note:** Deferred to Phase 2+)
- **Processing Time:** Average time per document, time per image
- **Success Rate:** Percentage of successfully processed images
- **Accuracy:** Quality of generated alt-text (user ratings)
- **Throughput:** Documents processed per hour
- **Token Efficiency:** Tokens used per image (cost optimization)

**Phase 1 Metrics (Manual Collection):**
- Log processing duration for each document
- Track success/failure counts in summary reports
- Collect anecdotal quality feedback from test users
- Monitor token usage and costs via logs

### 11.2 User Metrics (Phase 2+ when usage scales)
- **Adoption Rate:** Number of active professor users
- **Document Volume:** Number of documents processed
- **User Satisfaction:** Feedback scores and surveys
- **Return Usage:** Percentage of users returning after first use

### 11.3 Quality Metrics
- **ADA Compliance Rate:** Percentage of outputs meeting WCAG 2.1 AA
- **Validation Pass Rate:** Percentage passing automated quality gates
- **Manual Edit Rate:** Percentage of descriptions requiring user correction (Phase 2+)
- **Description Quality Score:** AI-based or human evaluation (Phase 2+)

### 11.4 Cost Metrics
- **Cost per Document:** Average AI API cost per processed document
- **Cost per Image:** Average cost to generate single alt-text
- **Monthly Spend:** Total API costs (for budgeting)
- **Token Efficiency:** Tokens used vs. theoretical minimum
- **Cost Alerts:** Warning when daily spend exceeds threshold (Phase 2+)

---

## 12. Project Phases

### 12.1 Phase 1: Local Prototype

#### 12.1.0: Local Prototype Feature Requirements

**Essential Features (Must Have):**

1. **Command-Line Interface**
   - Process single document via command-line arguments
   - Arguments specification:
     - `input_file` (required, positional): Path to document file
     - `--output, -o` (optional): Output file path (default: `{input}_annotated.{ext}`)
     - `--context, -c` (optional): Path to external context file (TXT or MD)
     - `--verbose, -v` (flag): Enable verbose logging to console
     - `--dry-run` (flag): Preview processing without modifying documents
     - `--backup, -b` (flag): Create backup of original file before processing
     - `--config` (optional): Path to custom config JSON file
     - `--log-file` (optional): Custom log file path (default: `ada_annotator.log`)
   - Exit codes:
     - `0`: Success
     - `1`: Invalid arguments or configuration error
     - `2`: Input file not found or inaccessible
     - `3`: Processing error (document/image extraction failure)
     - `4`: AI service error (unavailable, authentication, rate limit)
     - `5`: Output generation failure

2. **Multi-Format Document Support**
   - **DOCX**: Microsoft Word documents (Office 2007+)
   - **PPTX**: PowerPoint presentations (Office 2007+)
   - **Note:** PDF support deferred to Phase 2 due to complexity
   - **Note:** Legacy DOC format not supported (users should convert to DOCX)
   - Validate file format and size (max 50MB)
   - Display file information (name, size, image count, page count)
   - Windows-only deployment (use Windows-optimized libraries)

3. **Image Extraction**
   - Extract all images from document body, headers, footers
   - Extract images from slides (PPTX) and slide notes
   - Preserve image order and position metadata (critical for maintaining layout)
   - Support JPEG, PNG, GIF, BMP formats
   - Handle inline, floating, and anchored images
   - Save extracted images to temporary directory for inspection
   - Track image source location (page number, section, slide number)

4. **Context Analysis & Hierarchy**
   - **Context Priority Hierarchy** (from lowest to highest):
     1. **External Context File**: Optional TXT/MD file provided via `--context`
     2. **Document-Level Context**: Document title, subject, author metadata
     3. **Chapter/Section Context**: Current section heading, chapter title (if available)
     4. **Page/Slide Context**: Current page/slide title or header
     5. **Image-Local Context**: Surrounding paragraphs (2 before, 2 after), captions, figure labels
   - **Context Merging Algorithm**:
     - Concatenate contexts in priority order
     - Truncate if total exceeds AI token limit (reserve ~3000 tokens for context)
     - Deduplicate repeated text across context levels
     - Format as: `[External Context] | [Document: {title}] | [Section: {heading}] | [Local: {text}]`
   - Identify and extract image captions and figure labels
   - Extract alt-text from existing images (if any) for comparison
   - UTF-8 encoding required for all text extraction

5. **AI-Powered Alt-Text Generation**
   - Integrate Semantic Kernel with Azure OpenAI or OpenAI
   - **AI Service Availability Check**:
     - Validate AI service connection at startup
     - If configured model unavailable: Exit with code 4 and message "AI service unavailable: {model_name} not accessible"
     - Test API authentication before processing
   - Generate alt-text descriptions for each image using vision-capable model
   - Use GPT-4o (recommended) or GPT-4V for vision capabilities
   - Pass combined context (external + document + section + page + local) to AI
   - Console progress indicators: `"Processing image 3 of 12 (slide 5)..."`
   - **Prompt Template** (Semantic Kernel semantic function format):
     ```
     You are an accessibility expert creating alt-text for educational documents.

     Context: {{$context}}

     Image Analysis Task:
     Analyze the provided image and generate a concise, descriptive alt-text that:
     - Describes the essential content and purpose (100-150 characters preferred, max 250)
     - Avoids phrases like "image of" or "picture of"
     - For charts/graphs: Include key data points and trends
     - For diagrams: Describe structure and relationships
     - For screenshots: Describe UI elements and their purpose
     - Uses objective, factual language
     - Matches the technical level of the surrounding content

     Alt-text:
     ```
   - **Alt-Text Validation Rules**:
     - Length: 10-250 characters (warn if <50 or >200)
     - No forbidden phrases: "image of", "picture of", "graphic showing"
     - No technical jargon unless present in context
     - Must start with capital letter, end with period
     - No redundant whitespace
     - ASCII-compatible characters only (avoid emojis, special symbols)

6. **Document Output**
   - Apply generated alt-text to original document structure
   - **Critical**: Maintain all original formatting and image positioning
     - Images must remain in exact same location (page, position, size)
     - Alt-text modification should not trigger layout reflow
     - Preserve text wrapping, anchoring, and z-order
   - Generate annotated output document in same format as input
   - Preserve all non-image content unchanged (text, formatting, styles, metadata)
   - Create backup of original if `--backup` flag specified
   - Generate summary report (text file) with all annotations
   - **Failed Images Tracking**:
     - Maintain list of images that failed processing
     - Output format: `Failed: {image_name} on Page {page_num} - Reason: {error_message}`
     - Include in summary report and console output at completion
     - Partial success: Continue processing remaining images after failure

7. **Configuration Management**
   - **Config File Format**: JSON
   - **Default Config Location**: `config.json` in project root
   - **Config File Schema**:
     ```json
     {
       "ai": {
         "service_type": "azure_openai",
         "model": "gpt-4o",
         "temperature": 0.3,
         "max_tokens": 500,
         "timeout_seconds": 30
       },
       "alt_text": {
         "preferred_length": 150,
         "max_length": 250,
         "min_length": 10
       },
       "processing": {
         "max_file_size_mb": 50,
         "max_images_per_document": 100,
         "context_paragraphs_before": 2,
         "context_paragraphs_after": 2
       },
       "output": {
         "report_format": "markdown",
         "create_backup": false,
         "temp_directory": "./temp"
       },
       "logging": {
         "level": "INFO",
         "file": "ada_annotator.log",
         "format": "json"
       }
     }
     ```
   - **Sensitive Configuration**: `.env` file (in `.gitignore`)
     - API keys, endpoints, secrets
     - Never commit to repository
     - Loaded via `python-dotenv`
   - **Configuration Precedence**: CLI args > Environment variables > Config file > Defaults
   - Load API keys from `.env` file (never from config.json)
   - Support multiple AI service options (Azure OpenAI, OpenAI)
   - Prompt template stored as separate file (`prompts/alt_text_template.txt`)

8. **Error Handling & Logging**
   - **Logging Architecture**:
     - **Phase 1**: Local file logging with structured JSON format
     - **Future Phases**: Azure Application Insights integration
     - **Design Pattern**: Abstract logger interface for easy provider switching
     - Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
     - Structured logging with correlation IDs for tracking document processing
   - **Log Output**:
     - Console: Human-readable progress and errors (INFO+)
     - File: Structured JSON for analysis (DEBUG+)
     - Log rotation: Max 10MB per file, keep 5 historical files
   - **Log Content**:
     - Timestamp (ISO 8601), level, message, correlation_id
     - Document name, image count, processing duration
     - AI API calls (without sensitive data), token usage, costs
     - Errors with stack traces (redact sensitive paths)
   - Detailed console output with progress bars (using `rich` library)
   - Graceful handling of unsupported images (skip and log)
   - Continue processing on individual image failures
   - Clear error messages with troubleshooting hints
   - PII redaction in logs (document content, user paths)

**Command-Line Usage Examples:**
```bash
# Basic usage
ada-annotator document.docx

# With custom output path
ada-annotator slides.pptx --output annotated_slides.pptx

# With context file
ada-annotator slides.pptx --context lecture_notes.md

# Verbose mode with backup
ada-annotator document.docx --verbose --backup

# Dry run to preview
ada-annotator presentation.pptx --dry-run

# Custom config and log file
ada-annotator document.docx --config custom_config.json --log-file processing.log
```

**Nice-to-Have Features (Optional for Local Prototype):**

1. **Interactive Mode**
   - Review each generated alt-text before applying
   - Option to manually edit descriptions
   - Accept/Reject/Edit workflow per image
   - Regenerate individual descriptions with different prompts

2. **Enhanced Reporting**
   - JSON output with all annotations and metadata
   - CSV report with image details and alt-text
   - Markdown report with embedded image previews
   - Statistics (processing time, success rate, token usage)

3. **Advanced Context Options**
   - Extract text from images via OCR (for context, not alt-text)
   - Specify context radius (paragraphs before/after)
   - Document subject/domain hint for better context

4. **Configuration Profiles**
   - Save/load processing profiles (academic, technical, simple)
   - Different prompt templates per profile
   - Profile-specific AI settings

**Explicitly Out of Scope for Local Prototype:**
- PDF support → Phase 2 (deferred due to complexity)
- Legacy DOC format → Not supported (users convert to DOCX)
- Web UI (Streamlit) → Phase 2
- Batch processing (multiple files) → Phase 5
- User authentication → Phase 3
- Cloud storage → Phase 3
- Long description generation → Phase 2
- Image editing/manipulation → Phase 3
- Multi-language support → English only (UTF-8)
- LMS integration → Phase 4
- Real-time collaboration → Phase 4
- Performance metrics and monitoring → Phase 2+

#### 12.1.1: Core Document Processing & AI Integration
**Deliverables:**
- Command-line application with argument parsing (argparse)
- DOCX image extraction with position preservation
- PPTX image extraction with slide context
- Semantic Kernel integration with Azure OpenAI
- Alt-text generation using vision API with prompt template
- Multi-level context extraction (document, section, page, local)
- Output generation for DOCX with maintained image positioning
- JSON configuration management with .env for secrets
- Structured logging to local file

**Development Environment:**
- Windows 10/11 with Python 3.11+
- Visual Studio Code with Python extension
- API keys in `.env` file (not committed to Git)
- Test with sample DOCX and PPTX documents (3-5 images each)
- Project managed with `uv` for fast dependency management
- TDD approach: Write tests first, then implementation

**Success Criteria:**
- CLI accepts file path and all specified options
- Successfully extracts images from DOCX and PPTX with position metadata
- Extracts context using 4-level hierarchy
- Generates alt-text for 80%+ of test images
- Alt-text passes validation rules (length, format, content)
- Produces valid annotated documents with preserved image positions
- Images maintain exact layout positions after alt-text insertion
- Failed images tracked and reported with page numbers
- Console shows clear progress indicators
- AI service unavailability handled gracefully with exit code 4
- Test coverage >80% for core modules
- Runs on Windows development machine

**Implementation Tasks (TDD approach):**
1. Write test suite for CLI argument parsing → Implement CLI with argparse
2. Write tests for DOCX image extraction → Implement DOCX extractor with position tracking
3. Write tests for context hierarchy → Implement multi-level context extractor
4. Write tests for config management → Implement JSON config + .env loading
5. Write tests for Semantic Kernel service → Implement SK wrapper with AI availability check
6. Write tests for alt-text generation → Implement vision plugin with prompt template
7. Write tests for alt-text validation → Implement validation rules and quality gates
8. Write tests for document assembly → Implement DOCX assembler with position preservation
9. Write tests for failed image tracking → Implement error collection and reporting
10. Write tests for logging → Implement structured JSON logger with rotation
11. Integration tests for full pipeline
12. Create sample test documents (DOCX, PPTX) with various image types

#### 12.1.2: Enhanced Features & Documentation
**Deliverables:**
- Enhanced PPTX processing with slide notes extraction
- Context file support (--context parameter) for TXT/MD files
- Context merging algorithm (external + document + section + page + local)
- Summary report generation with failed images list
- Enhanced error handling with exit codes
- Cost tracking and logging for AI API usage
- Comprehensive documentation (README with Getting Started, SETUP_GUIDE)
- User-facing examples and troubleshooting guide

**Development Environment:**
- Continue local Windows development
- Test with varied documents (DOCX, PPTX) including complex layouts
- Test with context files (TXT, MD) of varying sizes
- Colleagues can test by cloning repo and following SETUP_GUIDE
- Performance testing with larger documents (30+ images)

**Success Criteria:**
- Process DOCX and PPTX with all features enabled
- Context file measurably improves alt-text quality (user validation)
- Context hierarchy correctly prioritizes external > document > section > page > local
- Clear console output with progress bars and completion summary
- Generate markdown summary report with failed images listed
- Cost tracking shows accurate token usage per document
- Handle edge cases: no images, corrupted files, large files (>20MB)
- Complete Getting Started guide with Python/UV installation steps
- Test coverage maintained >80%
- Successfully runs on clean Windows machine following setup guide

**Implementation Tasks (TDD approach):**
1. Write tests for PPTX slide notes extraction → Enhance PPTX extractor
2. Write tests for context file parsing → Implement TXT/MD reader
3. Write tests for 4-level context hierarchy → Implement merging algorithm with deduplication
4. Write tests for markdown report generation → Implement report generator with failed images section
5. Write tests for cost tracking → Implement token usage logging
6. Write tests for dry-run mode → Implement preview without file modification
7. Write tests for backup creation → Implement safe backup logic
8. Write end-to-end tests with real documents
9. Create Getting Started guide (Python, UV, Git, clone, install, configure, run)
10. Create troubleshooting documentation (common errors, solutions)
11. Create sample documents repository (test fixtures)
12. Performance profiling and optimization

### 12.2 Phase 2: Web UI & Enhanced Features

#### 12.2.1: Streamlit Web Interface
**Deliverables:**
- Streamlit web application wrapping CLI functionality
- File upload widget for all supported formats
- Context file upload option
- Progress bar and status updates
- Image preview with generated alt-text
- Download annotated document
- View/download summary report

**Development Environment:**
- Local Streamlit app on `localhost:8501`
- Reuse all Phase 1 CLI logic as backend
- Test with multiple concurrent uploads

**Success Criteria:**
- User-friendly web interface
- All Phase 1 features accessible via UI
- Real-time progress updates
- Preview images with alt-text before download
- Clear error messages
- Responsive design for desktop/tablet

**Implementation Tasks:**
1. Create Streamlit app.py with file upload
2. Integrate CLI backend as library
3. Implement progress tracking in UI
4. Add image preview with alt-text display
5. Enable context file upload
6. Create download buttons for output and report
7. Add configuration panel in sidebar

#### 12.2.2: Batch Processing & Review Interface
**Deliverables:**
- Batch processing (multiple files at once)
- Interactive review mode (edit alt-text before applying)
- Regenerate individual descriptions
- Enhanced reports with thumbnails
- User guide for professors

**Success Criteria:**
- Upload and process 5+ documents simultaneously
- Review and edit alt-text before finalizing
- Batch download all processed files
- Comprehensive reports with statistics
- User satisfaction >4/5 from test users

**Implementation Tasks:**
1. Implement batch file processing
2. Create alt-text review/edit interface
3. Add regeneration capability per image
4. Build enhanced report with thumbnails
5. Add batch download (ZIP file)
6. Write user guide documentation
7. Add keyboard shortcuts for review workflow

### 12.3 Phase 3: Cloud Deployment & Scale

#### 12.3.1: Azure Deployment
**Deliverables:**
- Deploy Streamlit app to Azure App Service
- Environment configuration in Azure
- HTTPS-enabled public URL
- Basic authentication (password or Azure AD)
- File storage with auto-cleanup
- Application monitoring and logging

**Infrastructure:**
- Azure App Service (Basic B1 tier: ~$55/month)
- Azure OpenAI Service endpoint
- Azure Blob Storage for temporary files (optional)
- Azure Application Insights for monitoring
- Azure Key Vault for secrets

**Success Criteria:**
- Accessible via public URL
- 5-10 concurrent users supported
- Automatic file cleanup after 24 hours
- Secure credential management
- Monitor usage and errors

#### 12.3.2: Performance & Production Readiness
**Deliverables:**
- Performance optimization for large documents
- Long description generation for complex images
- Enhanced context-aware processing
- Admin dashboard (basic analytics)
- Production documentation

**Success Criteria:**
- Process documents with 50+ images efficiently
- Generate long descriptions for charts/diagrams
- Context improves alt-text quality measurably
- Basic usage analytics available
- 99% uptime during business hours

### 12.4 Phase 4: Enterprise Scale (Future)

**Deliverables:**
- Migrate to Azure Functions (serverless)
- Queue-based processing for large batches
- User accounts with processing history
- API endpoints for integrations
- Advanced analytics dashboard

**Infrastructure:**
- Azure Functions (Consumption or Premium plan)
- Azure Queue Storage for job management
- Azure SQL or CosmosDB for user data
- API Management for external integrations

**Success Criteria:**
- Support 20+ concurrent users
- Process 100+ documents in batch
- RESTful API for LMS integration
- Cost-per-document <$0.50
- Enterprise SLA (99.9% uptime)

### 12.5 Phase 5: Advanced Features (Future)
**Potential Features:**
- Learning Management System (LMS) integration (Canvas, Blackboard, Moodle)
- Custom prompt templates library for different subjects (STEM, humanities, etc.)
- Multi-language support for international documents
- Desktop application with offline capability
- Advanced analytics and reporting dashboard
- Bulk operations via CLI (process entire directories)
- Plugin system for custom processors
- OCR integration for text extraction from images
- Accessibility scoring and compliance checker

---

## 13. Risk Assessment

### 13.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| AI service unavailability | Medium | High | Implement retry logic, fallback to cached/default descriptions |
| Poor alt-text quality | Medium | High | Human review interface, iterative prompt engineering |
| Document format complexity | High | Medium | Extensive testing, graceful degradation for unsupported features |
| Large file processing timeout | Medium | Medium | Implement chunking, progress tracking, async processing |
| API rate limiting | Medium | Medium | Implement queuing, rate limit handling, caching |

### 13.2 Business Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Low user adoption | Medium | High | User training, simple interface, clear value proposition |
| Cost overruns (AI API) | Medium | Medium | Usage monitoring, cost caps, efficient prompting |
| Privacy concerns | Low | High | Clear data policy, temporary storage, FERPA compliance |

### 13.3 Compliance Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| ADA non-compliance | Low | High | Expert review, accessibility testing, validation tools |
| FERPA violations | Low | High | No permanent storage, encryption, access controls |

---

## 14. Dependencies and Prerequisites

### 14.1 External Dependencies
- Azure OpenAI Service account (or OpenAI API key)
- Python 3.11+ runtime environment (Windows 10/11)
- Git for version control
- UV package manager for fast dependency installation
- Azure subscription (for Phase 3 deployment)

### 14.2 Required Accounts/Licenses
- Azure OpenAI access (may require application/approval)
- GitHub account for source control
- **Phase 1:** No additional accounts needed (local execution)
- **Phase 3:** Azure account with appropriate credits

### 14.3 Development Environment & Compatibility Matrix

#### Supported Platforms (Phase 1)
| Component | Requirement | Notes |
|-----------|-------------|-------|
| **Operating System** | Windows 10/11 (64-bit) | Windows-only for Phase 1 |
| **Python Version** | 3.11, 3.12 | 3.13 not yet tested |
| **Document Formats** | DOCX (Office 2007+), PPTX (Office 2007+) | PDF and DOC deferred |
| **Image Formats** | JPEG, PNG, GIF, BMP | SVG not supported |
| **Text Encoding** | UTF-8 | Required for all text processing |
| **File Size Limits** | Max 50MB per document | Configurable via config.json |
| **Language Support** | English only | Multi-language deferred to Phase 4 |

#### Development Tools
| Tool | Version | Purpose |
|------|---------|---------|
| **Python** | 3.11+ | Core runtime |
| **UV** | Latest | Fast package manager (replaces pip) |
| **Git** | 2.40+ | Version control |
| **Visual Studio Code** | Latest | Recommended IDE |
| **Python Extension (VS Code)** | Latest | Language support, debugging |
| **Pylance** | Latest | Type checking and IntelliSense |

#### Python Package Dependencies (from pyproject.toml)
- **Core:** semantic-kernel, openai, pydantic, pydantic-settings
- **Document Processing:** python-docx, python-pptx, Pillow
- **CLI & Utilities:** structlog, python-dotenv, rich (progress bars)
- **Development:** pytest, pytest-cov, pytest-asyncio, black, ruff, mypy

### 14.4 Getting Started Guide (Detailed in README.md)

**Prerequisites:**
1. Windows 10 or 11 (64-bit)
2. Internet connection (for UV, dependencies, AI API)
3. Azure OpenAI API key or OpenAI API key

**Installation Steps:**
1. **Install Python 3.11+**
   - Download from [python.org](https://www.python.org/downloads/)
   - During installation: Check "Add Python to PATH"
   - Verify: `python --version` (should show 3.11+)

2. **Install UV Package Manager**
   ```powershell
   # PowerShell (Windows)
   irm https://astral.sh/uv/install.ps1 | iex
   ```
   - Verify: `uv --version`

3. **Install Git**
   - Download from [git-scm.com](https://git-scm.com/download/win)
   - Use default installation options
   - Verify: `git --version`

4. **Clone Repository**
   ```powershell
   git clone https://github.com/YOUR_ORG/picture_annotations.git
   cd picture_annotations
   ```

5. **Install Dependencies**
   ```powershell
   uv pip install -e .
   ```

6. **Configure Environment**
   - Copy `.env.example` to `.env`
   - Edit `.env` with your API key:
     ```
     AZURE_OPENAI_API_KEY=your_key_here
     AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
     AZURE_OPENAI_DEPLOYMENT=gpt-4o
     ```

7. **Verify Installation**
   ```powershell
   ada-annotator --help
   ```

8. **Run First Document**
   ```powershell
   ada-annotator sample_document.docx --verbose
   ```

**Troubleshooting:**
- **Python not found:** Ensure Python is in PATH, restart terminal
- **UV installation failed:** Use pip as fallback: `pip install -e .`
- **API key error:** Verify .env file location and format
- **Import errors:** Run `uv pip install -e .` to reinstall dependencies

**See SETUP_GUIDE.md for comprehensive installation documentation.**

---

## 15. Open Questions and Assumptions

### 15.1 Assumptions
1. Users have basic command-line skills (Windows PowerShell)
2. Documents are in standard Office Open XML formats (DOCX, PPTX)
3. Internet connectivity available for AI API calls
4. Azure OpenAI access will be approved (or OpenAI API as fallback)
5. Images are of sufficient quality for AI vision analysis
6. Users run on Windows 10/11 with Python 3.11+ installed
7. Documents contain UTF-8 compatible text (English)
8. Users have permission to modify documents (not read-only)
9. API costs acceptable for educational use ($0.01-0.10 per document estimated)
10. Users accept temporary local file storage during processing

### 15.2 Open Questions & Decisions

#### Resolved Decisions (per user feedback)
1. **Q:** Support legacy DOC files?
   - **Decision:** No, users convert to DOCX (DOC processing too complex)

2. **Q:** Include PDF support in Phase 1?
   - **Decision:** No, defer to Phase 2 (PDF alt-text injection complex)

3. **Q:** Multi-platform support (Mac, Linux)?
   - **Decision:** Windows-only for Phase 1 (simplifies testing)

4. **Q:** Should the system support editing of generated alt-text before applying to document?
   - **Decision:** Phase 2 feature (review interface in web UI)

5. **Q:** What model should be used?
   - **Decision:** GPT-4o recommended (vision + cost-effective), configurable

6. **Q:** Context hierarchy structure?
   - **Decision:** External file > Document > Section > Page > Local

7. **Q:** Configuration file format?
   - **Decision:** JSON for config, .env for secrets

8. **Q:** Logging architecture?
   - **Decision:** Local JSON files (Phase 1), Azure App Insights (Phase 3)

#### Open Questions (TBD)
1. **Q:** Should decorative images be automatically identified?
   - **Status:** TBD, may implement heuristics in Phase 2

2. **Q:** How long should processed documents be retained?
   - **Status:** Phase 1 = immediate deletion; Phase 3 = 24-hour retention

3. **Q:** Integration with Learning Management Systems?
   - **Status:** Phase 4+ (Canvas, Blackboard APIs)

---

## 16. Glossary

- **ADA:** Americans with Disabilities Act - federal civil rights law prohibiting discrimination
- **Alt-text:** Alternative text describing an image for accessibility
- **FERPA:** Family Educational Rights and Privacy Act - protects student record privacy
- **Long Description:** Extended description for complex images beyond alt-text
- **OCR:** Optical Character Recognition - extracting text from images
- **Semantic Kernel:** Microsoft's SDK for AI orchestration and plugin development
- **WCAG:** Web Content Accessibility Guidelines - international accessibility standards

---

## 17. References and Resources

### 17.1 Technical Documentation
- [Microsoft Semantic Kernel Python SDK](https://learn.microsoft.com/en-us/semantic-kernel/overview/)
- [Azure OpenAI Service](https://learn.microsoft.com/en-us/azure/cognitive-services/openai/)
- [python-docx Documentation](https://python-docx.readthedocs.io/)
- [python-pptx Documentation](https://python-pptx.readthedocs.io/)

### 17.2 Accessibility Standards
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [WebAIM Alt Text Guide](https://webaim.org/techniques/alttext/)
- [W3C Image Concepts](https://www.w3.org/WAI/tutorials/images/)

### 17.3 Deployment Resources
- [Azure Functions Python Developer Guide](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

## 18. Approval and Sign-off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Project Sponsor | TBD | | |
| Technical Lead | TBD | | |
| Accessibility Consultant | TBD | | |
| End User Representative | TBD | | |

---

## Document Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-18 | GitHub Copilot | Initial requirements document |
| 1.1 | 2025-10-18 | GitHub Copilot | **Major Phase 1 Restructure:**<br>- Changed Phase 1 from Streamlit UI to CLI-only<br>- Added all document formats (DOCX, DOC, PDF, PPTX) to Phase 1<br>- Added context file support as core feature<br>- Moved web UI to Phase 2<br>- Moved batch processing to Phase 2<br>- Elevated context analysis to High priority<br>- Reorganized phases with clearer focus |
| 2.0 | 2025-10-18 | GitHub Copilot | **Comprehensive Requirements Refinement (20 improvements):**<br>1. CLI args specification with exit codes<br>2. Windows-only, DOCX/PPTX focus, removed DOC support<br>3. PDF deferred to Phase 2<br>4. 4-level context hierarchy (external>document>section>page>local)<br>5. Image position preservation requirements<br>6. Failed images tracking with page numbers<br>7. Semantic Kernel prompt template with validation rules<br>8. Performance metrics deferred to Phase 2+<br>9. Added Pydantic data models (Section 6.3)<br>10. Security implementation (Phase 3) with Phase 1 basics<br>11. AI availability check with exit code 4<br>12. Alt-text validation rules and quality gates<br>13. TDD approach with detailed test specifications<br>14. Detailed Getting Started in README (Python, UV, Git, setup)<br>15. Logging architecture (JSON local → Azure App Insights)<br>16. Config management spec (JSON + .env, .gitignore)<br>17. UTF-8 requirement, English-only<br>18. Cost management and monitoring requirements<br>19. Compatibility matrix (Windows, Python, formats)<br>20. Expanded SETUP_GUIDE with troubleshooting |
| 2.1 | 2025-10-18 | GitHub Copilot | **Removed Time Estimates:**<br>- Removed all schedule references (Week 1-2, Week 3-4, etc.)<br>- Changed section headers to focus on requirements only<br>- Maintained phase structure without time commitments<br>- Document now focuses purely on requirements without project timeline |

---

**End of Requirements Document**
