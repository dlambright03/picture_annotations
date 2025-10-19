"""
Context data model for hierarchical context extraction.

Contains all context levels for an image to provide to the AI service.
"""

from typing import Optional

from pydantic import BaseModel, Field


class ContextData(BaseModel):
    """
    Hierarchical context data for an image.
    
    Implements a 4-level context hierarchy:
    1. External context (from user-provided file)
    2. Document context (title, subject, author)
    3. Section context (nearest heading)
    4. Page context (slide title for PPTX)
    5. Local context (surrounding paragraphs)
    
    Attributes:
        external_context: Context from external file.
        document_context: Document-level metadata.
        section_context: Section or heading context.
        page_context: Page or slide context.
        local_context: Local surrounding text.
    """
    
    external_context: Optional[str] = Field(
        None,
        description="Context from external file (highest priority)"
    )
    document_context: str = Field(
        ...,
        description="Document-level metadata (title, subject)"
    )
    section_context: Optional[str] = Field(
        None,
        description="Section or heading context"
    )
    page_context: Optional[str] = Field(
        None,
        description="Page or slide context (PPTX only)"
    )
    local_context: str = Field(
        ...,
        description="Local surrounding text (paragraphs before/after)"
    )
    
    def get_merged_context(self, max_chars: int = 12000) -> str:
        """
        Merge all context levels into a single string with separators.
        
        Parameters:
            max_chars: Maximum characters to include (default 12000 ~
                      3000 tokens).
        
        Returns:
            str: Merged context string with level separators.
        """
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
        
        # Truncate if too long
        if len(merged) > max_chars:
            merged = merged[:max_chars] + "..."
        
        return merged
    
    class Config:
        """Pydantic model configuration."""
        
        json_schema_extra = {
            "example": {
                "external_context": "This is a biology textbook",
                "document_context": "Chapter 3: Cell Biology",
                "section_context": "Mitochondria Structure",
                "page_context": None,
                "local_context": (
                    "The mitochondria are known as the powerhouse of "
                    "the cell. They generate ATP through cellular "
                    "respiration."
                )
            }
        }
