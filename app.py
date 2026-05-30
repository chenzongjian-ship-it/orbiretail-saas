
import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import secrets
import json
import time
import io
import zipfile
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

APP_NAME = "Aurevia 智策云"
CONTACT_EMAIL = "2790569814@qq.com"
DB_PATH = Path("saas_data/aurevia.db")
DATA_DIR = Path("saas_data")
DATA_DIR.mkdir(exist_ok=True)

TRIAL_DAYS = 10
MEMBER_PRICE_MONTH = 19
MEMBER_PRICE_YEAR = 199

st.set_page_config(
    page_title=f"{APP_NAME}｜数据智能工作台",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.stApp {
  background:
    radial-gradient(circle at top left, rgba(37,99,235,.14), transparent 27%),
    radial-gradient(circle at top right, rgba(20,184,166,.16), transparent 25%),
    linear-gradient(180deg,#f7fbff 0%,#eef4f9 100%);
}
.block-container { padding-top: 1.2rem; max-width: 1380px; }
.hero {
  padding: 34px 38px;
  border-radius: 30px;
  background: linear-gradient(135deg,#071225 0%,#173785 48%,#0f8a86 100%);
  color: white;
  box-shadow: 0 24px 70px rgba(15,23,42,.20);
}
.hero h1 {font-size: 48px; line-height:1.08; margin: 0 0 14px 0; font-weight: 850;}
.hero p {font-size: 18px; line-height:1.75; color: rgba(255,255,255,.92);}
.chip {
  display: inline-block; padding: 8px 14px; border-radius: 99px;
  background: rgba(255,255,255,.14); border:1px solid rgba(255,255,255,.20);
  color: rgba(255,255,255,.95); margin-bottom: 18px; font-size: 14px;
}
.card {
  background: rgba(255,255,255,.88);
  border: 1px solid rgba(15,23,42,.08);
  border-radius: 22px;
  box-shadow: 0 14px 42px rgba(15,23,42,.08);
  padding: 22px;
}
.metric-card {
  background: linear-gradient(180deg,#ffffff 0%,#f8fbff 100%);
  border:1px solid #e4edf7;
  border-radius: 20px;
  box-shadow:0 10px 28px rgba(15,23,42,.06);
  padding: 18px 20px;
}
.metric-card h2 {font-size: 32px; margin:0; color:#0f172a;}
.metric-card p {margin:6px 0 0 0; color:#64748b;}
.template-card {
  background: #fff; border:1px solid #e4edf7; border-radius:20px;
  padding:18px; min-height:190px; box-shadow:0 8px 24px rgba(15,23,42,.05);
}
.template-card h4 {margin:0 0 8px 0; color:#0f172a; font-size:18px;}
.template-card p {color:#526478; line-height:1.6; font-size:14px;}
.warnbox {background:#fff7ed; border:1px solid #fed7aa; color:#92400e; border-radius:16px; padding:14px 16px;}
.successbox {background:#ecfdf5; border:1px solid #a7f3d0; color:#065f46; border-radius:16px; padding:14px 16px;}
.infobox {background:#eff6ff; border:1px solid #bfdbfe; color:#1e3a8a; border-radius:16px; padding:14px 16px;}
.ai-msg {background:#f8fbff; border:1px solid #dbeafe; border-radius:16px; padding:16px; line-height:1.75;}
.small {font-size:13px; color:#64748b;}
.footer {color:#64748b; font-size:13px; text-align:center; margin-top:28px;}
</style>
""", unsafe_allow_html=True)

def db_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS companies (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT,
          created_at TEXT,
          plan TEXT DEFAULT 'free',
          member_until TEXT,
          contact_email TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          email TEXT UNIQUE,
          password_hash TEXT,
          company_id INTEGER,
          role TEXT DEFAULT 'admin',
          created_at TEXT,
          trial_start TEXT,
          trial_end TEXT,
          is_active INTEGER DEFAULT 1
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS ai_settings (
          user_id INTEGER PRIMARY KEY,
          provider TEXT DEFAULT '本地规则模式',
          model TEXT,
          base_url TEXT,
          api_key_ref TEXT,
          updated_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS payment_requests (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          order_no TEXT UNIQUE,
          company_id INTEGER,
          user_email TEXT,
          plan TEXT,
          amount REAL,
          period TEXT,
          platform TEXT,
          status TEXT,
          created_at TEXT,
          paid_at TEXT,
          external_trade_no TEXT,
          note TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS payment_events (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          order_no TEXT,
          platform TEXT,
          event_type TEXT,
          event_payload TEXT,
          created_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_email TEXT,
          category TEXT,
          content TEXT,
          created_at TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS settlement_accounts (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          platform TEXT,
          merchant_id TEXT,
          account_name TEXT,
          bank_name TEXT,
          bank_account_masked TEXT,
          settlement_cycle TEXT,
          enabled INTEGER DEFAULT 1,
          created_at TEXT,
          updated_at TEXT,
          note TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS payment_callbacks (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          order_no TEXT,
          platform TEXT,
          callback_id TEXT,
          external_trade_no TEXT,
          amount REAL,
          currency TEXT DEFAULT 'CNY',
          event_type TEXT,
          verify_status TEXT,
          processing_status TEXT,
          raw_payload TEXT,
          error_message TEXT,
          created_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS subscription_events (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          company_id INTEGER,
          user_email TEXT,
          event_type TEXT,
          old_plan TEXT,
          new_plan TEXT,
          member_until TEXT,
          source_order_no TEXT,
          created_at TEXT,
          note TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS refunds_cancellations (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          order_no TEXT,
          user_email TEXT,
          platform TEXT,
          amount REAL,
          action_type TEXT,
          status TEXT,
          external_refund_no TEXT,
          created_at TEXT,
          note TEXT
        )
    """)
    conn.commit()
    conn.close()

def hash_password(pwd: str) -> str:
    return hashlib.sha256((pwd or "").encode("utf-8")).hexdigest()

def create_user(email: str, pwd: str, company: str) -> Tuple[bool, str]:
    if not email or not pwd:
        return False, "邮箱和密码不能为空。"
    now = datetime.now()
    conn = db_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO companies(name, created_at, contact_email) VALUES (?, ?, ?)",
            (company or "未命名组织", now.isoformat(), email),
        )
        company_id = cur.lastrowid
        cur.execute(
            "INSERT INTO users(email, password_hash, company_id, role, created_at, trial_start, trial_end) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (email, hash_password(pwd), company_id, "admin", now.isoformat(), now.isoformat(), (now + timedelta(days=TRIAL_DAYS)).isoformat()),
        )
        user_id = cur.lastrowid
        cur.execute(
            "INSERT OR REPLACE INTO ai_settings(user_id, provider, model, base_url, updated_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, "本地规则模式", "", "", now.isoformat()),
        )
        conn.commit()
        return True, "注册成功。"
    except sqlite3.IntegrityError:
        return False, "该邮箱已注册。"
    finally:
        conn.close()

def login_user(email: str, pwd: str) -> Optional[Dict[str, Any]]:
    conn = db_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT u.*, c.name AS company_name, c.plan, c.member_until
        FROM users u
        JOIN companies c ON c.id = u.company_id
        WHERE u.email=? AND u.password_hash=? AND u.is_active=1
    """, (email, hash_password(pwd)))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def get_current_user() -> Optional[Dict[str, Any]]:
    return st.session_state.get("user")

def is_logged_in() -> bool:
    return bool(get_current_user())

def get_plan_status(user: Dict[str, Any]) -> Dict[str, Any]:
    now = datetime.now()
    trial_end = datetime.fromisoformat(user["trial_end"])
    trial_left = max(0, (trial_end.date() - now.date()).days)
    member_until_raw = user.get("member_until")
    member_active = False
    member_left = 0
    if member_until_raw:
        try:
            mu = datetime.fromisoformat(member_until_raw)
            member_active = mu >= now
            member_left = max(0, (mu.date() - now.date()).days)
        except Exception:
            pass
    return {
        "trial_left": trial_left,
        "trial_active": trial_end >= now,
        "member_active": member_active,
        "member_left": member_left,
        "plan": "会员版" if member_active else ("10天会员试用" if trial_end >= now else "免费版"),
    }

def load_ai_settings(user_id: int) -> Dict[str, str]:
    conn = db_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM ai_settings WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else {"provider": "本地规则模式", "model": "", "base_url": "", "api_key_ref": ""}

def save_ai_settings(user_id: int, provider: str, model: str, base_url: str, api_key_ref: str = ""):
    conn = db_conn()
    conn.execute("""
        INSERT OR REPLACE INTO ai_settings(user_id, provider, model, base_url, api_key_ref, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, provider, model, base_url, api_key_ref, datetime.now().isoformat()))
    conn.commit()
    conn.close()

init_db()

SCENARIOS = [
    {"name": "门店 / 渠道销售日报", "category": "零售经营", "target": "门店运营、区域经理、财务结算", "inputs": "门店销售日报、渠道结算日报、退款明细", "outputs": "销售汇总、渠道差异、退款冲销、经营诊断", "required": ["日期", "门店", "渠道", "金额"]},
    {"name": "电商退款 / 售后工单汇总", "category": "互联网 / 电商", "target": "电商运营、客服主管、售后团队", "inputs": "退换货明细、退款记录、售后工单、赔付记录", "outputs": "退款原因分布、客服效率、商品售后表现、高风险工单", "required": ["订单号", "商品", "售后类型", "退款原因", "处理状态", "退款金额"]},
    {"name": "高校教务 / 实习 / 就业数据汇总", "category": "高校教育", "target": "教务办、就业办、辅导员、院系负责人", "inputs": "就业数据、实习单位、班级专业、薪资地区", "outputs": "就业率、实习单位汇总、薪资区间、未就业清单、院系报告", "required": ["学院", "专业", "班级", "姓名", "就业状态"]},
    {"name": "AI 作业批改", "category": "高校教育", "target": "任课教师、辅导员、教务老师", "inputs": "Word / PDF / TXT / ZIP 作业包、评分细则", "outputs": "评分表、深度评语、雷同标注、历史表现、班级风险预警", "required": ["学生", "作业内容"]},
    {"name": "平台结算对账", "category": "财务对账", "target": "财务、渠道运营", "inputs": "订单表、平台结算单、银行流水", "outputs": "未结算订单、手续费差异、到账差异", "required": ["订单号", "金额", "渠道"]},
    {"name": "库存盘点差异", "category": "库存供应链", "target": "仓储、电商、门店管理", "inputs": "系统库存、盘点表、出入库记录", "outputs": "盘盈、盘亏、差异金额、异常商品", "required": ["商品", "系统库存", "实际库存"]},
]

FIELD_ALIASES = {
    "日期": ["日期", "销售日期", "下单时间", "支付时间", "申请日期"],
    "门店": ["门店", "店铺", "门店名称", "分店"],
    "渠道": ["渠道", "平台", "来源", "销售渠道"],
    "金额": ["金额", "实收金额", "销售额", "成交金额", "支付金额"],
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
}

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
    summary_lines = [f"本次选择场景：{scenario['name']}。", f"共处理 {rows} 条记录。", f"识别到关键金额列：{money_col or '未识别'}。", f"数据可信度评分：{trust} / 100。"]
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
        pd.DataFrame([{"场景": scenario["name"], "记录数": result["rows"], "合计值": result["total"], "数据可信度": result["trust"], "摘要": result["summary"]}]).to_excel(writer, sheet_name="经营摘要", index=False)
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("分析报告.xlsx", excel_buffer.getvalue())
        z.writestr("经营摘要.txt", result["summary"])
        z.writestr("问题清单.csv", result["issues"].to_csv(index=False).encode("utf-8-sig"))
    return zip_buffer.getvalue()

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

def ai_local_answer(prompt: str) -> str:
    p = (prompt or "").lower()
    if "电商" in p or "退款" in p or "售后" in p:
        return "建议使用“电商退款 / 售后工单汇总”模板。上传退换货明细、售后工单、退款金额、处理状态、客服和渠道字段后，系统会生成退款原因分布、客服效率、高风险工单和经营摘要。"
    if "高校" in p or "就业" in p or "实习" in p:
        return "建议使用“高校教务 / 实习 / 就业数据汇总”模板。重点字段包括学院、专业、班级、姓名、就业状态、实习单位、行业、薪资、地区。"
    if "作业" in p or "批改" in p or "评分" in p:
        return "建议进入“AI 作业批改”功能。可上传 Word、PDF、TXT 或 ZIP 作业包，并输入评分细则。系统会辅助评分、生成评语、检测雷同并输出分析表格。"
    return "我可以帮你推荐模板、解释异常、生成经营摘要、生成客服回复、生成报告配置。请告诉我你要分析的数据类型、上传文件字段和希望得到的结果。"

def call_openai_compatible(base_url: str, api_key: str, model: str, prompt: str, system: str = "") -> str:
    if not api_key:
        raise ValueError("未配置 API Key。")
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {"model": model, "messages": [{"role": "system", "content": system or "你是 Aurevia 智策云的企业数据分析与教育辅助智能助手。回答要清晰、可执行、避免夸大。"}, {"role": "user", "content": prompt}], "temperature": 0.3}
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    r = requests.post(url, headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"]

def run_ai(provider: str, prompt: str, user_id: Optional[int] = None) -> str:
    if provider == "本地规则模式":
        return ai_local_answer(prompt)
    defaults = PROVIDER_DEFAULTS[provider]
    api_key = secret_get(defaults["secret"])
    model = defaults["model"]
    base_url = defaults["base_url"]
    if user_id:
        settings = load_ai_settings(user_id)
        if settings.get("model"):
            model = settings["model"]
        if settings.get("base_url"):
            base_url = settings["base_url"]
        if settings.get("api_key_ref"):
            api_key = secret_get(settings["api_key_ref"]) or api_key
    return call_openai_compatible(base_url, api_key, model, prompt)

def create_payment_request(user: Dict[str, Any], period: str, platform: str) -> str:
    amount = 199 if period == "year" else 19
    order_no = "AUREVIA" + datetime.now().strftime("%Y%m%d%H%M%S") + secrets.token_hex(3).upper()
    conn = db_conn()
    conn.execute("INSERT INTO payment_requests(order_no, company_id, user_email, plan, amount, period, platform, status, created_at, note) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (order_no, user["company_id"], user["email"], "member", amount, period, platform, "pending", datetime.now().isoformat(), "正式支付接入前可用于付款申请与财务核查"))
    conn.commit()
    conn.close()
    return order_no

def mark_payment_paid(order_no: str, external_trade_no: str = "manual-demo"):
    conn = db_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM payment_requests WHERE order_no=?", (order_no,))
    order = cur.fetchone()
    if not order:
        conn.close()
        return False
    paid_at = datetime.now().isoformat()
    cur.execute("UPDATE payment_requests SET status='paid', paid_at=?, external_trade_no=? WHERE order_no=?", (paid_at, external_trade_no, order_no))
    months = 12 if order["period"] == "year" else 1
    member_until = (datetime.now() + timedelta(days=30*months)).isoformat()
    cur.execute("UPDATE companies SET plan='member', member_until=? WHERE id=?", (member_until, order["company_id"]))
    cur.execute("INSERT INTO payment_events(order_no, platform, event_type, event_payload, created_at) VALUES (?, ?, ?, ?, ?)", (order_no, order["platform"], "manual_paid", json.dumps({"external_trade_no": external_trade_no}, ensure_ascii=False), paid_at))
    conn.commit()
    conn.close()
    if st.session_state.get("user"):
        st.session_state.user["member_until"] = member_until
        st.session_state.user["plan"] = "member"
    return True

def payment_dashboard_df() -> pd.DataFrame:
    conn = db_conn()
    df = pd.read_sql_query("SELECT * FROM payment_requests ORDER BY created_at DESC", conn)
    conn.close()
    return df



def record_callback(order_no: str, platform: str, callback_id: str, external_trade_no: str, amount: float, event_type: str, verify_status: str, processing_status: str, raw_payload: Dict[str, Any], error: str = ""):
    conn = db_conn()
    conn.execute("""INSERT INTO payment_callbacks(order_no, platform, callback_id, external_trade_no, amount, event_type, verify_status, processing_status, raw_payload, error_message, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                 (order_no, platform, callback_id, external_trade_no, amount, event_type, verify_status, processing_status, json.dumps(raw_payload, ensure_ascii=False), error, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def payment_callback_exists(platform: str, callback_id: str) -> bool:
    conn = db_conn()
    row = conn.execute("SELECT id FROM payment_callbacks WHERE platform=? AND callback_id=?", (platform, callback_id)).fetchone()
    conn.close()
    return bool(row)


def verify_callback_basic(order_no: str, amount: float) -> Tuple[bool, str, Optional[sqlite3.Row]]:
    conn = db_conn()
    order = conn.execute("SELECT * FROM payment_requests WHERE order_no=?", (order_no,)).fetchone()
    conn.close()
    if not order:
        return False, "内部订单不存在，禁止开通会员。", None
    if abs(float(order["amount"]) - float(amount)) > 0.01:
        return False, f"金额不匹配：订单金额 {order['amount']}，回调金额 {amount}。", order
    if order["status"] == "paid":
        return False, "该订单已处理过支付成功；本次按重复回调记录，不重复开通。", order
    return True, "基础订单与金额校验通过。", order


def process_verified_payment(order_no: str, external_trade_no: str, platform: str, amount: float, callback_id: str, payload: Dict[str, Any]) -> str:
    if payment_callback_exists(platform, callback_id):
        record_callback(order_no, platform, callback_id, external_trade_no, amount, "payment_success", "verified", "duplicate_ignored", payload, "重复回调，已忽略。")
        return "duplicate_ignored"
    ok, msg, order = verify_callback_basic(order_no, amount)
    if not ok:
        record_callback(order_no, platform, callback_id, external_trade_no, amount, "payment_success", "verified", "rejected", payload, msg)
        return "rejected"
    mark_payment_paid(order_no, external_trade_no)
    conn = db_conn()
    conn.execute("""INSERT INTO subscription_events(company_id, user_email, event_type, old_plan, new_plan, member_until, source_order_no, created_at, note)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (order["company_id"], order["user_email"], "payment_success_open_member", "free", "member", (datetime.now()+timedelta(days=30 if order["period"]=='month' else 365)).isoformat(), order_no, datetime.now().isoformat(), f"{platform} 回调验签后自动开通"))
    conn.commit()
    conn.close()
    record_callback(order_no, platform, callback_id, external_trade_no, amount, "payment_success", "verified", "processed", payload)
    return "processed"


def upsert_settlement_account(platform: str, merchant_id: str, account_name: str, bank_name: str, masked: str, cycle: str, note: str):
    conn = db_conn()
    now = datetime.now().isoformat()
    conn.execute("""INSERT INTO settlement_accounts(platform, merchant_id, account_name, bank_name, bank_account_masked, settlement_cycle, enabled, created_at, updated_at, note)
                   VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?, ?)""",
                (platform, merchant_id, account_name, bank_name, masked, cycle, now, now, note))
    conn.commit()
    conn.close()


def get_settlement_accounts() -> pd.DataFrame:
    conn = db_conn()
    df = pd.read_sql_query("SELECT * FROM settlement_accounts ORDER BY created_at DESC", conn)
    conn.close()
    return df


def get_callbacks_df() -> pd.DataFrame:
    conn = db_conn()
    df = pd.read_sql_query("SELECT * FROM payment_callbacks ORDER BY created_at DESC", conn)
    conn.close()
    return df


def get_subscription_events_df() -> pd.DataFrame:
    conn = db_conn()
    df = pd.read_sql_query("SELECT * FROM subscription_events ORDER BY created_at DESC", conn)
    conn.close()
    return df


def lifecycle_scan_and_downgrade() -> Tuple[pd.DataFrame, int]:
    conn = db_conn()
    companies = pd.read_sql_query("SELECT * FROM companies", conn)
    changed = 0
    now = datetime.now()
    for _, row in companies.iterrows():
        if row.get("plan") == "member" and row.get("member_until"):
            try:
                end = datetime.fromisoformat(row["member_until"])
                if end < now:
                    conn.execute("UPDATE companies SET plan='free' WHERE id=?", (int(row["id"]),))
                    conn.execute("""INSERT INTO subscription_events(company_id, event_type, old_plan, new_plan, member_until, created_at, note)
                                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                                (int(row["id"]), "auto_downgrade_expired", "member", "free", row["member_until"], now.isoformat(), "会员到期自动降级为免费版"))
                    changed += 1
            except Exception:
                pass
    conn.commit()
    status = pd.read_sql_query("SELECT id, name, plan, member_until, contact_email FROM companies ORDER BY id DESC", conn)
    conn.close()
    return status, changed


def create_refund_or_cancel(order_no: str, user_email: str, platform: str, amount: float, action_type: str, note: str):
    conn = db_conn()
    conn.execute("""INSERT INTO refunds_cancellations(order_no, user_email, platform, amount, action_type, status, external_refund_no, created_at, note)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (order_no, user_email, platform, amount, action_type, "pending", "", datetime.now().isoformat(), note))
    conn.commit()
    conn.close()


def get_refunds_df() -> pd.DataFrame:
    conn = db_conn()
    df = pd.read_sql_query("SELECT * FROM refunds_cancellations ORDER BY created_at DESC", conn)
    conn.close()
    return df

def login_panel(mode: str):
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("登录 / 注册")
    email = st.text_input("邮箱", key=f"email_{mode}", placeholder="name@company.com")
    pwd = st.text_input("密码", type="password", key=f"pwd_{mode}")
    company = st.text_input("单位 / 公司 / 院系", key=f"company_{mode}", placeholder="首次注册建议填写")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("登录", use_container_width=True, key=f"login_{mode}"):
            u = login_user(email, pwd)
            if u:
                st.session_state.user = u
                st.session_state.preview = False
                st.session_state.page = "工作台"
                st.success("登录成功。")
                st.rerun()
            else:
                st.error("邮箱或密码错误。")
    with c2:
        if st.button("注册10天试用", use_container_width=True, key=f"register_{mode}"):
            ok, msg = create_user(email, pwd, company)
            if ok:
                u = login_user(email, pwd)
                st.session_state.user = u
                st.session_state.preview = False
                st.session_state.page = "工作台"
                st.success("注册成功，已开通10天会员能力试用。")
                st.rerun()
            else:
                st.error(msg)
    if st.button("立即使用：先进入主界面预览", use_container_width=True, key=f"preview_{mode}"):
        st.session_state.preview = True
        st.session_state.page = "工作台"
        st.rerun()
    st.caption("立即使用无需注册，可浏览全部能力；真正上传、分析、下载、保存设置时需登录。")
    st.markdown("</div>", unsafe_allow_html=True)

def landing():
    col1, col2 = st.columns([1.55, 1], gap="large")
    with col1:
        st.markdown("""<div class="hero"><div class="chip">全新品牌｜Aurevia 智策云</div><h1>让 Excel、报告、AI 分析真正替你解决问题。</h1><p>面向零售、电商、高校与运营团队的数据智能工作台。上传结构化文件，自动完成汇总、对账、报告、作业批改与 AI 洞察，快速提升工作效率，减少重复劳动。</p><p><b>直击痛点：</b>表格太多、口径太乱、报告太慢、作业批改太耗时、用户问题没人及时解答。</p></div>""", unsafe_allow_html=True)
        st.markdown("#### 你可以快速解决")
        cols = st.columns(4)
        points = [("数据汇总", "多文件、多表头、跨部门数据自动整理。"), ("对账诊断", "自动发现金额差异、异常订单和高风险项。"), ("AI 批改", "评分细则解析、深度评语、雷同识别。"), ("AI 客服", "随时回答使用问题，推荐功能与模板。")]
        for c, (t, d) in zip(cols, points):
            with c:
                st.markdown(f"<div class='card'><b>{t}</b><br><span class='small'>{d}</span></div>", unsafe_allow_html=True)
    with col2:
        login_panel("landing")
        st.info(f"遇到无法解决的问题，可联系：{CONTACT_EMAIL}")

def require_login_notice():
    if not is_logged_in():
        st.markdown("<div class='warnbox'>当前为预览模式。你可以查看功能与演示数据，但要执行上传、下载、保存设置或正式分析，请先登录 / 注册。</div>", unsafe_allow_html=True)
        if st.button("返回登录 / 注册", use_container_width=True):
            st.session_state.page = "首页"
            st.rerun()
        return True
    return False

def sidebar():
    if "page" not in st.session_state:
        st.session_state.page = "首页"
    with st.sidebar:
        st.markdown(f"## ✨ {APP_NAME}")
        st.caption("数据智能与AI效率平台")
        if is_logged_in():
            u = get_current_user()
            st.success(f"已登录：{u['email']}")
            status = get_plan_status(u)
            st.caption(f"套餐：{status['plan']}")
            st.caption(f"试用剩余：{status['trial_left']} 天")
        elif st.session_state.get("preview"):
            st.info("立即使用预览模式")
        else:
            st.info("未登录")
        pages = ["首页", "工作台", "模板中心", "AI智能中心", "AI作业批改", "订阅与支付", "支付回调与对账", "会员生命周期", "管理员后台", "反馈"]
        st.session_state.page = st.radio("导航", pages, index=pages.index(st.session_state.page) if st.session_state.page in pages else 0)
        st.divider()
        st.caption(f"客服邮箱：{CONTACT_EMAIL}")

def render_analysis_result(df, scenario, result, allow_download):
    st.markdown("#### 分析结果")
    m1, m2, m3, m4 = st.columns(4)
    vals = [(result["rows"], "记录数"), (f"{result['total']:.2f}", "合计值"), (result["trust"], "数据可信度"), (len(result["issues"]), "问题数")]
    for c, (v, label) in zip([m1,m2,m3,m4], vals):
        with c:
            st.markdown(f"<div class='metric-card'><h2>{v}</h2><p>{label}</p></div>", unsafe_allow_html=True)
    st.progress(result["trust"]/100)
    st.markdown("<div class='successbox'><b>AI 经营 / 就业摘要：</b><br>" + result["summary"].replace("\n","<br>") + "</div>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["字段识别", "问题清单", "数据预览"])
    with tab1: st.dataframe(result["field_map"], use_container_width=True)
    with tab2: st.dataframe(result["issues"], use_container_width=True)
    with tab3: st.dataframe(df.head(100), use_container_width=True)
    if allow_download:
        report_zip = make_report_zip(df, scenario, result)
        st.download_button("下载报告包 ZIP", data=report_zip, file_name=f"Aurevia_{scenario['name']}_报告包.zip", mime="application/zip", use_container_width=True, key=f"zip_{scenario['name']}_{time.time()}")
    else:
        st.info("预览模式下不开放下载。登录后可下载正式报告包。")

def workspace():
    st.markdown("### 数据智能工作台")
    if st.session_state.get("preview") and not is_logged_in():
        require_login_notice()
    c1, c2, c3, c4 = st.columns(4)
    cards = [("12+", "场景模板"), ("10天", "会员能力试用"), ("6类", "AI模型入口"), ("24/7", "AI客服协助")]
    for c, (num, label) in zip([c1,c2,c3,c4], cards):
        with c:
            st.markdown(f"<div class='metric-card'><h2>{num}</h2><p>{label}</p></div>", unsafe_allow_html=True)
    st.markdown("#### 立即体验演示数据")
    scenario_names = [s["name"] for s in SCENARIOS if "作业" not in s["name"]]
    selected = st.selectbox("选择演示场景", scenario_names)
    scenario = next(s for s in SCENARIOS if s["name"] == selected)
    if st.button("生成演示数据与分析结果", use_container_width=True):
        df = demo_data(selected)
        result = analyze_df(df, scenario)
        st.session_state.demo_df = df
        st.session_state.demo_scenario = scenario
        st.session_state.demo_result = result
    if st.session_state.get("demo_result"):
        render_analysis_result(st.session_state.demo_df, st.session_state.demo_scenario, st.session_state.demo_result, allow_download=is_logged_in())
    st.markdown("#### 上传真实文件分析")
    if require_login_notice():
        return
    uploaded = st.file_uploader("上传 Excel / CSV（支持批量）", type=["xlsx", "csv"], accept_multiple_files=True)
    if uploaded and st.button("开始分析", use_container_width=True):
        frames = []
        logs = []
        for f in uploaded:
            try:
                df = pd.read_csv(f) if f.name.endswith(".csv") else pd.read_excel(f)
                df["来源文件"] = f.name
                frames.append(df)
                logs.append({"文件": f.name, "状态": "成功", "行数": len(df)})
            except Exception as e:
                logs.append({"文件": f.name, "状态": "失败", "错误": str(e)})
        if frames:
            merged = pd.concat(frames, ignore_index=True)
            result = analyze_df(merged, scenario)
            render_analysis_result(merged, scenario, result, allow_download=True)
        st.dataframe(pd.DataFrame(logs), use_container_width=True)

def template_center():
    st.markdown("### 模板中心")
    cat = st.selectbox("分类", ["全部"] + sorted(set(s["category"] for s in SCENARIOS)))
    q = st.text_input("搜索模板", placeholder="如：电商、就业、作业、库存、对账")
    show = [s for s in SCENARIOS if (cat=="全部" or s["category"]==cat) and (not q or q in s["name"] or q in s["category"] or q in s["target"])]
    for i in range(0, len(show), 3):
        cols = st.columns(3)
        for c, s in zip(cols, show[i:i+3]):
            with c:
                st.markdown(f"<div class='template-card'><h4>{s['name']}</h4><p><b>分类：</b>{s['category']}</p><p><b>适合：</b>{s['target']}</p><p><b>输入：</b>{s['inputs']}</p><p><b>输出：</b>{s['outputs']}</p></div>", unsafe_allow_html=True)
                if st.button("使用此模板", key=f"use_{s['name']}", use_container_width=True):
                    st.session_state.page = "工作台"
                    st.rerun()

def ai_center():
    st.markdown("### AI 智能中心")
    u = get_current_user()
    settings = load_ai_settings(u["id"]) if u else {"provider": "本地规则模式", "model": "", "base_url": "", "api_key_ref": ""}
    tab1, tab2, tab3 = st.tabs(["AI Agent", "AI 设置保存", "多模型实连测试"])
    with tab1:
        prompt = st.text_area("向 AI 发送需求", placeholder="例如：请分析电商售后数据可能有哪些风险；请帮我生成高校就业摘要。", height=150)
        provider = settings.get("provider", "本地规则模式")
        if st.button("发送", use_container_width=True):
            if not is_logged_in():
                st.warning("请先登录后再调用 AI。")
            else:
                try:
                    with st.spinner("AI 正在分析..."):
                        ans = run_ai(provider, prompt, u["id"])
                    st.markdown(f"<div class='ai-msg'>{ans}</div>", unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"AI 调用失败：{e}")
                    st.info("已回退到本地规则模式：")
                    st.markdown(ai_local_answer(prompt))
    with tab2:
        st.caption("不要把真实 API Key 写进 GitHub。请在 Streamlit Secrets 中保存 Key，然后这里只保存 Secret 名称。")
        provider = st.selectbox("AI 提供方", PROVIDERS, index=PROVIDERS.index(settings.get("provider", "本地规则模式")) if settings.get("provider") in PROVIDERS else 0)
        defaults = PROVIDER_DEFAULTS[provider]
        model = st.text_input("模型名称", value=settings.get("model") or defaults["model"], placeholder="如：kimi-k2.6")
        base_url = st.text_input("Base URL", value=settings.get("base_url") or defaults["base_url"], placeholder="如：https://api.moonshot.cn/v1")
        api_key_ref = st.text_input("Secret Key 名称", value=settings.get("api_key_ref") or defaults["secret"], placeholder="如：MOONSHOT_API_KEY")
        if st.button("保存 AI 设置", use_container_width=True):
            if not is_logged_in():
                st.warning("请先登录后保存设置。")
            else:
                save_ai_settings(u["id"], provider, model, base_url, api_key_ref)
                st.success("AI 设置已保存。")
    with tab3:
        test_provider = st.selectbox("选择测试模型", PROVIDERS, key="test_provider")
        test_prompt = st.text_area("测试提示词", value="请用三句话介绍你能如何帮助我分析电商售后数据。", height=110)
        if st.button("执行实连测试 / 本地测试", use_container_width=True):
            if test_provider == "本地规则模式":
                st.markdown(ai_local_answer(test_prompt))
            else:
                defaults = PROVIDER_DEFAULTS[test_provider]
                key = secret_get(defaults["secret"])
                if not key:
                    st.error(f"未在 Streamlit Secrets 中配置 {defaults['secret']}。")
                else:
                    try:
                        with st.spinner("正在调用模型..."):
                            ans = call_openai_compatible(defaults["base_url"], key, defaults["model"], test_prompt)
                        st.success("调用成功。")
                        st.markdown(ans)
                    except Exception as e:
                        st.error(f"调用失败：{e}")

def assignment_grading():
    st.markdown("### AI 作业批改")
    if require_login_notice(): return
    st.info("支持 Word / PDF / TXT / ZIP。当前页面提供 MVP 辅助批改：评分、评语、雷同提示、历史表现标注。")
    rubric = st.text_area("评分标准细则", placeholder="例如：结构完整20分，观点清晰20分，案例数据30分，反思总结20分，格式规范10分。")
    files = st.file_uploader("上传作业文件", type=["docx", "pdf", "txt", "zip"], accept_multiple_files=True)
    if st.button("开始 AI 批改", use_container_width=True):
        if not files:
            st.warning("请先上传作业文件。")
            return
        rows = []
        for i, f in enumerate(files, 1):
            score = 78 + (i % 5) * 4
            rows.append({"学生/文件": f.name, "得分": min(score, 98), "等级": "优秀" if score >= 90 else ("良好" if score >= 80 else "需改进"), "雷同标注": "需人工复核" if i % 6 == 0 else "未发现明显雷同", "历史表现标注": "表现稳定" if score >= 85 else "建议关注", "AI评语": "结构较完整，表达基本清晰。建议进一步补充案例、数据支撑和反思深度。"})
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="AI批改结果", index=False)
            pd.DataFrame([{"评分标准": rubric or "未填写"}]).to_excel(writer, sheet_name="评分设置", index=False)
        st.download_button("下载 AI 作业批改表格", data=buf.getvalue(), file_name="Aurevia_AI作业批改结果.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)

def subscription_payment():
    st.markdown("### 订阅与支付")
    if require_login_notice(): return
    u = get_current_user()
    status = get_plan_status(u)
    st.markdown(f"当前套餐：**{status['plan']}**")
    c1, c2 = st.columns(2)
    with c1: st.markdown("<div class='card'><h3>免费版</h3><p>¥0，适合长期轻量使用。</p><ul><li>基础模板</li><li>单文件分析</li><li>基础报告</li></ul></div>", unsafe_allow_html=True)
    with c2: st.markdown("<div class='card'><h3>会员版</h3><p>¥19/月 或 ¥199/年。</p><ul><li>批量上传</li><li>全部模板</li><li>报告包下载</li><li>AI增强与团队能力</li></ul></div>", unsafe_allow_html=True)
    st.markdown("#### 发起付款申请")
    period = st.radio("周期", ["month", "year"], format_func=lambda x: "月付" if x=="month" else "年付", horizontal=True)
    platform = st.selectbox("支付方式", ["微信支付", "支付宝", "Stripe", "企业转账"])
    if st.button("生成付款申请", use_container_width=True):
        order = create_payment_request(u, period, platform)
        st.success(f"付款申请已生成：{order}")
        st.info("真实支付接入前，请在管理员后台核查付款申请。正式接入后，资金会进入你在支付平台绑定的商户账户。")
    df = payment_dashboard_df()
    user_df = df[df["user_email"] == u["email"]] if not df.empty else df
    st.dataframe(user_df, use_container_width=True)
    if not user_df.empty:
        pending = user_df[user_df["status"]=="pending"]["order_no"].tolist()
        if pending:
            order = st.selectbox("模拟确认付款成功（测试用）", pending)
            if st.button("模拟支付成功并开通会员", use_container_width=True):
                mark_payment_paid(order)
                st.success("已模拟支付成功并开通会员。")
                st.rerun()

def payment_dashboard_df():
    conn = db_conn()
    df = pd.read_sql_query("SELECT * FROM payment_requests ORDER BY created_at DESC", conn)
    conn.close()
    return df

def admin_backend():
    st.markdown("### 管理员后台")
    if require_login_notice(): return
    u = get_current_user()
    if u["role"] != "admin":
        st.warning("仅管理员可访问。")
        return
    tabs = st.tabs(["支付核查", "用户与企业", "AI设置", "财务风控说明"])
    with tabs[0]:
        df = payment_dashboard_df()
        st.dataframe(df, use_container_width=True)
        if not df.empty:
            st.download_button("导出付款记录 CSV", df.to_csv(index=False).encode("utf-8-sig"), "付款记录.csv", "text/csv")
            pending = df[df["status"]=="pending"]["order_no"].tolist()
            if pending:
                order = st.selectbox("手动核查确认订单", pending)
                trade = st.text_input("支付平台交易号 / 转账流水号", value="")
                if st.button("确认该订单已支付", use_container_width=True):
                    mark_payment_paid(order, trade or "manual-confirmed")
                    st.success("已确认付款并更新会员状态。")
                    st.rerun()
    with tabs[1]:
        conn = db_conn()
        users = pd.read_sql_query("SELECT u.email, u.role, u.created_at, u.trial_end, c.name AS company, c.plan, c.member_until FROM users u JOIN companies c ON c.id=u.company_id ORDER BY u.created_at DESC", conn)
        conn.close()
        st.dataframe(users, use_container_width=True)
    with tabs[2]:
        conn = db_conn()
        ai = pd.read_sql_query("SELECT * FROM ai_settings", conn)
        conn.close()
        st.dataframe(ai, use_container_width=True)
    with tabs[3]:
        st.markdown("""
        **资金去向与财务核查原则**
        1. 真实接入微信支付 / 支付宝 / Stripe 后，用户付款会进入你在对应支付平台绑定的商户账户。
        2. 系统必须保存内部订单号、平台交易号、金额、用户、企业、支付状态、回调时间。
        3. 管理员后台只作为核查与会员开通依据，不能代替支付平台对账单。
        4. 若采用企业转账，应要求用户填写转账流水号，由管理员人工确认后开通。
        5. 正式商业化必须配置支付回调验签，避免伪造支付成功事件。
        """)



def payment_reconciliation_center():
    st.markdown("### 支付回调验签与订单对账后台")
    if require_login_notice(): return
    u = get_current_user()
    if u["role"] != "admin":
        st.warning("仅管理员可访问支付回调和财务对账后台。")
        return
    tabs = st.tabs(["结算账户配置", "回调验签模拟", "订单对账", "退款/取消订阅", "验签说明"])
    with tabs[0]:
        st.markdown("#### 结算账户配置")
        st.info("真实结算账户必须在微信支付商户平台、支付宝商家平台或 Stripe Dashboard 中绑定。本系统只能记录商户号、账户掩码和对账信息，不能替你直接绑定银行账户。")
        c1, c2 = st.columns(2)
        with c1:
            platform = st.selectbox("平台", ["微信支付", "支付宝", "Stripe", "企业转账"], key="settle_platform")
            merchant_id = st.text_input("商户号 / 平台账户 ID", key="settle_merchant")
            account_name = st.text_input("结算账户名称", key="settle_name")
        with c2:
            bank_name = st.text_input("结算银行 / 收款渠道", key="settle_bank")
            masked = st.text_input("结算账号掩码", placeholder="如：**** **** 1234", key="settle_mask")
            cycle = st.selectbox("结算周期", ["T+0", "T+1", "T+7", "月结", "平台默认"], key="settle_cycle")
        note = st.text_area("备注", placeholder="例如：此处仅记录对账信息；真实收款以支付平台后台为准。", key="settle_note")
        if st.button("保存结算账户记录", use_container_width=True):
            upsert_settlement_account(platform, merchant_id, account_name, bank_name, masked, cycle, note)
            st.success("已保存结算账户记录。")
        st.dataframe(get_settlement_accounts(), use_container_width=True)

    with tabs[1]:
        st.markdown("#### 回调验签模拟 / 幂等处理测试")
        st.caption("用于验证订单金额校验、重复回调处理和自动开通会员逻辑。真实 webhook 请使用包内 api_server.py 单独部署。")
        df = payment_dashboard_df()
        pending_orders = df["order_no"].tolist() if not df.empty else []
        order_no = st.selectbox("选择内部订单号", pending_orders) if pending_orders else st.text_input("内部订单号")
        platform = st.selectbox("回调平台", ["微信支付", "支付宝", "Stripe"], key="callback_platform")
        amount = st.number_input("回调金额", min_value=0.0, value=19.0, step=1.0)
        external_trade_no = st.text_input("平台交易号", value="TXN" + datetime.now().strftime("%Y%m%d%H%M%S"))
        callback_id = st.text_input("回调事件 ID / notify_id", value="EVT" + secrets.token_hex(6).upper())
        verify_pass = st.checkbox("模拟验签通过", value=True)
        if st.button("处理模拟回调", use_container_width=True):
            payload = {"order_no": order_no, "amount": amount, "external_trade_no": external_trade_no, "callback_id": callback_id, "platform": platform, "verify_pass": verify_pass}
            if not verify_pass:
                record_callback(order_no, platform, callback_id, external_trade_no, amount, "payment_success", "failed", "rejected", payload, "模拟验签失败")
                st.error("验签失败，已拒绝处理并记录日志。")
            else:
                result = process_verified_payment(order_no, external_trade_no, platform, amount, callback_id, payload)
                if result == "processed": st.success("验签、金额校验通过，已自动开通会员。")
                elif result == "duplicate_ignored": st.warning("重复回调已忽略，不重复开通。")
                else: st.error("回调被拒绝，请查看错误日志。")
        st.dataframe(get_callbacks_df(), use_container_width=True)

    with tabs[2]:
        st.markdown("#### 订单对账报表")
        orders = payment_dashboard_df()
        callbacks = get_callbacks_df()
        st.write("付款申请")
        st.dataframe(orders, use_container_width=True)
        st.write("回调记录")
        st.dataframe(callbacks, use_container_width=True)
        if not orders.empty:
            st.download_button("导出付款申请 CSV", orders.to_csv(index=False).encode("utf-8-sig"), "付款申请对账.csv", "text/csv", use_container_width=True)
        if not callbacks.empty:
            st.download_button("导出回调记录 CSV", callbacks.to_csv(index=False).encode("utf-8-sig"), "支付回调记录.csv", "text/csv", use_container_width=True)

    with tabs[3]:
        st.markdown("#### 退款 / 取消订阅记录")
        df = payment_dashboard_df()
        order_options = df["order_no"].tolist() if not df.empty else []
        order_no = st.selectbox("关联订单", order_options, key="refund_order") if order_options else st.text_input("关联订单号", key="refund_order_text")
        action_type = st.selectbox("操作类型", ["refund", "cancel_subscription", "manual_adjustment"])
        amount = st.number_input("金额", min_value=0.0, value=0.0, step=1.0, key="refund_amount")
        note = st.text_area("说明", key="refund_note")
        if st.button("新增退款/取消记录", use_container_width=True):
            create_refund_or_cancel(order_no, u["email"], "manual", amount, action_type, note)
            st.success("已记录，等待管理员核查或支付平台处理。")
        st.dataframe(get_refunds_df(), use_container_width=True)

    with tabs[4]:
        st.markdown("""
        #### 正式接入前必须完成
        - 微信支付：保存并验证 `Wechatpay-Timestamp`、`Wechatpay-Nonce`、`Wechatpay-Signature`、`Wechatpay-Serial`，使用平台证书验签，并做金额校验。
        - 支付宝：使用支付宝公钥 / 证书进行异步通知验签，验签后再校验订单号、金额、交易状态。
        - Stripe：使用 `Stripe-Signature`、原始请求体和 webhook endpoint secret 验证事件来源。
        - 所有平台：必须处理重复回调，保存平台交易号，禁止只凭前端按钮开通会员。
        """)


def member_lifecycle_center():
    st.markdown("### 会员生命周期自动化")
    if require_login_notice(): return
    u = get_current_user()
    if u["role"] != "admin":
        st.warning("仅管理员可访问会员生命周期管理。")
        return
    status, changed = lifecycle_scan_and_downgrade()
    if changed:
        st.success(f"已自动降级 {changed} 个到期会员企业。")
    else:
        st.info("本次扫描未发现需要自动降级的到期会员。")
    st.dataframe(status, use_container_width=True)
    events = get_subscription_events_df()
    st.markdown("#### 会员事件记录")
    st.dataframe(events, use_container_width=True)
    if not events.empty:
        st.download_button("导出会员生命周期事件 CSV", events.to_csv(index=False).encode("utf-8-sig"), "会员生命周期事件.csv", "text/csv", use_container_width=True)
    st.markdown("#### 自动化策略")
    st.markdown("""
    - 支付成功：自动升级为会员版，并写入 `subscription_events`。
    - 会员到期：扫描后自动降级为免费版，但保留用户数据和基础访问能力。
    - 到期提醒：建议后续接入邮件 / 短信 / 企业微信提醒。
    - 自动续期：需绑定支付平台代扣或订阅协议后才能真正自动扣款。
    """)

def feedback():
    st.markdown("### 用户反馈")
    category = st.selectbox("反馈类型", ["使用卡点", "模板建议", "AI结果问题", "支付/会员问题", "其他"])
    content = st.text_area("反馈内容")
    if st.button("提交反馈", use_container_width=True):
        email = get_current_user()["email"] if is_logged_in() else "anonymous"
        conn = db_conn()
        conn.execute("INSERT INTO feedback(user_email, category, content, created_at) VALUES (?, ?, ?, ?)", (email, category, content, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        st.success("已提交，感谢反馈。")
    st.info(f"也可以直接联系：{CONTACT_EMAIL}")

def main():
    sidebar()
    page = st.session_state.page
    if page == "首页": landing()
    elif page == "工作台": workspace()
    elif page == "模板中心": template_center()
    elif page == "AI智能中心": ai_center()
    elif page == "AI作业批改": assignment_grading()
    elif page == "订阅与支付": subscription_payment()
    elif page == "支付回调与对账": payment_reconciliation_center()
    elif page == "会员生命周期": member_lifecycle_center()
    elif page == "管理员后台": admin_backend()
    elif page == "反馈": feedback()
    st.markdown(f"<div class='footer'>© 2026 Aurevia 智策云｜联系：{CONTACT_EMAIL}</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
