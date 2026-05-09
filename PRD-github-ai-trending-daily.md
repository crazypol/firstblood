# PRD: GitHub 热门 AI 相关 Skill 每日统计项目

**Status**: Draft
**Author**: Alex (Product Manager)
**Last Updated**: 2026-05-09
**Version**: 1.0
**Stakeholders**: 用户

---

## 1. 问题陈述

### 背景

AI 领域发展极快，每天都有新的开源项目、工具、框架在 GitHub 上涌现。开发者、技术决策者和 AI 从业者面临以下核心痛点：

- **信息过载**：GitHub Trending 页面每天更新，但缺乏按 AI 领域筛选和聚合的能力
- **缺乏每日洞察**：手动浏览 GitHub 效率极低，容易错过关键项目
- **没有结构化的统计视图**：无法直观看到 AI 各子领域（LLM、Agent、RAG、MCP 等）的趋势变化
- **跨语言/跨平台信息碎片化**：英文 Trending 和中文社区的热点存在差异，缺乏统一的视角

### 目标用户画像

| 画像 | 描述 | 核心需求 |
|------|------|---------|
| **AI 开发者** | 使用开源 AI 工具构建应用的工程师 | 发现最新 AI 工具和框架，保持技术领先 |
| **技术决策者** | CTO、技术 VP、技术负责人 | 跟踪技术趋势，为技术选型提供参考 |
| **AI 研究者** | 学术界/工业界的研究人员 | 跟踪前沿研究实现和开源项目 |
| **技术爱好者** | 对 AI 感兴趣的开发者 | 学习最新的 AI 技能和技术 |

### 不解决的问题

- 不做 GitHub 之外的多平台聚合（如 Twitter、Reddit）— v1 聚焦 GitHub
- 不做深度代码分析 — 聚焦元数据和趋势统计
- 不做付费订阅 — 保持开源免费

---

## 2. 目标与成功指标

| 目标 | 指标 | 当前基线 | 目标 | 衡量周期 |
|------|------|---------|------|---------|
| 每日数据完整性 | 每天抓取的 AI 相关仓库数 | N/A | ≥ 50 个/天 | 每日 |
| 趋势分类准确率 | AI 子领域分类准确率 | N/A | ≥ 90% | 每周抽样 |
| 报告可用性 | 报告按时生成率 | N/A | 100% | 每日 |
| 项目使用率 | 周活跃用户数 | N/A | 50+ (上线后 30 天) | 每周 |

---

## 3. 竞品分析

| 产品 | 优势 | 劣势 | 我们的差异点 |
|------|------|------|-------------|
| **GitHub Trending** (官方) | 数据权威，实时更新 | 没有 AI 筛选维度，无历史趋势，只显示当天 | AI 领域深度过滤 + 历史趋势 |
| **Apify GitHub Trending Scraper** | 数据全面，支持过滤 | 付费服务，无中文支持，无 AI 分析 | 开源免费 + AI 摘要 + 中文支持 |
| **@wcj/github-rank** | 免费 JSON 数据 | 无分类，无 AI 分析，纯数据 | AI 智能分析 + 可视化报告 |
| **开源 GitHub Star Tracker** (中文) | AI 生成解读，飞书集成 | 仅支持飞书，需自建 | GitHub Pages 直接访问 + 多输出格式 |
| **mcp-github-trending** | MCP 协议，AI 原生 | 仅提供原始数据，无统计 | 完整统计体系 + 每日报告 |

---

## 4. 解决方案概述

### 核心定位

> **一个开源的、聚焦 AI 领域的 GitHub 每日趋势统计工具，自动抓取、分类、分析、报告 GitHub 上最热门的 AI 相关开源项目。**

### 核心工作流

```
GitHub Trending
     ↓
 每日自动抓取（GitHub Actions / 定时任务）
     ↓
 AI 领域分类（LLM / Agent / RAG / MCP / 多模态 / 推理 / 工具链 ...）
     ↓
 数据统计与分析（Star 增长、语言分布、领域分布、活跃度）
     ↓
 多格式报告（Markdown / JSON / Web Dashboard）
     ↓
 推送到多个渠道（GitHub Pages / Telegram / WeCom / Email）
```

### v1 核心功能

**功能 1：AI 领域趋势抓取**
- 每日定时从 GitHub Trending 抓取热门仓库
- 基于关键词、主题（Topics）、描述自动分类到 AI 子领域
- 支持的子领域：LLM / Agent / RAG / MCP / Multi-modal / AI Dev Tools / AI Infrastructure / AI Safety / ML Platform

**功能 2：多维统计分析**
- Star 增长趋势（日/周/月对比）
- 语言分布统计（Python / TypeScript / Rust / Go 等）
- AI 子领域分布统计
- 开发者/组织活跃度排名
- 新星项目识别（首次进入 Top 的项目）

**功能 3：AI 智能摘要**
- 每个热门项目的 AI 生成解读（中文 + 英文）
- 每日汇总报告：今日 AI 趋势要点
- 项目价值分析：为什么这个项目值得关注

**功能 4：多格式输出**
- Markdown 报告（适合 README / 文档）
- JSON 数据（适合二次开发）
- GitHub Pages 页面（可视化浏览）
- 可选推送到 IM 工具（Telegram / 企业微信）

---

## 5. 技术方案建议

### 技术栈选择

| 层 | 推荐方案 | 备选方案 | 选择理由 |
|---|---------|---------|---------|
| 抓取层 | Python + BeautifulSoup/httpx | Node.js + Puppeteer | 生态成熟，AI/NLP 库丰富 |
| 数据存储 | SQLite + JSON | PostgreSQL | 轻量，无需部署数据库 |
| AI 分析 | LLM API (Claude / DeepSeek) | 本地模型 | 成本低效果好，支持中文 |
| 调度 | GitHub Actions (Cron) | 自建服务器 | 零成本，CI/CD 天然集成 |
| 前端 | GitHub Pages + Astro/Vite | Next.js | 静态托管，零成本 |
| 通知 | Telegram Bot API | 企业微信 / Email | 开发者最常用的 IM |

### 数据模型（核心）

```json
{
  "repo": {
    "name": "owner/repo",
    "url": "https://github.com/owner/repo",
    "description": "...",
    "language": "Python",
    "topics": ["llm", "agent", "rag"],
    "stars": 15000,
    "stars_today": 850,
    "forks": 1200,
    "author": "owner",
    "ai_category": "agent",
    "ai_subcategories": ["mcp", "tool-use"],
    "first_seen": "2026-05-01",
    "summary_zh": "...",
    "summary_en": "..."
  },
  "daily_report": {
    "date": "2026-05-09",
    "total_ai_repos": 68,
    "categories": { "agent": 15, "llm": 20, "rag": 8, ... },
    "languages": { "Python": 35, "TypeScript": 18, ... },
    "top_gainers": [...],
    "new_entrants": [...],
    "insight_zh": "今日AI趋势要点...",
    "insight_en": "..."
  }
}
```

---

## 6. 发布计划

| 阶段 | 时间 | 范围 | 成功标准 |
|------|------|------|---------|
| **Phase 1: Core** | 第 1-2 周 | 抓取 + 分类 + 基础统计 + Markdown/JSON 输出 | 每日成功抓取 ≥ 50 个 AI 仓库 |
| **Phase 2: Intelligence** | 第 3-4 周 | AI 摘要 + 分类优化 + 趋势分析 | AI 分类准确率 ≥ 90% |
| **Phase 3: Visualization** | 第 5-6 周 | GitHub Pages 前端 + 图表可视化 | Dashboard 正常展示 |
| **Phase 4: Distribution** | 第 7 周 | Telegram / 企业微信推送 + 邮件订阅 | 推送成功率 ≥ 99% |
| **GA 发布** | 第 8 周 | 全功能上线 | 所有指标达标 |

---

## 7. 风险评估

| 风险 | 概率 | 影响 | 应对策略 |
|------|------|------|---------|
| GitHub Trending 反爬限制 | 中 | 高 | 使用 GitHub API 作为备选，请求间隔控制 |
| AI 分类不准确 | 中 | 中 | 人工标注种子数据 + 多层分类策略（关键词 + LLM 校验） |
| GitHub Actions Cron 不稳定 | 低 | 中 | 添加重试机制，fallback 到本地运行 |
| AI API 成本超支 | 中 | 低 | 摘要缓存 + 增量处理，控制 token 消耗 |

---

## 8. 开放问题

- [ ] v1 是否支持中文和英文双语输出？还是仅中文？
- [ ] 是否需要支持用户自定义关注的 AI 子领域？还是固定分类？
- [ ] 报告输出渠道优先级：GitHub Pages > Telegram > 其他？
- [ ] 数据历史保留多久？是否需要数据清理策略？

---

## 9. 附录

### 参考竞品
- [GitHub Trending](https://github.com/trending)
- [@wcj/github-rank](https://www.npmjs.com/package/@wcj/github-rank) — 每日 GitHub 排名 JSON 数据
- [Apify GitHub Trending Scraper](https://apify.com/automation-lab/github-trending-scraper) — 趋势抓取 API
- [mcp-github-trending](https://hexmos.com/freedevtools/mcp/git-workflow-management/hetaoBackend--mcp-github-trending/) — MCP 协议的 GitHub 趋势工具
