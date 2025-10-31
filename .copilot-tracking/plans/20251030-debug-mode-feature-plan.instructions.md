---
applyTo: '.copilot-tracking/changes/20251030-debug-mode-feature-changes.md'
---
<!-- markdownlint-disable-file -->
# Task Checklist: Debug Mode Feature Implementation

## Overview

Add a `--debug` CLI flag that generates a separate debug document containing all extracted images alongside their generated alt-text annotations for visual verification purposes.

## Objectives

- Add `--debug` CLI argument to enable debug output mode
- Create debug document generator utility function
- Generate formatted DOCX showing images with their metadata and alt-text
- Maintain compatibility with existing processing pipeline
- Support both DOCX and PPTX input formats

## Research Summary

### Project Files
- `src/ada_annotator/cli.py` - CLI entry point with argparse configuration
- `src/ada_annotator/document_processors/docx_extractor.py` - Image extraction with binary data
- `src/ada_annotator/models/image_metadata.py` - Contains `image_data` field for in-memory storage
- `pyproject.toml` - Confirms python-docx>=1.1.0 dependency available

### External References
- #file:../research/20251030-debug-mode-feature-research.md - Complete research findings and implementation patterns

### Standards References
- #file:../../.github/instructions/python.instructions.md - Python coding conventions (PEP 8, type hints, docstrings)

## Implementation Checklist

### [ ] Phase 1: CLI Argument Addition

- [ ] Task 1.1: Add `--debug` flag to argument parser
  - Details: .copilot-tracking/details/20251030-debug-mode-feature-details.md (Lines 15-35)

- [ ] Task 1.2: Update output path generation for debug mode
  - Details: .copilot-tracking/details/20251030-debug-mode-feature-details.md (Lines 37-58)

### [ ] Phase 2: Debug Document Generator

- [ ] Task 2.1: Create debug document generator utility function
  - Details: .copilot-tracking/details/20251030-debug-mode-feature-details.md (Lines 60-125)

- [ ] Task 2.2: Implement image and metadata formatting
  - Details: .copilot-tracking/details/20251030-debug-mode-feature-details.md (Lines 127-160)

### [ ] Phase 3: CLI Processing Logic Integration

- [ ] Task 3.1: Add conditional branching in process_document function
  - Details: .copilot-tracking/details/20251030-debug-mode-feature-details.md (Lines 162-195)

- [ ] Task 3.2: Update progress indicators for debug mode
  - Details: .copilot-tracking/details/20251030-debug-mode-feature-details.md (Lines 197-220)

### [ ] Phase 4: Testing and Validation

- [ ] Task 4.1: Test with DOCX input files
  - Details: .copilot-tracking/details/20251030-debug-mode-feature-details.md (Lines 222-245)

- [ ] Task 4.2: Test with PPTX input files
  - Details: .copilot-tracking/details/20251030-debug-mode-feature-details.md (Lines 247-270)

- [ ] Task 4.3: Verify compatibility with other CLI flags
  - Details: .copilot-tracking/details/20251030-debug-mode-feature-details.md (Lines 272-295)

## Dependencies

- `python-docx>=1.1.0` (already installed)
- `Pillow>=10.1.0` (already installed)
- No new external dependencies required

## Success Criteria

- `--debug` flag accepted by CLI without errors
- Debug document created with `_debug` suffix
- All extracted images appear in debug document at readable size
- Generated alt-text displayed correctly next to each image
- Metadata (dimensions, confidence, tokens) shown accurately
- Works seamlessly with both DOCX and PPTX inputs
- No interference with normal processing mode (without --debug)
- Follows project coding conventions (PEP 8, type hints, docstrings)
