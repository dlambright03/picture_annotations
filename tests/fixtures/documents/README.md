# Test Fixture Documents

This directory contains sample documents for testing.

## Creating Test Documents

To create proper test fixtures, you need actual DOCX and PPTX files.
Use Microsoft Word/PowerPoint or python-docx/python-pptx to create:

1. **sample.docx** - DOCX with various image types
   - Should contain: JPEG, PNG images
   - Should have: headings, paragraphs around images
   - Should include: document properties (title, subject)

2. **sample.pptx** - PPTX with images on slides
   - Should contain: images on different slides
   - Should have: slide titles
   - Should include: various image formats

3. **no_images.docx** - DOCX without any images
   - Edge case for testing empty image lists

4. **corrupted.docx** - Invalid/corrupted DOCX file
   - Edge case for testing error handling
   - Can create by: echo "not a real docx" > corrupted.docx

## Manual Creation Required

These files should be created manually or via script before running
integration tests. The unit tests will use mocks and don't require
these files.

## TODO for Test Setup

Run the following to create basic test fixtures:

```powershell
# Create minimal corrupted file
"This is not a valid DOCX file" | Out-File -FilePath "tests/fixtures/documents/corrupted.docx"

# For real DOCX/PPTX files, use python-docx/python-pptx or
# create manually with Office applications
```
