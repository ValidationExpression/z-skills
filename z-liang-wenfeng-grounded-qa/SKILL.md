---
name: liang-wenfeng-grounded-qa
description: Use when answering questions, generating interview questions, or summarizing viewpoints attributed to Liang Wenfeng based on the May 20 investor-meeting transcript supplied with this skill.
---

# Liang Wenfeng Grounded Q&A

## Purpose

Use the supplied transcript as the only authoritative source for Liang Wenfeng's views in this workflow. The goal is faithful source-grounded answering, not free-form impersonation.

## Source Files

- `references/topic-index.md`: read first to locate likely sections.
- `references/transcript-by-page.md`: authoritative searchable transcript with PDF page markers.
- `references/source-reliability.md`: source limitations and publication restrictions.
- `references/source.pdf`: original supplied PDF for verification.

## Required Workflow

1. Identify the exact claim or question being asked.
2. Search `references/topic-index.md` for relevant topics and synonyms.
3. Read the matching passages in `references/transcript-by-page.md`; do not rely on the index alone.
4. Classify the evidence:
   - **A — Explicit:** the transcript directly addresses the question.
   - **B — Limited inference:** the transcript gives relevant principles but does not address the named event, model, company, or date.
   - **C — Unsupported:** the transcript provides no reliable basis.
5. Answer according to the evidence class.
6. Include PDF page number and timestamp when available.
7. Before publishing or drafting public copy, apply the publication restrictions below.

## Answer Rules

### Evidence A — Explicit

- State the answer directly.
- Paraphrase by default; use short quotes only when wording matters.
- Cite as: `（PDF 第 X 页，约 HH:MM:SS）`.
- Preserve uncertainty words such as “可能”“我觉得”“我们的判断”.

### Evidence B — Limited inference

Begin with:

> 材料没有直接提到这一对象或事件。下面只能依据梁文锋在交流会中公开表达的判断标准作有限推断，不代表其本人对此事的最新观点。

Then separate:

- **原文依据**
- **有限推断**
- **仍无法确定的部分**

Never convert an inference into a direct quotation or first-person claim.

### Evidence C — Unsupported

Say clearly:

> 这份材料中没有足够信息回答，不能代替梁文锋补充观点。

Then optionally identify what new source would be needed.

## Roleplay Mode

When the user asks “现在你是梁文锋” or requests a first-person answer:

- Add once at the beginning: `以下是基于该交流会文字稿的模拟回答，不代表梁文锋本人最新观点。`
- Use first person only for Evidence A.
- For Evidence B or C, exit first-person voice and state the evidence limitation.
- Never claim access to private thoughts, current plans, or events after the recording date.

## Interview-Question Mode

When generating questions for journalists or creators:

- Prefer unresolved definitions, measurable standards, contradictions, timelines, and falsifiable claims.
- Avoid repeating broad questions already fully answered in the transcript.
- For each proposed question, explain briefly what new information it could elicit.
- Mark questions about later models or events as outside the transcript.

## Publication Restrictions

The moderator explicitly asked participants not to circulate sensitive figures or conditions, including card quantities, and not to record or share the meeting publicly.

For any public article, post, script, or media brief:

- Do not reproduce sensitive quantities concerning compute cards, procurement, financing, employee options, valuation, or other non-public operating details.
- Replace them with qualitative summaries such as “算力资源仍是主要瓶颈”.
- State that the transcript is an AI-assisted transcription and speaker attribution is inferred.
- Recommend verification against the original audio or an authorized source before publication.

For private research, the material may be searched, but still flag uncertain transcription and sensitive passages.

## Non-Negotiable Constraints

- Do not add web knowledge unless the user explicitly asks for an external comparison or update.
- Do not merge later news into Liang Wenfeng's views.
- Do not invent quotes, dates, model names, metrics, or company judgments.
- Do not silently correct suspected transcription errors; flag them.
- Do not treat speaker labels as fully verified.

## Output Templates

### Grounded Answer

```markdown
**结论：** ...

**原文依据：** ...（PDF 第 X 页，约 HH:MM:SS）

**边界：** ...
```

### Limited Inference

```markdown
材料没有直接提到这一对象或事件。下面只能依据梁文锋在交流会中表达的判断标准作有限推断，不代表其本人对此事的最新观点。

**原文依据：** ...

**有限推断：** ...

**无法确定：** ...
```

### Interview Questions

```markdown
1. **问题：** ...
   **为什么值得问：** ...
   **可追问：** ...
```

## Final Check

Before answering, verify:

- Did I locate and read the original passage?
- Did I distinguish direct evidence from inference?
- Did I preserve uncertainty and recording-date limits?
- Did I avoid restricted sensitive numbers in public-facing content?
- Did I provide page/time references where available?
