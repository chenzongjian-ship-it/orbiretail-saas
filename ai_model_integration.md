# Batch 44：真实大模型 API 接入说明

本版本支持两种 AI 模式：

1. 本地规则模式：无需 API Key，可稳定运行，适合演示和基础客服问答。
2. 真实大模型模式：支持 OpenAI、通义千问/阿里云百炼、智谱 GLM、DeepSeek 的 OpenAI 兼容 Chat Completions 接入。

## Streamlit Cloud Secrets 配置示例

在 Streamlit Cloud 的 Manage app → Secrets 中加入以下任一配置：

```toml
ORBI_AI_PROVIDER = "deepseek"
DEEPSEEK_API_KEY = "你的DeepSeek Key"
DEEPSEEK_MODEL = "deepseek-chat"
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
```

或：

```toml
ORBI_AI_PROVIDER = "openai"
OPENAI_API_KEY = "你的OpenAI Key"
OPENAI_MODEL = "gpt-4o-mini"
OPENAI_BASE_URL = "https://api.openai.com/v1"
```

通义千问：

```toml
ORBI_AI_PROVIDER = "qwen"
DASHSCOPE_API_KEY = "你的阿里云百炼 Key"
QWEN_MODEL = "qwen-plus"
QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
```

智谱：

```toml
ORBI_AI_PROVIDER = "zhipu"
ZHIPU_API_KEY = "你的智谱 Key"
ZHIPU_MODEL = "glm-4-flash"
ZHIPU_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"
```

## 新增 AI 能力

- 自动生成字段映射建议
- 自动解释异常问题
- 自动生成经营摘要
- 自动预测未来趋势并给出建议
- 自动生成客服回复
- 自动推荐场景模板
- 自动生成报告配置
- AI 就业数据洞察问答
- 教师评分标准自动解析
- AI 批改深度评语生成
- 班级学习风险预警
- 学生成长画像
- 作业批改历史趋势
- 教师一键生成评语

## 注意事项

真实大模型调用会消耗 API 额度。AI 输出应作为辅助建议，尤其在成绩批改、就业质量评价、财务经营结论等场景，最终结论应由教师、财务或管理人员复核。
