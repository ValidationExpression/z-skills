---
name: z-sci-viz-lab
description: 可视化科普 skill。当用户要求"可视化科普""互动科普实验""科学交互演示""把XX做成互动页面""像挂谷猜想那样做个科普页"时使用。把任何数学或科学概念（如挂谷猜想、日食、月食、太阳系、四季、月相、潮汐）变成电脑和手机都能访问的单页互动实验：先事实核验，再建直觉模型，给出正式定义，设计参数滑杆加实时反馈的互动实验，写清边界说明与来源追溯，最后用 Vite 打包单文件并发布到 Cloudflare Pages。支持两种方式：用 templates/prompt-template.txt 生成全新主题单页，或按 templates/scene-template.js 为 sci-viz-lab 现有项目扩展场景。
---

# z-sci-viz-lab：可视化科普

## 定位

把任何数学/科学概念变成"电脑手机都能访问的单页互动实验"。

不从一串定义和公式开始，而是让读者通过旋转、拖动和调参数先建立直觉，再进入正式定义、结论边界和权威来源。只要问题里存在空间关系、时间变化、尺度变化或参数影响，互动实验就有发挥空间。

## 核心流程（8 步）

1. **事实核验**：先查权威来源（官方页面、原始论文、可靠综述）再动手；禁止虚构定理、数字、引文和结论
2. **直觉模型**：把抽象概念转成可以操作的画面（三维模型、二维画布），先建立"这道题到底在问什么"的直觉
3. **正式定义**：在直觉之后给出准确定义与关键概念区分（例如 Lebesgue 测度 / Hausdorff 维数 / Minkowski 维数）
4. **互动实验设计**：参数滑杆 + 实时反馈；拖动旋转、滚轮缩放、重置视角、暂停动画；参数改变后立即更新模型与状态文字
5. **边界说明**：明确页面演示只用于建立直觉，不能充当数学证明；写清已解决与仍开放的问题
6. **来源追溯**：所有重要结论都能回到官方资料、原始论文或可靠综述，页面末尾列出来源链接
7. **Vite 单文件构建**：`npm run build`，用 vite-plugin-singlefile 打包成单个 `dist/index.html`
8. **Cloudflare Pages 发布**：`npm run deploy`，得到电脑手机都能直接访问的线上地址

详细方法论见 [references/workflow.md](references/workflow.md)。

## 两种使用方式

### 方式 A：全新主题，生成完整单页

使用 [templates/prompt-template.txt](templates/prompt-template.txt)（挂谷猜想完整提示词），替换以下五处后交给 AI 生成完整单页项目：

- **主题对象**：例如日食用太阳、月球、地球、光线、本影、半影
- **核心变量**：例如轨道倾角、时间、相对位置、食分
- **运动规则**：例如轨道运动、影锥变化、周期
- **时间线**：该主题的关键历史节点
- **权威资料**：官方页面、原始论文、可靠综述

模板中的事实核验、直觉模型、互动实验、边界说明、响应式检查和来源追溯要求原样保留。

### 方式 B：扩展 sci-viz-lab 现有项目

在现有 sci-viz-lab 项目中新增场景：

1. 复制 [templates/scene-template.js](templates/scene-template.js) 到 `src/scenes/<scene-id>.js`
2. 实现场景接口 `{ id, name, init(container), update(params), dispose(), getDefaultParams() }`
3. 在 `src/main.js` 中 `registerScene(myScene)` 注册
4. 在 `index.html` 的 `.scene-tabs` 中添加对应 Tab（`data-scene` 与场景 `id` 一致）
5. `npm run dev` 本地验证后构建发布

场景由 `scene-loader.js` 懒加载：激活时才 `init`，切走时 `dispose`，全局只有一个渲染循环。

## 实例：sci-viz-lab

- 仓库：https://github.com/tjxj/sci-viz-lab
- 线上：https://sci-viz-lab.pages.dev
- 10 个场景：挂谷猜想、日食、月食、太阳系、四季、月相、潮汐、卫星轨道、板块运动、光的折射

首个场景"挂谷猜想"包含：可旋转缩放的三维细管实验（四种排列）、二维线段重叠与 δ 邻域画布、证明思路五站式地图、时间线与可追溯来源。

## 技术栈与部署

- **技术栈**：Vite + Three.js（三维）+ HTML Canvas（二维）+ vite-plugin-singlefile
- **架构**：`src/scenes/` 场景插件架构，`registry.js` 注册表 + `scene-loader.js` 切换与渲染循环
- **视觉**：编辑部科学手册风（暖米白背景、深海军蓝实验区、红色强调、等宽字体参数标注）

```bash
npm install       # 安装依赖（Node.js >= 20）
npm run dev       # 本地开发
npm run build     # 构建，产出单文件 dist/index.html
npm run deploy    # 发布到 Cloudflare Pages（需先登录 Wrangler）
```

## 完成标准

- 页面在桌面与手机分辨率下无横向滚动，控件可键盘访问，遵守 prefers-reduced-motion
- 所有滑杆、按钮、拖动、缩放、重置实测可用，浏览器控制台无报错
- 边界说明与来源链接完整，无虚构内容
- `dist/index.html` 单文件可直接打开，线上地址可访问
