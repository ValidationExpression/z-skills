// 场景模块样板：sci-viz-lab 场景插件接口
// 用法：复制本文件到 src/scenes/<your-scene>.js，实现各钩子后在 src/main.js 中注册：
//   import myScene from "./scenes/<your-scene>.js";
//   registerScene(myScene);
// 并在 index.html 的 .scene-tabs 中添加对应 Tab：<button class="tab-btn" data-scene="my-scene">场景名</button>
//
// 场景接口约定（见 src/scenes/registry.js）：
//   { id, name, icon?, init(container), update(params), dispose(), getDefaultParams() }
// scene-loader 只维护一个 requestAnimationFrame 循环，每帧调用当前激活场景的 update；
// 切换场景时先调用旧场景 dispose，再清空容器并 init 新场景（懒加载，未激活不初始化）。

// import * as THREE from "three"; // 需要三维时启用

// 模块内部状态：渲染器、场景对象、DOM 引用等都收在这里，方便 dispose 时统一清理
const local = {
  renderer: null,
  scene: null,
  camera: null,
  paused: false,
};

export default {
  // id：唯一标识，与 index.html 中 Tab 的 data-scene 一致
  id: "my-scene",
  // name：中文场景名，用于 Tab 与占位提示
  name: "示例场景",

  // getDefaultParams：返回场景默认参数（滑杆初值等）
  // scene-loader 会在每帧 update 时把这些参数与 { delta, time } 合并后传入
  getDefaultParams() {
    return {
      sampleCount: 200, // 示例：样本数量滑杆
      delta: 0.05, // 示例：半径 / 邻域滑杆
    };
  },

  // init(container)：场景被激活时调用一次
  // 职责：向 container 写入本场景的 DOM（标题、画布、控制面板、说明文字），
  // 创建 Three.js 渲染器或 Canvas 上下文，绑定滑杆与按钮事件
  init(container) {
    container.innerHTML = `
      <section class="scene-panel">
        <h2>示例场景</h2>
        <canvas id="my-scene-canvas" aria-label="示例场景互动画布"></canvas>
        <!-- 参数滑杆：改变后立即更新模型与状态文字 -->
        <label>样本数量
          <input type="range" id="my-scene-count" min="80" max="900" value="200" />
        </label>
      </section>
    `;
    // 在此创建 renderer / scene / camera 或 2D context，存入 local
    // 注意性能：几何体、材质在 init 中创建，update 中只改变换，避免每帧重建对象
    // 遵守 prefers-reduced-motion：媒体查询命中时降低或停止自动运动
  },

  // update(params)：每帧调用，params = { ...defaultParams, delta, time }
  // delta 是与上一帧的间隔秒数，time 是累计秒数，用于驱动动画
  update(params) {
    if (local.paused) return;
    // 根据 params 更新模型姿态、动画进度与状态文字
    // local.renderer?.render(local.scene, local.camera);
  },

  // dispose()：切走场景时调用，释放 WebGL 资源、事件监听与定时器，防止内存泄漏
  dispose() {
    // local.renderer?.dispose();
    // 遍历 local.scene 释放 geometry / material / texture
    local.renderer = null;
    local.scene = null;
    local.camera = null;
  },
};
