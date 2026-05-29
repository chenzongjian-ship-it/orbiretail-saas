# OrbiRetail 奥比零售云 - Batch 42 电商公司场景包 + AI Agent 智能助手

本版本在商业版 SaaS 雏形基础上新增：

1. 电商退款 / 售后工单汇总场景包。
2. AI Agent 智能助手，支持模板推荐、上传指导、报告下载指导和客服答疑。
3. 电商售后专题分析：退款原因分布、渠道售后汇总、商品售后表现、客服工单效率、高风险工单。
4. 报告包增强：Excel 报告自动增加专题分析 Sheet。

## 部署到 Streamlit Cloud

上传覆盖仓库根目录的三个文件：

```text
app.py
requirements.txt
README.md
```

线上地址保持不变：

```text
https://orbiretail-saas.streamlit.app/
```

如需保留开发资料，可同时上传：

```text
docs/
ecommerce_template/
ai_agent/
api_server.py
docker-compose.yml
openapi_sample.json
```

## 本地运行

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## 电商场景建议字段

必需字段：订单号、商品、售后类型、退款原因、处理状态、退款金额。

可选字段：申请日期、店铺、渠道、赔付金额、响应时长、处理时长、客服、备注。

## AI Agent

进入工作台后，AI Agent 会出现在前置位置。用户可以直接输入：

```text
我要分析电商退款和售后工单
上传 Excel 有哪些字段要求
怎么下载问题清单和报告包
```

AI Agent 会自动推荐模板和操作路径。
