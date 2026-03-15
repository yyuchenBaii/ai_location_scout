import re

with open("SKILL.md", "r", encoding="utf-8") as f:
    content = f.read()

# Fix numbering
content = content.replace(" 4. **【核心约束】多点位对比", " 5. **【核心约束】多点位对比")

# Replace section 6 (previously 5) with the new checklists
old_section_start = " 6. **【高保真地图渲染交付标准】（必须严格执行）**："
old_section_end = " 7. **语言风格纪律**："

new_section = """ 6. **【高保真地图渲染交付标准】（必须严格执行）**：
    - 基础 HTML 模版中已经埋入了强大的渲染引擎 (`renderConcentricCircles`, `renderPOIs`, `renderHeatMap`) 并且自带了地图主题切换器。**你不需要手写复杂的图层生成逻辑**，只需专注提供高质量的数据阵列。
     
    #### 🎯 地图打点与功能验收标准 (MUST)：
    - [ ] **全量打点**：2km内竞品 **≥150个点位** 必须在地图上可见，每个点位 **≤100米误差** 真实还原。
    - [ ] **目标高亮**：目标选址中心点必须有醒目的特殊标记（差异化颜色与动画光环）。
    - [ ] **信息窗 (InfoWindow)**：点击每一个竞品 POI 时，弹出的框内**必须**包含：`门店名称`、`类型`、`价格带`、`距离`、`评分` 5个核心字段，缺一不可！
    - [ ] **热力图层**：必须依据竞品密集度注入 `heatData`，让全图显示红黄绿色泽的热力辐射效果。

    #### ❌ 常见偷工减料红线（DON'T DO，否则视为交付失败）：
    - ❌ 只打 3-4 个头部品牌（星巴克/瑞幸/M Stand），抛弃其他真实竞品，造成地图严重空旷。
    - ❌ 生成一堆假的点位，点位不可点击，或点击无反应报错。
    - ❌ 用静态图片代替真实地图API。
    - ❌ InfoWindow 极度敷衍，只写个名字，缺少价格/距离等关键信息。
    - ❌ 一运行就把原本模版里辛辛苦苦写的“地图主题切换功能（黑白地图切换按钮）”给删掉或搞坏了。

    #### 📝 失败案例对比参考：
    - 📉 **失败示例 v1**：只打了 3 个竞品，不可点击，无热力图，黑白切换按钮丢失 → 严重失职，用户投诉。
    - 📈 **成功示例 v2**：几十家竞品全量真实还原，InfoWindow 五维属性齐全，带热力图和切换按钮 → 极致震撼，通过验收。

    #### 👉 具体数据对接格式要求：
      - **同心辐射圈 (`circles`)**：注入 `radius` (半径), `color`, `title`, `desc`。建议至少画两层。
      - **多态 POI (`pois`)**：注入 `loc: [经度,纬度]`, `name`, `desc` 并且必须指定 `type`。
        🔥🔥🔥 **【极度强调：真实打点还原体系】要求你在生成 `pois` 时，必须将上述 Python 脚本抓取返回的 `top_competitors_for_map` 数组中的【全部数十个竞品】一个不落地全部转换为 `type: 'competitor'` 的 POI 点位插入地图！严禁遗漏只标几个！**
      - **竞品热力点 (`heatData`)**：利用转换出的几十个坐标，同步转化为热点阵列数据代表竞争烈度，渲染出热力图。
    - **最终注入点**：如果单体报告，修改 `<script>` 里写死预留的 `circles`, `pois`, `heatData` 变量。多体报告，在每个方案的 JSON 内增加。

    ### ✅ 输出前核心自检（必须全部打勾）
    - [ ] 地图右上角有"暗黑/经典"切换按钮且可点击？切换后底色从黑底变为高德默认蓝底？
    - [ ] 随机评估 3 个点位，确认 InfoWindow 正常弹出展示完整？
    - [ ] 地图上看到的点位数量与你的左侧数据表格里的宣告数字是否成正比？

"""

# Finding the start and end to splice
start_idx = content.find(old_section_start)
end_idx = content.find(old_section_end)

if start_idx != -1 and end_idx != -1:
    new_content = content[:start_idx] + new_section + content[end_idx:]
    with open("SKILL.md", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Successfully replaced section 6.")
else:
    print("Could not find sections.")

