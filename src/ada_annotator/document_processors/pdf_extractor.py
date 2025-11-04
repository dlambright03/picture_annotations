"""
PDF document image extractor (DEBUG MODE ONLY).

Extracts images from PDF documents for analysis and alt-text generation.
Note: PDF reassembly is not supported - use debug mode only.
"""

from io import BytesIO
from pathlib import Path

from PIL import Image

from ada_annotator.document_processors.base_extractor import DocumentExtractor
from ada_annotator.exceptions import ProcessingError
from ada_annotator.models import ImageMetadata


class PDFExtractor(DocumentExtractor):
    """
    Extract images from PDF documents (DEBUG MODE ONLY).

    This extractor can extract images from PDFs for analysis purposes,
    but does not support reassembling PDFs with alt-text. Use --debug
    flag to generate a DOCX report with images and annotations.

    Supports:
    - Image extraction from PDF pages
    - Multiple images per page
    - Various image formats (JPEG, PNG, etc.)
    - Page-level context
    """

    def __init__(self, document_path: Path):
        """
        Initialize PDF extractor.

        Args:
            document_path: Path to PDF file.

        Raises:
            FileNotFoundError: If file does not exist.
            ValueError: If file is not PDF format.
            ImportError: If PyMuPDF (fitz) is not installed.
        """
        super().__init__(document_path)

        # Validate PDF extension
        if document_path.suffix.lower() != ".pdf":
            raise ValueError(f"Not a PDF file: {document_path}")

        # Import PyMuPDF
        try:
            import fitz  # PyMuPDF
            self.fitz = fitz
        except ImportError as e:
            raise ImportError(
                "PyMuPDF (fitz) is required for PDF processing. "
                "Install with: pip install PyMuPDF"
            ) from e

        # Load PDF document
        try:
            self.pdf_document = self.fitz.open(str(document_path))
            self.logger.info(
                "pdf_loaded",
                document_path=str(document_path),
                page_count=len(self.pdf_document),
            )
        except Exception as e:
            raise ProcessingError(f"Failed to load PDF: {e}") from e

    def get_document_format(self) -> str:
        """
        Get document format identifier.

        Returns:
            str: 'PDF'
        """
        return "PDF"

    def extract_images(self) -> list[ImageMetadata]:
        """
        Extract all images from PDF document.

        Iterates through all pages and extracts embedded images with
        metadata and page context.

        Returns:
            List[ImageMetadata]: List of extracted images.

        Raises:
            ProcessingError: If extraction fails.
        """
        self.logger.info(
            "extraction_started",
            document_format="PDF",
            total_pages=len(self.pdf_document),
        )

        images = []

        try:
            # Iterate through all pages
            for page_idx in range(len(self.pdf_document)):
                page = self.pdf_document[page_idx]

                # Extract images from this page
                page_images = self._extract_images_from_page(page, page_idx)
                images.extend(page_images)

            self.logger.info(
                "extraction_completed",
                total_images=len(images),
                total_pages=len(self.pdf_document),
            )

            return images

        except Exception as e:
            self.logger.error(
                "extraction_failed",
                error=str(e),
            )
            raise ProcessingError(f"Failed to extract images: {e}") from e
        finally:
            # Clean up
            if hasattr(self, "pdf_document"):
                self.pdf_document.close()

    def _extract_images_from_page(
        self, page, page_idx: int
    ) -> list[ImageMetadata]:
        """
        Extract all images from a single PDF page.

        Args:
            page: The PyMuPDF page object.
            page_idx: Zero-based page index.

        Returns:
            List[ImageMetadata]: List of images from this page.
        """
        images = []

        try:
            # Get list of images on page
            image_list = page.get_images(full=True)

            for img_idx, img_info in enumerate(image_list):
                try:
                    # Extract image data
                    image_metadata = self._extract_image_from_info(
                        img_info, page_idx, img_idx
                    )

                    if image_metadata:
                        images.append(image_metadata)

                except Exception as e:
                    self.logger.warning(
                        "image_extraction_failed",
                        page_index=page_idx,
                        image_index=img_idx,
                        error=str(e),
                    )
                    continue

            self.logger.debug(
                "page_extraction_completed",
                page_index=page_idx,
                images_found=len(images),
            )

        except Exception as e:
            self.logger.warning(
                "page_extraction_failed",
                page_index=page_idx,
                error=str(e),
            )

        return images

    def _extract_image_from_info(
        self, img_info, page_idx: int, img_idx: int
    ) -> ImageMetadata | None:
        """
        Extract image metadata from PyMuPDF image info.

        Args:
            img_info: PyMuPDF image information tuple.
            page_idx: Zero-based page index.
            img_idx: Zero-based image index on page.

        Returns:
            Optional[ImageMetadata]: Image metadata if successful.
        """
        try:
            # Get xref (cross-reference number) for the image
            xref = img_info[0]

            # Extract image bytes
            base_image = self.pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]  # Extension like 'png', 'jpeg'

            # Normalize format
            format_str = image_ext.upper()
            if format_str in ["JPG", "JPEG"]:
                format_str = "JPEG"

            # Load with PIL to get dimensions and validate
            img = Image.open(BytesIO(image_bytes))

            # Create position metadata
            position = {
                "page_index": page_idx,
                "image_index": img_idx,
                "xref": xref,
            }

            # Create unique image ID
            image_id = f"page{page_idx}_img{img_idx}"

            # Create ImageMetadata with binary data
            metadata = ImageMetadata(
                image_id=image_id,
                filename=f"{image_id}.{format_str.lower()}",
                format=format_str,
                size_bytes=len(image_bytes),
                width_pixels=img.width,
                height_pixels=img.height,
                page_number=page_idx + 1,  # 1-based page number
                position=position,
                existing_alt_text=None,  # PDFs don't have alt-text in images
                image_data=image_bytes,  # Store binary data for processing
            )

            self.logger.debug(
                "image_extracted",
                image_id=image_id,
                page_index=page_idx,
                image_index=img_idx,
                format=format_str,
                xref=xref,
            )

            return metadata

        except Exception as e:
            self.logger.warning(
                "image_metadata_creation_failed",
                page_index=page_idx,
                image_index=img_idx,
                error=str(e),
            )
            return None
