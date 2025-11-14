---
mode: agent
model: Claude Sonnet 4
---
<!-- markdownlint-disable-file -->
# Implementation Prompt: Code Coverage Improvement to 80%+

## Implementation Instructions

### Step 1: Create Changes Tracking File

You WILL create `20251114-code-coverage-improvement-changes.md` in #file:../changes/ if it does not exist.

### Step 2: Execute Implementation

You WILL follow #file:../../.github/instructions/task-implementation.instructions.md
You WILL systematically implement #file:../plans/20251114-code-coverage-improvement-plan.instructions.md task-by-task
You WILL follow ALL project standards and conventions from #file:../../.github/instructions/python.instructions.md

**Implementation Strategy:**

#### Phase 1: High-Impact Quick Wins (Target: 40% coverage)
Execute all Phase 1 tasks sequentially:
- Task 1.1: Expand Document Processor Tests (highest impact: +25%)
- Task 1.2: Expand Context Extractor Tests (+7%)
- Task 1.3: Expand Alt-Text Generator Tests (+5%)
- Task 1.4: Expand Utility Module Tests (+5%)

Run coverage check after each major task group and document progress.

#### Phase 2: Critical Infrastructure (Target: 60% coverage)
Execute all Phase 2 tasks sequentially:
- Task 2.1: Add Application Workflow Tests (+2%)
- Task 2.2: Expand CLI Command Tests (+15%)
- Task 2.3: Expand Semantic Kernel Service Tests (+3%)

Run coverage check after each task group and verify 60% target.

#### Phase 3: Edge Cases and Integration (Target: 80%+ coverage)
Execute all Phase 3 tasks sequentially:
- Task 3.1: Add Error Handling Tests (+5%)
- Task 3.2: Add Configuration Tests (+2%)
- Task 3.3: Create Integration Test Suite (+5%)
- Task 3.4: Add Debug Document Tests (+2%)
- Task 3.5: Final Coverage Validation

Run full coverage analysis and verify 80%+ target achieved.

**Testing Guidelines:**
- Follow AAA pattern (Arrange, Act, Assert)
- Use meaningful test names describing the scenario
- Mock external dependencies (AI services, file I/O where appropriate)
- Test both success and failure paths
- Include edge cases and boundary conditions
- Use fixtures for common test data
- Ensure tests are independent and repeatable

**CRITICAL**: If ${input:phaseStop:true} is true, you WILL stop after each Phase for user review.
**CRITICAL**: If ${input:taskStop:false} is true, you WILL stop after each Task for user review.

### Step 3: Cleanup

When ALL Phases are checked off (`[x]`) and completed you WILL do the following:
  1. You WILL provide a markdown style link and a summary of all changes from #file:../changes/20251114-code-coverage-improvement-changes.md to the user:
    - You WILL keep the overall summary brief
    - You WILL add spacing around any lists
    - You MUST wrap any reference to a file in a markdown style link
  2. You WILL provide markdown style links to .copilot-tracking/plans/20251114-code-coverage-improvement-plan.instructions.md, .copilot-tracking/details/20251114-code-coverage-improvement-details.md, and .copilot-tracking/research/20251114-code-coverage-improvement-plan.md documents. You WILL recommend cleaning these files up as well.
  3. **MANDATORY**: You WILL attempt to delete .copilot-tracking/prompts/implement-code-coverage-improvement.prompt.md

## Success Criteria

- [ ] Changes tracking file created
- [ ] Phase 1 completed: 40%+ coverage achieved
- [ ] Phase 2 completed: 60%+ coverage achieved
- [ ] Phase 3 completed: 80%+ coverage achieved
- [ ] All plan items implemented with working tests
- [ ] All tests pass in test suite
- [ ] Coverage reports generated and verified
- [ ] Project conventions followed
- [ ] Changes file updated continuously with test additions
