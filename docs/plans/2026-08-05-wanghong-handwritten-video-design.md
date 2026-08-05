# 王虹学术手写动画视频 Skill 设计

## 目标

新增独立 Skill `z-wanghong-handwritten-video`，把文章、讲稿或技术主题整理为 16:9 纯画面手写动画，并输出无音轨的 H.264 MP4。原有 `z-wanghong-handwritten-ppt` 继续负责 HTML 幻灯片和逐页 PNG。

## 方案选择

采用 Remotion 数据驱动模板。相比对静态 PNG 做缩放和转场，这条路线可以逐字、逐项和逐路径控制手写动画；相比录制浏览器播放，逐帧渲染更稳定，也便于自动测试和复现。

## 架构

- `SKILL.md`：触发条件、内容拆分、视觉和动效规则、执行与验收流程。
- `templates/project/`：可直接渲染的 Remotion 工程，内容集中在 `src/deck.ts`。
- `scripts/scaffold_project.py`：把模板复制到目标目录，并拒绝覆盖非空目录。
- `scripts/check_project.py`：静态检查场景数量、时长、字段、纯画面约束和输出规格。
- `scripts/render_video.sh`：检查依赖后运行类型检查、封面导出和 H.264 MP4 渲染。
- `tests/`：先验证脚手架与校验器的失败路径，再验证成功路径。
- `examples/handwritten-motion-demo/`：可复现的演示数据和真实 MP4 样片。

## 数据与动效

每个场景配置标题、要点、强调词、持续秒数和版式。模板按场景顺序计算帧区间，使用 `Sequence`、`spring` 和 `interpolate` 驱动标题写入、荧光划线、要点分步出现、SVG 路径绘制与纸张式转场。画面固定 1920×1080、30fps，背景为淡暖白，主色沿用深蓝、玫红、绿色和少量荧光黄。

## 错误处理

目标目录非空时脚手架立即退出；场景少于 3 个、时长越界、文本过密、未知版式或出现音频配置时校验失败；缺少 Node/npm 或依赖时渲染脚本给出明确安装提示；成片必须由 `ffprobe` 确认只有视频流。

## 验收

1. Python 测试经历预期失败后全部通过。
2. TypeScript 与 ESLint 通过。
3. 真实渲染封面 PNG 和 MP4。
4. `ffprobe` 确认 1920×1080、30fps、H.264、无音轨，解码检查无错误。
5. Skill 通过 frontmatter、官方 `skills-ref`、JSON 与 `git diff --check` 检查。
