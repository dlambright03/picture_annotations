<!-- markdownlint-disable-file -->
# Task Research Notes: Debug Mode Feature

## Research Executed

### File Analysis
- `src/ada_annotator/cli.py`
  - Current CLI structure with argparse
  - Existing flags: `--verbose`, `--dry-run`, `--backup`, `--max-images`
  - Document processing pipeline: extract → generate → apply → save
  - Output path generation with `_annotated` suffix
- `src/ada_annotator/document_processors/docx_extractor.py`
  - Extracts images with metadata including `image_data` bytes
  - Uses python-docx library for document manipulation
  - Returns `ImageMetadata` objects with binary image data
- `src/ada_annotator/document_processors/docx_assembler.py`
  - Uses python-docx to create/modify documents
  - XML manipulation for alt-text application
  - Demonstrates document creation capability
- `src/ada_annotator/models/image_metadata.py`
  - Contains `image_data` field (bytes) for in-memory image storage
  - Marked with `exclude=True` to prevent JSON serialization

### Code Search Results
- `from docx import Document`
  - Used in extractor and assembler classes
  - Standard library for DOCX manipulation
- `python-docx>=1.1.0`
  - Already in project dependencies (pyproject.toml)
  - Supports creating documents, adding paragraphs, adding images

### External Research
- #fetch:https://learn.microsoft.com/en-us/office/open-xml/word/how-to-insert-a-picture-into-a-word-processing-document
  - Microsoft documentation on inserting pictures in Word documents
  - Shows XML structure and OpenXML SDK approach
  - Confirms feasibility of programmatic image insertion

### Project Conventions
- Standards referenced: `.github/instructions/python.instructions.md`
  - PEP 8 style guide compliance
  - Type hints for all functions
  - Comprehensive docstrings (PEP 257)
  - 4-space indentation, 79-character line limit
- Existing CLI patterns:
  - Uses argparse for argument parsing
  - Boolean flags with `action="store_true"`
  - Output path generation based on input path
  - Progress indicators with print statements

## Key Discoveries

### Project Structure
The project follows a modular architecture:
- **CLI Layer**: `src/ada_annotator/cli.py` - Entry point with argument parsing
- **Processor Layer**: `src/ada_annotator/document_processors/` - Extraction and assembly
- **Model Layer**: `src/ada_annotator/models/` - Data structures
- **Generator Layer**: `src/ada_annotator/generators/` - AI-powered alt-text generation

### Implementation Patterns

**Existing Document Processing Pipeline:**
```python
# 1. Extract images
extractor = DOCXExtractor(input_path)
images = extractor.extract_images()  # Returns ImageMetadata with image_data

# 2. Generate alt-text
generator = AltTextGenerator(settings, ai_service, context_extractor)
alt_text_results = await generator.generate_for_multiple_images(images)

# 3. Apply alt-text to document
assembler = DOCXAssembler(input_path, output_path)
status_map = assembler.apply_alt_text(alt_text_results)
assembler.save_document()
```

**python-docx Document Creation Pattern:**
```python
from docx import Document
from docx.shared import Inches
from io import BytesIO

# Create new document
doc = Document()

# Add heading
doc.add_heading('Debug Output', level=1)

# Add image from bytes
image_stream = BytesIO(image_bytes)
doc.add_picture(image_stream, width=Inches(4.0))

# Add text paragraph
doc.add_paragraph('Alt-text: Description here')

# Save document
doc.save(output_path)
```

### Complete Examples

**Creating Debug Document with Images and Text:**
```python
from docx import Document
from docx.shared import Inches
from io import BytesIO
from pathlib import Path

def create_debug_document(
    images: list[ImageMetadata],
    alt_text_results: list[AltTextResult],
    output_path: Path
) -> None:
    """
    Create debug document with images and their alt-text.

    Args:
        images: List of extracted image metadata.
        alt_text_results: List of generated alt-text results.
        output_path: Path where debug document will be saved.
    """
    doc = Document()
    doc.add_heading('Alt-Text Debug Output', level=1)

    # Create lookup for alt-text by image_id
    alt_text_map = {r.image_id: r for r in alt_text_results}

    for img in images:
        # Add image heading
        doc.add_heading(f'Image: {img.image_id}', level=2)

        # Add the actual image
        if img.image_data:
            image_stream = BytesIO(img.image_data)
            doc.add_picture(image_stream, width=Inches(4.0))

        # Add metadata
        doc.add_paragraph(f'Filename: {img.filename}')
        doc.add_paragraph(f'Format: {img.format}')
        doc.add_paragraph(f'Size: {img.width_pixels}x{img.height_pixels}px')

        # Add generated alt-text
        if img.image_id in alt_text_map:
            result = alt_text_map[img.image_id]
            doc.add_paragraph(f'Alt-Text: {result.alt_text}')
            doc.add_paragraph(f'Confidence: {result.confidence_score:.2f}')
        else:
            doc.add_paragraph('Alt-Text: [Generation failed]')

        # Add spacing
        doc.add_paragraph()

    doc.save(str(output_path))
```

### API and Schema Documentation

**ImageMetadata Model:**
- `image_id`: Unique identifier (e.g., "img-0-1")
- `image_data`: Binary image bytes (optional, used for in-memory processing)
- `filename`, `format`, `size_bytes`, `width_pixels`, `height_pixels`
- `existing_alt_text`: Pre-existing alt-text if present

**AltTextResult Model:**
- `image_id`: Matches ImageMetadata.image_id
- `alt_text`: Generated description (1-350 chars)
- `confidence_score`: AI confidence (0.0-1.0)
- `validation_passed`: Boolean
- `tokens_used`, `processing_time_seconds`

### Configuration Examples

**CLI Argument Addition:**
```python
parser.add_argument(
    "--debug",
    action="store_true",
    help="Generate debug document with images and annotations instead of applying alt-text"
)
```

**Output Path Generation for Debug Mode:**
```python
def generate_debug_output_path(input_path: Path) -> Path:
    """Generate output path for debug document."""
    return input_path.with_stem(f"{input_path.stem}_debug")
```

### Technical Requirements

**Dependencies:**
- ✅ `python-docx>=1.1.0` - Already installed
- ✅ `Pillow>=10.1.0` - Already installed for image processing
- ✅ No additional dependencies required

**Compatibility:**
- Works with DOCX and PPTX formats (both extractors return ImageMetadata)
- `image_data` field already available in ImageMetadata model
- python-docx supports adding images from BytesIO streams

**Implementation Considerations:**
1. Must extract images with `image_data` populated
2. Alt-text generation proceeds normally
3. Instead of applying to original document, create new debug document
4. Debug document shows each image with its metadata and generated alt-text
5. Debug output path uses `_debug` suffix instead of `_annotated`

## Recommended Approach

**Create a debug mode that outputs a separate document displaying each image alongside its generated alt-text for verification purposes.**

### Implementation Strategy

1. **Add `--debug` CLI Flag**
   - Boolean flag in argparse configuration
   - Mutually compatible with other flags
   - Changes output document format, not processing pipeline

2. **Create Debug Document Generator Module**
   - New function: `create_debug_document()`
   - Located in `src/ada_annotator/utils/` or as method in CLI
   - Takes images and alt-text results as input
   - Generates formatted DOCX with images and annotations

3. **Modify CLI Processing Logic**
   - Keep extraction and generation steps unchanged
   - Branch on `--debug` flag after alt-text generation
   - If debug: create debug document
   - If not debug: apply alt-text normally

4. **Debug Document Format**
   - Title: "Alt-Text Debug Output"
   - For each image:
     - Heading with image ID
     - Actual image (4-inch width)
     - Metadata (filename, format, dimensions)
     - Generated alt-text
     - Confidence score
     - Spacing between images

### Benefits of This Approach
- ✅ **Non-invasive**: Doesn't modify existing processing pipeline
- ✅ **Simple implementation**: Uses existing python-docx functionality
- ✅ **Useful for debugging**: Visual verification of alt-text quality
- ✅ **Works with both formats**: DOCX and PPTX extraction both supported
- ✅ **No new dependencies**: Uses libraries already in project

### Alternative Approaches Considered

**Alternative 1: Inline Debug Annotations**
- Apply alt-text AND add visible text captions in original document
- ❌ **Rejected**: Modifies original document structure, not truly "debug only"

**Alternative 2: JSON Output Format**
- Output images and alt-text as JSON with base64-encoded images
- ❌ **Rejected**: Less user-friendly, requires separate viewer

**Alternative 3: HTML Output**
- Generate HTML page with embedded images and alt-text
- ❌ **Rejected**: Adds complexity, doesn't match project's DOCX/PPTX focus

## Implementation Guidance

### Objectives
1. Add `--debug` CLI argument flag
2. Create debug document generator utility function
3. Modify CLI to branch on debug flag after alt-text generation
4. Generate formatted DOCX showing images with their alt-text
5. Use `_debug` suffix for output filename

### Key Tasks
1. **Update CLI Argument Parser** (`src/ada_annotator/cli.py`)
   - Add `--debug` flag to argparse
   - Update help text and usage examples

2. **Create Debug Document Generator** (new or in utils)
   - Function to create debug DOCX from images and results
   - Format: heading, image, metadata, alt-text per image

3. **Modify Processing Logic** (`src/ada_annotator/cli.py`)
   - After alt-text generation completes
   - Check if `--debug` flag is set
   - Branch to debug document creation instead of normal assembly

4. **Update Output Path Logic**
   - Generate `_debug` suffix path when in debug mode
   - Keep `_annotated` suffix for normal mode

5. **Test Implementation**
   - Test with DOCX input
   - Test with PPTX input
   - Verify image display quality
   - Verify alt-text display accuracy

### Dependencies
- No additional dependencies required
- Uses existing `python-docx` and `Pillow` libraries

### Success Criteria
- ✅ `--debug` flag accepted by CLI
- ✅ Debug document created with correct filename
- ✅ All extracted images appear in debug document
- ✅ Generated alt-text displayed next to each image
- ✅ Metadata (dimensions, confidence) shown correctly
- ✅ Works for both DOCX and PPTX inputs
- ✅ No interference with normal processing mode
