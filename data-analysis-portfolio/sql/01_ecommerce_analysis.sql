-- ============================================================
-- 作品1：MySQL 电商销售数据清洗与指标分析
-- 数据库：ecommerce_demo
-- 说明：本脚本与 ../data/*.csv 配套，导入后可直接运行
-- ============================================================

-- ---------- 0. 建库 ----------
CREATE DATABASE IF NOT EXISTS ecommerce_demo DEFAULT CHARSET utf8mb4;
USE ecommerce_demo;

-- ---------- 1. 建表 ----------
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS refunds;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS behavior;

CREATE TABLE users (
  user_id        VARCHAR(20)  PRIMARY KEY COMMENT '用户ID',
  register_time  DATETIME     COMMENT '注册时间',
  city           VARCHAR(20)  COMMENT '城市',
  channel        VARCHAR(20)  COMMENT '获客渠道'
) COMMENT '用户表';

CREATE TABLE products (
  product_id     VARCHAR(20)  PRIMARY KEY COMMENT '商品ID',
  category       VARCHAR(20)  COMMENT '品类',
  product_name   VARCHAR(100) COMMENT '商品名',
  price          DECIMAL(10,2) COMMENT '售价',
  cost           DECIMAL(10,2) COMMENT '成本'
) COMMENT '商品表';

CREATE TABLE orders (
  order_id       VARCHAR(20)  PRIMARY KEY COMMENT '订单ID',
  user_id        VARCHAR(20)  COMMENT '用户ID',
  order_time     DATETIME     COMMENT '下单时间',
  city           VARCHAR(20)  COMMENT '下单城市',
  status         VARCHAR(20)  COMMENT '状态：已支付/已退款/已取消'
) COMMENT '订单主表';

CREATE TABLE order_items (
  order_id       VARCHAR(20)  COMMENT '订单ID',
  product_id     VARCHAR(20)  COMMENT '商品ID',
  category       VARCHAR(20)  COMMENT '品类（冗余）',
  qty            INT          COMMENT '数量',
  unit_price     DECIMAL(10,2) COMMENT '成交单价',
  amount         DECIMAL(12,2) COMMENT '行金额',
  PRIMARY KEY (order_id, product_id)
) COMMENT '订单明细表';

CREATE TABLE refunds (
  refund_id      VARCHAR(20)  PRIMARY KEY,
  order_id       VARCHAR(20),
  user_id        VARCHAR(20),
  refund_time    DATETIME,
  refund_amount  DECIMAL(12,2),
  reason         VARCHAR(20)
) COMMENT '退款表';

CREATE TABLE behavior (
  event_id       VARCHAR(20)  PRIMARY KEY,
  user_id        VARCHAR(20),
  event_time     DATETIME,
  event_type     VARCHAR(20)  COMMENT '曝光/点击/加购/下单/支付',
  product_id     VARCHAR(20)
) COMMENT '用户行为流水';

-- 导入 CSV（示例，按本机路径调整）
-- LOAD DATA LOCAL INFILE 'data/users.csv'        INTO TABLE users        FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' IGNORE 1 ROWS;
-- LOAD DATA LOCAL INFILE 'data/products.csv'    INTO TABLE products    FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' IGNORE 1 ROWS;
-- LOAD DATA LOCAL INFILE 'data/orders.csv'      INTO TABLE orders      FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' IGNORE 1 ROWS;
-- LOAD DATA LOCAL INFILE 'data/order_items.csv' INTO TABLE order_items FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' IGNORE 1 ROWS;
-- LOAD DATA LOCAL INFILE 'data/refunds.csv'    INTO TABLE refunds     FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' IGNORE 1 ROWS;
-- LOAD DATA LOCAL INFILE 'data/behavior.csv'   INTO TABLE behavior    FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' IGNORE 1 ROWS;

-- ============================================================
-- 2. 数据清洗与质量检查
-- ============================================================

-- 2.1 重复订单
SELECT order_id, COUNT(*) c FROM orders GROUP BY order_id HAVING c > 1;

-- 2.2 孤儿订单明细（order_items 中的 order_id 不在 orders 表）
SELECT i.* FROM order_items i
LEFT JOIN orders o ON i.order_id = o.order_id
WHERE o.order_id IS NULL;

-- 2.3 异常金额（负数或为 0）
SELECT * FROM order_items WHERE amount <= 0 OR qty <= 0;

-- 2.4 指标口径：只统计"已支付"订单的 GMV
CREATE OR REPLACE VIEW v_paid_orders AS
SELECT o.order_id, o.user_id, o.order_time, o.city
FROM orders o WHERE o.status = '已支付';

CREATE OR REPLACE VIEW v_paid_items AS
SELECT i.* FROM order_items i
JOIN v_paid_orders o ON i.order_id = o.order_id;

-- ============================================================
-- 3. 核心指标：GMV / 订单量 / 客单价 / 同比环比
-- ============================================================

-- 3.1 月度大盘
SELECT
  DATE_FORMAT(order_time, '%Y-%m')                            AS ym,
  COUNT(DISTINCT o.order_id)                                 AS order_cnt,
  COUNT(DISTINCT o.user_id)                                  AS buyer_cnt,
  ROUND(SUM(i.amount), 2)                                    AS gmv,
  ROUND(SUM(i.amount) / COUNT(DISTINCT o.order_id), 2)        AS aov
FROM v_paid_orders o
JOIN v_paid_items i ON o.order_id = i.order_id
GROUP BY ym ORDER BY ym;

-- 3.2 同比环比（窗口函数 LAG）
WITH m AS (
  SELECT DATE_FORMAT(order_time,'%Y-%m') ym,
         SUM(i.amount) gmv
  FROM v_paid_orders o JOIN v_paid_items i ON o.order_id=i.order_id
  GROUP BY ym
)
SELECT ym, gmv,
       LAG(gmv,1)  OVER (ORDER BY ym) AS mom_prev,
       ROUND((gmv - LAG(gmv,1) OVER (ORDER BY ym)) /
             LAG(gmv,1) OVER (ORDER BY ym) * 100, 2) AS mom_pct,
       LAG(gmv,12) OVER (ORDER BY ym) AS yoy_prev,
       ROUND((gmv - LAG(gmv,12) OVER (ORDER BY ym)) /
             LAG(gmv,12) OVER (ORDER BY ym) * 100, 2) AS yoy_pct
FROM m ORDER BY ym;

-- ============================================================
-- 4. 品类 / 地区分析
-- ============================================================

-- 4.1 品类销售占比与同比
WITH c AS (
  SELECT i.category,
         YEAR(o.order_time) yr,
         SUM(i.amount) gmv
  FROM v_paid_orders o JOIN v_paid_items i ON o.order_id=i.order_id
  GROUP BY i.category, yr
)
SELECT category,
       SUM(CASE WHEN yr=2024 THEN gmv END) AS gmv_2024,
       SUM(CASE WHEN yr=2025 THEN gmv END) AS gmv_2025,
       ROUND((SUM(CASE WHEN yr=2025 THEN gmv END) -
              SUM(CASE WHEN yr=2024 THEN gmv END)) /
             SUM(CASE WHEN yr=2024 THEN gmv END) * 100, 2) AS yoy_pct,
       ROUND(SUM(gmv) / SUM(SUM(gmv)) OVER () * 100, 2) AS share_pct
FROM c GROUP BY category ORDER BY gmv_2025 DESC;

-- 4.2 城市 TOP10
SELECT city, COUNT(DISTINCT o.order_id) orders,
       ROUND(SUM(i.amount),2) gmv,
       RANK() OVER (ORDER BY SUM(i.amount) DESC) AS rk
FROM v_paid_orders o JOIN v_paid_items i ON o.order_id=i.order_id
GROUP BY city ORDER BY gmv DESC LIMIT 10;

-- ============================================================
-- 5. RFM 用户分层
-- ============================================================
-- 数据截止日取 2025-12-31
WITH rfm AS (
  SELECT user_id,
         DATEDIFF('2025-12-31', MAX(order_time)) AS recency,
         COUNT(DISTINCT order_id)                AS frequency,
         SUM(amount)                             AS monetary
  FROM v_paid_orders o
  JOIN (SELECT order_id, SUM(amount) amount FROM v_paid_items GROUP BY order_id) s
    ON o.order_id = s.order_id
  GROUP BY user_id
),
score AS (
  SELECT *,
    NTILE(5) OVER (ORDER BY recency ASC)        AS r_score,  -- 越近分越高
    NTILE(5) OVER (ORDER BY frequency DESC)    AS f_score,
    NTILE(5) OVER (ORDER BY monetary DESC)    AS m_score
  FROM rfm
)
SELECT
  CASE
    WHEN r_score>=4 AND f_score>=4 AND m_score>=4 THEN '高价值用户'
    WHEN r_score>=4 AND f_score<=2                THEN '新客/召回潜力'
    WHEN r_score<=2 AND f_score>=4                THEN '流失高价值'
    WHEN r_score<=2 AND f_score<=2                THEN '流失用户'
    ELSE '一般维持'
  END AS segment,
  COUNT(*) AS user_cnt,
  ROUND(AVG(monetary),2) AS avg_amount,
  ROUND(SUM(monetary) / SUM(SUM(monetary)) OVER () * 100, 2) AS gmv_share_pct
FROM score
GROUP BY segment ORDER BY gmv_share_pct DESC;

-- ============================================================
-- 6. 行为漏斗：曝光 → 点击 → 加购 → 下单 → 支付
-- ============================================================
SELECT event_type, COUNT(DISTINCT user_id) uv, COUNT(*) events
FROM behavior
GROUP BY event_type
ORDER BY FIELD(event_type, '曝光','点击','加购');
-- 注：下单/支付事件在 behavior 表中以订单数据为准，作品5中完整实现。
