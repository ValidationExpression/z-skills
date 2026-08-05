# 王虹学术手写动画视频 Skill 设计

## 目标

新增独立 Skill `z-wanghong-handwritten-video`，把 `z-wanghong-handwritten-ppt` 已生成的 HTML 直接做成 16:9 纯画面手写动画，并输出无音轨的 H.264 MP4。原有 Skill 继续负责内容拆分、HTML 视觉和逐页 PNG，本 Skill 只负责在原 DOM 上增加时间维度。

## 方案选择

采用 Puppeteer Core 驱动本机 Chrome/Chromium，直接打开原 HTML 并逐帧截图，再通过 FFmpeg 编码。视频层不创建文字节点、不重建页面，字号和排版由原 HTML/CSS 决定。截图前加载原 PPT Skill 预览封面的指定字体文件，并验证 Chrome 的实际字体记录。帧进度由脚本注入，避免依赖实时 CSS 动画。

## 架构

- `SKILL.md`：触发条件、同源 HTML 约束、执行与验收流程。
- `scripts/render_html_video.mjs`：读取原 `.deck > .slide`，按帧控制元素显隐、裁切、标记与 SVG 描边，并把 PNG 帧流送入 FFmpeg。
- `scripts/render_html_video.sh`：调用原 PPT Skill 的检查器，再完成 MP4 流与解码验收。
- `package.json`：固定 Puppeteer Core 版本，使用系统 Chrome/Chromium。
- `tests/`：约束渲染器必须锁定预览封面字形、不得重新排版，并验证无声 H.264 编码契约。
- `examples/handwritten-html-motion-demo/`：由原 HTML 直接生成的真实 MP4 样片。

## 数据与动效

每个 `.slide` 直接沿用原 DOM。渲染器按直接子元素顺序驱动透明度、位移和裁切；对 `.title-line`、原荧光标记和 SVG 图形分别控制写入或描边进度；最后使用原页面的暖白变量完成纸张式转场。画面固定 1920×1080、30fps，字形锁定为预览封面的指定字体，色值、字号和布局从输入 HTML 继承。

## 错误处理

原 HTML 未通过 `z-wanghong-handwritten-ppt/scripts/check_deck.py` 时立即退出；缺少原 Skill、Node、Chrome、Puppeteer Core 或 FFmpeg 时给出明确提示；找不到直接子页 `.deck > .slide` 时停止；成片必须由 `ffprobe` 确认只有一条视频流和零条音频流。

## 验收

1. Python 测试经历预期失败后全部通过。
2. Shell 与 Node 语法检查通过，依赖审计无漏洞。
3. 使用原 HTML 真实渲染封面 PNG 和 6 页 MP4 样片。
4. 将封面与原 Skill 静态截图对照，确认字形与布局来自同一 HTML。
5. `ffprobe` 确认 1920×1080、30fps、H.264、无音轨，解码检查无错误。
6. Skill 通过 frontmatter、官方 `skills-ref`、JSON 与 `git diff --check` 检查。
