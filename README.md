<img width="2400" height="753" alt="image" src="https://github.com/user-attachments/assets/4ccba7ca-61a3-49d2-b8b8-b837ffa3dceb" />
# LLM SQL Local Benchmark Dashboard 
(大模型 SQL 评测面板)

[English](#english) | [中文说明](#中文说明)

---

## 使用方式一： 🚀 GitHub Pages 在线访问地址 (GitHub Pages Service URL)
**[👉 点击此处运行在线测试 / Click here to experience online](https://wangxian001.github.io/SQL_LLM_benchmark/)**

---
---

## 使用方式二： 🚀 GitHub 拉取本仓库代码本地部署 <推荐>
**[👉 拉取本仓库代码本地部署 / Click here to local deployment ](https://github.com/wangxian001/SQL_LLM_benchmark)**

---
<img width="3263" height="1705" alt="image" src="https://github.com/user-attachments/assets/3f553304-b1c2-4edc-8831-bc56fe4393e9" />



## English

A client-side LLM SQL generation benchmark dashboard utilizing **DuckDB-Wasm** in the browser. It allows users to execute SQL generation tests on a dataset of 25 benchmark questions, check correct rates, monitor token consumption, and download full dialogue trace reports natively.

### 🔗 Reference & Original Repository
* **Original Project GitHub Repo**: [nlothian/llm-sql-benchmark](https://github.com/nlothian/llm-sql-benchmark)
* **Original Benchmark Webpage**: [sql-benchmark.nicklothian.com](https://sql-benchmark.nicklothian.com/)

### 💡 Why we built this project? (Differences & Advantages)
* **Origin**: The original benchmark utilizes an Astro/React framework setup, which requires heavy local compilation and npm dependencies, making it hard to host statically or run locally in corporate intranet offline environments without setup.
* **Differences & Enhancements**:
  1. **Single-Page HTML Structure**: The dashboard is written in a single self-contained `sql_benchmark.html` page, loading immediately with zero build setup.
  2. **Collapsible Reasoning/Dialogue Inspector**: Clicking any cell displays a comprehensive diagnostic log panel. It renders not only logs, but also the model's **reasoning/thinking process** and exact tool call arguments, making agent-mode debugging extremely easy.
  3. **High-Fidelity Themes**: Replicated the official light-mode palette and enhanced the heatmap to feature pink/dark-red diagonal gradient blocks for Failed cells, improving readability.
  4. **Flexible Exporter**: 
     - *Backend mode*: Automatically saves per-round CSV files to server directories (`trace_log/`).
     - *Serverless/GitHub Pages mode*: Runs completely in the browser and lets you export a single combined CSV table containing all rounds' details.

### 🛠️ Principles
1. **DuckDB-Wasm**: Relies on DuckDB-Wasm running fully client-side to query the AdventureWorks dataset.
2. **Correctness Check**: Validates model output against expected SQL output based on expected row counts, column counts, and first-row data equality.

### 📦 How to Run & Deploy
1. **Statically via GitHub Pages**:
   - Enable GitHub Pages on your repository (`main` branch root folder).
   - Go to `https://<your_username>.github.io/SQL_LLM_benchmark/`.
2. **Locally/Privately (Intranet Server)**:
   - Prepare Database Tables: `python download_tables.py`
   - Start Server: `python run_server.py`
   - Access `http://localhost:8000/sql_benchmark.html`.

---

## 中文说明

一个基于浏览器内 **DuckDB-Wasm** 运行的纯客户端大模型 SQL 生成局域网评测系统。用户可以通过该面板，针对内置的 25 道 AdventureWorks 数据集测试题，开展多轮次的 SQL 生成与正确率基准测试，并支持 Token 统计及交互 Trace 的一键合并导出。
<img width="3315" height="1940" alt="image" src="https://github.com/user-attachments/assets/85fcdcaa-a3c3-4d5b-92a0-d11b551b3cb9" />


### 🔗 原项目与参考地址
* **原项目 GitHub 仓库**: [nlothian/llm-sql-benchmark](https://github.com/nlothian/llm-sql-benchmark)
* **原项目在线评测网站**: [sql-benchmark.nicklothian.com](https://sql-benchmark.nicklothian.com/)

### 💡 为什么建立本项目？与原项目的区别与优势
* **建立初衷**：原项目基于 Astro/React 框架，需要繁琐的本地环境编译和 npm 包配置，不便于局域网内的快速部署、独立网页分发以及轻量二次开发。
* **主要区别与核心优势**：
  1. **极简单页面架构 (Single-Page)**：整个前端面板全部写在单个自包含的 HTML 网页文件 `sql_benchmark.html` 中，加载即用，免编译免构建。
  2. **内置思维链与调用解析 (Reasoning Trace)**：支持点击热力图方格展开详情，完整还原并渲染大模型的 **思维链路 (Thinking Process / Reasoning)** 以及工具调用的入参明细，极大地降低了 Agent 模式调试的门槛。
  3. **更优秀的视觉提示（对角半色格）**：完全高保真还原了原页面质感，并为失败 (Fail) 的格子加入了粉红-深红对角渐变区分，识别效率更高。
  4. **双模导出与保存**：
     - *服务端运行状态*：本地 Python 服务能实现每轮次自动在服务器存盘 CSV 到 `trace_log/` 目录下。
     - *无服务器/GitHub Pages 静态托管状态*：自动退化到纯前端模式，支持在浏览器内存中实时捕获多轮次的 Trace 细节，并提供 **“导出评测 CSV”** 功能，下载一张包含各轮各题 SQL、耗时、Token 消耗和完整 Trace 的合并大表，十分便于分析。
  5. **自动统计数据，直观查看多轮测试的数据；自动导出测试过程中的完整会话流程**：
    

### 🛠️ 实现原理
1. **DuckDB-Wasm**：利用浏览器内的 WebAssembly 版 DuckDB 引擎。前端在启动时自动拉取 AdventureWorks 数据集（CSV 文件格式），在用户浏览器本地的虚拟内存中构建关系型数据表，确保 SQL 的运行和检查不经过任何外部服务器。
2. **结果严密比对**：将大模型生成的 SQL 在 DuckDB-Wasm 执行后的返回值，与 AdventureWorks 标准参考结果进行比对，包括**行数、列数、以及第一行数据**的交叉校验，以确保 SQL 功能性的绝对正确。

### 📦 使用说明与部署方式
1. **通过 GitHub Pages 静态托管部署**：
   * 将此仓库 Fork 到您的 GitHub 下。
   * 在仓库设置的 **Settings -> Pages** 中，将 Source 设置为 `Deploy from a branch` 并选择 `main` 分支根目录。
   * 保存后，即可通过 `https://<您的用户名>.github.io/SQL_LLM_benchmark/` 访问静态页面并运行测试。
2. **本地/局域网私有化运行（推荐）**：
   * 确保本地安装了 Python。
   * 首先下载并初始化数据集：`python download_tables.py`
   * 启动本地 HTTP 服务：`python run_server.py`
   * 浏览器打开：`http://localhost:8000/sql_benchmark.html`。
