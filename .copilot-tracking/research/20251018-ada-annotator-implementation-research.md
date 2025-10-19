<!-- markdownlint-disable-file -->
# Task Research Notes: ADA Annotator CLI Implementation (Phase 1)

## Research Executed

### File Analysis
- **pyproject.toml**
  - Dependencies already configured: semantic-kernel, python-docx, python-pptx, Pillow, pydantic, structlog
  - UV package manager configured as build system
  - Test framework (pytest) with coverage configured
  - Code quality tools: black, ruff, mypy
- **.env.example**
  - Comprehensive environment variable structure for Azure OpenAI and OpenAI
  - Application settings for logging, file limits, AI parameters
- **src/ada_annotator/config.py**
  - Pydantic Settings class with full validation
  - Environment variable loading with proper precedence
  - AI service configuration validation method
- **src/ada_annotator/cli.py**
  - Placeholder CLI entry point (not implemented)
- **src/ada_annotator/app.py**
  - Streamlit UI skeleton (placeholder)
- **.github/instructions/python.instructions.md**
  - PEP 8 compliance required, type hints, docstrings mandatory
  - Edge case handling and testing requirements
  - 79 character line limit, 4-space indentation

### Code Search Results
- **semantic-kernel integration patterns**
  - Chat completion with image analysis well-documented
  - Multi-modal chat with ImageContent and TextContent classes
  - Plugin architecture with kernel_function decorator
- **python-docx usage**
  - No existing implementation found in workspace
  - Need to research extraction with position metadata preservation
- **Context analysis patterns**
  - No existing implementation in workspace
  - Requirements specify 4-level hierarchy (external, document, section, page, local)

### External Research

#### #githubRepo:"microsoft/semantic-kernel vision image analysis python"
- **Multi-Modal Chat Completion Pattern**:
  ```python
  from semantic_kernel.contents import ChatHistory, ChatMessageContent, ImageContent, TextContent
  
  chat_history = ChatHistory("Your job is describing images.")
  chat_history.add_message(
      ChatMessageContent(
          role="user",
          items=[
              TextContent("What's in this image?"),
              ImageContent(uri=uri),  # OR
              ImageContent.from_image_file(path="path/to/image.jpg"),
          ]
      )
  )
  response = await chat_completion_service.get_chat_message_content(chat_history)
  ```

- **Semantic Kernel Setup Pattern**:
  ```python
  from semantic_kernel import Kernel
  from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
  
  kernel = Kernel()
  chat_completion = AzureChatCompletion(
      deployment_name="your_models_deployment_name",
      api_key="your_api_key",
      base_url="your_base_url",
  )
  kernel.add_service(chat_completion)
  ```

#### #fetch:https://learn.microsoft.com/en-us/azure/ai-services/computer-vision/how-to/call-analyze-image-40
- **Azure OpenAI GPT-4o Vision API** (Alternative to Semantic Kernel):
  ```python
  from openai import AzureOpenAI
  
  client = AzureOpenAI(
      api_key=api_key,
      api_version="2023-12-01-preview",
      base_url=f"{api_base}/openai/deployments/{deployment_name}"
  )
  
  response = client.chat.completions.create(
      model=deployment_name,
      messages=[
          {"role": "system", "content": "You are a helpful assistant."},
          {"role": "user", "content": [
              {"type": "text", "text": "Describe this picture:"},
              {"type": "image_url", "image_url": {"url": "<image URL>"}}
          ]}
      ],
      max_tokens=2000
  )
  ```

- **Image Input Methods**:
  - **URL**: `{"type": "image_url", "image_url": {"url": "https://..."}}`
  - **Base64**: `{"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,{image_data}"}}`
  - **Local File**: Read file, encode to base64, use data URI

#### #fetch:https://python-docx.readthedocs.io/
- **DOCX Image Extraction** (from documentation research):
  - No native position metadata API in python-docx
  - Images accessed via `document.inline_shapes` and `paragraph._element.xpath()`
  - Position tracking requires XML parsing of underlying Office Open XML
  - Image metadata: `inline_shape.width`, `inline_shape.height`, `inline_shape.type`
  - Image binary data: `inline_shape.blob` or `inline_shape.part.blob`

#### #fetch:https://python-pptx.readthedocs.io/
- **PPTX Image Extraction Patterns**:
  ```python
  from pptx import Presentation
  
  prs = Presentation("presentation.pptx")
  for slide_num, slide in enumerate(prs.slides, start=1):
      for shape in slide.shapes:
          if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
              image = shape.image
              image_bytes = image.blob
              # Position: shape.left, shape.top, shape.width, shape.height
              print(f"Slide {slide_num}: Image at ({shape.left}, {shape.top})")
  ```

### Project Conventions Referenced
- **PEP 8 Compliance**: 79-character lines, 4-space indentation, descriptive names
- **Type Hints**: All function signatures must include types
- **Docstrings**: PEP 257 format with Parameters/Returns sections
- **Error Handling**: Clear exception messages, edge case coverage
- **Testing**: pytest with >80% coverage, unit tests for all modules

## Key Discoveries

### Project Structure Analysis
- **Existing Configuration**: Fully configured pyproject.toml with all dependencies
- **Environment Management**: Robust Settings class with pydantic validation
- **Placeholder Code**: CLI and Streamlit UI are skeletons only
- **Missing Implementation**: All core processing logic needs to be built
- **Test Infrastructure**: pytest configured but no tests exist yet

### Semantic Kernel Multi-Modal Implementation Patterns

**Pattern 1: Semantic Kernel with Vision (Recommended for Requirements)**
```python
# Advantages: Plugin architecture, abstraction, multi-service support
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatHistory, ChatMessageContent, ImageContent, TextContent
from semantic_kernel.connectors.ai import FunctionChoiceBehavior

# Setup kernel
kernel = Kernel()
chat_service = AzureChatCompletion(
    deployment_name=settings.azure_openai_deployment_name,
    api_key=settings.azure_openai_api_key,
    base_url=settings.azure_openai_endpoint,
)
kernel.add_service(chat_service)

# Configure execution settings
execution_settings = AzureChatPromptExecutionSettings()
execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()
execution_settings.temperature = settings.ai_temperature
execution_settings.max_tokens = settings.ai_max_tokens

# Create chat history with image analysis
chat_history = ChatHistory("You are an accessibility expert creating alt-text for educational documents.")
chat_history.add_message(
    ChatMessageContent(
        role="user",
        items=[
            TextContent(f"Context: {context_data.get_merged_context()}"),
            TextContent("Generate concise alt-text (100-150 chars, max 250)"),
            ImageContent.from_image_file(path=str(image_path)),
        ]
    )
)

# Get AI response
result = await chat_service.get_chat_message_content(
    chat_history=chat_history,
    settings=execution_settings,
    kernel=kernel,
)
alt_text = str(result)
```

**Pattern 2: Direct Azure OpenAI Client (Simpler Alternative)**
```python
# Advantages: Simpler, fewer dependencies, direct control
from openai import AzureOpenAI
import base64

client = AzureOpenAI(
    api_key=settings.azure_openai_api_key,
    api_version="2024-02-15-preview",
    base_url=f"{settings.azure_openai_endpoint}/openai/deployments/{settings.azure_openai_deployment_name}"
)

# Encode image to base64
with open(image_path, "rb") as f:
    image_data = base64.b64encode(f.read()).decode("utf-8")

# API call
response = client.chat.completions.create(
    model=settings.azure_openai_deployment_name,
    messages=[
        {"role": "system", "content": "You are an accessibility expert..."},
        {"role": "user", "content": [
            {"type": "text", "text": f"Context: {context_data.get_merged_context()}"},
            {"type": "text", "text": "Generate alt-text..."},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
        ]}
    ],
    max_tokens=settings.ai_max_tokens,
    temperature=settings.ai_temperature,
)
alt_text = response.choices[0].message.content
```

**Decision**: Use **Pattern 1 (Semantic Kernel)** per requirements specification (TR-4.1.2)

### DOCX Image Extraction with Position Metadata

**Challenge**: python-docx does not natively provide image position metadata

**Solution Approach** (discovered through documentation analysis):
```python
from docx import Document
from docx.oxml.ns import qn
from docx.shared import Inches

def extract_images_with_position(docx_path: Path) -> List[ImageMetadata]:
    """Extract images with position metadata from DOCX."""
    doc = Document(docx_path)
    images = []
    
    # Method 1: Inline shapes (images in text flow)
    for para_idx, paragraph in enumerate(doc.paragraphs):
        for run in paragraph.runs:
            # Check for inline images
            inline_shapes = run._element.xpath('.//a:blip')
            for blip in inline_shapes:
                # Extract image relationship ID
                rId = blip.get(qn('r:embed'))
                image_part = doc.part.related_parts[rId]
                
                # Get image binary
                image_bytes = image_part.blob
                
                # Position metadata (approximate)
                position = {
                    "paragraph_index": para_idx,
                    "type": "inline",
                    "x": 0,  # Inline images flow with text
                    "y": 0,
                }
                
                images.append(ImageMetadata(
                    image_id=f"img_{para_idx}_{len(images)}",
                    filename=f"image_{len(images)}.{image_part.content_type.split('/')[-1]}",
                    format=image_part.content_type.split('/')[-1].upper(),
                    size_bytes=len(image_bytes),
                    position=position,
                    page_number=None,  # DOCX doesn't have page concept
                ))
    
    # Method 2: Drawing shapes (floating images)
    for shape in doc.inline_shapes:
        if shape.type == 3:  # PICTURE type
            # Extract position from shape properties
            # Note: Requires deeper XML parsing for exact position
            pass
    
    return images
```

**Limitation Discovered**: DOCX format does not store absolute page positions. Images are positioned relative to paragraphs/sections. Requirements specify maintaining "exact position" - this is achievable for recreation but not for absolute x/y coordinates.

### PPTX Image Extraction with Slide Context

**Complete Example** (from python-pptx docs):
```python
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pathlib import Path
from io import BytesIO
from PIL import Image

def extract_pptx_images(pptx_path: Path) -> List[ImageMetadata]:
    """Extract images from PowerPoint with slide context."""
    prs = Presentation(pptx_path)
    images = []
    
    for slide_num, slide in enumerate(prs.slides, start=1):
        # Get slide title for context
        slide_title = ""
        for shape in slide.shapes:
            if shape.has_text_frame and shape.text_frame.text:
                slide_title = shape.text_frame.text
                break
        
        # Extract images
        for shape_idx, shape in enumerate(slide.shapes):
            if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                image = shape.image
                image_bytes = image.blob
                
                # Load with Pillow to get dimensions
                img = Image.open(BytesIO(image_bytes))
                
                # Position metadata (in EMUs - English Metric Units)
                position = {
                    "x": shape.left,
                    "y": shape.top,
                    "width": shape.width,
                    "height": shape.height,
                    "anchor_type": "floating",
                    "slide_title": slide_title,
                }
                
                images.append(ImageMetadata(
                    image_id=f"slide{slide_num}_img{shape_idx}",
                    filename=f"slide{slide_num}_image{shape_idx}.{image.ext}",
                    format=image.content_type.split('/')[-1].upper(),
                    size_bytes=len(image_bytes),
                    width_pixels=img.width,
                    height_pixels=img.height,
                    page_number=slide_num,
                    position=position,
                ))
    
    return images
```

### Context Extraction Strategies

**4-Level Hierarchy Implementation Approach**:

```python
class ContextExtractor:
    """Extract multi-level context for images."""
    
    def extract_docx_context(self, doc: Document, image_id: str) -> ContextData:
        """Extract 4-level context from DOCX."""
        # Level 1: External context (from --context file)
        external_context = self._load_external_context() if self.context_file else None
        
        # Level 2: Document-level context
        document_context = f"{doc.core_properties.title} - {doc.core_properties.subject}"
        
        # Level 3: Section context (find nearest heading)
        section_context = self._find_nearest_heading(doc, image_id)
        
        # Level 4: Page/slide context (not applicable for DOCX)
        page_context = None
        
        # Level 5: Local context (surrounding paragraphs)
        local_context = self._extract_surrounding_text(doc, image_id, paragraphs_before=2, paragraphs_after=2)
        
        return ContextData(
            external_context=external_context,
            document_context=document_context,
            section_context=section_context,
            page_context=page_context,
            local_context=local_context,
        )
    
    def _find_nearest_heading(self, doc: Document, image_id: str) -> str:
        """Find nearest heading above image."""
        # Iterate backwards from image paragraph
        # Find first paragraph with style "Heading 1", "Heading 2", etc.
        pass
    
    def _extract_surrounding_text(self, doc: Document, image_id: str, paragraphs_before: int, paragraphs_after: int) -> str:
        """Extract N paragraphs before/after image."""
        # Find image paragraph index
        # Extract text from [index-N : index+N+1]
        # Concatenate with " | " separator
        pass
```

### Alt-Text Validation Implementation

**Validation Rules from Requirements**:
```python
class AltTextValidator:
    """Validate alt-text against ADA compliance rules."""
    
    FORBIDDEN_PHRASES = ["image of", "picture of", "graphic showing"]
    MIN_LENGTH = 10
    MAX_LENGTH = 250
    PREFERRED_LENGTH = 150
    
    def validate(self, alt_text: str) -> tuple[bool, list[str]]:
        """
        Validate alt-text and return (passed, warnings).
        
        Returns:
            tuple: (validation_passed, list_of_warnings)
        """
        warnings = []
        
        # Length checks
        if len(alt_text) < self.MIN_LENGTH:
            raise ValueError(f"Alt-text too short: {len(alt_text)} < {self.MIN_LENGTH}")
        if len(alt_text) > self.MAX_LENGTH:
            raise ValueError(f"Alt-text too long: {len(alt_text)} > {self.MAX_LENGTH}")
        if len(alt_text) < 50:
            warnings.append(f"Alt-text short: {len(alt_text)} chars (preferred: {self.PREFERRED_LENGTH})")
        if len(alt_text) > 200:
            warnings.append(f"Alt-text long: {len(alt_text)} chars (preferred: {self.PREFERRED_LENGTH})")
        
        # Content checks
        for phrase in self.FORBIDDEN_PHRASES:
            if phrase in alt_text.lower():
                raise ValueError(f"Forbidden phrase detected: '{phrase}'")
        
        # Formatting checks
        if not alt_text[0].isupper():
            raise ValueError("Alt-text must start with capital letter")
        
        # Auto-correct missing period
        if not alt_text.endswith('.'):
            alt_text += '.'
            warnings.append("Added missing period")
        
        return (True, warnings)
```

### API and Schema Documentation

**Pydantic Models** (from requirements Section 6.3):
```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Literal
from datetime import datetime
from pathlib import Path

class ImageMetadata(BaseModel):
    """Metadata for extracted image."""
    image_id: str
    filename: str
    format: Literal["JPEG", "PNG", "GIF", "BMP"]
    size_bytes: int
    width_pixels: int
    height_pixels: int
    page_number: Optional[int] = None
    position: dict
    existing_alt_text: Optional[str] = None

class ContextData(BaseModel):
    """Hierarchical context for image."""
    external_context: Optional[str] = None
    document_context: str
    section_context: Optional[str] = None
    page_context: Optional[str] = None
    local_context: str
    
    def get_merged_context(self, max_tokens: int = 3000) -> str:
        """Merge contexts with truncation."""
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
        if len(merged) > max_tokens * 4:
            merged = merged[:max_tokens * 4] + "..."
        return merged

class AltTextResult(BaseModel):
    """Generated alt-text with validation."""
    image_id: str
    alt_text: str
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    validation_passed: bool
    validation_warnings: List[str] = Field(default_factory=list)
    tokens_used: int
    processing_time_seconds: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class DocumentProcessingResult(BaseModel):
    """Complete processing result."""
    input_file: Path
    output_file: Path
    document_type: Literal["DOCX", "PPTX"]
    total_images: int
    successful_images: int
    failed_images: int
    images_processed: List[AltTextResult]
    errors: List[dict]
    total_tokens_used: int
    estimated_cost_usd: float
    processing_duration_seconds: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

### Configuration Management

**Existing Config Class** (from config.py analysis):
- Already implements pydantic Settings with full validation
- Loads from .env file automatically
- Validates AI service configuration
- Temperature, max_tokens, timeouts configured
- Path validation with auto-creation

**Additional Required Settings**:
```python
# Add to Settings class
context_paragraphs_before: int = Field(default=2, ge=0, le=10)
context_paragraphs_after: int = Field(default=2, ge=0, le=10)
dry_run: bool = False
create_backup: bool = False
log_file: Path = Field(default=Path("ada_annotator.log"))
```

### Logging Architecture

**Structured Logging Pattern** (using structlog):
```python
import structlog
from structlog.processors import JSONRenderer
from pathlib import Path

def setup_logging(log_file: Path, log_level: str) -> None:
    """Configure structured JSON logging."""
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure file handler
    handler = logging.FileHandler(log_file)
    handler.setFormatter(logging.Formatter("%(message)s"))
    
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, log_level.upper()))

# Usage
logger = structlog.get_logger()
logger.info("processing_document", document_name="example.docx", image_count=5, correlation_id="uuid-123")
```

## Recommended Approach

### Recommended Implementation Strategy

**Choice: Semantic Kernel with Multi-Modal Chat Completion**

**Rationale**:
1. **Requirements Compliance**: TR-4.1.2 explicitly specifies Semantic Kernel
2. **Plugin Architecture**: Extensible for future features (Phase 2+)
3. **Multi-Service Support**: Easy to swap Azure OpenAI  OpenAI
4. **Abstraction Layer**: Cleaner separation of concerns
5. **Microsoft Ecosystem**: Better integration with Azure services

**Trade-offs Considered**:
- **Complexity**: Semantic Kernel adds abstraction overhead vs. direct OpenAI client
- **Verdict**: Complexity justified by extensibility and requirements compliance

### Implementation Phases

**Phase 1.1: Core Infrastructure (Week 1)**
1. CLI argument parser with argparse
2. Structured logging setup (structlog + JSON)
3. Configuration loading validation
4. Error handling framework with exit codes
5. Pydantic data models (ImageMetadata, ContextData, etc.)

**Phase 1.2: Document Processing (Week 2)**
6. DOCX image extractor with position tracking
7. PPTX image extractor with slide context
8. Context extraction (4-level hierarchy)
9. External context file loader (TXT/MD)

**Phase 1.3: AI Integration (Week 3)**
10. Semantic Kernel initialization
11. Azure OpenAI service configuration
12. Multi-modal chat completion with image analysis
13. Alt-text validation and quality gates
14. Token usage tracking and cost calculation

**Phase 1.4: Output Generation (Week 4)**
15. DOCX assembler with position preservation
16. PPTX assembler with slide integrity
17. Markdown report generator
18. Failed images tracking and reporting

**Phase 1.5: Testing & Documentation (Week 5)**
19. Unit tests for all modules (>80% coverage)
20. Integration tests with sample documents
21. Update README with usage examples
22. Complete SETUP_GUIDE with troubleshooting

## Implementation Guidance

### Objectives
1. Build Phase 1 CLI application per requirements Section 12.1.0
2. Implement TDD approach: write tests first, then implementation
3. Achieve >80% test coverage for all core modules
4. Handle all specified edge cases and error scenarios
5. Maintain code quality (PEP 8, type hints, docstrings)

### Key Tasks
1. **CLI Implementation**: argparse with all specified arguments and exit codes
2. **Document Processors**: python-docx and python-pptx with position metadata
3. **Context Extraction**: 4-level hierarchy with merging algorithm
4. **AI Service Integration**: Semantic Kernel with Azure OpenAI vision
5. **Alt-Text Validation**: Quality gates per requirements Section 7.2
6. **Output Generation**: Preserve image positions, generate reports
7. **Error Handling**: Graceful failures, clear messages, logging
8. **Testing**: pytest with fixtures for sample documents

### Dependencies
- **Python Libraries**: All specified in pyproject.toml (already installed)
- **Azure OpenAI**: API key and endpoint from .env file
- **Sample Documents**: Create test fixtures (DOCX, PPTX with various images)
- **Test Images**: Various types (photo, chart, diagram, screenshot)

### Success Criteria
1.  CLI accepts all specified arguments and flags
2.  Extracts images from DOCX and PPTX with metadata
3.  Extracts 4-level context hierarchy correctly
4.  Generates alt-text using Semantic Kernel + Azure OpenAI
5.  Validates alt-text per quality gates
6.  Preserves image positions in output documents
7.  Tracks failed images with page numbers and reasons
8.  Generates markdown summary report
9.  Handles all edge cases (no images, corrupted files, API errors)
10.  Test coverage >80% for core modules
11.  All tests pass (unit + integration)
12.  Documentation complete (README, SETUP_GUIDE)

### Implementation Notes
- **DOCX Position Preservation**: Use XML manipulation to maintain image anchors
- **PPTX Position Preservation**: Direct shape manipulation with python-pptx
- **Context Merging**: Implement smart truncation to fit token limits
- **AI Service Availability**: Check at startup before processing
- **Token Tracking**: Count tokens for cost estimation (rough: chars/4)
- **Error Recovery**: Continue processing remaining images after failure
- **Logging**: Structured JSON with correlation IDs for tracing

### Critical Decisions Made
1.  **Use Semantic Kernel** (not direct OpenAI client)
2.  **Phase 1 = CLI only** (Streamlit UI deferred to Phase 2)
3.  **DOCX + PPTX only** (PDF deferred to Phase 2)
4.  **Position preservation** (critical requirement, requires XML/shape manipulation)
5.  **4-level context hierarchy** (external > document > section > page > local)
6.  **Structured JSON logging** (for future Azure App Insights migration)
7.  **TDD approach** (write tests first, then implementation)

## Technical Challenges Identified

1. **DOCX Position Preservation**: python-docx doesn't expose native position API
   - **Solution**: XML parsing of underlying Office Open XML structure
   - **Complexity**: High - requires understanding OOXML spec
   
2. **Context Truncation**: Merged context may exceed token limits
   - **Solution**: Smart truncation with priority (external > local > section > page)
   - **Complexity**: Medium - implement character-based truncation with ellipsis

3. **Image Format Handling**: Multiple formats (JPEG, PNG, GIF, BMP)
   - **Solution**: Pillow for format detection and conversion
   - **Complexity**: Low - Pillow handles this well

4. **AI Service Timeout**: Long-running API calls
   - **Solution**: Implement timeout (30s default) with retry logic
   - **Complexity**: Medium - exponential backoff for rate limits

5. **Failed Image Tracking**: Maintain processing state across failures
   - **Solution**: Collect errors in list, continue processing, report at end
   - **Complexity**: Low - straightforward error collection

## Next Steps

1. **Validate Approach**: Confirm with user that Semantic Kernel is preferred approach
2. **Create Test Fixtures**: Generate sample DOCX/PPTX with various image types
3. **Write Test Suite**: Start with test_cli.py, test_config.py, test_docx_extractor.py
4. **Implement CLI**: argparse with all arguments and exit codes
5. **Implement Document Extractors**: DOCX and PPTX with position metadata
6. **Implement Context Extraction**: 4-level hierarchy with merging
7. **Implement AI Service**: Semantic Kernel with Azure OpenAI
8. **Implement Validation**: Alt-text quality gates
9. **Implement Output Generation**: DOCX/PPTX with position preservation
10. **Integration Testing**: End-to-end tests with real documents
11. **Documentation**: Update README and SETUP_GUIDE

