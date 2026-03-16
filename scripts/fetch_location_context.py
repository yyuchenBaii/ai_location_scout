import os
import sys
import json
import ssl
import urllib.request
from urllib.parse import urlencode

# macOS Python 3.12 SSL workaround
_SSL_CTX = ssl._create_unverified_context()

# 【使用说明】
# 地段画像脚本 — 调用逆地理编码 + 步行路径规划，生成选址地段的客观上下文信息
# 用法：python fetch_location_context.py "<经度,纬度>"
# 输出：行政区、所属商圈、周边地标、到最近地铁口的步行时长及截流判定

AMAP_WEB_KEY = os.environ.get("AMAP_WEB_KEY", "YOUR_AMAP_LBS_WEB_SERVICE_KEY")


def _amap_get(url, params):
    """通用 GET 请求封装"""
    req_url = f"{url}?{urlencode(params)}"
    try:
        with urllib.request.urlopen(
            urllib.request.Request(req_url), context=_SSL_CTX, timeout=8
        ) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"status": "0", "_error": str(e)}


def fetch_regeo(location):
    """逆地理编码：坐标 → 行政区划 + 商圈 + 周边地标"""
    result = _amap_get(
        "https://restapi.amap.com/v3/geocode/regeo",
        {
            "key": AMAP_WEB_KEY,
            "location": location,
            "extensions": "all",   # 含 pois（周边地标）和 businessAreas
            "radius": 500,
            "output": "json",
        }
    )
    if result.get("status") != "1":
        return None, result.get("info", "逆地理编码失败")

    regeo = result.get("regeocode") or {}
    addr_comp = regeo.get("addressComponent") or {}
    if isinstance(addr_comp, list):
        addr_comp = {}

    district = addr_comp.get("district") if isinstance(addr_comp.get("district"), str) else ""
    township = addr_comp.get("township") if isinstance(addr_comp.get("township"), str) else ""
    street_num = addr_comp.get("streetNumber") or {}
    if isinstance(street_num, list):
        street_num = {}
    street = street_num.get("street") if isinstance(street_num.get("street"), str) else ""
    number = street_num.get("number") if isinstance(street_num.get("number"), str) else ""
    formatted = regeo.get("formatted_address") if isinstance(regeo.get("formatted_address"), str) else ""

    # 商圈（可能有多个，取前两个）
    biz_areas = addr_comp.get("businessAreas") or []
    if isinstance(biz_areas, dict):
        biz_areas = [biz_areas]  # Just in case AMap returns a single dict instead of list
    elif isinstance(biz_areas, str):
        biz_areas = []
    biz_area_names = [b.get("name", "") for b in biz_areas[:2] if isinstance(b, dict) and b.get("name")]

    # 周边地标（取前3个，距离最近的知名 POI）
    pois = regeo.get("pois") or []
    if not isinstance(pois, list):
        pois = []
    landmarks = []
    for p in pois[:3]:
        name = p.get("name", "")
        dist = p.get("distance", "")
        direction = p.get("direction", "")
        if name and dist:
            landmarks.append(f"{direction}{dist}米处{name}" if direction else f"距{name}{dist}米")

    return {
        "district": district,
        "township": township,
        "street_address": f"{street}{number}" if street else "",
        "formatted_address": formatted,
        "business_areas": biz_area_names,
        "nearby_landmarks": landmarks,
    }, None


def fetch_nearest_metro(location):
    """在 500m 内搜索最近地铁站入口，返回其坐标和名称"""
    result = _amap_get(
        "https://restapi.amap.com/v3/place/around",
        {
            "key": AMAP_WEB_KEY,
            "location": location,
            "keywords": "地铁站",
            "types": "150500",   # 地铁站类型
            "radius": 1500,
            "extensions": "base",
            "offset": 5,
            "page": 1,
            "output": "json",
            "sortrule": "distance",
        }
    )
    if result.get("status") != "1":
        return None, None

    pois = result.get("pois", [])
    if not pois:
        return None, None

    metro = pois[0]
    return metro.get("location", ""), metro.get("name", "未知地铁站")


def fetch_walk_time(origin, destination):
    """步行路径规划：返回步行时长（分钟）和距离（米）"""
    result = _amap_get(
        "https://restapi.amap.com/v3/direction/walking",
        {
            "key": AMAP_WEB_KEY,
            "origin": origin,
            "destination": destination,
            "output": "json",
        }
    )
    if result.get("status") != "1":
        return None, None

    try:
        route = result.get("route", {}).get("paths", [])[0]
        if isinstance(route, list) or not route: return None, None
        duration_sec = int(route.get("duration", 0))
        distance_m = int(route.get("distance", 0))
        return round(duration_sec / 60, 1), distance_m
    except (KeyError, IndexError, ValueError, TypeError):
        return None, None

def fetch_poi_count(location, types, radius=500):
    """搜索周边指定类型的 POI 数量"""
    result = _amap_get(
        "https://restapi.amap.com/v3/place/around",
        {
            "key": AMAP_WEB_KEY,
            "location": location,
            "types": types,
            "radius": radius,
            "extensions": "base",
            "offset": 1,
            "page": 1,
            "output": "json",
        }
    )
    if result.get("status") != "1":
        return 0
    return int(result.get("count", 0))


def fetch_location_context(location):
    """
    主函数：聚合逆地理编码 + 最近地铁步行时长
    :param location: "经度,纬度" 字符串
    """
    # Step 1: 逆地理编码
    regeo_data, err = fetch_regeo(location)
    if err:
        return {"error": f"逆地理编码失败: {err}"}

    # Step 2: 找最近地铁站入口
    metro_loc, metro_name = fetch_nearest_metro(location)

    metro_info = {}
    if metro_loc:
        walk_min, walk_m = fetch_walk_time(location, metro_loc)
        if walk_min is not None:
            metro_info = {
                "nearest_metro": metro_name,
                "metro_walk_minutes": walk_min,
                "metro_walk_meters": walk_m,
                # 核心判定：步行≤5分钟 = 地铁截流位（高客流），>5分钟 = 非截流位
                "metro_flow_capture": walk_min <= 5,
                "metro_flow_label": (
                    f"✅ 地铁截流位（步行{walk_min}分钟）"
                    if walk_min <= 5 else
                    f"⚠️ 非截流位（步行{walk_min}分钟，地铁自然客流有限）"
                ),
            }
        else:
            metro_info = {"nearest_metro": metro_name, "metro_walk_minutes": None}
    else:
        metro_info = {
            "nearest_metro": "1500m内无地铁站",
            "metro_flow_capture": False,
            "metro_flow_label": "❌ 无地铁覆盖，客流依赖周边自然人流",
        }

    # Step 3: 获取写字楼与住宅区数量，进行潮汐推演
    office_count = fetch_poi_count(location, "120200", radius=500) # 写字楼
    residential_count = fetch_poi_count(location, "120300", radius=500) # 住宅区

    return {
        **regeo_data,
        **metro_info,
        "office_count": office_count,
        "residential_count": residential_count,
        "_note": "以上数据来源：高德逆地理编码 + 步行路径规划，均为真实 API 数据，可溯源验证。",
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "用法: python fetch_location_context.py <经度,纬度>"}))
        sys.exit(1)

    loc = sys.argv[1]
    result = fetch_location_context(loc)
    print(json.dumps(result, ensure_ascii=False, indent=2))
