<!-- markdownlint-disable-file -->
# Task Details: Debug Mode Feature Implementation

## Research Reference

**Source Research**: #file:../research/20251030-debug-mode-feature-research.md

## Phase 1: CLI Argument Addition

### Task 1.1: Add `--debug` flag to argument parser

Add a new CLI argument flag to enable debug output mode.

- **Files**:
  - `src/ada_annotator/cli.py` - Add `--debug` argument in `create_argument_parser()` function
- **Success**:
  - `--debug` flag accepted by CLI
  - Help text displays correctly with `--help`
  - Flag accessible in parsed args
- **Research References**:
  - #file:../research/20251030-debug-mode-feature-research.md (Lines 125-132) - CLI argument pattern
- **Dependencies**:
  - None

**Implementation Details:**
Add the following argument after the existing `--dry-run` argument:

```python
parser.add_argument(
    "--debug",
    action="store_true",
    help="Generate debug document with images and annotations instead of applying alt-text",
)
```

### Task 1.2: Update output path generation for debug mode

Create a helper function to generate debug-specific output paths with `_debug` suffix.

- **Files**:
  - `src/ada_annotator/cli.py` - Add `generate_debug_output_path()` function after `generate_output_path()`
- **Success**:
  - Function returns Path with `_debug` suffix
  - Maintains file extension from input
  - Follows existing code patterns
- **Research References**:
  - #file:../research/20251030-debug-mode-feature-research.md (Lines 134-140) - Output path generation pattern
- **Dependencies**:
  - Task 1.1 completion

**Implementation Details:**

```python
def generate_debug_output_path(input_path: Path) -> Path:
    """
    Generate default debug output path from input path.

    Adds '_debug' suffix before file extension.

    Args:
        input_path: Path to input file.

    Returns:
        Path: Generated debug output file path.

    Example:
        >>> generate_debug_output_path(Path("document.docx"))
        Path("document_debug.docx")
    """
    return input_path.with_stem(f"{input_path.stem}_debug")
```

## Phase 2: Debug Document Generator

### Task 2.1: Create debug document generator utility function

Create a new utility function to generate debug documents with images and alt-text.

- **Files**:
  - `src/ada_annotator/utils/debug_document.py` - New file with `create_debug_document()` function
- **Success**:
  - Function creates valid DOCX document
  - Includes all images with alt-text
  - Formatted consistently
  - Proper error handling
- **Research References**:
  - #file:../research/20251030-debug-mode-feature-research.md (Lines 77-123) - Complete implementation example
- **Dependencies**:
  - None

**Implementation Details:**

Create new file `src/ada_annotator/utils/debug_document.py`:

```python
"""
Debug document generator for visual verification of alt-text.

Creates formatted DOCX documents showing extracted images alongside
their generated alt-text annotations.
"""

from io import BytesIO
from pathlib import Path

import structlog
from docx import Document
from docx.shared import Inches

from ada_annotator.models import AltTextResult, ImageMetadata


def create_debug_document(
    images: list[ImageMetadata],
    alt_text_results: list[AltTextResult],
    output_path: Path,
) -> None:
    """
    Create debug document with images and their alt-text.

    Generates a formatted DOCX document displaying each extracted image
    alongside its metadata and generated alt-text for visual verification.

    Args:
        images: List of extracted image metadata with binary data.
        alt_text_results: List of generated alt-text results.
        output_path: Path where debug document will be saved.

    Raises:
        OSError: If unable to save document to output path.
    """
    logger = structlog.get_logger(__name__)

    doc = Document()
    doc.add_heading("Alt-Text Debug Output", level=1)
    doc.add_paragraph(
        f"Total Images: {len(images)} | "
        f"Successful Annotations: {len(alt_text_results)}"
    )
    doc.add_paragraph()  # Spacing

    # Create lookup for alt-text by image_id
    alt_text_map = {r.image_id: r for r in alt_text_results}

    for idx, img in enumerate(images, 1):
        # Add image heading
        doc.add_heading(f"Image {idx}: {img.image_id}", level=2)

        # Add the actual image
        if img.image_data:
            try:
                image_stream = BytesIO(img.image_data)
                doc.add_picture(image_stream, width=Inches(4.0))
            except Exception as e:
                logger.warning(
                    "failed_to_add_image",
                    image_id=img.image_id,
                    error=str(e),
                )
                doc.add_paragraph(f"[Image could not be displayed: {e}]")
        else:
            doc.add_paragraph("[No image data available]")

        # Add metadata
        doc.add_paragraph(f"Filename: {img.filename}")
        doc.add_paragraph(f"Format: {img.format}")
        doc.add_paragraph(
            f"Dimensions: {img.width_pixels}x{img.height_pixels} pixels"
        )

        # Add generated alt-text
        if img.image_id in alt_text_map:
            result = alt_text_map[img.image_id]
            doc.add_paragraph(f"Alt-Text: {result.alt_text}")
            doc.add_paragraph(f"Confidence: {result.confidence_score:.2%}")
            doc.add_paragraph(f"Tokens Used: {result.tokens_used}")
            doc.add_paragraph(
                f"Processing Time: {result.processing_time_seconds:.2f}s"
            )
        else:
            doc.add_paragraph("Alt-Text: [Generation failed or not processed]")

        # Add spacing between images
        doc.add_paragraph()
        doc.add_paragraph("─" * 70)  # Visual separator
        doc.add_paragraph()

    # Save document
    doc.save(str(output_path))
    logger.info(
        "debug_document_created",
        output_path=str(output_path),
        total_images=len(images),
    )
```

### Task 2.2: Implement image and metadata formatting

Ensure proper formatting and error handling for image display.

- **Files**:
  - `src/ada_annotator/utils/debug_document.py` - Already implemented in Task 2.1
- **Success**:
  - Images display at consistent 4-inch width
  - Metadata formatted consistently
  - Graceful handling of missing image data
  - Visual separators between entries
- **Research References**:
  - #file:../research/20251030-debug-mode-feature-research.md (Lines 77-123) - Formatting patterns
- **Dependencies**:
  - Task 2.1 completion

**Note:** This task is completed as part of Task 2.1 implementation above.

## Phase 3: CLI Processing Logic Integration

### Task 3.1: Add conditional branching in process_document function

Modify the CLI processing logic to branch based on `--debug` flag.

- **Files**:
  - `src/ada_annotator/cli.py` - Modify `process_document()` function and `main()` function
- **Success**:
  - Debug mode creates debug document instead of applying alt-text
  - Normal mode unchanged
  - Proper error handling in both paths
  - Correct output path used for each mode
- **Research References**:
  - #file:../research/20251030-debug-mode-feature-research.md (Lines 53-75) - Processing pipeline pattern
- **Dependencies**:
  - Phase 1 and Phase 2 completion

**Implementation Details:**

In `main()` function, update the output path generation logic:

```python
# Generate or validate output path
if args.output:
    output_path = Path(args.output)
else:
    if args.debug:
        output_path = generate_debug_output_path(input_path)
    else:
        output_path = generate_output_path(input_path)
    logger.info("output_path_generated", path=str(output_path))
```

In `process_document()` function, add debug mode handling after alt-text generation:

```python
# Step 4: Apply alt-text to document OR create debug document
if debug_mode:
    print("[4/4] Creating debug document...")
    from ada_annotator.utils.debug_document import create_debug_document

    create_debug_document(images, alt_text_results, output_path)
    print(f"    Debug document created: {output_path}")
else:
    print("[4/4] Applying alt-text to document...")
    # ... existing assembly code ...
```

Add `debug_mode` parameter to `process_document()` function signature.

### Task 3.2: Update progress indicators for debug mode

Update CLI progress messages to reflect debug mode operation.

- **Files**:
  - `src/ada_annotator/cli.py` - Update print statements in `main()` and `process_document()`
- **Success**:
  - Clear indication when debug mode is active
  - Progress messages accurate for debug workflow
  - Final output message mentions debug document
- **Research References**:
  - None specific - follow existing CLI patterns
- **Dependencies**:
  - Task 3.1 completion

**Implementation Details:**

In `main()` function, update display summary:

```python
# Display processing summary
print(f"\nADA Annotator v{__version__}")
print("=" * 70)
print(f"Input File:    {input_path}")
print(f"Output File:   {output_path}")
if args.context:
    print(f"Context File:  {args.context}")
if args.debug:
    print("\n[DEBUG MODE] Will generate debug document with images and annotations")
if args.dry_run:
    print("\n[!] DRY RUN MODE - No files will be modified")
if args.backup:
    print("\n[+] Backup will be created before processing")
print("=" * 70)
```

## Phase 4: Testing and Validation

### Task 4.1: Test with DOCX input files

Verify debug mode works correctly with DOCX input documents.

- **Files**:
  - Manual testing with sample DOCX files
  - Verify output document quality
- **Success**:
  - Debug document created successfully
  - All images extracted and displayed
  - Alt-text shown correctly
  - No errors or warnings
- **Research References**:
  - #file:../research/20251030-debug-mode-feature-research.md (Lines 142-155) - Technical requirements
- **Dependencies**:
  - Phase 3 completion

**Test Commands:**

```bash
# Test basic debug mode
uv run annotate "test.docx" --debug

# Test with custom output path
uv run annotate "test.docx" --debug --output "my_debug.docx"

# Test with context file
uv run annotate "test.docx" --debug --context "context.txt"

# Test with max images limit
uv run annotate "test.docx" --debug --max-images 5
```

### Task 4.2: Test with PPTX input files

Verify debug mode works correctly with PPTX input presentations.

- **Files**:
  - Manual testing with sample PPTX files
  - Verify output document quality
- **Success**:
  - Debug document created successfully
  - All slides' images extracted and displayed
  - Alt-text shown correctly
  - No errors or warnings
- **Research References**:
  - #file:../research/20251030-debug-mode-feature-research.md (Lines 142-155) - Technical requirements
- **Dependencies**:
  - Phase 3 completion

**Test Commands:**

```bash
# Test basic debug mode with PPTX
uv run annotate "presentation.pptx" --debug

# Test with verbose logging
uv run annotate "presentation.pptx" --debug --verbose
```

### Task 4.3: Verify compatibility with other CLI flags

Test that debug mode works correctly with all other CLI flags.

- **Files**:
  - Manual testing with various flag combinations
- **Success**:
  - `--debug` works with `--verbose`
  - `--debug` works with `--context`
  - `--debug` works with `--max-images`
  - `--debug` works with `--backup` (should not create backup in debug mode)
  - `--debug` and `--dry-run` together handled appropriately
- **Research References**:
  - None specific - verify existing functionality
- **Dependencies**:
  - Phase 3 completion

**Test Combinations:**

```bash
# Debug with verbose
uv run annotate "test.docx" --debug --verbose

# Debug with context
uv run annotate "test.docx" --debug --context "context.txt"

# Debug with max images
uv run annotate "test.docx" --debug --max-images 10

# Debug with backup (verify no backup created)
uv run annotate "test.docx" --debug --backup

# Debug with dry-run (should probably error or warn)
uv run annotate "test.docx" --debug --dry-run
```

## Dependencies

- `python-docx>=1.1.0` (already installed in project)
- `Pillow>=10.1.0` (already installed in project)

## Success Criteria

- ✅ `--debug` flag accepted by CLI without errors
- ✅ Debug document created with `_debug` suffix
- ✅ All extracted images appear in debug document
- ✅ Generated alt-text displayed correctly next to each image
- ✅ Metadata (dimensions, confidence) shown correctly
- ✅ Works for both DOCX and PPTX inputs
- ✅ No interference with normal processing mode
- ✅ Follows Python coding conventions (PEP 8, type hints, docstrings)
- ✅ Proper error handling and logging
- ✅ Compatible with other CLI flags
