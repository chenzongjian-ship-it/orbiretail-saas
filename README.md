# Batch 49：侧边栏恢复 + 导航报错修复

本版本修复两个关键问题：

1. 侧边栏收起后无法再次打开。
   - 原因：此前隐藏了 Streamlit header，导致左上角原生侧边栏展开按钮不可用。
   - 修复：保留 header 与侧边栏按钮，仅隐藏不必要的顶部工具栏装饰。

2. 页面点击后回弹 / 报错。
   - 原因：程序在 Streamlit radio 组件创建之后又修改了同名 session_state key，触发 StreamlitAPIException。
   - 修复：侧边栏导航从 radio 改为 button 列表；导航只维护单一 page 状态，不再修改 nav_page widget state。

## 部署

上传覆盖：

- app.py
- requirements.txt
- README.md

建议继续保留：

- .streamlit/config.toml
- docs/
- migrations/

提交信息建议：

```text
Batch 49 sidebar navigation fix
```

然后等待 Streamlit Cloud 自动重新部署。如果没有刷新，点击 Manage app → Reboot app。
