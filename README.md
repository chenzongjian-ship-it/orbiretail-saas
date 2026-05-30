# Batch 48：导航稳定性修复 + 顶部原生白条隐藏

本版本基于 Batch 47 做稳定性修复：

1. 修复侧边栏导航需要点击两次、页面回弹的问题。
2. 使用 `page` 与 `nav_page` 双状态同步，避免 Streamlit radio 与程序跳转状态冲突。
3. 隐藏 Streamlit 原生顶部工具栏 / 白条，让产品更像独立 SaaS。
4. 保留 Batch 47 的支付回调验签、订单对账、会员生命周期、管理员后台等能力。

## 部署

上传覆盖以下文件即可：

```text
app.py
requirements.txt
README.md
```

建议同时保留：

```text
.streamlit/config.toml
docs/
migrations/
```

线上地址仍为：

```text
https://orbiretail-saas.streamlit.app/
```

如果 Streamlit Cloud 未自动更新，请点击右下角 Manage app → Reboot app。
