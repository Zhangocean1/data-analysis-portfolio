#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
作品1 配套：生成模拟电商数据集
表：users / products / orders / order_items / refunds / behavior
时间范围：2024-01-01 ~ 2025-12-31
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os

np.random.seed(42)
OUT = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(OUT, exist_ok=True)

# ---------- 维度表 ----------
cities = ["上海", "北京", "广州", "深圳", "杭州", "成都", "南京", "武汉", "苏州", "西安", "重庆", "长沙"]
channels = ["自然搜索", "朋友圈广告", "抖音", "小红书", "线下门店", "老客推荐"]
categories = {
    "服饰":  {"price": (80, 500),  "cost_rate": 0.45},
    "数码":  {"price": (300, 5000), "cost_rate": 0.75},
    "家居":  {"price": (50, 800),  "cost_rate": 0.5},
    "食品":  {"price": (20, 200),  "cost_rate": 0.55},
    "美妆":  {"price": (60, 600),  "cost_rate": 0.4},
    "母婴":  {"price": (40, 400),  "cost_rate": 0.55},
    "运动":  {"price": (100, 1000),"cost_rate": 0.5},
    "图书":  {"price": (20, 150),  "cost_rate": 0.35},
}

# ---------- users ----------
n_users = 2000
reg_start = datetime(2023, 1, 1)
reg_end = datetime(2025, 11, 30)
users = pd.DataFrame({
    "user_id": [f"U{100000+i}" for i in range(n_users)],
    "register_time": [reg_start + timedelta(days=int(np.random.uniform(0, (reg_end-reg_start).days))) for _ in range(n_users)],
    "city": np.random.choice(cities, n_users, p=[0.13,0.12,0.10,0.10,0.09,0.09,0.07,0.07,0.07,0.06,0.05,0.05]),
    "channel": np.random.choice(channels, n_users, p=[0.20,0.18,0.22,0.15,0.10,0.15]),
})
users["register_date"] = users["register_time"].dt.date

# ---------- products ----------
products = []
pid = 1
for cat, cfg in categories.items():
    n_prod = 12  # 每类 12 个
    for i in range(n_prod):
        price = round(np.random.uniform(*cfg["price"]), 2)
        cost = round(price * cfg["cost_rate"] * np.random.uniform(0.9, 1.1), 2)
        products.append({
            "product_id": f"P{pid:04d}",
            "category": cat,
            "product_name": f"{cat}商品{pid:03d}",
            "price": price,
            "cost": cost,
        })
        pid += 1
products = pd.DataFrame(products)

# ---------- orders / order_items ----------
start = datetime(2024, 1, 1)
end = datetime(2025, 12, 31)
days = (end - start).days

# 业务量有季节波动：双11/双12/618/春节前高峰
order_rows = []
item_rows = []
oid = 1
iid = 1

# 活跃用户比例：约 60% 用户下过单
active_users = users.sample(frac=0.62, random_state=1).reset_index(drop=True)

for idx, u in active_users.iterrows():
    # 每个活跃用户 1~25 个订单
    n_orders = max(1, int(np.random.poisson(3.5)))
    for _ in range(n_orders):
        # 下单时间偏向注册后
        days_since_reg = max(1, (start - u["register_time"]).days)
        if days_since_reg < 0:
            continue
        rand_day = int(np.random.uniform(max(0, days_since_reg), days))
        order_time = start + timedelta(days=rand_day, hours=int(np.random.uniform(8,23)), minutes=int(np.random.uniform(0,59)))
        # 季节倍率
        m = order_time.month
        seasonal = 1.0
        if m in [6, 11, 12]: seasonal = 1.6
        if m == 2: seasonal = 0.6
        if np.random.random() > seasonal / 1.6:  # 抽稀模拟
            continue
        status = np.random.choice(["已支付", "已退款", "已取消"], p=[0.88, 0.07, 0.05])
        order_id = f"O{oid:07d}"
        order_rows.append({
            "order_id": order_id,
            "user_id": u["user_id"],
            "order_time": order_time,
            "city": u["city"],
            "status": status,
        })
        oid += 1
        # 1~4 个商品
        n_items = np.random.choice([1,2,3,4], p=[0.45,0.30,0.15,0.10])
        for _ in range(n_items):
            p = products.sample(1, random_state=np.random.randint(0,999999)).iloc[0]
            qty = int(np.random.choice([1,1,1,2,3]))
            discount = np.random.choice([1.0,0.95,0.9,0.85,0.8], p=[0.4,0.2,0.2,0.12,0.08])
            unit_price = round(p["price"] * discount, 2)
            item_rows.append({
                "order_id": order_id,
                "product_id": p["product_id"],
                "category": p["category"],
                "qty": qty,
                "unit_price": unit_price,
                "amount": round(unit_price * qty, 2),
            })
            iid += 1

orders = pd.DataFrame(order_rows)
order_items = pd.DataFrame(item_rows)

# ---------- refunds ----------
refunded_orders = orders[orders["status"] == "已退款"].sample(frac=1.0, random_state=2).reset_index(drop=True)
refund_rows = []
for _, o in refunded_orders.iterrows():
    items = order_items[order_items["order_id"] == o["order_id"]]
    refund_rows.append({
        "refund_id": f"R{len(refund_rows)+1:06d}",
        "order_id": o["order_id"],
        "user_id": o["user_id"],
        "refund_time": o["order_time"] + timedelta(days=int(np.random.uniform(1,15))),
        "refund_amount": round(items["amount"].sum() * np.random.uniform(0.7,1.0), 2),
        "reason": np.random.choice(["质量问题","七天无理由","描述不符","物流破损","其他"]),
    })
refunds = pd.DataFrame(refund_rows)

# ---------- behavior 行为流水 ----------
# 每个活跃用户每天若干行为，漏斗：曝光→点击→加购→下单→支付
behavior_rows = []
bid = 1
for idx, u in active_users.iterrows():
    n_sessions = int(np.random.poisson(8))  # 该用户会有 8 次访问会话
    for s in range(n_sessions):
        rand_day = int(np.random.uniform(0, days))
        ts = start + timedelta(days=rand_day, hours=int(np.random.uniform(8,23)), minutes=int(np.random.uniform(0,59)))
        # 漏斗
        n_expo = int(np.random.randint(5, 25))
        for _ in range(n_expo):
            p = products.sample(1).iloc[0]
            behavior_rows.append({"event_id": f"B{bid:08d}", "user_id": u["user_id"], "event_time": ts, "event_type": "曝光", "product_id": p["product_id"]})
            bid += 1
            # 点击转化 ~25%
            if np.random.random() < 0.25:
                behavior_rows.append({"event_id": f"B{bid:08d}", "user_id": u["user_id"], "event_time": ts + timedelta(seconds=int(np.random.uniform(2,30))), "event_type": "点击", "product_id": p["product_id"]})
                bid += 1
                # 加购 ~30%
                if np.random.random() < 0.30:
                    behavior_rows.append({"event_id": f"B{bid:08d}", "user_id": u["user_id"], "event_time": ts + timedelta(seconds=int(np.random.uniform(30,180))), "event_type": "加购", "product_id": p["product_id"]})
                    bid += 1
behavior = pd.DataFrame(behavior_rows)

# ---------- 输出 ----------
users.drop(columns=["register_date"]).to_csv(os.path.join(OUT, "users.csv"), index=False, encoding="utf-8-sig")
products.to_csv(os.path.join(OUT, "products.csv"), index=False, encoding="utf-8-sig")
orders.to_csv(os.path.join(OUT, "orders.csv"), index=False, encoding="utf-8-sig")
order_items.to_csv(os.path.join(OUT, "order_items.csv"), index=False, encoding="utf-8-sig")
refunds.to_csv(os.path.join(OUT, "refunds.csv"), index=False, encoding="utf-8-sig")
behavior.to_csv(os.path.join(OUT, "behavior.csv"), index=False, encoding="utf-8-sig")

print("=== 数据集生成完成 ===")
for name, df in [("users",users),("products",products),("orders",orders),("order_items",order_items),("refunds",refunds),("behavior",behavior)]:
    print(f"{name:15s} rows={len(df):>7d}")
print(f"GMV(已支付): {order_items.merge(orders[orders.status=='已支付'][['order_id']],on='order_id')['amount'].sum():,.2f}")
