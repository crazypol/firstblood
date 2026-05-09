# 开发计划 — GitHub AI Trending Daily

**版本**: 1.0
**日期**: 2026-05-09
**负责人**: Dev Manager
**状态**: Approved

---

## 1. 技术栈决策

### ADR-001：技术选型

| 层级 | 技术 | 版本 | 理由 |
|------|------|------|------|
| **运行时** | Python 3.12+ | latest | AI/NLP 生态成熟，团队熟悉度高 |
| **抓取** | httpx + BeautifulSoup4 | — | 异步支持好，解析稳定 |
| **数据处理** | Pandas 2.x | — | 数据分析标准库 |
| **数据存储** | SQLite (via sqlite3) | 内置 | 零依赖，适合单机数据量 |
| **AI 分类/摘要** | Claude API / DeepSeek API | — | 中文能力优秀，成本可控 |
| **调度** | GitHub Actions Cron | — | 零成本托管，与 GitHub 生态集成 |
| **前端框架** | Astro 5.x | latest | 静态站点生成，性能好，组件灵活 |
| **图表** | ECharts 5.x | — | 功能全面，中文文档好 |
| **CSS** | Tailwind CSS 4.x | — | 原子化 CSS，开发效率高 |
| **静态托管** | GitHub Pages | — | 零成本，CI/CD 自动部署 |
| **通知** | Telegram Bot API | — | 开发者友好，API 简单 |

### 项目架构

```
┌─────────────────────────────────────────────────────┐
│                   GitHub Actions                      │
│  ┌─────────────┐  ┌──────────┐  ┌────────────────┐  │
│  │ 抓取 Pipeline│→│分类 Pipeline│→│ 报告 Pipeline   │  │
│  └─────────────┘  └──────────┘  └────────────────┘  │
│                          │                           │
├──────────────────────────┼──────────────────────────┤
│                          ▼                           │
│  ┌──────────────────────────────────────────────────┐│
│  │               data/ (Git 仓库内)                   ││
│  │  ┌──────┐  ┌────────┐  ┌──────────┐              ││
│  │  │raw/  │→│processed/│→│reports/  │              ││
│  │  └──────┘  └────────┘  └──────────┘              ││
│  └──────────────────────────────────────────────────┘│
├──────────────────────────┬──────────────────────────┤
│                          ▼                           │
│  ┌──────────────────────────────────────────────────┐│
│  │               GitHub Pages (Astro)                 ││
│  │  ┌──────────┐  ┌──────┐  ┌────────────────────┐  ││
│  │  │Dashboard │→│分类页│→│ 每日报告页           │  ││
│  │  └──────────┘  └──────┘  └────────────────────┘  ││
│  └──────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────┘
```

---

## 2. 项目目录结构

```
firstblood/
├── .github/
│   └── workflows/
│       ├── daily-fetch.yml         # 每日抓取工作流
│       └── deploy-pages.yml        # GitHub Pages 部署
│
├── src/
│   ├── scraper/
│   │   ├── __init__.py
│   │   ├── trending.py             # GitHub Trending 抓取
│   │   └── github_api.py           # GitHub API 补充数据
│   │
│   ├── classifier/
│   │   ├── __init__.py
│   │   ├── rules.py                # 关键词规则分类
│   │   └── llm_classifier.py       # LLM 辅助分类
│   │
│   ├── analyzer/
│   │   ├── __init__.py
│   │   ├── stats.py                # 统计计算
│   │   └── trends.py               # 趋势分析
│   │
│   ├── reporter/
│   │   ├── __init__.py
│   │   ├── markdown.py             # Markdown 报告生成
│   │   ├── json_exporter.py        # JSON 导出
│   │   └── insights.py             # AI 洞察生成
│   │
│   └── notifier/
│       ├── __init__.py
│       └── telegram.py             # Telegram 推送
│
├── frontend/                       # Astro 前端项目
│   ├── src/
│   │   ├── pages/
│   │   │   ├── index.astro         # Dashboard 首页
│   │   │   ├── category/[slug].astro # 分类页
│   │   │   └── report/[date].astro # 每日报告
│   │   ├── components/
│   │   │   ├── StatCard.astro
│   │   │   ├── RepoCard.astro
│   │   │   ├── CategoryChart.astro
│   │   │   ├── TrendLine.astro
│   │   │   └── ...
│   │   └── styles/
│   │       └── global.css
│   ├── astro.config.mjs
│   └── package.json
│
├── data/
│   ├── raw/                        # 原始抓取数据 (JSON)
│   ├── processed/                  # 处理后数据 (JSON)
│   └── reports/                    # 每日报告 (Markdown)
│
├── scripts/
│   ├── run-pipeline.sh             # 本地运行完整流水线
│   └── init-db.sh                  # 初始化数据库
│
├── tests/
│   ├── test_scraper.py
│   ├── test_classifier.py
│   ├── test_analyzer.py
│   └── test_reporter.py
│
├── config.py                       # 全局配置
├── requirements.txt
├── Makefile
├── README.md
└── UI-DESIGN-SYSTEM.md
```

---

## 3. 里程碑计划（8 周）

```
Week 1    Week 2    Week 3    Week 4    Week 5    Week 6    Week 7    Week 8
│         │         │         │         │         │         │         │
├─ P1 ────┤         │         │         │         │         │         │
│ Core    │         │         │         │         │         │         │
│ Pipeline│         │         │         │         │         │         │
│ 完成    │         │         │         │         │         │         │
├─────────┴─ P2 ────┤         │         │         │         │         │
│          Intelligence           │         │         │         │         │
│          AI 分类 + 摘要          │         │         │         │         │
│          完成                    │         │         │         │         │
├────────────────────┴── P3 ─────┤         │         │         │         │
│                     Visualization          │         │         │         │
│                     GitHub Pages 前端       │         │         │         │
│                     完成                    │         │         │         │
├───────────────────────────┴── P4 ─────────┤         │         │         │
│                                Distribution           │         │         │
│                                通知 + 部署              │         │         │
│                                完成                     │         │         │
├──────────────────────────────────┴── GA ──────────────┤
│                                             上线发布     │
```

---

## 4. Phase 1：Core Pipeline（第 1-2 周）

**目标**: 完成数据抓取、分类、基础统计的端到端流水线，输出 Markdown 和 JSON 报告。

### Task 1.1：项目脚手架 (D1)
| 项 | 内容 |
|------|------|
| 描述 | 初始化项目结构、配置、依赖管理 |
| 交付物 | `requirements.txt`, `config.py`, `Makefile`, 目录结构 |
| 工时 | 0.5 人天 |
| 验收标准 | `make install` 可安装所有依赖，`make test` 可运行 |

### Task 1.2：GitHub Trending 抓取器 (D1-D3)
| 项 | 内容 |
|------|------|
| 描述 | 实现 `src/scraper/trending.py`，抓取 GitHub Trending 页面的每日/每周/每月热门仓库 |
| 关键逻辑 | 解析 HTML，提取仓库名、描述、Star 数、Fork 数、语言、Topics |
| 输出 | JSON 文件存入 `data/raw/YYYY-MM-DD.json` |
| 工时 | 2 人天 |
| 验收标准 | 单次运行成功抓取 ≥ 100 个仓库；数据字段完整 ≥ 90% |

### Task 1.3：GitHub API 补充 (D3-D4)
| 项 | 内容 |
|------|------|
| 描述 | 实现 `src/scraper/github_api.py`，通过 GitHub REST API 补充 Star 历史、Topics 等数据 |
| 注意 | 仅对 Trending 抓取不到的字段做补充，减少 API 调用 |
| 工时 | 1 人天 |
| 验收标准 | API 调用频率 ≤ 5000 次/小时(GitHub 限制) |

### Task 1.4：规则分类器 (D4-D6)
| 项 | 内容 |
|------|------|
| 描述 | 实现 `src/classifier/rules.py`，基于关键词 + Topics 将仓库分类到 AI 子领域 |
| 分类体系 | LLM, Agent, RAG, MCP, Multi-modal, AI Dev Tools, AI Infra, AI Safety, ML Platform |
| 工时 | 2 人天 |
| 验收标准 | 在 50 个标注样本上准确率 ≥ 70% |

### Task 1.5：统计分析 (D6-D7)
| 项 | 内容 |
|------|------|
| 描述 | 实现 `src/analyzer/stats.py` 和 `trends.py`，计算各维度统计数据 |
| 统计项 | 分类分布、语言分布、Star 增长、新星项目识别、组织排名 |
| 工时 | 1.5 人天 |
| 验收标准 | 全部统计指标计算正确，与手动计算结果一致 |

### Task 1.6：Markdown + JSON 报告生成 (D7-D9)
| 项 | 内容 |
|------|------|
| 描述 | 实现 `src/reporter/markdown.py` 和 `json_exporter.py`，生成最终报告 |
| 交付物 | Markdown 报告 + JSON 数据文件 |
| 工时 | 1.5 人天 |
| 验收标准 | Markdown 报告排版正确，JSON 符合 schema |

### Task 1.7：GitHub Actions 工作流 (D10)
| 项 | 内容 |
|------|------|
| 描述 | 配置 `.github/workflows/daily-fetch.yml`，每日 UTC 0:00 自动运行完整流水线 |
| 工时 | 0.5 人天 |
| 验收标准 | Actions 定时触发成功，产出物正确提交到 data/ 目录 |

### Phase 1 Gate 检查
- [ ] 单次 `make pipeline` 可完成抓取→分类→统计→报告的端到端流程
- [ ] 输出数据格式稳定，无破坏性变更风险
- [ ] GitHub Actions 可正常运行并提交结果
- [ ] 测试覆盖 ≥ 70%

---

## 5. Phase 2：Intelligence（第 3-4 周）

**目标**: 引入 LLM 提升分类准确率，生成 AI 智能摘要和每日洞察。

### Task 2.1：LLM 分类器 (D11-D13)
| 项 | 内容 |
|------|------|
| 描述 | 实现 `src/classifier/llm_classifier.py`，使用 Claude/DeepSeek API 对规则分类结果进行二次校验 |
| 策略 | 规则分类 + LLM 校验的两阶段策略：规则高置信度的直接输出，低置信度的交给 LLM |
| 工时 | 2 人天 |
| 验收标准 | 分类准确率 ≥ 90% |

### Task 2.2：AI 项目摘要 (D13-D16)
| 项 | 内容 |
|------|------|
| 描述 | 实现 `src/reporter/insights.py`，为每个 Top 项目生成 AI 解读 |
| 输出 | 中文摘要 (50-100 字) + 英文摘要 + 项目价值标签 |
| 成本控制 | 仅对 Top 30 项目生成，缓存已生成的摘要 |
| 工时 | 3 人天 |
| 验收标准 | 摘要内容准确、无幻觉、格式统一 |

### Task 2.3：每日洞察生成 (D16-D18)
| 项 | 内容 |
|------|------|
| 描述 | 基于当天所有数据，LLM 生成每日趋势洞察（200-300 字） |
| 提示 | LLM Prompt 包含：Top 项目列表、分类分布变化、值得关注的新趋势 |
| 工时 | 1.5 人天 |
| 验收标准 | 洞察有信息量，非模板化，每日不同 |

### Task 2.4：分类体系优化 (D18-D20)
| 项 | 内容 |
|------|------|
| 描述 | 根据实际运行数据迭代优化分类规则和 Prompt |
| 活动 | 收集错误案例 → 更新关键词库 → 优化 LLM Prompt |
| 工时 | 1.5 人天 |
| 验收标准 | 连续 7 天分类准确率 ≥ 90% |

### Phase 2 Gate 检查
- [ ] 分类准确率 ≥ 90%（基于 100 条随机抽样）
- [ ] AI 摘要无明显幻觉（人工审核 30 条）
- [ ] LLM API 日均消耗 ≤ $2

---

## 6. Phase 3：Visualization（第 5-6 周）

**目标**: 基于 UI 设计稿实现 GitHub Pages 前端，提供可视化浏览体验。

### Task 3.1：Astro 项目初始化 (D21)
| 项 | 内容 |
|------|------|
| 描述 | 初始化 `frontend/` 目录，配置 Astro + Tailwind CSS |
| 效果 | 引入 Inter 字体、Lucide 图标、ECharts |
| 工时 | 0.5 人天 |
| 验收标准 | `npm run dev` 正常启动 |

### Task 3.2：设计系统实现 (D21-D23)
| 项 | 内容 |
|------|------|
| 描述 | 实现 CSS 变量、设计 Token、基础组件（Button/Card/Tag/Input/Nav） |
| 参考 | `UI-DESIGN-SYSTEM.md` 第 2-3 节 |
| 工时 | 2 人天 |
| 验收标准 | 组件库与设计稿一致，明暗主题切换正常，WCAG AA 达标 |

### Task 3.3：Dashboard 首页 (D23-D26)
| 项 | 内容 |
|------|------|
| 描述 | 实现首页全部区块：概览卡片、分类分布图、趋势图、Top 10 列表、新星项目、语言分布 |
| 组件 | StatCard, RepoCard, CategoryChart, TrendLine, LanguageBar |
| 数据 | 读取 `data/reports/latest.json` |
| 工时 | 3 人天 |
| 验收标准 | 各区块数据正确、图表可交互、响应式适配 |

### Task 3.4：分类浏览页 (D26-D28)
| 项 | 内容 |
|------|------|
| 描述 | 实现按 AI 子领域筛选的仓库列表页 |
| 功能 | 分类标签切换、排序、列表/卡片切换、分页加载 |
| 工时 | 2 人天 |
| 验收标准 | 分类筛选正确、排序正常、页面响应式 |

### Task 3.5：每日报告页 (D28-D30)
| 项 | 内容 |
|------|------|
| 描述 | 实现按日期查看的详细报告页面 |
| 功能 | 执行摘要、数据表格、Markdown/JSON 下载 |
| 工时 | 1.5 人天 |
| 验收标准 | 日期切换正常、下载文件正确 |

### Task 3.6：GitHub Pages 部署 (D30)
| 项 | 内容 |
|------|------|
| 描述 | 配置 `.github/workflows/deploy-pages.yml`，数据更新后自动部署前端 |
| 工时 | 0.5 人天 |
| 验收标准 | Actions 推送 pages 分支后，GitHub Pages 自动更新 |

### Phase 3 Gate 检查
- [ ] 所有页面在 Chrome / Safari / Firefox 上显示正常
- [ ] 移动端 (< 768px) 布局无错乱
- [ ] Lighthouse 评分 ≥ 90（Performance, Accessibility, Best Practices）
- [ ] 明暗主题切换正常

---

## 7. Phase 4：Distribution（第 7 周）

**目标**: 实现多渠道通知推送，完成生产部署。

### Task 4.1：Telegram Bot 推送 (D31-D33)
| 项 | 内容 |
|------|------|
| 描述 | 实现 `src/notifier/telegram.py`，每日报告生成后推送到 Telegram 频道 |
| 格式 | 消息摘要 + 链接到 GitHub Pages |
| 工时 | 2 人天 |
| 验收标准 | 推送成功率 ≥ 99%，消息格式正确 |

### Task 4.2：企业微信推送 (可选) (D33-D35)
| 项 | 内容 |
|------|------|
| 描述 | 实现企业微信机器人推送（Markdown 消息） |
| 工时 | 1.5 人天 |
| 验收标准 | 推送格式正常，链接可点 |

### Task 4.3：生产环境部署与监控 (D35-D37)
| 项 | 内容 |
|------|------|
| 描述 | 配置生产环境、设置监控告警 |
| 活动 | 确保 Actions 运行失败通知到人、设置数据完整性检查 |
| 工时 | 1.5 人天 |
| 验收标准 | 监控告警可用，Fail 能及时通知 |

---

## 8. 测试策略

| 层级 | 工具 | 覆盖内容 | CI 执行 |
|------|------|---------|---------|
| **单元测试** | pytest | 工具函数、分类器、统计计算 | Actions push |
| **集成测试** | pytest + httpx | 抓取器端到端（mock 网络） | Actions daily |
| **快照测试** | pytest | Markdown/JSON 输出一致性 | Actions push |
| **E2E 前端** | Playwright | 页面渲染、交互 | Actions deploy |

### 测试目标
- 单元测试覆盖率 ≥ 80%
- 关键路径（抓取→分类→报告）集成测试覆盖
- 前端页面快照对比测试

---

## 9. 风险管理

| 风险 | 可能性 | 影响 | 应对 | 负责人 |
|------|--------|------|------|--------|
| GitHub 反爬限制 | 中 | 高 | 降级到 GitHub API + 请求限速 | Phase 1 |
| LLM Token 超支 | 中 | 中 | 缓存 + 仅 Top 30 走 LLM + 限时 Prompt | Phase 2 |
| Actions 运行时超限 | 低 | 中 | 优化流水线耗时，拆分工作流 | Phase 1 |
| 前端数据格式不兼容 | 低 | 高 | Pipeline 端先定义 Schema，前端按 Schema 消费 | Phase 1+3 |

---

## 10. 人员建议

| 角色 | 人数 | 负责 |
|------|------|------|
| **后端工程师** | 1 人 | Phase 1 + 2（抓取、分类、AI 分析） |
| **前端工程师** | 1 人 | Phase 3（Astro 前端 + 可视化） |
| **运维/DevOps** | 兼职 | Phase 4（CI/CD、监控、部署） |
| **QA** | 兼职 | 测试覆盖、报告审核 |

建议开发人员可复用（前后端同一个人），但并行开发需 2 人。

---

## 11. 时间线总表

```
Phase 1: Core Pipeline      Week 1-2   10 工作日  10 人天
Phase 2: Intelligence        Week 3-4   10 工作日  9 人天
Phase 3: Visualization       Week 5-6   10 工作日  9.5 人天
Phase 4: Distribution         Week 7     5 工作日  5 人天
GA Release                    Week 8     5 工作日  —
─────────────────────────────────────────────────────
总计                                   40 天     33.5 人天
```

> 注：若 1 人全职开发，预计 8 周完成。若 2 人并行（后端+前端），可压缩至 5-6 周。

---

## 12. 交付物清单

| # | 交付物 | 归属 Phase | 格式 |
|---|--------|-----------|------|
| 1 | GitHub Trending 抓取器 | P1 | Python 模块 |
| 2 | AI 分类器（规则+LLM） | P1+P2 | Python 模块 |
| 3 | 统计分析引擎 | P1 | Python 模块 |
| 4 | Markdown 报告生成器 | P1 | Python 模块 |
| 5 | JSON 数据导出 | P1 | Python 模块 |
| 6 | GitHub Actions 工作流 | P1 | YAML |
| 7 | AI 智能摘要 | P2 | Python 模块 |
| 8 | 每日洞察 | P2 | Python 模块 |
| 9 | 设计 Token + 基础组件 | P3 | Astro/Vue |
| 10 | Dashboard 首页 | P3 | Astro 页面 |
| 11 | 分类浏览页 | P3 | Astro 页面 |
| 12 | 每日报告页 | P3 | Astro 页面 |
| 13 | GitHub Pages 部署 | P3 | YAML |
| 14 | Telegram 推送 | P4 | Python 模块 |
| 15 | 企业微信推送（可选） | P4 | Python 模块 |
| 16 | README + 使用文档 | 贯穿 | Markdown |

---

**开发经理**: Dev Manager
**日期**: 2026-05-09
**下一步**: 确认计划后进入 Phase 1 Core Pipeline 开发
