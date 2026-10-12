# 数据字典

数据集为模拟数据（非真实公司数据），用于作品集演示。

## users（用户表，2000 行）

| 字段 | 类型 | 说明 |
|---|---|---|
| user_id | VARCHAR(20) | 用户唯一ID，主键 |
| register_time | DATETIME | 注册时间 |
| city | VARCHAR(20) | 所在城市（12 个一二线城市） |
| channel | VARCHAR(20) | 获客渠道：自然搜索/朋友圈广告/抖音/小红书/线下门店/老客推荐 |

## products（商品表，96 行）

| 字段 | 类型 | 说明 |
|---|---|---|
| product_id | VARCHAR(20) | 商品ID，主键 |
| category | VARCHAR(20) | 品类：服饰/数码/家居/食品/美妆/母婴/运动/图书 |
| product_name | VARCHAR(100) | 商品名 |
| price | DECIMAL(10,2) | 标价 |
| cost | DECIMAL(10,2) | 成本 |

## orders（订单主表，约 3100 行）

| 字段 | 类型 | 说明 |
|---|---|---|
| order_id | VARCHAR(20) | 订单ID，主键 |
| user_id | VARCHAR(20) | 下单用户 |
| order_time | DATETIME | 下单时间 |
| city | VARCHAR(20) | 下单城市 |
| status | VARCHAR(20) | 已支付 / 已退款 / 已取消 |

## order_items（订单明细，约 6000 行）

| 字段 | 类型 | 说明 |
|---|---|---|
| order_id | VARCHAR(20) | 订单ID |
| product_id | VARCHAR(20) | 商品ID |
| category | VARCHAR(20) | 品类冗余 |
| qty | INT | 数量 |
| unit_price | DECIMAL(10,2) | 成交单价（含折扣） |
| amount | DECIMAL(12,2) | 行金额 = unit_price × qty |

## refunds（退款表，约 240 行）

| 字段 | 类型 | 说明 |
|---|---|---|
| refund_id | VARCHAR(20) | 退款ID |
| order_id | VARCHAR(20) | 原订单ID |
| user_id | VARCHAR(20) | 用户ID |
| refund_time | DATETIME | 退款时间 |
| refund_amount | DECIMAL(12,2) | 退款金额 |
| reason | VARCHAR(20) | 退款原因 |

## behavior（行为流水，约 19 万行）

| 字段 | 类型 | 说明 |
|---|---|---|
| event_id | VARCHAR(20) | 事件ID |
| user_id | VARCHAR(20) | 用户ID |
| event_time | DATETIME | 事件时间 |
| event_type | VARCHAR(20) | 曝光 / 点击 / 加购 |
| product_id | VARCHAR(20) | 涉及商品 |

## 指标口径

- **GMV**：仅统计 status='已支付' 订单的 order_items.amount 合计
- **客单价 AOV**：GMV / 支付订单数
- **复购率**：下单 ≥2 次的用户数 / 下单用户数
- **漏斗转化率**：下一级 UV / 上一级 UV
- **RFM**：R=距 2025-12-31 天数，F=支付订单数，M=累计支付金额；各按 5 分位打分
