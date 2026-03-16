import os
import sys
import json
import ssl
import urllib.request
from urllib.parse import urlencode

# macOS Python 3.12 SSL workaround
_SSL_CTX = ssl._create_unverified_context()

# 【使用说明】
# 升级版竞品深度扫描脚本 — 充分利用 place/around extensions=all 已返回的 biz_ext 字段
# 新增输出字段：price_distribution（价格带分布）、rating_avg、top_threats、business_area 覆盖度
# 用法：python fetch_amap_poi.py "<经度,纬度>" "<业态关键字>" [半径米数，默认2000]

AMAP_WEB_KEY = os.environ.get("AMAP_WEB_KEY", "YOUR_AMAP_LBS_WEB_SERVICE_KEY")


def _classify_price(cost_str):
    """将 biz_ext.cost 字符串转换为价格带标签"""
    try:
        cost = float(cost_str)
        if cost < 20:
            return "cheap"
        elif cost <= 50:
            return "moderate"
        else:
            return "expensive"
    except (ValueError, TypeError):
        return "unknown"


def _threat_level(rating, distance_m):
    """评估单个竞品的威胁等级"""
    try:
        r = float(rating)
        d = int(distance_m)
    except (ValueError, TypeError):
        return "未知"

    if r >= 4.5 and d <= 200:
        return "极高"
    elif r >= 4.0 and d <= 500:
        return "高"
    elif r >= 3.5 and d <= 1000:
        return "中"
    else:
        return "低"


def fetch_poi_data(location, keywords, radius=2000):
    """
    调用高德周边搜索 API，深度解析 biz_ext 字段
    :param location: 经纬度字符串 "119.967,30.380"
    :param keywords: 搜索关键字，例如 "咖啡" 或 "居酒屋"
    :param radius: 搜索半径（米），默认 2000
    """
    all_pois = []
    total_count = 0

    # 多页抓取（最多 3 页 × 50 条 = 150 条），避免只取 50 条时数据截断
    for page in range(1, 4):
        url = "https://restapi.amap.com/v3/place/around"
        params = {
            "key": AMAP_WEB_KEY,
            "location": location,
            "keywords": keywords,
            "radius": radius,
            "extensions": "all",   # 必须 all 才能拿到 biz_ext
            "output": "json",
            "offset": 50,
            "page": page,
            "sortrule": "distance",
        }
        try:
            req = urllib.request.Request(
                f"{url}?{urlencode(params)}"
            )
            with urllib.request.urlopen(req, context=_SSL_CTX, timeout=8) as resp:
                result = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            break

        if result.get("status") != "1":
            return {"error": "高德 API 返回失败", "info": result.get("info")}

        pois = result.get("pois", [])
        if page == 1:
            total_count = int(result.get("count", 0))
        all_pois.extend(pois)
        if len(pois) < 50:  # 最后一页不足50条，停止翻页
            break

    if not all_pois:
        return {"error": "未找到任何竞品 POI", "search_keyword": keywords}

    # ── 价格带分布 ──────────────────────────────────────────────
    price_dist = {"expensive": 0, "moderate": 0, "cheap": 0, "unknown": 0}
    ratings = []
    business_areas = set()

    for p in all_pois:
        biz = p.get("biz_ext", {})
        price_dist[_classify_price(biz.get("cost", ""))] += 1
        rating = biz.get("rating", "")
        if rating and rating not in ("[]", "暂无"):
            try:
                ratings.append(float(rating))
            except ValueError:
                pass
        ba = p.get("business_area", "")
        if ba:
            business_areas.add(ba)

    rating_avg = round(sum(ratings) / len(ratings), 1) if ratings else None

    # ── TOP 威胁（距离 <500m 且评分 ≥4.0）──────────────────────
    top_threats = []
    for p in all_pois:
        biz = p.get("biz_ext", {})
        dist = p.get("distance", "9999")
        rating = biz.get("rating", "")
        cost = biz.get("cost", "")
        try:
            if int(dist) <= 500 and float(rating) >= 4.0:
                top_threats.append({
                    "name": p["name"],
                    "distance_m": int(dist),
                    "rating": float(rating),
                    "avg_cost_yuan": float(cost) if cost else None,
                    "business_area": p.get("business_area", ""),
                    "threat_level": _threat_level(rating, dist),
                    "location": p.get("location", ""),
                })
        except (ValueError, TypeError):
            continue

    top_threats.sort(key=lambda x: (-{"极高": 4, "高": 3, "中": 2, "低": 1}.get(x["threat_level"], 0), x["distance_m"]))

    # ── 最近竞品（无论评分）────────────────────────────────────
    closest = all_pois[0]
    closest_biz = closest.get("biz_ext", {})

    return {
        "search_keyword": keywords,
        "search_radius_meters": radius,
        "total_competitors_found": total_count,
        "fetched_sample_size": len(all_pois),

        # 最近对手
        "closest_competitor": {
            "name": closest["name"],
            "distance_m": int(closest.get("distance", 0)),
            "rating": closest_biz.get("rating", "暂无"),
            "avg_cost_yuan": closest_biz.get("cost", "暂无"),
            "business_area": closest.get("business_area", ""),
            "location": closest.get("location", ""),
        },

        # 竞争总体评级
        "competition_level": (
            "🔥 极度红海" if total_count > 50 else
            "⚠️ 存在显著竞争" if total_count > 20 else
            "🟢 局部蓝海"
        ),

        # 价格带分布（真实数据，可直接引用）
        "price_distribution": price_dist,
        "price_insight": (
            f"区域内{price_dist['cheap']}家低价(<20元) / "
            f"{price_dist['moderate']}家中档(20-50元) / "
            f"{price_dist['expensive']}家高端(>50元)"
        ),

        # 评分概况
        "rating_avg": rating_avg,
        "high_quality_count": len([r for r in ratings if r >= 4.0]),

        # 极高/高 威胁竞品（500m内评分≥4.0）
        "top_threats": top_threats[:8],
        "top_threats_count": len(top_threats),

        # 商圈覆盖
        "business_areas_covered": list(business_areas),

        # 地图打点用（保留原字段，供 HTML 模板注入）
        "top_competitors_for_map": [
            {
                "name": p["name"],
                "location": p.get("location", ""),
                "type": "competitor",
                "distance_m": int(p.get("distance", 0)),
                "rating": p.get("biz_ext", {}).get("rating", ""),
                "avg_cost": p.get("biz_ext", {}).get("cost", ""),
                "business_area": p.get("business_area", ""),
            }
            for p in all_pois[:60]
        ],
    }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({"error": "用法: python fetch_amap_poi.py <经度,纬度> <关键字> [半径]"}))
        sys.exit(1)

    loc = sys.argv[1]
    kw = sys.argv[2]
    rad = int(sys.argv[3]) if len(sys.argv) > 3 else 2000

    result_data = fetch_poi_data(loc, kw, rad)
    print(json.dumps(result_data, ensure_ascii=False, indent=2))
