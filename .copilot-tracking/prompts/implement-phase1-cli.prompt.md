---
mode: agent
model: Claude Sonnet 4
---
<!-- markdownlint-disable-file -->
# Implementation Prompt: Phase 1 CLI Implementation

## Implementation Instructions

### Step 1: Create Changes Tracking File

You WILL create `20251018-phase1-cli-implementation-changes.md` in #file:../changes/ if it does not exist.

### Step 2: Execute Implementation

You WILL follow #file:../../.github/instructions/task-implementation.instructions.md
You WILL systematically implement #file:../plans/20251018-phase1-cli-implementation-plan.instructions.md task-by-task
You WILL follow ALL project standards and conventions

**CRITICAL**: If ${input:phaseStop:true} is true, you WILL stop after each Phase for user review.
**CRITICAL**: If ${input:taskStop:false} is true, you WILL stop after each Task for user review.

### Implementation Guidelines

**Test-Driven Development (TDD)**:
- You WILL write tests BEFORE implementing each module
- You WILL run tests after each implementation
- You WILL ensure >80% code coverage

**Code Quality Standards**:
- You WILL follow #file:../../.github/instructions/python.instructions.md
- You WILL include type hints on all functions
- You WILL write PEP 257 docstrings for all modules, classes, and functions
- You WILL maintain 79-character line limit
- You WILL use 4-space indentation

**Error Handling**:
- You WILL handle all edge cases documented in requirements
- You WILL provide clear error messages
- You WILL log all errors with structured logging
- You WILL continue processing after non-fatal errors

**Dependencies Between Phases**:
- Phase 1.1 (Infrastructure) MUST be completed first
- Phase 1.2 (CLI) depends on Phase 1.1
- Phase 1.3-1.4 (Extractors) can be parallel after Phase 1.1
- Phase 1.5 (Context) depends on Phase 1.1
- Phase 1.6-1.7 (AI Integration) depends on Phase 1.1
- Phase 1.8 (Validation) can be parallel with Phase 1.6-1.7
- Phase 1.9-1.10 (Output) depends on Phase 1.3-1.4
- Phase 1.11 (Reporting) depends on all previous phases
- Phase 1.12 (Testing) runs throughout implementation
- Phase 1.13 (Documentation) runs at the end

**Integration Points**:
- All modules MUST use structured logging from Phase 1.1
- All modules MUST use Pydantic models from Phase 1.1
- Document extractors MUST return ImageMetadata objects
- Context extractor MUST return ContextData objects
- AI service MUST accept ContextData and ImageMetadata
- Validators MUST return AltTextResult objects
- Assemblers MUST accept AltTextResult objects

### Step 3: Testing After Each Phase

After completing each Phase, you WILL:
1. Run all unit tests for that phase: `pytest tests/unit/test_*.py -v`
2. Check test coverage: `pytest --cov=src/ada_annotator --cov-report=term-missing`
3. Verify coverage is increasing toward >80% goal
4. Fix any failing tests before proceeding
5. Update changes file with test results

### Step 4: Validation Checkpoints

At these checkpoints, you WILL validate implementation quality:

**After Phase 1.1 (Infrastructure)**:
- Verify structured logging writes JSON to file
- Verify all Pydantic models validate correctly
- Verify error handling framework works
- Run: `pytest tests/unit/test_models.py tests/unit/test_logging.py -v`

**After Phase 1.4 (Extractors)**:
- Verify DOCX extraction with test documents
- Verify PPTX extraction with test documents
- Check position metadata is captured
- Run: `pytest tests/unit/test_docx_extractor.py tests/unit/test_pptx_extractor.py -v`

**After Phase 1.7 (AI Integration)**:
- Verify Semantic Kernel initializes successfully
- Test alt-text generation with sample image
- Verify token tracking works
- Run: `pytest tests/unit/test_ai_service.py -v`

**After Phase 1.10 (Output)**:
- Verify DOCX output preserves positions
- Verify PPTX output preserves positions
- Check alt-text is applied correctly
- Run integration test with complete workflow

**After Phase 1.12 (Testing)**:
- Verify >80% test coverage achieved
- All tests passing
- Run: `pytest --cov=src/ada_annotator --cov-report=html`
- Open `htmlcov/index.html` to review coverage

### Step 5: Cleanup

When ALL Phases are checked off (`[x]`) and completed you WILL do the following:

1. You WILL provide a markdown style link and a summary of all changes from #file:../changes/20251018-phase1-cli-implementation-changes.md to the user:
   - You WILL keep the overall summary brief
   - You WILL add spacing around any lists
   - You MUST wrap any reference to a file in a markdown style link

2. You WILL run final validation:
   - `pytest --cov=src/ada_annotator --cov-report=term-missing`
   - Verify >80% coverage
   - Verify all tests pass
   - Run type checking: `mypy src/ada_annotator`
   - Run linting: `ruff check src/ada_annotator`
   - Run formatting check: `black --check src/ada_annotator`

3. You WILL provide markdown style links to:
   - [`.copilot-tracking/plans/20251018-phase1-cli-implementation-plan.instructions.md`](.copilot-tracking/plans/20251018-phase1-cli-implementation-plan.instructions.md)
   - [`.copilot-tracking/details/20251018-phase1-cli-implementation-details.md`](.copilot-tracking/details/20251018-phase1-cli-implementation-details.md)
   - [`.copilot-tracking/research/20251018-ada-annotator-implementation-research.md`](.copilot-tracking/research/20251018-ada-annotator-implementation-research.md)
   
4. You WILL recommend cleaning these files up as well.

5. **MANDATORY**: You WILL attempt to delete `.copilot-tracking/prompts/implement-phase1-cli.prompt.md`

## Success Criteria

- [ ] Changes tracking file created and updated continuously
- [ ] All 13 phases completed with all tasks checked off
- [ ] All plan items implemented with working code
- [ ] All detailed specifications satisfied
- [ ] Test coverage >80% for all modules
- [ ] All pytest tests passing (unit + integration)
- [ ] Type checking passes (mypy)
- [ ] Linting passes (ruff)
- [ ] Formatting passes (black)
- [ ] Project conventions followed (#file:../../.github/instructions/python.instructions.md)
- [ ] Changes file comprehensive and accurate
- [ ] Documentation complete (README, SETUP_GUIDE, inline docs)
- [ ] CLI fully functional with all arguments
- [ ] DOCX and PPTX processing working end-to-end
- [ ] Alt-text generation using Semantic Kernel + Azure OpenAI
- [ ] Position preservation verified
- [ ] Error handling tested with edge cases
- [ ] Markdown reports generated correctly

## Quality Gates

Before marking this task complete, verify:

1. **Functionality**: Run CLI with sample documents and verify output
   ```powershell
   python -m ada_annotator.cli --input tests/fixtures/documents/sample.docx --output output.docx --log-level INFO
   ```

2. **Testing**: All tests pass with >80% coverage
   ```powershell
   pytest --cov=src/ada_annotator --cov-report=term-missing --cov-fail-under=80
   ```

3. **Code Quality**: Type checking and linting pass
   ```powershell
   mypy src/ada_annotator
   ruff check src/ada_annotator
   black --check src/ada_annotator
   ```

4. **Documentation**: README and SETUP_GUIDE are complete and accurate

5. **Integration**: End-to-end workflow works with real Azure OpenAI API

## Notes for Implementation

- Start with Phase 1.1 (Infrastructure) - it's foundational
- Use TDD approach: write tests first, then implementation
- Commit after each completed phase
- Update changes file continuously, not at the end
- Test with real Azure OpenAI API early (don't wait until the end)
- Create sample test documents that represent real use cases
- Focus on error handling - many edge cases to cover
- Keep modules small and focused (single responsibility)
- Use type hints everywhere - helps catch bugs early
- Structure logging from the start - easier than adding later
