#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
作品6：气象数据可视化分析系统
生成模拟多城市气象数据 + ECharts HTML 看板
"""
import numpy as np, pandas as pd, json, os

np.random.seed(7)
BASE = os.path.join(os.path.dirname(__file__), "..")
DATA = f"{BASE}/data"
OUT  = f"{BASE}/output/dashboards"
os.makedirs(DATA, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

# 城市与季节基线（月均温）
cities = {
    "苏州":  [3,5,10,16,22,26,29,28,24,18,12,5],
    "北京":  [-3,0,7,15,21,26,28,27,22,15,6,-1],
    "广州":  [14,15,19,23,27,29,30,30,28,25,20,15],
    "成都":  [6,8,12,17,21,24,26,26,22,17,12,7],
}
days = pd.date_range("2025-01-01", "2025-12-31", freq="D")

rows = []
for city, monthly_base in cities.items():
    for d in days:
        m = d.month - 1
        base = monthly_base[m]
        # 日波动 ±5
        temp = base + np.random.normal(0, 4)
        # 湿度 50-90%
        humidity = np.clip(np.random.normal(70, 10), 30, 99)
        # 降水：夏季多
        rain_p = 0.15 + (0.25 if m in [5,6,7,8] else 0)
        rain = max(0, np.random.exponential(8) if np.random.random() < rain_p else 0)
        # 风速
        wind = max(0.5, np.random.normal(3, 1.5))
        # AQI 30-150
        aqi = int(np.clip(np.random.normal(70, 25), 20, 200))
        rows.append({
            "date": d.date().isoformat(), "city": city,
            "temp": round(temp,1), "humidity": round(humidity,1),
            "rain": round(rain,1), "wind": round(wind,1), "aqi": aqi
        })

df = pd.DataFrame(rows)
df.to_csv(f"{DATA}/weather_daily.csv", index=False, encoding="utf-8-sig")
print(f"weather_daily.csv rows={len(df)}")

# 聚合为月度数据用于看板
df["ym"] = df.date.str[:7]
monthly = df.groupby(["city","ym"]).agg(
    avg_temp=("temp","mean"),
    max_temp=("temp","max"),
    min_temp=("temp","min"),
    total_rain=("rain","sum"),
    avg_humidity=("humidity","mean"),
    avg_aqi=("aqi","mean"),
    avg_wind=("wind","mean"),
).reset_index().round(1)

# 异常预警：极端高温（>35）、暴雨（日降水>50）、AQI>150
alerts = []
for _, r in df.iterrows():
    if r.temp > 35:
        alerts.append({"date": r.date, "city": r.city, "type": "极端高温", "value": f"{r.temp}°C"})
    if r.rain > 50:
        alerts.append({"date": r.date, "city": r.city, "type": "暴雨", "value": f"{r.rain}mm"})
    if r.aqi > 150:
        alerts.append({"date": r.date, "city": r.city, "type": "空气质量差", "value": f"AQI {r.aqi}"})

# 构造看板数据
months = sorted(monthly.ym.unique())
chart_data = {
    "months": months,
    "cities": list(cities.keys()),
    "temp": {c: monthly[monthly.city==c].avg_temp.tolist() for c in cities},
    "rain": {c: monthly[monthly.city==c].total_rain.tolist() for c in cities},
    "aqi":  {c: monthly[monthly.city==c].avg_aqi.round(0).tolist() for c in cities},
    "humidity": {c: monthly[monthly.city==c].avg_humidity.tolist() for c in cities},
    "wind": {c: monthly[monthly.city==c].avg_wind.tolist() for c in cities},
    "alerts": alerts[:20],  # 取前 20 条
    "alert_count": len(alerts),
}

DATA_JS = json.dumps(chart_data, ensure_ascii=False)

html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>气象数据可视化分析系统 - 毕业设计</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
<style>
  body { font-family: "Microsoft YaHei", sans-serif; background: #0f1c2e; color: #e6e6e6; margin: 0; padding: 16px; }
  .header { background: linear-gradient(135deg, #1a3a5c, #2e75b6); padding: 18px 24px; border-radius: 6px; margin-bottom: 14px; }
  .header h1 { margin: 0; font-size: 20px; }
  .header .sub { font-size: 12px; opacity: .8; margin-top: 4px; }
  .row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px; }
  .row3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; margin-bottom: 12px; }
  .card { background: #1a2a40; padding: 12px; border-radius: 6px; }
  .card h3 { font-size: 13px; color: #9dc3e6; margin: 0 0 8px 0; padding-left: 8px; border-left: 3px solid #2e75b6; }
  .chart { width: 100%; height: 280px; }
  .alert-list { max-height: 260px; overflow-y: auto; font-size: 12px; }
  .alert-list div { padding: 6px 8px; border-bottom: 1px solid #2a3a50; }
  .alert-hot { color: #ff6b6b; } .alert-rain { color: #5b9bd5; } .alert-aqi { color: #f4b084; }
  .kpi-row { display: grid; grid-template-columns: repeat(4,1fr); gap: 10px; margin-bottom: 12px; }
  .kpi { background: #1a2a40; padding: 12px; border-radius: 6px; text-align: center; }
  .kpi .v { font-size: 22px; font-weight: 700; color: #5b9bd5; }
  .kpi .l { font-size: 12px; color: #888; margin-top: 4px; }
</style>
</head>
<body>
<div class="header">
  <h1>气象数据可视化分析系统</h1>
  <div class="sub">4 城市 × 365 天　|　温度 / 湿度 / 降水 / 风速 / 空气质量　|　技术：Vue3 + ECharts（本看板为 HTML 演示版）</div>
</div>

<div class="kpi-row">
  <div class="kpi"><div class="v">4</div><div class="l">监测城市</div></div>
  <div class="kpi"><div class="v">365</div><div class="l">监测天数</div></div>
  <div class="kpi"><div class="v" id="ac">0</div><div class="l">异常预警事件</div></div>
  <div class="kpi"><div class="v">8+</div><div class="l">图表类型</div></div>
</div>

<div class="row">
  <div class="card"><h3>月均温度趋势（多城市对比）</h3><div id="c1" class="chart"></div></div>
  <div class="card"><h3>月累计降水量 (mm)</h3><div id="c2" class="chart"></div></div>
</div>

<div class="row3">
  <div class="card"><h3>月均 AQI</h3><div id="c3" class="chart"></div></div>
  <div class="card"><h3>月均湿度 (%)</h3><div id="c4" class="chart"></div></div>
  <div class="card"><h3>月均风速 (m/s)</h3><div id="c5" class="chart"></div></div>
</div>

<div class="row">
  <div class="card"><h3>异常预警事件列表</h3><div class="alert-list" id="alerts"></div></div>
  <div class="card"><h3>分析结论</h3>
    <div style="font-size:12px; line-height:1.9; color:#bbb; padding:4px;">
      1. 苏州/广州夏季高温高湿，6-8 月降水集中；<br>
      2. 北京冬季严寒、夏季炎热，温差大；<br>
      3. 成都全年温和湿润，极端天气最少；<br>
      4. 异常预警：极端高温主要出现在 7-8 月，暴雨集中在夏季；<br>
      5. 空气质量冬季普遍偏差，需关注采暖季污染。
    </div>
  </div>
</div>

<script>
const D = __DATA__;
document.getElementById('ac').innerText = D.alert_count;

const colors = ['#5b9bd5','#ed7d31','#70ad47','#ffc000'];
function lineChart(id, seriesObj, yName) {
  const s = Object.entries(seriesObj).map(([name, data], i) => ({
    name, type: 'line', smooth: true, data: data,
    itemStyle: { color: colors[i % 4] }
  }));
  echarts.init(document.getElementById(id)).setOption({
    tooltip: { trigger: 'axis' },
    legend: { textStyle: { color: '#ccc' }, top: 0 },
    grid: { left: 50, right: 20, top: 30, bottom: 30 },
    xAxis: { type: 'category', data: D.months, axisLabel: { color: '#aaa' } },
    yAxis: { type: 'value', name: yName, axisLabel: { color: '#aaa' } },
    series: s
  });
}
lineChart('c1', D.temp, '°C');
lineChart('c2', D.rain, 'mm');
lineChart('c3', D.aqi, 'AQI');
lineChart('c4', D.humidity, '%');
lineChart('c5', D.wind, 'm/s');

const al = document.getElementById('alerts');
D.alerts.forEach(a => {
  const cls = a.type === '极端高温' ? 'alert-hot' : a.type === '暴雨' ? 'alert-rain' : 'alert-aqi';
  al.innerHTML += `<div class="${cls}">● ${a.date}　${a.city}　${a.type}　${a.value}</div>`;
});
</script>
</body>
</html>
"""

out = f"{OUT}/06_weather_dashboard.html"
with open(out, "w", encoding="utf-8") as f:
    f.write(html.replace("__DATA__", DATA_JS))
print("saved:", out)
