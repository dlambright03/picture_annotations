# Troubleshooting Guide - ADA Annotator

This guide provides solutions to common issues encountered when using the ADA Annotator application.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Configuration Issues](#configuration-issues)
- [Document Processing Issues](#document-processing-issues)
- [API and Network Issues](#api-and-network-issues)
- [Performance Issues](#performance-issues)
- [Testing and Development Issues](#testing-and-development-issues)
- [Common Error Messages](#common-error-messages)

---

## Installation Issues

### UV Package Manager Not Found

**Symptoms:**
```powershell
uv: command not found
```

**Solutions:**

**Windows:**
```powershell
# Reinstall UV
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Add to PATH
$env:Path += ";$env:USERPROFILE\.local\bin"

# Restart terminal
```

**macOS/Linux:**
```bash
# Reinstall UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH
export PATH="$HOME/.local/bin:$PATH"
source ~/.bashrc
```

### Python Version Incompatibility

**Symptoms:**
- `Python 3.11 or higher required` error
- Import errors for modern type hints

**Solutions:**
```powershell
# Check Python version
python --version

# Install Python 3.11+ from python.org
# Then create venv with specific version
uv venv --python 3.11
```

### Module Import Errors

**Symptoms:**
```python
ModuleNotFoundError: No module named 'ada_annotator'
```

**Solutions:**
```powershell
# Ensure virtual environment is activated
.\.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate      # macOS/Linux

# Reinstall in editable mode
uv pip install -e ".[dev]"

# Verify installation
python -c "import ada_annotator; print(ada_annotator.__file__)"
```

---

## Configuration Issues

### Missing Environment Variables

**Symptoms:**
- `ValidationError: AZURE_OPENAI_ENDPOINT` error
- `Configuration not found` messages

**Solutions:**

1. **Verify .env file exists:**
   ```powershell
   Test-Path .env
   ```

2. **Check .env file contents:**
   ```powershell
   cat .env
   ```

3. **Ensure required variables are set:**
   ```bash
   AI_SERVICE_TYPE=azure_openai
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_API_KEY=your-api-key-here
   AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
   ```

4. **No extra spaces or quotes:**
   ```bash
   # WRONG
   AZURE_OPENAI_ENDPOINT = "https://..."
   
   # CORRECT
   AZURE_OPENAI_ENDPOINT=https://...
   ```

### Azure OpenAI Connection Failed

**Symptoms:**
- `APIError: Connection failed`
- `AuthenticationError` messages
- Timeout errors

**Diagnostic Steps:**

1. **Test endpoint URL:**
   ```powershell
   # Verify URL is reachable
   Test-NetConnection your-resource.openai.azure.com -Port 443
   ```

2. **Validate credentials with curl:**
   ```powershell
   $headers = @{
       "api-key" = "your-api-key"
       "Content-Type" = "application/json"
   }
   
   $body = @{
       messages = @(@{ role = "user"; content = "Test" })
       max_tokens = 10
   } | ConvertTo-Json
   
   Invoke-RestMethod -Uri "https://your-resource.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-02-15-preview" -Method Post -Headers $headers -Body $body
   ```

3. **Common fixes:**
   - Ensure endpoint URL ends with `/`
   - Verify deployment name matches Azure Portal exactly
   - Check API key is valid (regenerate if needed)
   - Confirm API version is supported

### Wrong Deployment Name

**Symptoms:**
- `DeploymentNotFound` error
- `Model not found` messages

**Solutions:**

1. **Find correct deployment name:**
   - Go to Azure Portal
   - Navigate to Azure OpenAI resource
   - Click "Model deployments"
   - Copy exact deployment name

2. **Update .env:**
   ```bash
   AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o  # Exact name from portal
   ```

3. **Verify deployment has vision capabilities:**
   - Must be GPT-4o or GPT-4V model
   - Check "Capabilities" in Azure Portal

---

## Document Processing Issues

### No Images Found in Document

**Symptoms:**
- `No images found in document` message
- Empty extraction results

**Possible Causes:**
1. Document has no embedded images
2. Images are linked externally (not embedded)
3. Document uses unsupported image format

**Solutions:**

1. **Verify document has images:**
   - Open in Word/PowerPoint
   - Check images are actually embedded
   - Right-click image  Picture Format  ensure not linked

2. **Re-embed external images:**
   - Copy image
   - Delete original
   - Paste as embedded image

3. **Test with sample document:**
   ```powershell
   python -m ada_annotator.cli --input tests/fixtures/documents/sample.docx --dry-run
   ```

### Corrupted Document Errors

**Symptoms:**
- `ProcessingError: Failed to open document`
- `zipfile.BadZipFile` errors
- `lxml.etree` parsing errors

**Solutions:**

1. **Open and re-save in Office:**
   - Open document in Word/PowerPoint
   - Save As  New file
   - Try processing new file

2. **Check file extension:**
   ```powershell
   # Ensure extension matches content
   .docx = Word document
   .pptx = PowerPoint presentation
   ```

3. **Verify file permissions:**
   ```powershell
   # Check file is readable
   Test-Path -Path document.docx -PathType Leaf
   Get-Acl document.docx
   ```

4. **Test with known-good file:**
   ```powershell
   python -m ada_annotator.cli --input tests/fixtures/documents/sample.docx --output test.docx
   ```

### Position Preservation Issues

**Symptoms:**
- Images appear in wrong locations
- Layout broken after processing

**Understanding Position Systems:**

**DOCX (Paragraph-based):**
- Position is relative to paragraphs (flow layout)
- Images stay in same paragraph
- May appear different in different Word views
- Check in "Print Layout" view (most reliable)

**PPTX (Coordinate-based):**
- Position preserved with EMU precision
- Should be pixel-perfect
- Verify in PowerPoint "Normal" view

**Debugging:**
```powershell
# Enable debug logging to see position metadata
python -m ada_annotator.cli \
    --input document.docx \
    --output output.docx \
    --log-level DEBUG
    
# Check logs for position data
cat logs/ada-annotator.log | ConvertFrom-Json | Where-Object { $_.event -like "*position*" }
```

### Alt-Text Not Applied

**Symptoms:**
- Output document has no alt-text
- Only some images have alt-text

**Diagnostic Steps:**

1. **Check report file:**
   ```powershell
   cat output_report.md
   # Look for "Failed Images" section
   ```

2. **Review logs:**
   ```powershell
   cat logs/ada-annotator.log | ConvertFrom-Json | Where-Object { $_.level -eq "error" }
   ```

3. **Common causes:**
   - API errors (check Azure OpenAI status)
   - Rate limiting (reduce batch size)
   - Validation failures (check warnings)
   - Image format issues

4. **Retry with smaller batch:**
   ```powershell
   python -m ada_annotator.cli \
       --input document.docx \
       --output output.docx \
       --max-images 5
   ```

---

## API and Network Issues

### Rate Limit Exceeded (429 Error)

**Symptoms:**
- `APIError: Rate limit exceeded (429)`
- Processing stops partway through

**Solutions:**

1. **Check Azure OpenAI quota:**
   - Go to Azure Portal
   - Navigate to Azure OpenAI resource
   - Check "Quota" section
   - View TPM (Tokens Per Minute) limit

2. **Reduce processing rate:**
   ```powershell
   # Process fewer images at a time
   python -m ada_annotator.cli \
       --input document.docx \
       --output output.docx \
       --max-images 10
   ```

3. **Wait and retry:**
   - Built-in retry logic will handle transient limits
   - For persistent issues, wait 60 seconds between runs

4. **Increase quota (if needed):**
   - Request quota increase in Azure Portal
   - Can take 24-48 hours for approval

### Timeout Errors

**Symptoms:**
- `APIError: Request timeout`
- Long processing times with eventual failure

**Solutions:**

1. **Check network connectivity:**
   ```powershell
   Test-NetConnection your-resource.openai.azure.com -Port 443
   ```

2. **Verify Azure OpenAI service status:**
   - Check Azure Status page
   - Look for region-specific outages

3. **Reduce image size/complexity:**
   - Large images may timeout
   - Consider resizing images before processing

4. **Enable debug logging:**
   ```powershell
   python -m ada_annotator.cli \
       --input document.docx \
       --output output.docx \
       --log-level DEBUG
   ```

### SSL Certificate Errors

**Symptoms:**
- `SSLError` or certificate verification failed

**Solutions:**

1. **Update CA certificates:**
   ```powershell
   # Windows: Update Windows
   # macOS: Update certificates
   # Linux: sudo update-ca-certificates
   ```

2. **Check corporate proxy:**
   - May need proxy configuration
   - Contact IT for proxy settings

---

## Performance Issues

### Slow Processing Times

**Symptoms:**
- Processing takes much longer than expected
- 10+ seconds per image

**Optimization Strategies:**

1. **Measure baseline:**
   ```powershell
   # Time a small test
   Measure-Command {
       python -m ada_annotator.cli \
           --input tests/fixtures/documents/sample.docx \
           --output test.docx \
           --max-images 1
   }
   ```

2. **Check network latency:**
   ```powershell
   Test-NetConnection your-resource.openai.azure.com
   ```

3. **Optimize context size:**
   - Keep context files under 2000 characters
   - Shorter context = fewer tokens = faster processing

4. **Use dry-run for testing:**
   ```powershell
   # Test extraction without API calls
   python -m ada_annotator.cli --input document.docx --dry-run
   ```

### High Memory Usage

**Symptoms:**
- System slow during processing
- Out of memory errors

**Solutions:**

1. **Process in smaller batches:**
   ```powershell
   python -m ada_annotator.cli \
       --input large_document.docx \
       --output output.docx \
       --max-images 50
   ```

2. **Close other applications**

3. **Monitor memory:**
   ```powershell
   # Windows Task Manager
   # Look for python.exe process
   ```

### High Token Usage / Costs

**Symptoms:**
- Unexpected high costs
- Large token counts in reports

**Analysis:**
```powershell
# Review token usage in report
cat output_report.md
# Look for "Resource Usage" section

# Typical ranges:
# - Simple images: 100-300 tokens
# - Complex images: 500-1000 tokens  
# - With context: +50-200 tokens
```

**Optimization:**

1. **Reduce context size:**
   - Trim context files to essentials
   - Remove verbose metadata

2. **Process selectively:**
   ```powershell
   # Only process images that need alt-text
   # Skip images with existing good alt-text
   ```

3. **Monitor costs:**
   ```powershell
   # Check Azure Cost Management
   # Set up budget alerts
   ```

---

## Testing and Development Issues

### Tests Failing

**Symptoms:**
- `pytest` tests fail
- Coverage below 80%

**Solutions:**

1. **Run specific test:**
   ```powershell
   pytest tests/unit/test_failing.py -v -s
   ```

2. **Check dependencies:**
   ```powershell
   uv pip install -e ".[dev]"
   ```

3. **Clear cache:**
   ```powershell
   pytest --cache-clear
   ```

4. **View coverage:**
   ```powershell
   pytest --cov=src/ada_annotator --cov-report=html
   # Open htmlcov/index.html
   ```

### Type Checking Errors

**Symptoms:**
- `mypy` errors
- Type incompatibility messages

**Solutions:**

1. **Run mypy:**
   ```powershell
   mypy src/ada_annotator
   ```

2. **Check type stubs:**
   ```powershell
   # Some packages need type stubs
   uv pip install types-Pillow types-python-docx
   ```

### Linting Errors

**Symptoms:**
- `ruff` check failures
- `black` formatting issues

**Solutions:**

1. **Auto-fix:**
   ```powershell
   ruff check src/ tests/ --fix
   black src/ tests/ --line-length 79
   ```

2. **Check specific rules:**
   ```powershell
   ruff check src/ --select E501  # Line too long
   ```

---

## Common Error Messages

### `FileError: Input file not found`

**Cause:** Specified input file doesn't exist

**Solution:**
```powershell
# Check file path
Test-Path document.docx

# Use absolute path
python -m ada_annotator.cli --input "C:\full\path\to\document.docx" --output output.docx
```

### `FileError: Unsupported file format`

**Cause:** File extension not .docx or .pptx

**Solution:**
```powershell
# Only DOCX and PPTX supported
# Convert other formats first
```

### `ValidationError: Alt-text too short`

**Cause:** Generated alt-text < 10 characters

**Context:** This is a validation warning, not a critical error. The alt-text is still applied.

**Solution:**
```powershell
# Check report for validation warnings
cat output_report.md

# Review and manually improve short descriptions
```

### `ProcessingError: Failed to extract images`

**Cause:** Document structure issue or corrupted file

**Solution:**
```powershell
# Try re-saving document
# Check with --dry-run first
python -m ada_annotator.cli --input document.docx --dry-run
```

### `APIError: Invalid authentication credentials`

**Cause:** Wrong API key or endpoint

**Solution:**
```powershell
# Verify .env configuration
cat .env

# Regenerate API key in Azure Portal
# Update .env with new key
```

---

## Getting Additional Help

If you're still experiencing issues after trying these solutions:

1. **Enable debug logging:**
   ```powershell
   python -m ada_annotator.cli \
       --input document.docx \
       --output output.docx \
       --log-level DEBUG
   ```

2. **Review structured logs:**
   ```powershell
   cat logs/ada-annotator.log | ConvertFrom-Json | Format-List
   ```

3. **Run tests to verify installation:**
   ```powershell
   pytest -v
   ```

4. **Check documentation:**
   - [README.md](../README.md)
   - [SETUP_GUIDE.md](../SETUP_GUIDE.md)
   - [docs/requirements.md](requirements.md)

5. **Report bugs:**
   - GitHub Issues (include logs and error messages)
   - Provide minimal reproducible example

---

**Document Version:** 1.0  
**Last Updated:** October 27, 2025  
**Project:** ADA Annotator Phase 1
