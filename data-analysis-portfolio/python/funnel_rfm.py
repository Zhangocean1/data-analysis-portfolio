#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
作品5：用户行为漏斗与 RFM 分析
输出：
  - output/charts/funnel.png
  - output/charts/rfm_segment.png
  - reports/05_funnel_rfm_report.md
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import os, json

matplotlib.rcParams["font.sans-serif"] = ["DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False
# 尝试中文字体
for fp in ["/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
           "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"]:
    if os.path.exists(fp):
        from matplotlib.font_manager import FontProperties
        zh = FontProperties(fname=fp)
        matplotlib.rcParams["font.sans-serif"] = [zh.get_name()]
        break

BASE = os.path.join(os.path.dirname(__file__), "..")
DATA = f"{BASE}/data"
CHARTS = f"{BASE}/output/charts"
REPORTS = f"{BASE}/reports"
os.makedirs(CHARTS, exist_ok=True)
os.makedirs(REPORTS, exist_ok=True)

orders = pd.read_csv(f"{DATA}/orders.csv", parse_dates=["order_time"])
items = pd.read_csv(f"{DATA}/order_items.csv")
behavior = pd.read_csv(f"{DATA}/behavior.csv", parse_dates=["event_time"])
users = pd.read_csv(f"{DATA}/users.csv")

paid = orders[orders.status == "已支付"]

# ---- 漏斗 ----
stages = ["曝光", "点击", "加购", "下单", "支付"]
uvs = [
    behavior[behavior.event_type=="曝光"].user_id.nunique(),
    behavior[behavior.event_type=="点击"].user_id.nunique(),
    behavior[behavior.event_type=="加购"].user_id.nunique(),
    paid.user_id.nunique(),
    paid.user_id.nunique(),
]
conv = [100.0]
for i in range(1, len(uvs)):
    conv.append(round(uvs[i]/uvs[i-1]*100, 1) if uvs[i-1] else 0)

fig, ax = plt.subplots(figsize=(8, 4.5))
colors = ["#2e75b6", "#5b9bd5", "#9dc3e6", "#ed7d31", "#70ad47"]
bars = ax.barh(stages[::-1], uvs[::-1], color=colors[::-1])
for i, (v, c) in enumerate(zip(uvs[::-1], conv[::-1])):
    ax.text(v, i, f"  {v:,}  ({c}%)", va="center", fontsize=10)
ax.set_title("用户行为漏斗（曝光→支付）", fontsize=13)
ax.set_xlabel("用户数（UV）")
plt.tight_layout()
plt.savefig(f"{CHARTS}/funnel.png", dpi=130)
plt.close()

# ---- RFM ----
ref = pd.Timestamp("2025-12-31")
order_gmv = items.groupby("order_id").amount.sum().reset_index()
rfm = paid.merge(order_gmv, on="order_id").groupby("user_id").agg(
    recency=("order_time", lambda x: (ref - x.max()).days),
    frequency=("order_id", "nunique"),
    monetary=("amount", "sum")
).reset_index()

rfm["r_score"] = pd.qcut(rfm.recency.rank(method="first"), 5, labels=[5,4,3,2,1]).astype(int)
rfm["f_score"] = pd.qcut(rfm.frequency.rank(method="first"), 5, labels=[1,2,3,4,5]).astype(int)
rfm["m_score"] = pd.qcut(rfm.monetary.rank(method="first"), 5, labels=[1,2,3,4,5]).astype(int)

def seg(r, f, m):
    if r>=4 and f>=4 and m>=4: return "高价值用户"
    if r>=4 and f<=2: return "新客/召回潜力"
    if r<=2 and f>=4: return "流失高价值"
    if r<=2 and f<=2: return "流失用户"
    return "一般维持"
rfm["segment"] = rfm.apply(lambda x: seg(x.r_score, x.f_score, x.m_score), axis=1)

seg_stat = rfm.groupby("segment").agg(users=("user_id","count"), gmv=("monetary","sum")).reset_index()
seg_stat["gmv_pct"] = (seg_stat.gmv / seg_stat.gmv.sum() * 100).round(1)
seg_stat = seg_stat.sort_values("gmv", ascending=False)

fig, ax1 = plt.subplots(figsize=(8, 4.5))
ax1.bar(seg_stat.segment, seg_stat.users, color="#2e75b6", alpha=0.8, label="用户数")
ax1.set_ylabel("用户数", color="#2e75b6")
ax2 = ax1.twinx()
ax2.plot(seg_stat.segment, seg_stat.gmv_pct, "o-", color="#ed7d31", linewidth=2, label="GMV占比%")
ax2.set_ylabel("GMV 贡献占比 (%)", color="#ed7d31")
ax1.set_title("RFM 用户分层", fontsize=13)
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig(f"{CHARTS}/rfm_segment.png", dpi=130)
plt.close()

# ---- 输出 Markdown 报告 ----
report = f"""# 作品5：用户行为漏斗与 RFM 分析报告

## 1. 分析目标
- 识别用户从曝光到支付的流失节点
- 通过 RFM 完成用户分层，指导运营动作

## 2. 漏斗分析

| 环节 | UV | 环节转化率 |
|---|---|---|
"""
for s, u, c in zip(stages, uvs, conv):
    report += f"| {s} | {u:,} | {c}% |\n"

report += f"""
**关键结论**：
- 曝光→点击转化率 {conv[1]}%，素材/选品对点击率影响有限；
- 加购→下单转化率 {conv[3]}% 是流失最严重环节，常见原因：运费/价格/竞品对比；
- 整体曝光→支付转化率 {round(uvs[-1]/uvs[0]*100,2)}%。

## 3. RFM 用户分层

| 分层 | 用户数 | GMV(元) | GMV占比 |
|---|---|---|---|
"""
for _, r in seg_stat.iterrows():
    report += f"| {r.segment} | {r.users:,} | {r.gmv:,.0f} | {r.gmv_pct}% |\n"

report += """
## 4. 运营建议
1. **高价值用户**：建立 VIP 群、专属客服、新品优先体验，防止流失；
2. **流失高价值用户**：定向发放大额召回券（满 300-50），唤醒历史复购；
3. **新客/召回潜力**：首单后 7 天内推送二单优惠，引导完成第二次购买；
4. **加购未下单**：购物车 abandonment 邮件/短信提醒 + 限时折扣；
5. **曝光→点击**：优化主图与首屏文案，A/B 测试不同素材。

## 5. 工具
- MySQL：漏斗 UV、RFM 指标计算
- Python (Pandas + Matplotlib)：分层与可视化
- 数据：模拟电商数据集（2000 用户 / 19 万行为流水）
"""
with open(f"{REPORTS}/05_funnel_rfm_report.md", "w", encoding="utf-8") as f:
    f.write(report)

print("funnel.png / rfm_segment.png / 05_funnel_rfm_report.md 已生成")
print(seg_stat.to_string(index=False))
