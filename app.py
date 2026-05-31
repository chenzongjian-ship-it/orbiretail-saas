import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import json
import io
import zipfile
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

APP_NAME = "Aurevia 智策云"
APP_SUBTITLE = "数据智能与AI效率平台"
CONTACT_EMAIL = "2790569814@qq.com"
DATA_DIR = Path("saas_data")
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "aurevia_free.db"

st.set_page_config(
    page_title=f"{APP_NAME}｜免费开放版",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------
# CSS
# ----------------------------
st.markdown(
    """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: visible !important; background: transparent !important;}
[data-testid="stToolbar"] {display: none !important;}
[data-testid="stDecoration"] {display: none !important;}
.stApp {
  background:
    radial-gradient(circle at top left, rgba(37,99,235,.12), transparent 28%),
    radial-gradient(circle at top right, rgba(20,184,166,.16), transparent 28%),
    linear-gradient(180deg, #f7fbff 0%, #eef5fa 100%);
}
.block-container { padding-top: 1.2rem; max-width: 1420px; }
.hero {
  padding: 34px 38px;
  border-radius: 30px;
  background: linear-gradient(135deg,#071225 0%,#163987 48%,#0f8d85 100%);
  color: white;
  box-shadow: 0 24px 70px rgba(15,23,42,.18);
}
.hero h1 {font-size: 48px; line-height:1.12; margin:0 0 12px 0; font-weight:850;}
.hero p {font-size:18px; line-height:1.75; color:rgba(255,255,255,.92);}
.chip {
  display:inline-block; padding:8px 14px; border-radius:999px;
  background:rgba(255,255,255,.14); border:1px solid rgba(255,255,255,.22);
  color:rgba(255,255,255,.96); margin-bottom:18px; font-size:14px;
}
.card, .metric-card, .template-card {
  background: rgba(255,255,255,.90);
  border: 1px solid rgba(15,23,42,.08);
  border-radius: 22px;
  box-shadow: 0 14px 42px rgba(15,23,42,.07);
  padding: 22px;
}
.metric-card h2 {font-size: 32px; margin:0; color:#0f172a;}
.metric-card p {margin:6px 0 0 0; color:#64748b;}
.template-card {min-height: 220px;}
.template-card h4 {margin:0 0 8px 0; color:#0f172a; font-size:18px;}
.template-card p {color:#526478; line-height:1.65; font-size:14px;}
.badge-free {
  display:inline-block; padding:6px 11px; border-radius:999px;
  background:#ecfdf5; color:#047857; border:1px solid #a7f3d0; font-size:13px;
}
.warnbox {background:#fff7ed; border:1px solid #fed7aa; color:#92400e; border-radius:16px; padding:14px 16px;}
.successbox {background:#ecfdf5; border:1px solid #a7f3d0; color:#065f46; border-radius:16px; padding:14px 16px;}
.infobox {background:#eff6ff; border:1px solid #bfdbfe; color:#1e3a8a; border-radius:16px; padding:14px 16px;}
.ai-msg {background:#f8fbff; border:1px solid #dbeafe; border-radius:16px; padding:16px; line-height:1.75;}
.small {font-size:13px; color:#64748b;}
.footer {color:#64748b; font-size:13px; text-align:center; margin-top:30px;}
</style>
""",
    unsafe_allow_html=True,
)

# ----------------------------
# Database
# ----------------------------
def db_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = db_conn()
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          email TEXT UNIQUE,
          password_hash TEXT,
          organization TEXT,
          role TEXT DEFAULT 'user',
          created_at TEXT,
          is_active INTEGER DEFAULT 1
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS feedback (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_email TEXT,
          category TEXT,
          content TEXT,
          created_at TEXT
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS ai_settings (
          user_email TEXT PRIMARY KEY,
          provider TEXT DEFAULT '本地规则模式',
          model TEXT,
          base_url TEXT,
          secret_name TEXT,
          updated_at TEXT
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS analysis_history (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_email TEXT,
          scenario TEXT,
          rows_count INTEGER,
          trust_score INTEGER,
          issue_count INTEGER,
          created_at TEXT
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS grading_history (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          student TEXT,
          assignment_type TEXT,
          score REAL,
          level TEXT,
          similarity_note TEXT,
          created_at TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def hash_password(pwd: str) -> str:
    return hashlib.sha256((pwd or "").encode("utf-8")).hexdigest()


def create_user(email: str, pwd: str, org: str) -> str:
    if not email or not pwd:
        return "邮箱和密码不能为空。"
    conn = db_conn()
    try:
        conn.execute(
            "INSERT INTO users(email, password_hash, organization, role, created_at) VALUES (?, ?, ?, ?, ?)",
            (email, hash_password(pwd), org or "未填写组织", "admin" if email == CONTACT_EMAIL else "user", datetime.now().isoformat()),
        )
        conn.commit()
        return "注册成功。当前版本为免费开放版，可直接使用核心功能。"
    except sqlite3.IntegrityError:
        return "该邮箱已注册，可以直接登录。"
    finally:
        conn.close()


def login_user(email: str, pwd: str) -> Optional[Dict[str, Any]]:
    conn = db_conn()
    row = conn.execute(
        "SELECT * FROM users WHERE email=? AND password_hash=? AND is_active=1",
        (email, hash_password(pwd)),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


init_db()

# ----------------------------
# Session
# ----------------------------
for key, default in {
    "page": "首页",
    "user": None,
    "last_result": None,
    "last_df": None,
    "last_scenario": None,
}.items():
    st.session_state.setdefault(key, default)


def is_logged_in() -> bool:
    return st.session_state.get("user") is not None


def current_email() -> str:
    return st.session_state["user"]["email"] if is_logged_in() else "访客"

# ----------------------------
# Scenario definitions
# ----------------------------
SCENARIOS = [
    {"name": "门店 / 渠道销售日报", "category": "零售经营", "target": "门店运营、区域经理、财务结算", "inputs": "门店销售日报、渠道结算日报、退款明细", "outputs": "销售汇总、渠道差异、退款冲销、经营诊断", "required": ["日期", "门店", "渠道", "金额"]},
    {"name": "电商退款 / 售后工单汇总", "category": "互联网 / 电商", "target": "电商运营、客服主管、售后团队", "inputs": "退换货明细、退款记录、售后工单、赔付记录", "outputs": "退款原因分布、客服效率、商品售后表现、高风险工单", "required": ["订单号", "商品", "售后类型", "退款原因", "处理状态", "退款金额"]},
    {"name": "高校教务 / 实习 / 就业数据汇总", "category": "高校教育", "target": "教务办、就业办、辅导员、院系负责人", "inputs": "就业数据、实习单位、班级专业、薪资地区", "outputs": "就业率、实习单位汇总、薪资区间、未就业清单、院系报告", "required": ["学院", "专业", "班级", "姓名", "就业状态"]},
    {"name": "AI 作业批改", "category": "高校教育", "target": "任课教师、辅导员、教务老师", "inputs": "Word / PDF / TXT / ZIP 作业包、评分细则", "outputs": "评分表、深度评语、雷同标注、历史表现、班级风险预警", "required": ["学生", "作业内容"]},
    {"name": "平台结算对账", "category": "财务对账", "target": "财务、渠道运营", "inputs": "订单表、平台结算单、银行流水", "outputs": "未结算订单、手续费差异、到账差异", "required": ["订单号", "金额", "渠道"]},
    {"name": "库存盘点差异", "category": "库存供应链", "target": "仓储、电商、门店管理", "inputs": "系统库存、盘点表、出入库记录", "outputs": "盘盈、盘亏、差异金额、异常商品", "required": ["商品", "系统库存", "实际库存"]},
    {"name": "月度费用汇总", "category": "财务对账", "target": "行政、财务、部门负责人", "inputs": "费用报销表、项目费用表、部门费用表", "outputs": "费用合计、部门排名、异常金额、问题清单", "required": ["部门", "月份", "类别", "金额"]},
    {"name": "销售业绩分析", "category": "销售运营", "target": "销售主管、运营团队", "inputs": "销售明细、区域表、产品表", "outputs": "销售排名、区域趋势、产品贡献、异常波动", "required": ["销售人员", "区域", "商品", "金额"]},
]

FIELD_ALIASES = {
    "日期": ["日期", "销售日期", "下单时间", "支付时间", "申请日期"],
    "门店": ["门店", "店铺", "门店名称", "分店"],
    "渠道": ["渠道", "平台", "来源", "销售渠道"],
    "金额": ["金额", "实收金额", "销售额", "成交金额", "支付金额", "费用金额"],
    "退款金额": ["退款金额", "退货金额", "退款", "售后金额"],
    "订单号": ["订单号", "工单号", "售后单号", "交易号"],
    "商品": ["商品", "商品名称", "SKU", "产品"],
    "售后类型": ["售后类型", "工单类型", "退换货类型"],
    "退款原因": ["退款原因", "售后原因", "退货原因", "投诉原因"],
    "处理状态": ["处理状态", "工单状态", "售后状态"],
    "学院": ["学院", "院系", "二级学院", "所属学院"],
    "专业": ["专业", "专业名称", "培养专业"],
    "班级": ["班级", "行政班", "班级名称"],
    "姓名": ["姓名", "学生姓名", "学生"],
    "就业状态": ["就业状态", "就业去向", "毕业去向", "是否就业"],
    "薪资": ["薪资", "月薪", "薪酬", "税前薪资"],
    "部门": ["部门", "部门名称", "所属部门"],
    "月份": ["月份", "月", "统计月份"],
    "类别": ["类别", "费用类别", "分类"],
    "销售人员": ["销售人员", "业务员", "员工", "负责人"],
    "区域": ["区域", "地区", "大区", "城市"],
    "系统库存": ["系统库存", "账面库存", "库存数量"],
    "实际库存": ["实际库存", "盘点数量", "实盘数量"],
}

# ----------------------------
# Utilities
# ----------------------------
def find_col(df: pd.DataFrame, std_name: str) -> Optional[str]:
    aliases = FIELD_ALIASES.get(std_name, [std_name])
    lower_cols = {str(c).strip().lower(): c for c in df.columns}
    for a in aliases:
        key = str(a).strip().lower()
        if key in lower_cols:
            return lower_cols[key]
    return None


def map_fields(df: pd.DataFrame, required: List[str]) -> pd.DataFrame:
    rows = []
    for field in required:
        col = find_col(df, field)
        rows.append({"标准字段": field, "识别列": col or "", "状态": "已识别" if col else "缺失", "建议": "" if col else f"建议补充或将相近列映射为“{field}”。"})
    return pd.DataFrame(rows)


def read_uploaded_files(files: List[Any]) -> pd.DataFrame:
    frames = []
    for f in files:
        try:
            if f.name.lower().endswith(".csv"):
                df = pd.read_csv(f)
            else:
                df = pd.read_excel(f)
            df["来源文件"] = f.name
            frames.append(df)
        except Exception as e:
            st.warning(f"文件 {f.name} 读取失败：{e}")
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def demo_data(scenario_name: str) -> pd.DataFrame:
    if "电商" in scenario_name:
        return pd.DataFrame({
            "订单号": [f"TK{i:04d}" for i in range(1, 16)],
            "商品": ["无线耳机", "蓝牙音箱", "智能手表", "无线耳机", "保温杯"] * 3,
            "售后类型": ["退货", "退款", "换货", "投诉", "仅退款"] * 3,
            "退款原因": ["质量问题", "尺码不符", "物流破损", "七天无理由", "描述不符"] * 3,
            "处理状态": ["已完成", "处理中", "已完成", "超时", "已完成"] * 3,
            "退款金额": [199, 89, 299, 159, 49, 219, 99, 399, 189, 59, 179, 78, 299, 166, 49],
            "处理时长": [4, 18, 7, 52, 6, 3, 20, 10, 60, 5, 8, 17, 6, 48, 4],
            "客服": ["张三", "李四", "王五", "张三", "赵六"] * 3,
            "渠道": ["天猫", "京东", "抖音", "拼多多", "自营"] * 3,
        })
    if "高校" in scenario_name:
        return pd.DataFrame({
            "学院": ["信息工程学院"]*8 + ["商学院"]*6,
            "专业": ["软件工程", "计算机科学", "数据科学", "软件工程"]*3 + ["市场营销", "会计学"],
            "班级": ["软工2301", "计科2302", "数据2301", "软工2301"]*3 + ["营销2301", "会计2301"],
            "姓名": [f"学生{i}" for i in range(1, 15)],
            "就业状态": ["已就业", "实习中", "升学", "待就业", "已就业", "已就业", "待就业"]*2,
            "实习单位": ["腾讯", "字节跳动", "阿里云", "未填写", "京东", "美团", "未填写"]*2,
            "行业": ["互联网", "互联网", "云计算", "未填写", "电商", "本地生活", "未填写"]*2,
            "薪资": [9000, 8500, 0, 0, 7000, 7600, 0, 8800, 7200, 0, 0, 6500, 6000, 0],
        })
    return pd.DataFrame({
        "日期": pd.date_range("2026-05-01", periods=15).strftime("%Y-%m-%d"),
        "门店": ["人民广场店", "西湖店", "天河店"] * 5,
        "渠道": ["美团", "饿了么", "线下POS", "抖音", "京东"] * 3,
        "订单号": [f"SO{i:04d}" for i in range(1, 16)],
        "金额": [1280, 1560, 980, 2100, 760, 1890, 990, 1330, 2210, 560, 1760, 900, 2340, 680, 1200],
        "退款金额": [0, 120, 0, 0, 50, 0, 90, 0, 0, 0, 200, 0, 0, 30, 0],
        "平台佣金": [60, 80, 0, 120, 40, 90, 70, 0, 130, 30, 88, 0, 140, 20, 0],
    })


def analyze_df(df: pd.DataFrame, scenario: Dict[str, Any]) -> Dict[str, Any]:
    field_map = map_fields(df, scenario["required"])
    missing = field_map[field_map["状态"] == "缺失"]["标准字段"].tolist()
    rows = len(df)
    money_col = find_col(df, "金额") or find_col(df, "退款金额") or find_col(df, "薪资")
    total = 0.0
    if money_col:
        total = pd.to_numeric(df[money_col], errors="coerce").fillna(0).sum()
    issue_count = int(len(missing) * 3)
    if money_col:
        issue_count += int(pd.to_numeric(df[money_col], errors="coerce").isna().sum())
    trust = max(20, min(100, 100 - len(missing) * 12 - issue_count * 2))
    summary_lines = [
        f"本次选择场景：{scenario['name']}。",
        f"共处理 {rows} 条记录。",
        f"识别到关键金额列：{money_col or '未识别'}。",
        f"数据可信度评分：{trust} / 100。",
    ]
    if missing:
        summary_lines.append("存在缺失字段：" + "、".join(missing) + "，建议先补齐再用于正式汇报。")
    else:
        summary_lines.append("必需字段识别完整，可以进入进一步分析和报告输出。")
    if "电商" in scenario["name"]:
        reason_col = find_col(df, "退款原因")
        if reason_col:
            top_reason = df[reason_col].astype(str).value_counts().idxmax()
            summary_lines.append(f"最高频退款/售后原因是：{top_reason}，建议优先分析对应商品和客服处理流程。")
    if "高校" in scenario["name"]:
        status_col = find_col(df, "就业状态")
        if status_col:
            done = df[status_col].astype(str).str.contains("已就业|升学|实习", regex=True).sum()
            rate = done / max(rows, 1) * 100
            summary_lines.append(f"就业/升学/实习等已落实人数 {done} 人，落实率约 {rate:.1f}%。")
    issues = [{"级别": "高", "问题类型": "缺失必需字段", "问题详情": f"缺少字段：{m}", "建议处理": f"补充 {m} 字段或建立字段别名映射。"} for m in missing]
    issue_df = pd.DataFrame(issues) if issues else pd.DataFrame(columns=["级别", "问题类型", "问题详情", "建议处理"])
    return {"field_map": field_map, "trust": trust, "summary": "\n".join(summary_lines), "issues": issue_df, "total": total, "rows": rows}


def make_report_zip(df: pd.DataFrame, scenario: Dict[str, Any], result: Dict[str, Any]) -> bytes:
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="原始数据", index=False)
        result["field_map"].to_excel(writer, sheet_name="字段识别", index=False)
        result["issues"].to_excel(writer, sheet_name="问题清单", index=False)
        pd.DataFrame([{"场景": scenario["name"], "记录数": result["rows"], "合计值": result["total"], "数据可信度": result["trust"], "摘要": result["summary"]}]).to_excel(writer, sheet_name="分析摘要", index=False)
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("分析报告.xlsx", excel_buffer.getvalue())
        z.writestr("分析摘要.txt", result["summary"])
        z.writestr("问题清单.csv", result["issues"].to_csv(index=False).encode("utf-8-sig"))
    return zip_buffer.getvalue()

# ----------------------------
# AI
# ----------------------------
PROVIDERS = ["OpenAI", "Kimi / Moonshot", "通义千问", "智谱 GLM", "DeepSeek", "本地规则模式"]
PROVIDER_DEFAULTS = {
    "OpenAI": {"secret": "OPENAI_API_KEY", "model": "gpt-4o-mini", "base_url": "https://api.openai.com/v1"},
    "Kimi / Moonshot": {"secret": "MOONSHOT_API_KEY", "model": "kimi-k2.6", "base_url": "https://api.moonshot.cn/v1"},
    "通义千问": {"secret": "DASHSCOPE_API_KEY", "model": "qwen-plus", "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"},
    "智谱 GLM": {"secret": "ZHIPU_API_KEY", "model": "glm-4-flash", "base_url": "https://open.bigmodel.cn/api/paas/v4"},
    "DeepSeek": {"secret": "DEEPSEEK_API_KEY", "model": "deepseek-chat", "base_url": "https://api.deepseek.com/v1"},
    "本地规则模式": {"secret": "", "model": "", "base_url": ""},
}


def secret_get(name: str) -> str:
    try:
        return st.secrets.get(name, "")
    except Exception:
        return ""


def save_ai_settings(email: str, provider: str, model: str, base_url: str, secret_name: str):
    conn = db_conn()
    conn.execute(
        "INSERT OR REPLACE INTO ai_settings(user_email, provider, model, base_url, secret_name, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
        (email, provider, model, base_url, secret_name, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def load_ai_settings(email: str) -> Dict[str, str]:
    conn = db_conn()
    row = conn.execute("SELECT * FROM ai_settings WHERE user_email=?", (email,)).fetchone()
    conn.close()
    if row:
        return dict(row)
    return {"provider": "本地规则模式", "model": "", "base_url": "", "secret_name": ""}


def ai_local_answer(prompt: str) -> str:
    p = (prompt or "").lower()
    if "电商" in p or "退款" in p or "售后" in p:
        return "建议使用“电商退款 / 售后工单汇总”模板。上传退换货明细、售后工单、退款金额、处理状态、客服和渠道字段后，系统会生成退款原因分布、客服效率、高风险工单和经营摘要。"
    if "高校" in p or "就业" in p or "实习" in p:
        return "建议使用“高校教务 / 实习 / 就业数据汇总”模板。重点字段包括学院、专业、班级、姓名、就业状态、实习单位、行业、薪资、地区。"
    if "作业" in p or "批改" in p or "评分" in p:
        return "建议进入“AI 作业批改”功能。可上传 Word、PDF、TXT 或 ZIP 作业包，并输入评分细则。系统会辅助评分、生成评语、检测雷同并输出分析表格。"
    return "我可以帮你推荐模板、解释异常、生成经营摘要、生成客服回复、生成报告配置。请告诉我你要分析的数据类型、上传文件字段和希望得到的结果。"


def call_openai_compatible(base_url: str, api_key: str, model: str, prompt: str) -> str:
    if not api_key:
        raise ValueError("未配置 API Key。")
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {"model": model, "messages": [{"role": "system", "content": "你是 Aurevia 智策云的数据分析、教育辅助和客服智能助手。回答要清晰、克制、可执行。"}, {"role": "user", "content": prompt}], "temperature": 0.3}
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    r = requests.post(url, headers=headers, json=payload, timeout=35)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def run_ai(prompt: str, provider: Optional[str] = None) -> str:
    settings = load_ai_settings(current_email()) if is_logged_in() else {"provider": "本地规则模式"}
    provider = provider or settings.get("provider") or "本地规则模式"
    if provider == "本地规则模式":
        return ai_local_answer(prompt)
    defaults = PROVIDER_DEFAULTS.get(provider, PROVIDER_DEFAULTS["本地规则模式"])
    model = settings.get("model") or defaults.get("model", "")
    base_url = settings.get("base_url") or defaults.get("base_url", "")
    secret_name = settings.get("secret_name") or defaults.get("secret", "")
    api_key = secret_get(secret_name)
    return call_openai_compatible(base_url, api_key, model, prompt)

# ----------------------------
# Layout / Navigation
# ----------------------------
NAV_PAGES = ["首页", "工作台", "模板中心", "AI智能中心", "AI作业批改", "系统后台", "反馈"]

def set_page(page: str):
    st.session_state.page = page
    st.rerun()


def sidebar():
    with st.sidebar:
        st.markdown(f"### ✨ {APP_NAME}")
        st.caption(APP_SUBTITLE)
        if is_logged_in():
            st.markdown(f"<div class='successbox'>已登录：<br>{current_email()}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='infobox'>当前：访客模式<br>免费开放，可先体验。</div>", unsafe_allow_html=True)
        st.markdown("---")
        st.caption("导航")
        for page in NAV_PAGES:
            active = "● " if st.session_state.page == page else "○ "
            if st.button(active + page, key=f"nav_{page}", use_container_width=True):
                set_page(page)
        st.markdown("---")
        st.caption(f"客服邮箱：{CONTACT_EMAIL}")
        st.caption("当前版本：永久免费开放核心功能")


def login_panel():
    tabs = st.tabs(["登录", "注册"])
    with tabs[0]:
        email = st.text_input("邮箱", key="login_email")
        pwd = st.text_input("密码", type="password", key="login_pwd")
        if st.button("登录", use_container_width=True):
            user = login_user(email, pwd)
            if user:
                st.session_state.user = user
                st.success("登录成功。")
                st.rerun()
            else:
                st.error("邮箱或密码错误。")
    with tabs[1]:
        email = st.text_input("注册邮箱", key="reg_email")
        pwd = st.text_input("注册密码", type="password", key="reg_pwd")
        org = st.text_input("单位 / 公司 / 院系", key="reg_org")
        if st.button("注册并免费使用", use_container_width=True):
            msg = create_user(email, pwd, org)
            st.success(msg)


def render_home():
    c1, c2 = st.columns([1.5, 1], gap="large")
    with c1:
        st.markdown(
            """
            <div class='hero'>
              <div class='chip'>永久免费开放核心功能｜Aurevia 智策云</div>
              <h1>把复杂数据、报告和批改工作，交给 AI 和模板系统先处理。</h1>
              <p>面向零售、电商、高校、运营和教师的效率平台。它不是为了“收费而收费”，而是先把产品做得真正有用：帮用户减少重复整理、快速发现问题、生成清晰报告。</p>
              <p><b>当前策略：</b>核心功能免费开放，先验证真实价值和用户喜好。</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("### 产品真正要解决什么")
        pcols = st.columns(4)
        cards = [
            ("数据太乱", "自动识别字段、生成映射建议。"),
            ("报告太慢", "一键输出摘要、问题清单、报告包。"),
            ("批改太累", "辅助评分、评语、雷同检测和历史表现。"),
            ("用户不会用", "AI Agent 像客服一样引导操作。"),
        ]
        for col, (title, desc) in zip(pcols, cards):
            with col:
                st.markdown(f"<div class='metric-card'><h2>{title}</h2><p>{desc}</p></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 进入系统")
        st.markdown("<span class='badge-free'>免费使用</span>", unsafe_allow_html=True)
        st.write("注册只用于保存反馈、AI 设置和历史记录；核心分析能力免费开放。")
        login_panel()
        st.markdown("</div>", unsafe_allow_html=True)


def scenario_selector() -> Dict[str, Any]:
    names = [s["name"] for s in SCENARIOS]
    selected = st.selectbox("选择场景模板", names)
    return next(s for s in SCENARIOS if s["name"] == selected)


def render_result(df: pd.DataFrame, scenario: Dict[str, Any], result: Dict[str, Any]):
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("记录数", result["rows"])
    m2.metric("关键金额合计", f"{result['total']:,.2f}")
    m3.metric("问题数", len(result["issues"]))
    m4.metric("数据可信度", f"{result['trust']} / 100")
    st.progress(result["trust"] / 100)
    st.markdown("#### AI / 规则诊断摘要")
    st.info(result["summary"])
    st.markdown("#### 字段识别")
    st.dataframe(result["field_map"], use_container_width=True)
    if len(result["issues"]):
        st.markdown("#### 问题清单")
        st.dataframe(result["issues"], use_container_width=True)
    with st.expander("查看原始数据", expanded=False):
        st.dataframe(df, use_container_width=True)
    report_zip = make_report_zip(df, scenario, result)
    st.download_button("下载报告包 ZIP", data=report_zip, file_name=f"Aurevia_{scenario['name']}_报告包.zip", mime="application/zip", use_container_width=True, key="download_report_zip")


def record_history(scenario: str, result: Dict[str, Any]):
    if not is_logged_in():
        return
    conn = db_conn()
    conn.execute("INSERT INTO analysis_history(user_email, scenario, rows_count, trust_score, issue_count, created_at) VALUES (?, ?, ?, ?, ?, ?)", (current_email(), scenario, result["rows"], result["trust"], len(result["issues"]), datetime.now().isoformat()))
    conn.commit()
    conn.close()


def render_workspace():
    st.markdown("## 数据智能工作台")
    st.markdown("<div class='successbox'>当前版本已移除收费系统，核心功能免费开放。建议你先用演示数据体验，再上传真实文件。</div>", unsafe_allow_html=True)
    scenario = scenario_selector()
    st.markdown(f"<div class='card'><h3>{scenario['name']}</h3><p><b>适合用户：</b>{scenario['target']}</p><p><b>建议输入：</b>{scenario['inputs']}</p><p><b>输出结果：</b>{scenario['outputs']}</p></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("生成演示数据并分析", use_container_width=True):
            df = demo_data(scenario["name"])
            result = analyze_df(df, scenario)
            st.session_state.last_df = df
            st.session_state.last_result = result
            st.session_state.last_scenario = scenario
            record_history(scenario["name"], result)
            st.rerun()
    with c2:
        uploaded = st.file_uploader("上传 Excel / CSV，可多选", type=["xlsx", "csv"], accept_multiple_files=True)
        if st.button("分析上传文件", use_container_width=True):
            if uploaded:
                df = read_uploaded_files(uploaded)
                if len(df):
                    result = analyze_df(df, scenario)
                    st.session_state.last_df = df
                    st.session_state.last_result = result
                    st.session_state.last_scenario = scenario
                    record_history(scenario["name"], result)
                    st.rerun()
            else:
                st.warning("请先上传文件，或直接使用演示数据。")
    if st.session_state.last_result is not None:
        render_result(st.session_state.last_df, st.session_state.last_scenario, st.session_state.last_result)


def render_templates():
    st.markdown("## 模板中心")
    categories = ["全部"] + sorted(set(s["category"] for s in SCENARIOS))
    cat = st.selectbox("分类筛选", categories)
    kw = st.text_input("搜索模板", placeholder="例如：电商、就业、作业、库存、费用")
    items = SCENARIOS
    if cat != "全部":
        items = [s for s in items if s["category"] == cat]
    if kw:
        items = [s for s in items if kw.lower() in json.dumps(s, ensure_ascii=False).lower()]
    cols = st.columns(3)
    for idx, s in enumerate(items):
        with cols[idx % 3]:
            st.markdown(f"<div class='template-card'><h4>{s['name']}</h4><p><b>分类：</b>{s['category']}</p><p><b>适合：</b>{s['target']}</p><p><b>输入：</b>{s['inputs']}</p><p><b>输出：</b>{s['outputs']}</p></div>", unsafe_allow_html=True)


def render_ai_center():
    st.markdown("## AI 智能中心")
    st.caption("AI 可用于推荐模板、解释异常、生成摘要、生成客服回复、辅助报告配置。")
    settings = load_ai_settings(current_email()) if is_logged_in() else {"provider": "本地规则模式"}
    c1, c2 = st.columns([1, 1])
    with c1:
        provider = st.selectbox("模型服务商", PROVIDERS, index=PROVIDERS.index(settings.get("provider", "本地规则模式")))
        defaults = PROVIDER_DEFAULTS[provider]
        model = st.text_input("模型名称", value=settings.get("model") or defaults.get("model", ""))
        base_url = st.text_input("Base URL", value=settings.get("base_url") or defaults.get("base_url", ""))
        secret_name = st.text_input("Secrets Key 名称", value=settings.get("secret_name") or defaults.get("secret", ""), help="不要把真实 API Key 写在这里。请在 Streamlit Secrets 中配置。")
        if st.button("保存 AI 设置", use_container_width=True):
            if is_logged_in():
                save_ai_settings(current_email(), provider, model, base_url, secret_name)
                st.success("AI 设置已保存。")
            else:
                st.warning("请先登录，才能保存 AI 设置。")
    with c2:
        prompt = st.text_area("向 AI 提问", placeholder="例如：帮我分析电商售后数据该选哪个模板？", height=170)
        if st.button("发送", use_container_width=True):
            try:
                st.markdown("#### AI 回复")
                st.write(run_ai(prompt, provider=provider))
            except Exception as e:
                st.error(f"AI 调用失败：{e}")
                st.info("可以先切换到“本地规则模式”，或检查 Streamlit Secrets 中的 API Key 配置。")


def score_assignment_text(text: str, rubric: str) -> Dict[str, Any]:
    words = len(text)
    score = 60
    hits = []
    for key in ["结构", "观点", "案例", "数据", "反思", "结论", "引用", "实验", "实习"]:
        if key in text or key in rubric:
            score += 4
            hits.append(key)
    score = min(96, max(40, score + min(words // 300, 10)))
    level = "优秀" if score >= 85 else "良好" if score >= 75 else "及格" if score >= 60 else "需改进"
    return {"字数": words, "得分": score, "等级": level, "命中要点": "、".join(hits) or "基础要点", "评语": f"该作业整体表现为{level}。建议进一步强化论证深度、结构完整性和案例支撑。"}


def render_grading():
    st.markdown("## AI 作业批改")
    st.markdown("<div class='infobox'>当前为辅助批改工具，适合初筛、生成评语和统计分析。正式成绩仍建议教师复核。</div>", unsafe_allow_html=True)
    assignment_type = st.selectbox("作业类型", ["通用文字作业", "课程论文", "实习报告", "实验报告", "读书报告", "代码说明文档"])
    rubric = st.text_area("评分标准细则", placeholder="例如：结构完整20分；观点清晰20分；案例和数据30分；反思总结20分；格式规范10分。", height=120)
    uploaded = st.file_uploader("上传 TXT 作业文件（MVP版），后续可扩展 Word/PDF/ZIP 深度解析", type=["txt"], accept_multiple_files=True)
    if st.button("开始批改", use_container_width=True):
        rows = []
        for f in uploaded or []:
            text = f.read().decode("utf-8", errors="ignore")
            res = score_assignment_text(text, rubric)
            student = Path(f.name).stem
            rows.append({"学生/文件": student, "作业类型": assignment_type, **res})
        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True)
            out = io.BytesIO()
            with pd.ExcelWriter(out, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name="批改结果", index=False)
                pd.DataFrame([{"评分标准": rubric, "作业类型": assignment_type}]).to_excel(writer, sheet_name="评分设置", index=False)
            st.download_button("下载批改结果 Excel", out.getvalue(), "AI作业批改结果.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        else:
            st.warning("请先上传 TXT 作业文件。")


def render_feedback():
    st.markdown("## 用户反馈")
    category = st.selectbox("反馈类型", ["使用卡点", "模板建议", "AI结果问题", "功能建议", "其他"])
    content = st.text_area("反馈内容", height=180)
    if st.button("提交反馈", use_container_width=True):
        if content.strip():
            conn = db_conn()
            conn.execute("INSERT INTO feedback(user_email, category, content, created_at) VALUES (?, ?, ?, ?)", (current_email(), category, content, datetime.now().isoformat()))
            conn.commit()
            conn.close()
            st.success("反馈已提交，感谢你帮助产品变得更好。")
        else:
            st.warning("请填写反馈内容。")
    st.info(f"遇到无法解决的问题，也可以联系：{CONTACT_EMAIL}")


def render_admin():
    st.markdown("## 系统后台")
    if not is_logged_in() or current_email() != CONTACT_EMAIL:
        st.warning("仅管理员可访问后台。")
        return
    tab1, tab2, tab3 = st.tabs(["用户", "反馈", "分析记录"])
    conn = db_conn()
    with tab1:
        users = pd.read_sql_query("SELECT email, organization, role, created_at FROM users ORDER BY created_at DESC", conn)
        st.dataframe(users, use_container_width=True)
    with tab2:
        fb = pd.read_sql_query("SELECT * FROM feedback ORDER BY created_at DESC", conn)
        st.dataframe(fb, use_container_width=True)
    with tab3:
        hist = pd.read_sql_query("SELECT * FROM analysis_history ORDER BY created_at DESC", conn)
        st.dataframe(hist, use_container_width=True)
    conn.close()


def render_audit():
    st.markdown("## 专业审核：下一步如何把产品做得更好")
    st.markdown(
        """
### 核心判断
现在最重要的不是收费，而是把产品做成“用户一用就感觉省时间”的工具。建议以免费开放核心功能换取真实反馈、真实数据场景和产品口碑。

### 产品应继续丰富的方向
1. **场景深度优先**：每个场景不只做汇总，还要给出问题清单、诊断摘要、下一步建议。
2. **AI 不做摆设**：AI 要能回答“我该选哪个模板”“这个异常为什么出现”“我的数据缺什么字段”。
3. **样例体验必须强**：用户不准备数据也能1分钟看到价值。
4. **报告可直接交付**：报告包应包含 Excel、摘要、问题清单、模板说明。
5. **教育场景要慎重**：AI批改应标注“辅助”，避免替代教师最终判断。
6. **隐私与安全**：明确上传文件的处理边界，后续补充数据删除、导出和隐私说明。
7. **减少复杂按钮**：主界面只保留高频入口；高级功能放到后台或设置页。

### 建议下一个版本
Batch 51：免费版体验打磨 + 样例报告库 + 用户首次成功路径优化
- 3个强样例：电商售后、高校就业、门店经营
- 一键生成完整报告包
- AI解释每个指标
- 用户反馈自动分类
- 文件上传错误自助修复提示
        """
    )

# ----------------------------
# Main
# ----------------------------
def main():
    sidebar()
    page = st.session_state.page
    if page == "首页":
        render_home()
    elif page == "工作台":
        render_workspace()
    elif page == "模板中心":
        render_templates()
    elif page == "AI智能中心":
        render_ai_center()
    elif page == "AI作业批改":
        render_grading()
    elif page == "系统后台":
        render_admin()
    elif page == "反馈":
        render_feedback()
    render_audit() if page == "首页" else None
    st.markdown(f"<div class='footer'>© 2026 {APP_NAME}｜免费开放核心功能｜联系：{CONTACT_EMAIL}</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
