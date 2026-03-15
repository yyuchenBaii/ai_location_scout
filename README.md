# 🕵️‍♂️ Location Scout Ultimate (AI 顶级开店选址专家)

这是一个基于大语言模型（LLM）的**高阶商业地产咨询智能体 Skill 包**。
结合高德地图（AMap）JSAPI 和 LBS Web 服务能力，它可以根据用户口语化的需求，智能推演**“小白选址、多方案对比、加盟商防坑”**等 8 大核心商业场景，并实时渲染出极具科技感与数据密度的可交互《暗黑定制研报》。

---

## ✨ 核心特性

1. **🧠 智能意图路由 (8-Case Intent Router)**
   大模型不再是刻板的问答机，而是被赋予了顶级地产咨询合伙人的“人格”。它能自动识别 8 种典型的选址困境：
   - `Case 1`: 散户核验（“这个地址能不能开？” $\rightarrow$ 侧重防守排雷）
   - `Case 2/3`: 对比与探索（“80万预算开咖啡馆选哪？” $\rightarrow$ 生成多址对比前端页面）
   - `Case 5`: 房东视角反向招商（“我有个铺子适合租给谁？”）
   ...详见 `SKILL.md` 的路由逻辑设定。

2. **📊 10 维深度数据解剖模型**
   自动穿透：宏观能级、客流潮汐、红海竞争度、有效客质鉴伪、租售比预警、非量化黑天鹅风险、落位视觉盲区、天花板测算。

3. **🌍 真机现实挂载 (Tool Use / Function Calling)**
   内置轻量级 Python 爬虫 `scripts/fetch_amap_poi.py`。
   AI 分析时不会“幻觉瞎编分数”，而是静默请求真实世界（高德 LBS API）获取半径 2 公里内的竞品饱和度、Top 质量对手距离，再融合进分析面板。

4. **🖥️ 前端沉浸式交付 (Zero-Waste UI)**
   针对“多选比对”或“深度剖析”，直接通过大模型吐出完整的包含交互 JS/CSS 的单页面 HTML (`resources/` 模板)。
   - 内置基于 `AntV G2Plot` 的雷达图。
   - 内置高德 3D 暗黑底图与高价值节点/风险红海标记。

---

## 🚀 目录结构

```text
ai_location_scout/
├── SKILL.md                          # 核心！大脑提示词与意图路由逻辑，放入 System Prompt
├── resources/                        
│   ├── report_template.html          # 单一选址场景下，大模型最终吐出的深度报告前端骨架
│   └── location_report_comparison.html # 多址对比场景下，自带 JS 切换器的高频交互面板
└── scripts/                          
    └── fetch_amap_poi.py             # 供 Agent 平台 Action 节点调用的 Python 工具脚本 (获取周边咖啡/餐饮竞品数)
```

---

## 🛠️ 安装与配置指南

无论你使用的是 **Coze (扣子), Dify, FastGPT, 还是终端工具 OpenClaw**，部署逻辑均一致。

### 1. 配置提示词 (System Prompt)
将本项目根目录下的 `SKILL.md` 内容全文复制，粘贴到你的 Agent 系统的“人设与回复逻辑”中。

### 2. 申请并填入高德地图双端 API Key
考虑到安全隔离，本项目将前端画图与后端取数的 Key 分离处理。请前往 [高德开放平台](https://console.amap.com/) 免费申请：
- **Web 前端 (JS API) Key**：
  替换 `resources/*.html` 中头部的 `securityJsCode` 与 `src="...key="` 参数。
- **Web 服务 (LBS) Key**：
  替换 `scripts/fetch_amap_poi.py` 顶部的 `AMAP_WEB_KEY = ""` 变量。

### 3. 配置工具调用 (Tools / Action / Plugins)
将 `scripts/fetch_amap_poi.py` 包装为一个 Python 工具/函数，暴露给大模型。
- **工具名称**: `fetch_real_poi_data`
- **入参**: `location` (经纬度字符串, 如 "119.967,30.380"), `keywords` (如 "咖啡")
- **返回**: 结构化的 JSON 数据（含有 `total_competitors_found`, `competition_level` 等）。

---

## ⚠️ 隐私声明与贡献
你可以自由克隆体验这份极致的 Prompt 工程。**【强烈建议在 Push 至公网前，清除你在文件内硬编码的个人 API Keys！】**
