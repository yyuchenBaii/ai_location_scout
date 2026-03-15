import re

with open("SKILL.md", "r", encoding="utf-8") as f:
    content = f.read()

# Update conclusion rule to mention sidebar
content = content.replace(
    '🔥🔥�� **严禁自己在地图上乱加绝对定位的 div 遮挡地图！你必须将最终的横向对比结论直接写入模版中预留好的 `<div id="ui-global-conclusion-content">` 容器内。**',
    '🔥🔥🔥 **严禁自己在地图上乱加绝对定位的 div 遮挡地图！你必须将最终的结论直接写入侧边栏底部的 `<div id="ui-global-conclusion-content">` 容器内。**'
)

# Update checklist to mention White Style
content = content.replace(
    '- [ ] 地图右上角有"暗黑/经典"切换按钮且可点击？切换后底色从黑底变为高德默认蓝底？',
    '- [ ] 地图是否为默认经典白色高德风格？（严禁生成暗黑切换按钮）'
)

# Add sidebar check to checklist
if '最终结论是否已填入侧边栏底部的' not in content:
    content = content.replace(
        '- [ ] 随机评估 3 个点位',
        '- [ ] 最终结论是否已填入侧边栏底部的 `ui-global-conclusion-content` 容器？（严禁遮挡地图）\n    - [ ] 随机评估 3 个点位'
    )

with open("SKILL.md", "w", encoding="utf-8") as f:
    f.write(content)
