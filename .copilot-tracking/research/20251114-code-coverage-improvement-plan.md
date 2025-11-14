<!-- markdownlint-disable-file -->
# Task Research Notes: Code Coverage Improvement to 80%+

## Research Executed

### Coverage Analysis
- Analyzed `coverage.xml` and `htmlcov/index.html`
  - **Current Coverage**: 23% (419 of 1,828 lines covered)
  - **Target Coverage**: 80% (1,462 lines need to be covered)
  - **Gap**: 1,043 additional lines need test coverage

### File Coverage Assessment
- Reviewed individual file coverage from coverage report
  - Files with 0% coverage: `app.py`, `debug_document.py`
  - Files with low coverage (<20%): CLI modules, document processors, generators, utilities
  - Files with good coverage (>80%): Models, exceptions
  - Files with 100% coverage: `__init__.py` files, some model files

### Existing Test Structure
- Reviewed `tests/` directory structure
  - Unit tests exist for: alt_text_generator, cli, context_extractor, document processors, error handlers, image utils, json handler, models, retry handler, semantic kernel service
  - Integration tests directory exists but is empty
  - Test fixtures directory contains sample documents

### Project Configuration
- Reviewed `pyproject.toml`
  - Test framework: pytest with pytest-cov
  - Coverage configuration includes XML and HTML reports
  - Async testing with pytest-asyncio
  - Mocking with pytest-mock

## Key Discoveries

### Coverage Gaps by Module

#### Critical Gaps (0-20% coverage)
1. **CLI Module (`cli.py`)** - 9% coverage
   - 316 of 346 lines uncovered
   - Main entry point and command processing
   - File validation and path handling
   - Multiple commands: extract, generate, validate, assemble

2. **Application Module (`app.py`)** - 0% coverage
   - 31 of 31 lines uncovered
   - Core application workflow orchestration
   - Document processing pipeline

3. **Document Processors** - 14-19% coverage
   - DOCX Assembler: 15% (79/93 lines uncovered)
   - DOCX Extractor: 14% (92/107 lines uncovered)
   - PPTX Assembler: 19% (73/90 lines uncovered)
   - PPTX Extractor: 18% (75/91 lines uncovered)
   - PDF Extractor: 17% (60/72 lines uncovered)

4. **Alt-Text Generator** - 18% coverage
   - 114 of 139 lines uncovered
   - Core AI generation logic
   - Batch processing
   - Cost calculation

5. **Context Extractor** - 11% coverage
   - 137 of 154 lines uncovered
   - Document context extraction
   - Multi-level context gathering

6. **Utility Modules** - 12-36% coverage
   - Image Utils: 12% (72/82 lines)
   - JSON Handler: 18% (50/61 lines)
   - Report Generator: 16% (58/69 lines)
   - Logging: 32% (21/31 lines)
   - Error Handler: 27% (30/41 lines)

7. **Semantic Kernel Service** - 28% coverage
   - 54 of 75 lines uncovered
   - AI service integration
   - Azure OpenAI communication

8. **Debug Document** - 0% coverage
   - 43 of 43 lines uncovered
   - PDF debugging functionality

#### Good Coverage (>80%)
- **Models**: 83-100% coverage
- **Exceptions**: 88% coverage
- **__init__.py** files: 100% coverage

### Test Patterns Identified

#### Existing Test Quality
- Good unit test structure with clear class organization
- Proper use of fixtures and mocks
- Async test support for async functions
- Parametrized tests in some modules
- Edge case testing (empty inputs, invalid data)

#### Missing Test Coverage Areas
1. **Integration Tests**: Empty integration test directory
2. **CLI End-to-End**: Commands not tested in realistic scenarios
3. **Document Processing Workflows**: Full extraction/assembly cycles untested
4. **Error Recovery**: Exception handling paths largely untested
5. **AI Service Integration**: Mocked but not integration tested
6. **File I/O Operations**: Real file operations minimally tested

## Recommended Approach

### Phase 1: High-Impact Quick Wins (Target: 40% coverage)

Focus on modules with existing test infrastructure that need expansion.

#### 1.1 Expand Document Processor Tests
- **Target Files**: `docx_extractor.py`, `docx_assembler.py`, `pptx_extractor.py`, `pptx_assembler.py`, `pdf_extractor.py`
- **Current**: 14-19% coverage
- **Actions**:
  - Test complete extraction workflows with real documents
  - Test edge cases: empty documents, corrupted files, missing images
  - Test assembler with various alt-text scenarios
  - Test error handling and recovery paths
  - Add tests for helper methods currently untested

#### 1.2 Expand Context Extractor Tests
- **Target File**: `context_extractor.py`
- **Current**: 11% coverage
- **Actions**:
  - Test all context extraction methods (document, section, page, local)
  - Test context merging and truncation
  - Test with various document types and structures
  - Test error scenarios (missing metadata, invalid structure)

#### 1.3 Expand Alt-Text Generator Tests
- **Target File**: `alt_text_generator.py`
- **Current**: 18% coverage
- **Actions**:
  - Test batch processing methods
  - Test error handling and retry logic
  - Test cost calculation for various scenarios
  - Test validation with edge cases
  - Add integration-style tests with mock AI service

#### 1.4 Expand Utility Module Tests
- **Target Files**: `image_utils.py`, `json_handler.py`, `report_generator.py`
- **Current**: 12-18% coverage
- **Actions**:
  - Test image processing functions
  - Test JSON serialization/deserialization edge cases
  - Test report generation with various data scenarios
  - Test file I/O error handling

### Phase 2: Critical Infrastructure (Target: 60% coverage)

#### 2.1 Application Workflow Tests
- **Target File**: `app.py`
- **Current**: 0% coverage
- **Actions**:
  - Create integration-style tests for complete workflows
  - Test extract → generate → assemble pipeline
  - Test error propagation through workflow
  - Test with real document samples from fixtures

#### 2.2 CLI Command Tests
- **Target File**: `cli.py`
- **Current**: 9% coverage
- **Actions**:
  - Test each CLI command with realistic arguments
  - Test file validation logic
  - Test output path generation
  - Test error handling and user feedback
  - Test argument parsing edge cases
  - Add integration tests that run commands end-to-end

#### 2.3 Semantic Kernel Service Tests
- **Target File**: `semantic_kernel_service.py`
- **Current**: 28% coverage
- **Actions**:
  - Test service initialization with various configurations
  - Test prompt construction
  - Test response parsing
  - Test error handling (API errors, timeouts, invalid responses)
  - Test retry logic

### Phase 3: Edge Cases and Integration (Target: 80%+ coverage)

#### 3.1 Error Handling Paths
- **Target Files**: `error_handler.py`, `retry_handler.py`, `error_tracker.py`
- **Actions**:
  - Test all error scenarios
  - Test retry mechanisms with various failure modes
  - Test error tracking and reporting
  - Test error recovery workflows

#### 3.2 Logging and Monitoring
- **Target File**: `logging.py`
- **Current**: 32% coverage
- **Actions**:
  - Test logger configuration
  - Test log output formatting
  - Test log levels and filtering
  - Test structured logging

#### 3.3 Configuration Management
- **Target File**: `config.py`
- **Current**: 69% coverage
- **Actions**:
  - Test environment variable loading
  - Test configuration validation
  - Test default values
  - Test invalid configuration handling

#### 3.4 Integration Test Suite
- **Target Directory**: `tests/integration/`
- **Actions**:
  - Create end-to-end workflow tests
  - Test with real Azure OpenAI (in CI with credentials)
  - Test complete document processing pipelines
  - Test error scenarios across module boundaries

#### 3.5 Debug Document Module
- **Target File**: `debug_document.py`
- **Current**: 0% coverage
- **Actions**:
  - Test PDF debugging functionality
  - Test output generation
  - Test with various document types

## Implementation Guidance

### Objectives
1. Achieve 80%+ code coverage across the project
2. Improve test quality and maintainability
3. Catch bugs and edge cases before production
4. Enable confident refactoring

### Key Tasks

#### Task 1: Expand Document Processor Tests
- Files to modify: `tests/unit/test_docx_extractor.py`, `test_docx_assembler.py`, `test_pptx_extractor.py`, `test_pptx_assembler.py`, `test_pdf_extractor.py`
- Add comprehensive test cases for all methods
- Use fixtures from `tests/fixtures/` for real documents
- Estimated impact: +25% coverage

#### Task 2: Expand Context Extractor Tests
- File to modify: `tests/unit/test_context_extractor.py`
- Test all context extraction methods
- Add edge case tests
- Estimated impact: +7% coverage

#### Task 3: Expand Alt-Text Generator Tests
- File to modify: `tests/unit/test_alt_text_generator.py`
- Test batch processing and error handling
- Add integration-style tests with mocked AI
- Estimated impact: +5% coverage

#### Task 4: Expand Utility Tests
- Files to modify: `tests/unit/test_image_utils.py`, `test_json_handler.py`, `test_report_generator.py`
- Add missing test cases
- Test error scenarios
- Estimated impact: +5% coverage

#### Task 5: Add Application Workflow Tests
- File to create/modify: `tests/unit/test_app.py` or `tests/integration/test_workflow.py`
- Test complete workflows
- Mock external dependencies
- Estimated impact: +2% coverage

#### Task 6: Expand CLI Tests
- File to modify: `tests/unit/test_cli.py`
- Test all commands and their options
- Add integration tests for CLI commands
- Estimated impact: +15% coverage

#### Task 7: Expand Service Tests
- File to modify: `tests/unit/test_semantic_kernel_service.py`
- Test all service methods
- Test error handling
- Estimated impact: +3% coverage

#### Task 8: Add Integration Tests
- Directory: `tests/integration/`
- Create end-to-end workflow tests
- Test with real dependencies (where possible)
- Estimated impact: +5% coverage

#### Task 9: Error Handling and Edge Cases
- Files to modify: Various test files
- Add error scenario tests
- Test boundary conditions
- Estimated impact: +10% coverage

### Dependencies
- pytest, pytest-cov, pytest-asyncio, pytest-mock (already installed)
- Sample documents in `tests/fixtures/`
- Mock configurations for Azure OpenAI

### Success Criteria
- Overall coverage reaches 80% or higher
- All critical paths have test coverage
- Error handling paths are tested
- No untested public methods in core modules
- Integration tests cover main workflows
- CI pipeline runs all tests successfully

### Testing Strategy

#### Unit Test Priorities
1. **Critical Business Logic**: Alt-text generation, validation, context extraction
2. **Document Processing**: Extract and assemble operations for all formats
3. **Error Handling**: All exception paths and recovery mechanisms
4. **Utilities**: Image processing, JSON handling, report generation

#### Integration Test Priorities
1. **End-to-End Workflows**: Complete document processing pipelines
2. **CLI Commands**: Real command execution with file I/O
3. **Error Propagation**: Cross-module error handling

#### Test Quality Guidelines
- Each test should be independent and repeatable
- Use meaningful test names that describe the scenario
- Follow AAA pattern: Arrange, Act, Assert
- Mock external dependencies (AI services, file I/O where appropriate)
- Use fixtures for common test data
- Test both success and failure paths
- Include edge cases and boundary conditions

### Execution Plan

#### Week 1: Quick Wins (Target: 40%)
- Days 1-2: Expand document processor tests
- Days 3-4: Expand context extractor and alt-text generator tests
- Day 5: Expand utility tests and measure progress

#### Week 2: Critical Infrastructure (Target: 60%)
- Days 1-2: Add application workflow tests
- Days 3-4: Expand CLI tests
- Day 5: Expand service tests and measure progress

#### Week 3: Complete Coverage (Target: 80%+)
- Days 1-2: Add integration tests
- Days 3-4: Error handling and edge case tests
- Day 5: Final coverage validation and documentation

### Monitoring Progress
- Run `pytest --cov=ada_annotator --cov-report=term-missing` after each phase
- Review `htmlcov/index.html` to identify remaining gaps
- Track coverage percentage in CI/CD pipeline
- Aim for incremental improvements (17% → 40% → 60% → 80%)

### Notes
- Focus on high-value tests that catch real bugs
- Avoid testing trivial code (getters/setters, simple property access)
- Prioritize testing business logic and error handling
- Integration tests are valuable but shouldn't replace unit tests
- Maintain test quality over quantity
