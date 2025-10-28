import asyncio
from pathlib import Path
from ada_annotator.config import get_settings
from ada_annotator.ai_services import SemanticKernelService
from ada_annotator.document_processors import DOCXExtractor

async def test_single_image():
    settings = get_settings()
    service = SemanticKernelService(settings)
    
    # Extract first image
    extractor = DOCXExtractor(Path(r'c:\Users\ladavid\Downloads\C342 FA25 Chapter 17 Lecture Notes.docx'))
    images = extractor.extract_images()
    
    if images:
        img = images[0]
        print(f"Testing with image: {img.image_id}")
        print(f"Size: {img.width_pixels}x{img.height_pixels}")
        print(f"Existing alt-text: {img.existing_alt_text}")
        
        alt_text = await service.generate_alt_text(img, "Chemistry textbook chapter on aromatic compounds")
        print(f"\nGenerated alt-text ({len(alt_text)} chars):")
        print(alt_text)

if __name__ == '__main__':
    asyncio.run(test_single_image())
