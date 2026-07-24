# z-video-downloader

把视频链接下载成本地视频文件。支持 YouTube、Bilibili、Vimeo、X/Twitter、TikTok、抖音、Instagram、Facebook、**微信视频号** 等平台及常见视频直链。

## 功能特性

- 单个/多个/批量链接下载
- 断点续传（直链 `.part` + HTTP Range / yt-dlp 分片续传）
- 字幕、封面、元数据
- 下载历史去重
- 平台风控自动 cookie 重试
- **微信视频号分享链接在线解析（无需本地安装额外工具）**

## 微信视频号支持

识别 `https://weixin.qq.com/sph/xxx` 格式的分享链接，通过在线解析服务自动获取视频真实地址并下载。

- 默认同时保存 H.264（高清兼容版）和 H.265（省空间版）
- 无需微信登录态、无需安装证书、无需修改系统代理
- 文件名自动从视频描述/作者昵称生成

```bash
python3 scripts/download_video.py --title "视频号主题" "https://weixin.qq.com/sph/Axv548mzBF"
```

## 其他平台

```bash
# YouTube
python3 scripts/download_video.py --title "主题名" "https://www.youtube.com/watch?v=..."

# Bilibili
python3 scripts/download_video.py --title "主题名" "https://www.bilibili.com/video/BV..."

# 批量下载
python3 scripts/download_video.py --title "主题名" --url-file "video-urls.txt"
```

## 依赖

- Python 3.10+
- `requests`
- `yt-dlp`（平台视频）
- `ffmpeg`（音视频合并）

## 致谢

- [ltaoo/wx_channels_download](https://github.com/ltaoo/wx_channels_download) — 微信视频号下载器，本项目视频号在线解析能力基于其提供的公开解析服务（`sph.litao.workers.dev`）
- [joeseesun/qiaomu-wx-video](https://github.com/joeseesun/qiaomu-wx-video) — 视频号下载 skill 工作流参考
- [kanadeblisst00/WechatVideoSniffer2.0](https://github.com/kanadeblisst00/WechatVideoSniffer2.0) — 前端解密上游
- [Hanson/WechatSphDecrypt](https://github.com/Hanson/WechatSphDecrypt) — 后端解密上游

## 免责声明

本项目仅用于技术交流学习和研究目的，请遵守法律法规，请勿用作任何非法用途。请尊重内容创作者权益，仅下载您有权访问和保存的内容。
