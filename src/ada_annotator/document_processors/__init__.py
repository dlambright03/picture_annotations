"""
Document processors for extracting images from various formats.

Supports DOCX and PPTX formats with position metadata and
existing alt-text extraction. Also includes document assemblers
for applying alt-text to output documents.
"""

from ada_annotator.document_processors.base_assembler import (
    DocumentAssembler
)
from ada_annotator.document_processors.base_extractor import (
    DocumentExtractor
)
from ada_annotator.document_processors.docx_assembler import (
    DOCXAssembler
)
from ada_annotator.document_processors.docx_extractor import (
    DOCXExtractor
)
from ada_annotator.document_processors.pptx_extractor import (
    PPTXExtractor
)

__all__ = [
    "DocumentAssembler",
    "DocumentExtractor",
    "DOCXAssembler",
    "DOCXExtractor",
    "PPTXExtractor",
]

