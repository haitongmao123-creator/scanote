# 识笺 - Scannote

一个智能PDF/Word文档识别与命名工具，支持本地模式和AI模式。

## 功能特点

- 📄 支持PDF和Word文档（.doc/.docx）
- 🤖 AI模式（智谱AI glm-4v-flash），支持图片识别
- 💻 本地模式，无需网络
- 🎯 自动识别文档标题和产品名
- 📋 可自定义命名规则
- 💾 一键下载重命名后的文件

## 使用方法

1. 开启AI模式（可选）
   - 访问 [智谱AI开放平台](https://open.bigmodel.cn/)
   - 获取API Key
   - 在设置中填写并保存

2. 拖拽或选择文件
   - 将PDF/Word文件拖拽到页面
   - 或点击选择文件

3. 自动识别与下载
   - 系统自动识别文档标题
   - 点击下载按钮获取重命名后的文件

## 本地运行

```bash
# 使用Python启动本地服务器
python3 -m http.server 8080
```

然后在浏览器打开 http://localhost:8080

## GitHub Pages 部署

本项目已配置为可直接通过GitHub Pages部署：

1. Fork本仓库
2. 进入仓库 Settings → Pages
3. 选择部署源为 `main` 分支和 `/root` 目录
4. 保存后几分钟即可通过 `https://你的用户名.github.io/识笺/` 访问

## 技术栈

- 纯前端，无需后端
- PDF.js 用于PDF处理
- 智谱AI API 用于智能识别
