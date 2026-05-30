# Batch 44 更新说明

本批重点加强 AI 能力，并保留本地规则模式，确保没有 API Key 时产品仍可正常运行。

## 主要更新

1. 新增 AI 智能中心。
2. 预留 OpenAI、通义千问、智谱、DeepSeek 接入。
3. AI Agent 可基于当前数据生成经营分析、趋势预测、字段映射建议、异常解释、客服回复和报告配置。
4. AI 作业批改增强：评分标准解析、深度评语、教师一键评语、班级风险预警、学生成长画像、历史趋势。
5. 高校就业数据支持 AI 问答。
6. 原有零售、电商、财务、库存、人事等模板均可使用 AI 进行经营摘要和未来趋势分析。

## 部署建议

只更新 Streamlit Cloud 时，至少上传：

- app.py
- requirements.txt
- README.md
- .streamlit/config.toml

如需保存文档和样例，可一起上传 docs、education_template、ecommerce_template、ai_agent 等目录。
