import os
import sys
import json
import urllib.request
from urllib.parse import urlencode

# 【使用说明】
# 本脚本旨在被 OpenClaw 或其他 Agent 平台在后台调用 (Function Calling)。
# Agent 在获取用户提供的地理位置并解析出经纬度后，向本脚本传入坐标和业态关键字。
# 脚本返回该坐标周边 2 公里内的真实竞品密度、最高分评价店及价格带，供 Agent 生成最终的研报数据。

# 高德地图 Web 服务 API Key (建议通过环境变量注入，此处为演示占位)
AMAP_WEB_KEY = "YOUR_AMAP_LBS_WEB_SERVICE_KEY"

def fetch_poi_data(location, keywords, radius=2000):
    """
    调用高德周边搜索 API
    :param location: 经纬度 "119.967, 30.380" 形态
    :param keywords: 搜索关键字，例如 "咖啡" 或 "便利店"
    :param radius: 搜索半径 (米)
    :return: 包含数量统计和竞品列表的字典
    """
    url = "https://restapi.amap.com/v3/place/around"
    params = {
        "key": AMAP_WEB_KEY,
        "location": location,
        "keywords": keywords,
        "radius": radius,
        "extensions": "all",
        "output": "json",
        "offset": 50,  # 一页最多取 50 条 (用于评估竞争度)
        "page": 1
    }
    
    query_string = urlencode(params)
    request_url = f"{url}?{query_string}"
    
    try:
        req = urllib.request.Request(request_url)
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if result.get("status") == "1":
                pois = result.get("pois", [])
                
                # 简单的数据清洗与商业洞察提取
                total_competitors = int(result.get("count", 0))
                closest_competitor = pois[0]["name"] if pois else "无"
                closest_distance = pois[0]["distance"] if pois else "未知"
                
                # 提取评分最高的竞品 (粗略提取评价好于 4.0 的店)
                high_rating_competitors = [p for p in pois if p.get("biz_ext", {}).get("rating", "0") >= "4.0"]
                
                insight = {
                    "search_keyword": keywords,
                    "search_radius_meters": radius,
                    "total_competitors_found": total_competitors,
                    "closest_competitor": f"{closest_competitor} (距离 {closest_distance}米)",
                    "competition_level": "🔥 极度红海 (饱和)" if total_competitors > 30 else ("⚠️ 存在竞争" if total_competitors > 10 else "🟢 局部蓝海"),
                    "high_quality_combatants": len(high_rating_competitors),
                    "raw_top_3": [{"name": p["name"], "type": p["type"], "distance": p["distance"]} for p in pois[:3]]
                }
                return insight
            else:
                return {"error": "高德 API 返回失败", "info": result.get("info")}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # 解析命令行参数
    # 用法示例： python fetch_amap_poi.py "119.967,30.380" "咖啡"
    if len(sys.argv) < 3:
        print(json.dumps({"error": "缺少参数。用法: python fetch_amap_poi.py <经纬度> <关键字>"}))
        sys.exit(1)
        
    loc = sys.argv[1]
    kw = sys.argv[2]
    
    # 强制加上类型限制避免搜出毫不相干的比如咖啡工厂
    # 在实际应用可以更精细
    result_data = fetch_poi_data(loc, kw)
    
    # 标准的输出现场，大模型通过读取 stdout 的 JSON 来吸收真实环境数据
    print(json.dumps(result_data, ensure_ascii=False, indent=2))
