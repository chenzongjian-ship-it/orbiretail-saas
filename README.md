# OrbiRetail 奥比零售云 - Batch 44 AI Agent 增强版

本版本在 Batch 43 的基础上重点加强 AI 能力：

- OpenAI / 通义千问 / 智谱 / DeepSeek API 接入预留
- AI Agent 智能中心
- AI 批改深度评语生成
- 教师评分标准自动解析
- AI 就业数据洞察问答
- 班级学习风险预警
- 学生成长画像
- 作业批改历史趋势
- 教师一键生成评语
- 自动生成字段映射建议
- 自动解释异常问题
- 自动生成经营摘要
- 自动生成客服回复
- 自动推荐场景模板
- 自动生成报告配置

## 本地运行

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

打开：

```text
http://localhost:8501
```

## Streamlit Cloud 更新方式

上传覆盖以下文件到 GitHub 仓库根目录：

```text
app.py
requirements.txt
README.md
```

建议同时上传：

```text
.streamlit/config.toml
docs/
ai_agent/
education_template/
ecommerce_template/
```

提交后 Streamlit Cloud 会自动重新部署。

## AI API 配置

在 Streamlit Cloud → Manage app → Secrets 中配置其中一种：

```toml
ORBI_AI_PROVIDER = "deepseek"
DEEPSEEK_API_KEY = "你的Key"
DEEPSEEK_MODEL = "deepseek-chat"
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
```

或：

```toml
ORBI_AI_PROVIDER = "openai"
OPENAI_API_KEY = "你的Key"
OPENAI_MODEL = "gpt-4o-mini"
OPENAI_BASE_URL = "https://api.openai.com/v1"
```

通义千问 / 阿里云百炼：

```toml
ORBI_AI_PROVIDER = "qwen"
DASHSCOPE_API_KEY = "你的Key"
QWEN_MODEL = "qwen-plus"
QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
```

智谱：

```toml
ORBI_AI_PROVIDER = "zhipu"
ZHIPU_API_KEY = "你的Key"
ZHIPU_MODEL = "glm-4-flash"
ZHIPU_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"
```

不配置 API Key 时，系统会自动使用本地规则模式，仍可运行。

## 联系方式

遇到无法解决的问题，请联系：2790569814@qq.com
