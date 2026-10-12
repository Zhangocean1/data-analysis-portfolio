#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
计算电商核心指标，输出 dashboard_data.json，供 HTML 看板使用
"""
import pandas as pd
import json, os

BASE = os.path.join(os.path.dirname(__file__), "..")
DATA = os.path.join(BASE, "data")
OUT  = os.path.join(BASE, "output", "dashboards")
os.makedirs(OUT, exist_ok=True)

users = pd.read_csv(f"{DATA}/users.csv", parse_dates=["register_time"])
products = pd.read_csv(f"{DATA}/products.csv")
orders = pd.read_csv(f"{DATA}/orders.csv", parse_dates=["order_time"])
items = pd.read_csv(f"{DATA}/order_items.csv")
refunds = pd.read_csv(f"{DATA}/refunds.csv", parse_dates=["refund_time"])
behavior = pd.read_csv(f"{DATA}/behavior.csv", parse_dates=["event_time"])

paid = orders[orders.status == "已支付"].copy()
paid_items = items.merge(paid[["order_id"]], on="order_id")

# --- 大盘 KPI ---
gmv = paid_items.amount.sum()
order_cnt = len(paid)
buyer_cnt = paid.user_id.nunique()
aov = gmv / order_cnt
refund_rate = len(refunds) / len(orders) * 100
repeat = (paid.groupby("user_id").size() >= 2).sum() / buyer_cnt * 100

# --- 月度趋势 ---
paid["ym"] = paid.order_time.dt.to_period("M").astype(str)
monthly = paid_items.merge(paid[["order_id","ym","user_id"]], on="order_id").groupby("ym").agg(
    gmv=("amount","sum"), orders=("order_id","nunique"), users=("user_id","nunique")
).reset_index()
monthly["gmv"] = monthly.gmv.round(0)

# --- 品类占比 ---
cat = paid_items.merge(paid[["order_id","order_time"]], on="order_id")
cat["yr"] = cat.order_time.dt.year
cat_gmv = cat.groupby(["category","yr"]).amount.sum().unstack(fill_value=0).reset_index()
cat_gmv.columns = ["category","gmv_2024","gmv_2025"] if 2024 in cat_gmv.columns else ["category","gmv_2024","gmv_2025"]
cat_gmv["yoy_pct"] = ((cat_gmv.gmv_2025 - cat_gmv.gmv_2024) / cat_gmv.gmv_2024 * 100).round(1)
cat_gmv = cat_gmv.sort_values("gmv_2025", ascending=False)

# --- 城市 TOP10 ---
city = paid_items.merge(paid[["order_id","city"]], on="order_id").groupby("city").amount.sum().reset_index()
city.columns = ["city","gmv"]
city = city.sort_values("gmv", ascending=False)

# --- 渠道 ---
ch = paid.merge(users[["user_id","channel"]], on="user_id").groupby("channel").agg(
    users=("user_id","nunique"), gmv=("user_id","count")
).reset_index()
# 用 items 算真实 GMV
ch_gmv = paid_items.merge(paid[["order_id","user_id"]], on="order_id").merge(users[["user_id","channel"]], on="user_id").groupby("channel").amount.sum().reset_index()
ch_gmv.columns = ["channel","gmv"]

# --- 漏斗 ---
funnel = []
expo_uv = behavior[behavior.event_type=="曝光"].user_id.nunique()
click_uv = behavior[behavior.event_type=="点击"].user_id.nunique()
cart_uv = behavior[behavior.event_type=="加购"].user_id.nunique()
order_uv = paid.user_id.nunique()
pay_uv = order_uv  # 已支付即支付
funnel = [
    {"stage":"曝光","uv":int(expo_uv)},
    {"stage":"点击","uv":int(click_uv)},
    {"stage":"加购","uv":int(cart_uv)},
    {"stage":"下单","uv":int(order_uv)},
    {"stage":"支付","uv":int(pay_uv)},
]

# --- RFM ---
ref_date = pd.Timestamp("2025-12-31")
rfm = paid.merge(paid_items.groupby("order_id").amount.sum().reset_index(), on="order_id")
rfm_agg = rfm.groupby("user_id").agg(
    recency=("order_time", lambda x: (ref_date - x.max()).days),
    frequency=("order_id","nunique"),
    monetary=("amount","sum")
).reset_index()
# 5 分位
import numpy as np
rfm_agg["r_score"] = pd.qcut(rfm_agg.recency.rank(method="first"), 5, labels=[5,4,3,2,1]).astype(int)
rfm_agg["f_score"] = pd.qcut(rfm_agg.frequency.rank(method="first"), 5, labels=[1,2,3,4,5]).astype(int)
rfm_agg["m_score"] = pd.qcut(rfm_agg.monetary.rank(method="first"), 5, labels=[1,2,3,4,5]).astype(int)
def seg(r,f,m):
    if r>=4 and f>=4 and m>=4: return "高价值用户"
    if r>=4 and f<=2: return "新客/召回潜力"
    if r<=2 and f>=4: return "流失高价值"
    if r<=2 and f<=2: return "流失用户"
    return "一般维持"
rfm_agg["segment"] = rfm_agg.apply(lambda x: seg(x.r_score,x.f_score,x.m_score), axis=1)
rfm_seg = rfm_agg.groupby("segment").agg(users=("user_id","count"), gmv=("monetary","sum")).reset_index()
rfm_seg["gmv_pct"] = (rfm_seg.gmv / rfm_seg.gmv.sum() * 100).round(1)

data = {
    "kpi": {
        "gmv": round(gmv,0),
        "gmv_fmt": f"¥{gmv/10000:.1f}万",
        "orders": int(order_cnt),
        "buyers": int(buyer_cnt),
        "aov": round(aov,0),
        "refund_rate": round(refund_rate,1),
        "repeat_rate": round(repeat,1),
    },
    "monthly": {"ym": monthly.ym.tolist(), "gmv": monthly.gmv.tolist(), "orders": monthly.orders.tolist()},
    "category": {"name": cat_gmv.category.tolist(), "gmv_2024": cat_gmv.gmv_2024.round(0).tolist(),
                 "gmv_2025": cat_gmv.gmv_2025.round(0).tolist(), "yoy": cat_gmv.yoy_pct.tolist()},
    "city": {"name": city.city.tolist(), "gmv": city.gmv.round(0).tolist()},
    "channel": {"name": ch_gmv.channel.tolist(), "gmv": ch_gmv.gmv.round(0).tolist()},
    "funnel": funnel,
    "rfm": {"name": rfm_seg.segment.tolist(), "users": rfm_seg.users.tolist(), "gmv_pct": rfm_seg.gmv_pct.tolist()},
}

with open(f"{OUT}/dashboard_data.json","w",encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("dashboard_data.json saved")
print(json.dumps(data["kpi"], ensure_ascii=False, indent=2))
