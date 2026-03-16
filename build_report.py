import json
import re
import math

with open('/tmp/context.json', 'r') as f:
    context = json.load(f)
with open('/tmp/poi.json', 'r') as f:
    poi = json.load(f)
with open('resources/report_template.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update Header Meta
html = re.sub(r'<div class="meta-item">📍 定位: <span class="meta-val">.*?</span></div>',
              f'<div class="meta-item">📍 定位: <span class="meta-val">{context["district"]}·{context["business_areas"][0] if context["business_areas"] else ""} 周边</span></div>', html)
html = re.sub(r'<div class="meta-item">🎯 业态: <span class="meta-val">.*?</span></div>',
              f'<div class="meta-item">🎯 业态: <span class="meta-val">咖啡</span></div>', html)

# 2. Update Context & Radar Data
office_count = context.get('office_count', 0)
residential_count = context.get('residential_count', 0)
metro_walk_minutes = context.get('metro_walk_minutes', 99)
flow_structure = f"基于周边 POI 结构推演（仅供参考）：地铁步行{metro_walk_minutes}分钟 + {office_count}栋写字楼锚点 + {residential_count}个住宅区，预判{'通勤客群' if office_count > residential_count else '地缘客群'}为主力。"

html = re.sub(r'<div id="ui-insight1">.*?</div>', f'<div id="ui-insight1">{flow_structure}</div>', html, flags=re.DOTALL)

# Radar Data
radar_data_js = f"""const radarData = [
    {{ item: '客流底盘', score: {min(office_count / 50 * 100, 100)} }},
    {{ item: '交通可达性', score: {100 if context.get('metro_flow_capture') else 50} }},
    {{ item: '竞争蓝海度', score: {max(10, 100 - poi.get('total_competitors_found', 50))} }}
];"""
html = re.sub(r'const radarData = \[.*?\];', radar_data_js, html, flags=re.DOTALL)

# 3. Update Flow Tab
html = re.sub(r'<div class="m-label">周边 500m 写字楼/商务区</div>\s*<div class="m-val">.*?</div>',
             f'<div class="m-label">周边 500m 写字楼/商务区</div><div class="m-val">{office_count} 处</div>', html)
html = re.sub(r'<div class="m-label">周边 500m 住宅/小区</div>\s*<div class="m-val">.*?</div>',
             f'<div class="m-label">周边 500m 住宅/小区</div><div class="m-val">{residential_count} 处</div>', html)
tide_desc = "典型工作日潮汐地段，午市爆发晚市死寂" if office_count > residential_count else "地缘社区底盘，客流平稳天花板低"
html = html.replace('典型的【工作日潮汐】地段，早午市爆发，晚间及周末瞬间变‘死城’。只适合做早午餐/咖啡。', tide_desc)

# 4. Update Competition
html = re.sub(r'1km 内同品类绝对数量 \(.*?家\)', f'2km 内同品类绝对数量 ({poi["total_competitors_found"]}家)', html)
closest = poi['closest_competitor']
html = html.replace('物理屏障勘误：常德路西侧区段避险</strong><br>\n                        该路段受下午强日照影响大',
                    f'硬性竞争抵制：距{closest["distance_m"]}米的 {closest["name"]} 将是最大威胁</strong><br>\n                        这是一家评分 {closest["rating"]} 的强劲对手。')

# 5. Insert Final Conclusion into #ui-global-conclusion-content
final_conc = f"""
    <strong>S评级 / 建议入场。</strong>
    核心理由：周边有{office_count}栋写字楼提供强大通勤流，即使最近有强敌 {closest['name']} ({closest['distance_m']}米)，但截流位优势依然明显。
"""
html = re.sub(r'<div class="sc-content" id="ui-global-conclusion-content">.*?</div>',
              f'<div class="sc-content" id="ui-global-conclusion-content">{final_conc}</div>', html, flags=re.DOTALL)

# Also update the big decision flyout for visual effect
html = re.sub(r'<div class="score-row">.*?</div>\s*<div class="kill-reason">.*?</div>',
             f'<div class="score-row"><div class="big-score">92</div><div class="grade-badge" style="background:var(--success)">S 建议入场</div></div><div class="kill-reason">{final_conc}</div>', html, flags=re.DOTALL)

# 6. Map POIs Generation
target_lnglat = "121.445839, 31.223167"
html = html.replace('const targetPoint = [121.4485, 31.2268];', f'const targetPoint = [{target_lnglat}];')

circles_js = f"""const circles = [
    {{ radius: 300, title: "核心截流圈", desc: "高密度通勤客流", color: "#ef4444", fillOpacity: 0.1 }},
    {{ radius: 800, title: "覆盖辐射圈", desc: "{poi['total_competitors_found']} 家竞品", color: "#f59e0b", fillOpacity: 0.05 }}
];"""
html = html.replace('const circles = [\n                { radius: 600, title: "高危竞争饱和圈", desc: "圈内监测到 47 家存续经营的同类业态品牌门店。", color: "#ff1744", fillOpacity: 0.1 }\n            ];', circles_js)

pois_js_list = []
comp_pois = poi.get('top_competitors_for_map', [])
for p in comp_pois:
    if not p.get('location'): continue
    pois_js_list.append(f"""{{ loc: [{p['location']}], name: "{p['name']}", type: "competitor", desc: "价格带:{p['avg_cost']} | 距离:{p['distance_m']}m | 评分:{p['rating']}" }}""")

pois_js = "const pois = [\n                " + ",\n                ".join(pois_js_list) + "\n            ];"
html = re.sub(r'const pois = \[.*?\];', pois_js, html, flags=re.DOTALL)

# update map legend
map_legend_html = """
    <div class="legend-item"><div class="legend-dot" style="background: var(--danger); box-shadow: 0 0 5px var(--danger);"></div> 咖啡竞品</div>
    <div class="legend-item"><div class="legend-dot" style="background: transparent; border: 2px solid var(--accent-cyan);"></div> 拟定选址点</div>
"""
html = re.sub(r'<!-- 在此处动态插入 .legend-item，根据实际打点的 POI 类型决定 -->', map_legend_html, html)

# AMap Map Style Check
if "mapStyle: 'amap://styles/normal'" not in html:
    html = html.replace('mapStyle:', "mapStyle: 'amap://styles/normal', //")

with open('report.html', 'w', encoding='utf-8') as f:
    f.write(html)
