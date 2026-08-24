## Context

Repository rules require Chinese-first prose, English technical terms, bilingual H2/H3 headings, pure-English H1 headings, and ASCII punctuation. Commands and configuration have already passed syntax and argv validation.

## Goals / Non-Goals

**Goals:**

- Normalize human-readable prose without changing decisions or commands.
- Keep `SKILL.md` concise and references progressively disclosed by mode.
- Detect remaining language inconsistency, duplicated guidance, and contradictions through a second skill-creator review.

**Non-Goals:**

- Translate variable names, YAML keys, state enums, command output, or OpenSpec normative requirements.
- Add files, alter runtime VM data, or run live KVM checks.

## Decisions

1. Frontmatter description remains concise English because it participates in automatic skill selection.
2. H1 remains English; H2/H3 use English followed by Chinese.
3. Explanatory prose uses Simplified Chinese; product/tool names and code identifiers remain English.
4. Shell code blocks are byte-preserved except surrounding prose; any accidental command change fails the existing syntax/argv validation.

## Risks / Trade-offs

- [Over-translation can obscure standard terms] -> Keep recognized technical nouns and all identifiers in English.
- [Mechanical rewriting can alter command semantics] -> Compare command blocks and rerun syntax/argv checks.
