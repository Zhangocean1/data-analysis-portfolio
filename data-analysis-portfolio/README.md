# 数据分析作品集 · 张海洋

> 大数据工程技术 · 求职岗位：数据分析工程师 / BI 数据开发
> 技术栈：MySQL、Excel、Python (Pandas)、ECharts / FineBI、Vue3

本作品集包含 6 个作品，覆盖 **取数 → 清洗 → 分析 → 可视化 → 自动化报表** 全流程。
所有数据为模拟数据（非真实公司数据），可直接复现。

---

## 作品一览

| # | 作品 | 主要工具 | 产出 | 对应简历点 |
|---|---|---|---|---|
| 1 | 电商销售数据 SQL 分析 | MySQL | SQL 脚本、数据字典、分析报告 | 多表联查、窗口函数、指标口径 |
| 2 | 经营日报/周报自动化模板 | Excel + Python | Excel 模板、日报脚本 | 透视表、SUMIFS、日报自动化 |
| 3 | 电商经营分析看板 | ECharts (HTML) | 可交互 HTML 看板 | BI 看板、同比环比、下钻 |
| 4 | Python 数据清洗与自动化报表 | Python (Pandas/openpyxl) | 脚本、自动生成的 Excel 日报 | Pandas、自动化出表 |
| 5 | 用户行为漏斗与 RFM 分析 | MySQL + Python | 漏斗图、RFM 分层图、分析报告 | 漏斗分析、用户分层、运营建议 |
| 6 | 气象数据可视化分析系统 | Vue3 + ECharts (HTML 演示) | 多城市气象看板、异常预警 | 毕业设计、多图表联动、预警 |

---

## 目录结构

```
data-analysis-portfolio/
├── data/                          # 模拟数据集（CSV）
│   ├── users.csv                  # 用户表 2000 行
│   ├── products.csv               # 商品表 96 行
│   ├── orders.csv                 # 订单主表 ~3100 行
│   ├── order_items.csv            # 订单明细 ~6000 行
│   ├── refunds.csv                # 退款表 ~240 行
│   ├── behavior.csv               # 行为流水 ~19 万行
│   ├── weather_daily.csv          # 气象数据 1460 行
│   └── DATA_DICTIONARY.md         # 数据字典与指标口径
├── sql/
│   └── 01_ecommerce_analysis.sql   # 作品1：建表+清洗+核心指标+RFM
├── python/
│   ├── generate_data.py            # 生成模拟数据
│   ├── compute_metrics.py          # 计算看板指标
│   ├── build_dashboard_html.py     # 生成电商看板 HTML
│   ├── build_weather_dashboard.py  # 生成气象看板 HTML
│   ├── daily_report.py             # 作品4：自动生成 Excel 日报
│   └── funnel_rfm.py               # 作品5：漏斗+RFM
├── output/
│   ├── dashboards/
│   │   ├── 03_ecommerce_dashboard.html   # 作品3：电商经营看板
│   │   └── 06_weather_dashboard.html     # 作品6：气象看板
│   ├── excel/
│   │   └── 经营日报_YYYYMMDD.xlsx         # 作品2/4：自动日报
│   └── charts/
│       ├── funnel.png                # 作品5：漏斗图
│       └── rfm_segment.png            # 作品5：RFM 分层图
└── reports/
    └── 05_funnel_rfm_report.md       # 作品5：分析报告
```

---

## 快速复现

```bash
# 1. 生成模拟数据
python python/generate_data.py

# 2. 计算看板指标
python python/compute_metrics.py

# 3. 生成电商看板 HTML
python python/build_dashboard_html.py

# 4. 自动生成 Excel 日报
python python/daily_report.py

# 5. 漏斗 + RFM 分析
python python/funnel_rfm.py

# 6. 生成气象看板
python python/build_weather_dashboard.py
```

看板 HTML 直接用浏览器打开即可，无需服务器。

---

## 核心指标速览（模拟数据）

| 指标 | 数值 |
|---|---|
| GMV（2024-2025） | ¥477.2 万 |
| 支付订单数 | 2,761 |
| 购买用户数 | 1,130 |
| 客单价 | ¥1,728 |
| 退款率 | 7.7% |
| 复购率 | 71.3% |

## 联系

- 张海洋　|　19862394979　|　3316374220@qq.com　|　现居苏州
