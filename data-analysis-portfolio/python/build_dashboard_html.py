#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""读取 dashboard_data.json，生成自包含 HTML 看板（ECharts CDN）"""
import json, os

BASE = os.path.join(os.path.dirname(__file__), "..")
with open(f"{BASE}/output/dashboards/dashboard_data.json", encoding="utf-8") as f:
    data = json.load(f)

DATA_JS = json.dumps(data, ensure_ascii=False)

html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>电商经营分析看板 - 张海洋作品集</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: "Microsoft YaHei", -apple-system, sans-serif; background: #f0f2f5; color: #333; padding: 16px; }
  .header { background: linear-gradient(135deg, #1f4e79, #2e75b6); color: #fff; padding: 16px 24px; border-radius: 6px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; }
  .header h1 { font-size: 20px; font-weight: 600; }
  .header .meta { font-size: 12px; opacity: .85; }
  .kpi-row { display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; margin-bottom: 16px; }
  .kpi { background: #fff; padding: 14px 16px; border-radius: 6px; border-left: 3px solid #2e75b6; }
  .kpi .label { font-size: 12px; color: #888; margin-bottom: 6px; }
  .kpi .value { font-size: 22px; font-weight: 700; color: #1f4e79; }
  .kpi.alt { border-left-color: #ed7d31; } .kpi.alt .value { color: #ed7d31; }
  .kpi.g { border-left-color: #70ad47; } .kpi.g .value { color: #70ad47; }
  .grid { display: grid; grid-template-columns: 2fr 1fr; gap: 12px; margin-bottom: 12px; }
  .grid3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; margin-bottom: 12px; }
  .card { background: #fff; padding: 12px; border-radius: 6px; }
  .card h3 { font-size: 14px; color: #555; margin-bottom: 8px; padding-left: 8px; border-left: 3px solid #2e75b6; }
  .chart { width: 100%; height: 280px; }
  .chart-tall { height: 320px; }
  .footer { text-align: center; color: #999; font-size: 12px; padding: 16px 0; }
</style>
</head>
<body>
<div class="header">
  <div>
    <h1>电商经营分析看板</h1>
    <div class="meta">数据周期：2024-01 ~ 2025-12　|　工具：MySQL + Python(Pandas) + ECharts　|　作者：张海洋</div>
  </div>
</div>

<div class="kpi-row">
  <div class="kpi"><div class="label">GMV</div><div class="value" id="k1"></div></div>
  <div class="kpi"><div class="label">支付订单数</div><div class="value" id="k2"></div></div>
  <div class="kpi"><div class="label">购买用户数</div><div class="value" id="k3"></div></div>
  <div class="kpi alt"><div class="label">客单价</div><div class="value" id="k4"></div></div>
  <div class="kpi alt"><div class="label">退款率</div><div class="value" id="k5"></div></div>
  <div class="kpi g"><div class="label">复购率</div><div class="value" id="k6"></div></div>
</div>

<div class="grid">
  <div class="card"><h3>月度 GMV 与订单趋势</h3><div id="c1" class="chart chart-tall"></div></div>
  <div class="card"><h3>用户行为漏斗</h3><div id="c2" class="chart chart-tall"></div></div>
</div>

<div class="grid3">
  <div class="card"><h3>品类 GMV 同比（2024 vs 2025）</h3><div id="c3" class="chart"></div></div>
  <div class="card"><h3>城市 GMV TOP10</h3><div id="c4" class="chart"></div></div>
  <div class="card"><h3>获客渠道 GMV 分布</h3><div id="c5" class="chart"></div></div>
</div>

<div class="grid3">
  <div class="card" style="grid-column: span 2;"><h3>RFM 用户分层（用户数 vs GMV 贡献占比）</h3><div id="c6" class="chart"></div></div>
  <div class="card"><h3>分析结论</h3>
    <div style="font-size:12px; line-height:1.8; color:#555; padding:4px;">
      1. 6 月、11 月为销售高峰，与 618/双11 大促一致；<br>
      2. 数码、服饰为 GMV 前二品类，图书增长乏力；<br>
      3. 曝光→点击转化率约 25%，加购→下单流失最大；<br>
      4. 高价值用户贡献约 40% GMV，需重点维护。
    </div>
  </div>
</div>

<div class="footer">本看板为模拟数据演示，仅用于作品集展示　|　张海洋 · 数据分析工程师</div>

<script>
const D = __DATA__;
document.getElementById('k1').innerText = D.kpi.gmv_fmt;
document.getElementById('k2').innerText = D.kpi.orders.toLocaleString();
document.getElementById('k3').innerText = D.kpi.buyers.toLocaleString();
document.getElementById('k4').innerText = '¥' + D.kpi.aov;
document.getElementById('k5').innerText = D.kpi.refund_rate + '%';
document.getElementById('k6').innerText = D.kpi.repeat_rate + '%';

const baseGrid = { left: 50, right: 20, top: 30, bottom: 30 };

echarts.init(document.getElementById('c1')).setOption({
  tooltip: { trigger: 'axis' },
  legend: { data: ['GMV(元)','订单数'], top: 0 },
  grid: baseGrid,
  xAxis: { type: 'category', data: D.monthly.ym, axisLabel: { rotate: 45 } },
  yAxis: [
    { type: 'value', name: 'GMV' },
    { type: 'value', name: '订单数' }
  ],
  series: [
    { name: 'GMV(元)', type: 'line', smooth: true, data: D.monthly.gmv, itemStyle: { color: '#2e75b6' }, areaStyle: { opacity: .15 } },
    { name: '订单数', type: 'bar', yAxisIndex: 1, data: D.monthly.orders, itemStyle: { color: '#ed7d31', opacity: .7 } }
  ]
});

echarts.init(document.getElementById('c2')).setOption({
  tooltip: { trigger: 'item', formatter: '{b}: {c}' },
  series: [{
    type: 'funnel', left: '10%', width: '80%',
    label: { formatter: '{b}\\n{c}' },
    data: D.funnel.map(x => ({ name: x.stage, value: x.uv }))
  }]
});

echarts.init(document.getElementById('c3')).setOption({
  tooltip: { trigger: 'axis' },
  legend: { data: ['2024','2025'], top: 0 },
  grid: baseGrid,
  xAxis: { type: 'category', data: D.category.name, axisLabel: { rotate: 30 } },
  yAxis: { type: 'value' },
  series: [
    { name: '2024', type: 'bar', data: D.category.gmv_2024, itemStyle: { color: '#a5c8e5' } },
    { name: '2025', type: 'bar', data: D.category.gmv_2025, itemStyle: { color: '#2e75b6' } }
  ]
});

echarts.init(document.getElementById('c4')).setOption({
  tooltip: { trigger: 'axis' },
  grid: { left: 60, right: 20, top: 20, bottom: 20 },
  xAxis: { type: 'value' },
  yAxis: { type: 'category', data: D.city.name.slice(0,10).reverse() },
  series: [{ type: 'bar', data: D.city.gmv.slice(0,10).reverse(), itemStyle: { color: '#70ad47' } }]
});

echarts.init(document.getElementById('c5')).setOption({
  tooltip: { trigger: 'item' },
  series: [{
    type: 'pie', radius: ['40%','70%'],
    data: D.channel.name.map((n,i)=>({name:n, value: D.channel.gmv[i]}))
  }]
});

echarts.init(document.getElementById('c6')).setOption({
  tooltip: { trigger: 'axis' },
  legend: { data: ['用户数','GMV贡献占比(%)'], top: 0 },
  grid: baseGrid,
  xAxis: { type: 'category', data: D.rfm.name },
  yAxis: [
    { type: 'value', name: '用户数' },
    { type: 'value', name: 'GMV占比%', max: 100 }
  ],
  series: [
    { name: '用户数', type: 'bar', data: D.rfm.users, itemStyle: { color: '#2e75b6' } },
    { name: 'GMV贡献占比(%)', type: 'line', yAxisIndex: 1, data: D.rfm.gmv_pct, itemStyle: { color: '#ed7d31' } }
  ]
});
</script>
</body>
</html>
"""

out_path = f"{BASE}/output/dashboards/03_ecommerce_dashboard.html"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html.replace("__DATA__", DATA_JS))
print("saved:", out_path)
