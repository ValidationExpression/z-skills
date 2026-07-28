# z-sci-viz-lab

可视化科普 skill：把任何数学/科学概念变成电脑手机都能访问的单页互动实验。

源自实际项目 [sci-viz-lab](https://github.com/tjxj/sci-viz-lab)（线上 [sci-viz-lab.pages.dev](https://sci-viz-lab.pages.dev)），首个场景是王虹获菲尔兹奖的挂谷猜想互动实验。

## 使用指南

1. **全新主题**：拿 `templates/prompt-template.txt`，替换主题对象、核心变量、运动规则、时间线、权威资料五处，交给 AI 生成完整 Vite 单页项目
2. **扩展现有项目**：按 `templates/scene-template.js` 编写场景模块，在 sci-viz-lab 的 `src/main.js` 注册并添加 Tab
3. 完整流程与检查清单见 `references/workflow.md` 和 `SKILL.md`

构建与部署：

```bash
npm run build     # 单文件 dist/index.html
npm run deploy    # Cloudflare Pages
```

## 目录说明

```text
z-sci-viz-lab/
├── SKILL.md                     # 触发词、8 步核心流程、两种使用方式、完成标准
├── README.md                    # 本文件
├── templates/
│   ├── prompt-template.txt      # 挂谷猜想完整提示词模板（可替换主题复刻）
│   └── scene-template.js        # sci-viz-lab 场景模块样板（registry 接口）
└── references/
    └── workflow.md              # 方法论详解：事实核验→直觉→定义→互动→边界→来源→构建→部署
```

## 示例触发语

- "帮我做一个日食的可视化科普页面"
- "把开普勒定律做成互动科普实验"
- "像挂谷猜想那样做个科普页，主题是潮汐"
- "给 sci-viz-lab 加一个月相场景"
- "做一个科学交互演示，讲光的折射"
