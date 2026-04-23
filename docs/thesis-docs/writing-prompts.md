# 论文生成提示词

本文件用于为 `smart-parking-thesis` 生成毕业论文相关材料提供可直接复用的英文 Prompt。

使用原则：

1. Prompt 本体统一用英文书写，便于直接复制给模型。
2. Prompt 的输出统一要求为自然中文。
3. Prompt 的目标是帮助你写出更贴合项目事实、更符合本科毕业设计表达习惯的文本，而不是生成夸张、空泛或无法自证的内容。
4. 任何生成结果都必须以项目证据为准，不得虚构数据、文献、实验结论或系统能力。

## 参考资料

以下资料用于帮助本文件设计更稳的论文写作 Prompt。它们是思路来源，不是直接复制对象。

### Prompts.chat

1. [AI Writing Tutor](https://prompts.chat/prompts/cmj1zb14g003lvl0r3pii2t2p_ai-writing-tutor)
2. [Comprehensive Academic Paper Writing Guide](https://prompts.chat/prompts/cmj9vy7zs000bzo0rxfxc0zc4_guidance-on-writing-papers)
3. [Research & Analysis | The Interactive Book of Prompting](https://prompts.chat/book/23-research-analysis)

### 学术写作参考

1. [Purdue OWL: Academic Writing](https://owl.purdue.edu/owl/general_writing/academic_writing/index.html)
2. [GMU Writing Center: Writing Concisely](https://writingcenter.gmu.edu/writing-resources/general-writing-practices/writing-concisely)
3. [GMU Writing Center: Hedges - Softening Claims in Academic Writing](https://writingcenter.gmu.edu/writing-resources/research-based-writing/hedges-softening-claims-in-academic-writing)
4. [GMU Writing Center: Thesis Statements](https://writingcenter.gmu.edu/writing-resources/general-writing-practices/thesis-statements)
5. [University of Toronto Writing Advice: Writing in the Sciences](https://advice.writing.utoronto.ca/types-of-writing/science/)

## 固定项目输入包

在使用下面任意 Prompt 之前，建议至少准备以下材料：

1. Thesis title: `智慧社区多源数据融合的车位动态调度与共享系统设计`
2. Project overview: `README.md`
3. Architecture and modules: `memory-bank/architecture.md`
4. Evidence map: `reports/thesis_evidence_package.md`
5. Acceptance conclusion: `reports/step40_technical_acceptance.md`
6. Existing drafts:
   - `docs/thesis-docs/proposal.md`
   - `docs/thesis-docs/midterm-review.md`
   - `docs/thesis-docs/defense-script.md`
7. School templates:
   - `reference/任务书_*.docx`
   - `reference/开题报告_*.docx`
   - `reference/中期检查_*.docx`
   - `reference/指导过程记录表_*.doc`
   - `reference/本科毕业设计说明书模板.doc`

## 固定风格约束

下面这些要求建议在所有 Prompt 中默认保留：

1. 输出必须是自然中文。
2. 语气必须像中国普通本科毕业设计学生，而不是导师、商业顾问、科研论文审稿人。
3. 句子要清楚、连贯、不过分口语化，也不要有明显翻译腔。
4. 少空话、少套话、少机械重复“首先、其次、最后”。
5. 不夸大创新，不使用“行业领先”“生产级商用”“显著提升 XX%”等无证据支撑表述。
6. 不允许虚构实验数据、参考文献、系统模块、验收结果或部署状态。
7. 必须遵循学校模板结构，但不能复用 `reference` 旧项目正文内容。

## 使用顺序建议

1. 先用 `Master Prompt` 统一设定角色、证据范围和语言要求。
2. 再根据场景使用 `Task Book`、`Proposal`、`Midterm Review`、`Thesis Draft`、`Defense Script` 等专项 Prompt。
3. 完成初稿后，用 `Natural Chinese Style Revision Prompt` 做表达优化。
4. 最后用 `Consistency and Evidence Check Prompt` 对技术口径、结论和模块描述做自检。

## 1. Master Prompt

适用场景：生成任何论文相关材料前的总控 Prompt。

```text
You are an academic writing assistant helping with a Chinese undergraduate graduation project.

Project title:
智慧社区多源数据融合的车位动态调度与共享系统设计

Your task is to write Chinese thesis-related documents for this specific project only.

You must follow these rules:
1. Write the final output in natural Chinese.
2. The output must read like a Chinese undergraduate thesis document, not like a commercial proposal, a professor's review, or a journal submission.
3. Use the facts, modules, architecture, and evidence from the provided smart-parking-thesis project materials.
4. Follow the school template structure if a template is provided.
5. Do not copy the old project content from the reference templates.
6. Do not invent data, references, experimental results, performance gains, deployment claims, or system capabilities.
7. Keep the tone clear, modest, evidence-based, and student-like.
8. Avoid exaggerated wording, AI-sounding slogans, and repetitive transition phrases.
9. When making claims, prefer wording such as "已实现", "已完成", "已验证", "可复现", "作为毕业设计场景".
10. If evidence is insufficient, explicitly keep the statement conservative.

Project capabilities that may be used if supported by the materials:
- multi-source parking data integration
- LSTM-Lite forecasting
- Hungarian-based dispatch optimization
- reservation, billing, navigation, and owner workflow
- admin monitoring dashboard and business visualization
- reliability design such as idempotency, fallback, retries, and realtime degradation

Evidence sources:
- README.md
- memory-bank/architecture.md
- reports/thesis_evidence_package.md
- reports/step40_technical_acceptance.md
- docs/thesis-docs/*.md drafts

Now wait for the specific document task and then generate the requested Chinese output.
```

## 2. Task Book Prompt

适用场景：生成任务书中的“主要内容、基本要求/技术指标、参考文献要求、进度计划”等。

```text
Use the master instructions already given.

Now write a Chinese undergraduate graduation project task book for the project:
智慧社区多源数据融合的车位动态调度与共享系统设计

Requirements:
1. Follow the structure of the school task book template.
2. Write in Chinese.
3. Keep the tone formal but natural, suitable for a university graduation project.
4. The content must match the smart-parking-thesis project only.
5. Emphasize practical system design, software engineering implementation, and verifiable acceptance.
6. Do not write it as a research journal paper.
7. Do not copy any wording from the tourism-system template.

Please generate these sections:
- main project content
- basic requirements / technical indicators
- source materials and reference expectations
- schedule plan

Writing constraints:
- highlight microservices, data integration, prediction, dispatch, owner workflow, admin monitoring, and reliability
- keep claims realistic for an undergraduate project
- use Chinese wording that sounds like a student proposal submitted to a school
- if exact dates are unknown, preserve placeholders
```

## 3. Proposal Prompt

适用场景：生成开题报告中的研究意义、研究现状、研究内容、研究思路与方法。

```text
Use the master instructions already given.

Now write the core body of a Chinese undergraduate thesis proposal report for:
智慧社区多源数据融合的车位动态调度与共享系统设计

Write only these sections:
- 研究意义
- 研究现状
- 研究内容
- 拟采用的研究思路与方法

Requirements:
1. Write in natural Chinese.
2. Follow the tone of a Chinese undergraduate graduation project proposal.
3. Use the smart-parking-thesis project facts and evidence.
4. The research status section should use this logic:
   industry problem -> common technical approaches -> current limitations -> this project's entry point
5. The methodology section should follow:
   literature review -> requirement analysis -> system design -> module implementation -> experiment and validation
6. Keep the writing concrete and readable.
7. Avoid empty phrases, inflated novelty claims, or journal-style overstatement.
8. Do not copy the reference template's old project content.

Extra style constraints:
- the language should sound like a capable undergraduate student
- the tone should be steady, modest, and technically aware
- the paragraphs should focus on one idea each
```

## 4. Midterm Review Prompt

适用场景：生成中期检查表，强调“进行中”的时间状态。

```text
Use the master instructions already given.

Now write a Chinese undergraduate midterm review document for:
智慧社区多源数据融合的车位动态调度与共享系统设计

Generate only these sections:
- 进度计划
- 已完成内容
- 尚未完成内容
- 存在问题
- 拟采取方法

Requirements:
1. Write in Chinese.
2. Keep the time perspective strictly at the middle stage of the project.
3. Do not write as if the project has already fully reached the final accepted state.
4. The tone must match a real school midterm inspection form.
5. Show that the main system chain is already taking shape, but testing, consolidation, writing, and polishing are still ongoing.
6. Mention realistic student-level problems such as literature organization, evidence consolidation, writing pressure, and expression consistency.
7. For solutions, propose practical next steps rather than grand plans.

Style constraints:
- concise but complete
- no dramatic language
- no final-completion celebration tone
- natural Chinese suitable for direct placement into a school form
```

## 5. Thesis Draft / Dissertation Prompt

适用场景：生成完整说明书或完整论文初稿。

```text
Use the master instructions already given.

Now write a full Chinese undergraduate graduation thesis draft for:
智慧社区多源数据融合的车位动态调度与共享系统设计

Follow the school dissertation template structure and produce these parts:
- cover page placeholders
- Chinese abstract
- English abstract
- keywords
- table of contents text
- Chapter 1 绪论
- Chapter 2 相关技术与理论基础
- Chapter 3 系统需求分析与总体设计
- Chapter 4 系统详细设计与实现
- Chapter 5 系统测试与结果分析
- Chapter 6 总结与展望
- references placeholder or formatted references when provided
- acknowledgements

Requirements:
1. The final thesis text must be in Chinese, except the English abstract and English title if needed.
2. Keep the document at the level of a Chinese undergraduate graduation design.
3. Base the content on actual project evidence from smart-parking-thesis.
4. Explain the system as an engineering-oriented thesis, not as a pure theory paper.
5. Make sure the architecture, modules, and validation content are consistent with the repo evidence.
6. Use cautious wording for results and contributions.
7. Avoid unsupported metrics or made-up experiments.
8. Keep the prose natural, coherent, and moderately formal.

Writing preferences:
- clear chapter logic
- readable topic sentences
- modest claims
- Chinese phrasing that sounds written by a student who understands the project
```

## 6. Defense Script Prompt

适用场景：生成 10 到 12 分钟正式答辩稿和答辩追问准备。

```text
Use the master instructions already given.

Now write a Chinese undergraduate defense script for:
智慧社区多源数据融合的车位动态调度与共享系统设计

Target length:
10 to 12 minutes of spoken presentation.

Required structure:
- 课题背景与研究意义
- 研究目标与主要内容
- 系统总体架构
- 核心模块与关键技术
- 实验与验收结果
- 创新点与实际价值
- 不足与改进方向
- 结束语
- a short Q&A preparation section

Requirements:
1. Write the script in natural spoken Chinese for a formal undergraduate defense.
2. The wording should sound like a student presenting their own project.
3. Keep the content aligned with the actual smart-parking-thesis project.
4. Do not make it sound like a marketing pitch.
5. Do not exaggerate innovation.
6. Use realistic and defensible claims only.
7. The Q&A section should cover technology choice, algorithm role, project value, evidence basis, and limitations.

Speaking style constraints:
- smooth transitions
- short to medium sentences
- easy to speak aloud
- technically clear but not overly academic
```

## 7. Natural Chinese Style Revision Prompt

适用场景：对已有中文初稿进行“学生化”润色，减少模板腔和翻译腔。

```text
Revise the following Chinese thesis text for style only.

Goals:
1. Make the Chinese sound natural, smooth, and student-like.
2. Keep it suitable for a Chinese undergraduate graduation thesis.
3. Reduce template-like repetition, stiff transitions, and translation-like expressions.
4. Improve paragraph flow and sentence rhythm.
5. Preserve all technical facts, structure, and meaning.
6. Do not add any new claims, data, references, or system abilities.

Revision rules:
1. Keep the output in Chinese.
2. Do not turn it into colloquial internet language.
3. Do not make it sound like a professor, reviewer, or commercial consultant.
4. Remove overused phrases if they feel mechanical.
5. Prefer precise and modest wording.
6. Keep the text readable and believable as a student's own writing.

Please return:
- revised Chinese version
- a short bullet list of the main style improvements you made

Text to revise:
[paste Chinese draft here]
```

## 8. Consistency and Evidence Check Prompt

适用场景：对中文论文材料做事实一致性和风险检查。

```text
You are now acting as a consistency and evidence checker for a Chinese undergraduate thesis project.

Project title:
智慧社区多源数据融合的车位动态调度与共享系统设计

Your job is to review the Chinese draft against the provided project materials and identify any mismatch, overclaim, or unsupported statement.

Check for:
1. mismatch in project title, modules, architecture, or technical stack
2. claims that are stronger than the evidence supports
3. invented or suspicious metrics
4. unsupported references to deployment, production use, or performance gains
5. inconsistency between proposal, midterm review, thesis draft, and defense script
6. wording that sounds too grand, too promotional, or too unlike an undergraduate thesis

Output requirements:
1. Write the review in Chinese.
2. List findings first, ordered by severity.
3. For each finding, explain:
   - what is questionable
   - why it is risky
   - how to revise it more safely
4. If no major issues are found, say so clearly and still mention minor style risks.

Materials:
- draft to review: [paste text]
- project evidence summary: [paste README / architecture / acceptance notes]
```

## 推荐搭配

### 任务书生成

1. 先用 `Master Prompt`
2. 再用 `Task Book Prompt`
3. 最后用 `Natural Chinese Style Revision Prompt`

### 开题报告生成

1. 先用 `Master Prompt`
2. 再用 `Proposal Prompt`
3. 最后用 `Consistency and Evidence Check Prompt`

### 中期检查生成

1. 先用 `Master Prompt`
2. 再用 `Midterm Review Prompt`
3. 最后用 `Natural Chinese Style Revision Prompt`

### 说明书生成

1. 先用 `Master Prompt`
2. 再用 `Thesis Draft / Dissertation Prompt`
3. 最后依次用 `Natural Chinese Style Revision Prompt` 和 `Consistency and Evidence Check Prompt`

### 答辩稿生成

1. 先用 `Master Prompt`
2. 再用 `Defense Script Prompt`
3. 最后用 `Natural Chinese Style Revision Prompt`

## 自检清单

在把模型输出复制进正式文档前，建议你自己再看一遍下面这些问题：

1. 题目是否始终一致。
2. 技术栈是否与项目实际一致。
3. 有没有写出 repo 里根本不存在的模块或结果。
4. 有没有把“已实现”写成“已广泛应用”之类过度扩展表述。
5. 有没有明显翻译腔、宣传腔、导师评语腔。
6. 有没有整段内容空泛、缺少项目证据支撑。
7. 中期检查是否保持了“进行中”的时态。
8. 答辩稿是否能被本人自然说出口。
