"""
JSON handler for alt-text data persistence.

Provides functions to save and load alt-text results in JSON format,
enabling separation of generation and application workflows.
Also generates HTML reports for human-readable review.
"""

import base64
import json
from pathlib import Path

import structlog

from ada_annotator.models import AltTextResult, ImageMetadata


logger = structlog.get_logger(__name__)


def save_alt_text_to_json(
    results: list[AltTextResult],
    images: list[ImageMetadata],
    output_path: Path,
    source_document: Path,
) -> None:
    """
    Save alt-text results to JSON file with embedded images.

    Images are base64-encoded for human review alongside alt-text.

    Args:
        results: List of alt-text generation results.
        images: List of image metadata (must include image_data).
        output_path: Path where JSON will be saved.
        source_document: Path to source document.

    Raises:
        OSError: If unable to write file.
    """
    # Create data structure
    data = {
        "version": "1.0",
        "source_document": str(source_document),
        "document_type": source_document.suffix.upper().lstrip("."),
        "total_images": len(images),
        "processed_images": len(results),
        "alt_text_results": [
            {
                "image_id": result.image_id,
                "alt_text": result.alt_text,
                "is_decorative": result.is_decorative,
                "confidence_score": round(result.confidence_score, 3),
                "validation_passed": result.validation_passed,
                "validation_warnings": result.validation_warnings,
                "tokens_used": result.tokens_used,
                "processing_time_seconds": result.processing_time_seconds,
            }
            for result in results
        ],
        "images": [
            {
                "image_id": img.image_id,
                "filename": img.filename,
                "format": img.format,
                "width_pixels": img.width_pixels,
                "height_pixels": img.height_pixels,
                "page_number": img.page_number,
                "position": img.position,
                "existing_alt_text": img.existing_alt_text,
                # Base64-encode image data for human review
                "image_data_base64": (
                    base64.b64encode(img.image_data).decode("utf-8")
                    if img.image_data
                    else None
                ),
            }
            for img in images
        ],
    }

    # Write to file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info(
        "alt_text_saved_to_json",
        output_path=str(output_path),
        total_results=len(results),
    )


def load_alt_text_from_json(json_path: Path) -> dict:
    """
    Load alt-text results from JSON file.

    Args:
        json_path: Path to JSON file.

    Returns:
        Dictionary with alt-text results and metadata.

    Raises:
        FileNotFoundError: If JSON file doesn't exist.
        ValueError: If JSON is invalid or incompatible version.
    """
    if not json_path.exists():
        raise FileNotFoundError(f"JSON file not found: {json_path}")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Validate version
    if data.get("version") != "1.0":
        raise ValueError(
            f"Unsupported JSON version: {data.get('version')}. "
            "Expected version 1.0"
        )

    logger.info(
        "alt_text_loaded_from_json",
        json_path=str(json_path),
        total_results=len(data.get("alt_text_results", [])),
    )

    return data


def generate_json_output_path(input_path: Path) -> Path:
    """
    Generate default JSON output path from input path.

    Args:
        input_path: Path to input document.

    Returns:
        Path: Generated JSON file path.

    Example:
        >>> generate_json_output_path(Path("document.docx"))
        Path("document_alttext.json")
    """
    return input_path.with_stem(f"{input_path.stem}_alttext").with_suffix(".json")


def generate_html_output_path(input_path: Path) -> Path:
    """
    Generate default HTML output path from input path.

    Args:
        input_path: Path to input document.

    Returns:
        Path: Generated HTML file path.

    Example:
        >>> generate_html_output_path(Path("document.docx"))
        Path("document_alttext.html")
    """
    return input_path.with_stem(f"{input_path.stem}_alttext").with_suffix(".html")


def save_alt_text_to_html(
    results: list[AltTextResult],
    images: list[ImageMetadata],
    output_path: Path,
    source_document: Path,
) -> None:
    """
    Save alt-text results to HTML file with embedded images for easy review.

    Creates an interactive HTML page showing each image alongside its generated
    alt-text, metadata, and validation status.

    Args:
        results: List of alt-text generation results.
        images: List of image metadata (must include image_data).
        output_path: Path where HTML will be saved.
        source_document: Path to source document.

    Raises:
        OSError: If unable to write file.
    """
    # Create mapping of image_id to results
    result_map = {r.image_id: r for r in results}

    # Build HTML content
    html_parts = [
        """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alt-Text Review - """ + source_document.name + """</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            text-align: center;
        }
        .header h1 {
            font-size: 2rem;
            margin-bottom: 0.5rem;
            font-weight: 600;
        }
        .header p {
            opacity: 0.9;
            font-size: 1rem;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            padding: 2rem;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
        }
        .stat {
            text-align: center;
            padding: 1rem;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            color: #667eea;
            display: block;
        }
        .stat-label {
            color: #6c757d;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-top: 0.5rem;
        }
        .images {
            padding: 2rem;
        }
        .image-card {
            background: #fff;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            margin-bottom: 2rem;
            overflow: hidden;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .image-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .image-header {
            background: #f8f9fa;
            padding: 1rem 1.5rem;
            border-bottom: 1px solid #e9ecef;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 0.5rem;
        }
        .image-id {
            font-weight: 600;
            color: #495057;
            font-family: "Courier New", monospace;
        }
        .badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .badge-success {
            background: #d4edda;
            color: #155724;
        }
        .badge-warning {
            background: #fff3cd;
            color: #856404;
        }
        .badge-decorative {
            background: #e2e3e5;
            color: #383d41;
        }
        .image-content {
            display: grid;
            grid-template-columns: minmax(300px, 1fr) 1.5fr;
            gap: 2rem;
            padding: 1.5rem;
        }
        @media (max-width: 768px) {
            .image-content {
                grid-template-columns: 1fr;
            }
        }
        .image-preview {
            text-align: center;
        }
        .image-preview img {
            max-width: 100%;
            height: auto;
            border-radius: 4px;
            border: 1px solid #dee2e6;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .image-dimensions {
            margin-top: 0.5rem;
            color: #6c757d;
            font-size: 0.875rem;
        }
        .image-details {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        .detail-section {
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 6px;
            border-left: 4px solid #667eea;
        }
        .detail-section h3 {
            font-size: 0.875rem;
            color: #495057;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.5rem;
            font-weight: 600;
        }
        .detail-section p {
            color: #212529;
            line-height: 1.6;
        }
        .alt-text {
            font-size: 1rem;
            font-style: italic;
        }
        .metadata {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 0.75rem;
        }
        .metadata-item {
            display: flex;
            flex-direction: column;
        }
        .metadata-label {
            font-size: 0.75rem;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .metadata-value {
            font-weight: 600;
            color: #212529;
            margin-top: 0.25rem;
        }
        .warnings {
            background: #fff3cd;
            border-left-color: #ffc107;
        }
        .warnings ul {
            margin-left: 1.25rem;
            color: #856404;
        }
        .warnings li {
            margin-top: 0.25rem;
        }
        .footer {
            background: #f8f9fa;
            padding: 1.5rem;
            text-align: center;
            color: #6c757d;
            font-size: 0.875rem;
            border-top: 1px solid #e9ecef;
        }
        .no-results {
            padding: 3rem;
            text-align: center;
            color: #6c757d;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Alt-Text Review Report</h1>
            <p>""" + source_document.name + """</p>
        </div>
        
        <div class="stats">
            <div class="stat">
                <span class="stat-value">""" + str(len(images)) + """</span>
                <span class="stat-label">Total Images</span>
            </div>
            <div class="stat">
                <span class="stat-value">""" + str(len(results)) + """</span>
                <span class="stat-label">Processed</span>
            </div>
            <div class="stat">
                <span class="stat-value">""" + str(sum(1 for r in results if r.validation_passed)) + """</span>
                <span class="stat-label">Validated</span>
            </div>
            <div class="stat">
                <span class="stat-value">""" + str(sum(1 for r in results if r.is_decorative)) + """</span>
                <span class="stat-label">Decorative</span>
            </div>
        </div>
        
        <div class="images">
"""
    ]

    # Add each image
    for img in images:
        result = result_map.get(img.image_id)
        
        # Convert image to base64 for embedding
        if img.image_data:
            img_base64 = base64.b64encode(img.image_data).decode('utf-8')
            img_format = img.format.lower()
            if img_format == 'jpeg':
                img_format = 'jpg'
            img_src = f"data:image/{img_format};base64,{img_base64}"
        else:
            img_src = ""

        # Status badge
        if result:
            if result.is_decorative:
                status_badge = '<span class="badge badge-decorative">Decorative</span>'
            elif result.validation_passed:
                status_badge = '<span class="badge badge-success">Validated</span>'
            else:
                status_badge = '<span class="badge badge-warning">Warnings</span>'
        else:
            status_badge = '<span class="badge badge-warning">No Result</span>'

        # Image card HTML
        html_parts.append(f"""
            <div class="image-card">
                <div class="image-header">
                    <span class="image-id">{img.image_id}</span>
                    {status_badge}
                </div>
                <div class="image-content">
                    <div class="image-preview">
                        <img src="{img_src}" alt="Preview of {img.image_id}">
                        <div class="image-dimensions">
                            {img.width_pixels} × {img.height_pixels} px
                            {' • ' + img.format if img.format else ''}
                            {' • Page ' + str(img.page_number) if img.page_number else ''}
                        </div>
                    </div>
                    <div class="image-details">
""")

        # Alt-text section
        if result:
            if result.is_decorative:
                html_parts.append("""
                        <div class="detail-section">
                            <h3>Decorative Image</h3>
                            <p class="alt-text">This image is marked as decorative and does not require alt-text.</p>
                        </div>
""")
            else:
                html_parts.append(f"""
                        <div class="detail-section">
                            <h3>Generated Alt-Text</h3>
                            <p class="alt-text">"{result.alt_text}"</p>
                        </div>
""")

            # Metadata section
            html_parts.append(f"""
                        <div class="detail-section">
                            <h3>Metadata</h3>
                            <div class="metadata">
                                <div class="metadata-item">
                                    <span class="metadata-label">Confidence</span>
                                    <span class="metadata-value">{result.confidence_score:.1%}</span>
                                </div>
                                <div class="metadata-item">
                                    <span class="metadata-label">Tokens Used</span>
                                    <span class="metadata-value">{result.tokens_used:,}</span>
                                </div>
                                <div class="metadata-item">
                                    <span class="metadata-label">Processing Time</span>
                                    <span class="metadata-value">{result.processing_time_seconds:.2f}s</span>
                                </div>
                                <div class="metadata-item">
                                    <span class="metadata-label">File Size</span>
                                    <span class="metadata-value">{img.size_bytes / 1024:.1f} KB</span>
                                </div>
                            </div>
                        </div>
""")

            # Warnings section
            if result.validation_warnings:
                warnings_html = "\n".join(f"<li>{w}</li>" for w in result.validation_warnings)
                html_parts.append(f"""
                        <div class="detail-section warnings">
                            <h3>Validation Warnings</h3>
                            <ul>
                                {warnings_html}
                            </ul>
                        </div>
""")
        else:
            html_parts.append("""
                        <div class="detail-section warnings">
                            <h3>Processing Error</h3>
                            <p>No alt-text result available for this image.</p>
                        </div>
""")

        # Existing alt-text if present
        if img.existing_alt_text:
            html_parts.append(f"""
                        <div class="detail-section">
                            <h3>Existing Alt-Text</h3>
                            <p class="alt-text">"{img.existing_alt_text}"</p>
                        </div>
""")

        html_parts.append("""
                    </div>
                </div>
            </div>
""")

    # Close HTML
    html_parts.append(f"""
        </div>
        
        <div class="footer">
            <p>Generated by ADA Annotator • {len(results)} images processed • Document: {source_document.name}</p>
        </div>
    </div>
</body>
</html>
""")

    # Write HTML file
    html_content = "".join(html_parts)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    logger.info(
        "alt_text_saved_to_html",
        output_path=str(output_path),
        total_results=len(results),
    )
