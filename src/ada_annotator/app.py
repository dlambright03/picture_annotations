"""
Streamlit web application for ADA Annotator.

Provides a user-friendly interface for uploading documents and
generating ADA-compliant alt-text for images.
"""

import streamlit as st

from ada_annotator import __version__
from ada_annotator.config import get_settings


def main() -> None:
    """Main Streamlit application entry point."""
    # Page configuration
    st.set_page_config(
        page_title="ADA Annotator",
        page_icon="🖼️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Load settings
    settings = get_settings()

    # Title and description
    st.title("🖼️ ADA Annotator")
    st.markdown(
        f"""
        ### Automated Image Accessibility for Educational Documents

        **Version:** {__version__} | **Environment:** {settings.environment}

        Upload a Word document to automatically generate ADA-compliant alt-text
        descriptions for all images using AI-powered analysis.
        """
    )

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.info(
            f"""
            **AI Service:** {settings.ai_service_type}

            **Model Settings:**
            - Temperature: {settings.ai_temperature}
            - Max Tokens: {settings.ai_max_tokens}

            **Alt-Text Limits:**
            - Preferred: {settings.preferred_alt_text_length} chars
            - Maximum: {settings.max_alt_text_length} chars
            """
        )

        st.header("ℹ️ About")
        st.markdown(
            """
            This tool helps educators make their documents accessible
            by automatically generating descriptive alt-text for images.

            **Supported Formats:**
            - Microsoft Word (.docx)
            - PDF (.pdf) - Coming soon
            - PowerPoint (.pptx) - Coming soon
            """
        )

    # Main content area
    st.header("📄 Upload Document")

    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a Word document",
        type=["docx"],
        help=f"Maximum file size: {settings.max_upload_size_mb}MB",
    )

    if uploaded_file is not None:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        st.info(
            "**Note:** Document processing not yet implemented. This is the UI skeleton."
        )

        # Show file details
        col1, col2 = st.columns(2)
        with col1:
            st.metric("File Name", uploaded_file.name)
        with col2:
            file_size_mb = uploaded_file.size / (1024 * 1024)
            st.metric("File Size", f"{file_size_mb:.2f} MB")

        # Placeholder for processing button
        if st.button("🚀 Process Document", type="primary", disabled=True):
            st.warning(
                "Document processing will be implemented in the next iteration."
            )

        # Placeholder for results
        st.header("📊 Results")
        st.info("Results will appear here after processing is implemented.")

    else:
        st.info("👆 Upload a document to get started")

    # Footer
    st.divider()
    st.caption(
        "Made with ❤️ for accessibility in education | "
        "[GitHub](https://github.com/yourusername/ada-annotator) | "
        "[Documentation](docs/requirements.md)"
    )


if __name__ == "__main__":
    main()
