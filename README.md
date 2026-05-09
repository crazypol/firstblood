# AI Trend Daily 🤖

> GitHub 热门 AI 相关项目每日趋势统计

自动抓取、分类、分析、报告 GitHub 上最热门的 AI 相关开源项目，每日更新。

## 功能

- **📊 每日抓取** — 自动从 GitHub Trending 获取热门仓库
- **🏷️ AI 分类** — 将项目自动分类到 LLM / Agent / RAG / MCP / 多模态等子领域
- **📈 多维统计** — Star 增长、语言分布、领域分布、新星项目识别
- **🤖 AI 洞察** — LLM 生成的每日趋势解读和项目摘要
- **🌐 可视化** — GitHub Pages 前端展示
- **🔔 通知推送** — Telegram / 企业微信

## 快速开始

```bash
# 安装依赖
make install

# 运行完整流水线（不含 AI 摘要）
python -m src.pipeline

# 运行含 AI 摘要（需配置 API Key）
python -m src.pipeline --ai

# 运行测试
make test
```

## 配置

复制 `.env.example` 为 `.env` 并填写配置项：

```bash
cp .env.example .env
```

| 变量 | 必需 | 说明 |
|------|------|------|
| `ANTHROPIC_API_KEY` | AI 功能需要 | Claude API Key |
| `OPENAI_API_KEY` | 备选 | OpenAI / DeepSeek API Key |
| `GITHUB_TOKEN` | 建议 | GitHub API Token（提高频率限制）|

## 项目结构

```
src/
├── scraper/          # GitHub Trending 抓取
│   ├── trending.py   # Trending 页面解析
│   └── github_api.py # GitHub API 补充
├── classifier/       # AI 领域分类
│   ├── rules.py      # 关键词规则分类
│   └── llm_classifier.py  # LLM 辅助分类
├── analyzer/         # 统计分析
│   ├── stats.py      # 每日统计
│   └── trends.py     # 趋势分析
├── reporter/         # 报告生成
│   ├── markdown.py   # Markdown 报告
│   ├── json_exporter.py # JSON 导出
│   └── insights.py   # AI 洞察
├── notifier/         # 通知推送
│   └── telegram.py   # Telegram
└── pipeline.py       # 主流水线
```

## 数据输出

- `data/reports/YYYY-MM-DD.md` — Markdown 报告
- `data/reports/YYYY-MM-DD.json` — JSON 数据
- `data/raw/YYYY-MM-DD.json` — 原始抓取数据

## 许可

MIT
