import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import json
import io
import zipfile
import requests
try:
    import plotly.express as px
except Exception:
    px = None
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

APP_NAME = "Aurevia 智策云"
APP_SUBTITLE = "数据智能与AI效率平台｜Batch 66 手机端完整优化版"
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

@media (max-width: 768px) {
  .block-container { padding: .75rem .85rem; }
  .hero { padding: 22px 20px; border-radius: 22px; }
  .hero h1 { font-size: 30px; line-height: 1.18; }
  .hero p { font-size: 15px; line-height: 1.65; }
  .card, .metric-card, .template-card { padding: 16px; border-radius: 18px; }
  .mobile-card { padding: 16px !important; }
  .desktop-only { display: none !important; }
}
.mobile-card {
  background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
  border: 1px solid rgba(15,23,42,.08);
  border-radius: 20px;
  padding: 18px;
  box-shadow: 0 12px 32px rgba(15,23,42,.06);
  margin-bottom: 12px;
}
.report-chip {
  display:inline-block; padding:6px 10px; border-radius:999px;
  background:#eef6ff; border:1px solid #bfdbfe; color:#1d4ed8; font-size:12px; margin-right:6px;
}
.step-card {
  padding: 18px; border-radius: 20px; background:#ffffff;
  border:1px solid #e5edf7; box-shadow:0 10px 26px rgba(15,23,42,.05);
}


.action-pill {display:inline-block; padding:7px 12px; border-radius:999px; background:#eef2ff; color:#3730a3; border:1px solid #c7d2fe; font-size:13px; margin:3px 4px 3px 0;}
.insight-card {background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%); border:1px solid #dbeafe; border-radius:20px; padding:18px; box-shadow:0 12px 32px rgba(15,23,42,.06); margin-bottom:12px;}
.recommend-card {background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 65%, #0f766e 100%); color:white; border-radius:24px; padding:24px; box-shadow:0 18px 50px rgba(15,23,42,.18);}
.recommend-card p { color: rgba(255,255,255,.90); }
.chart-panel {background:#ffffff; border:1px solid #e5edf7; border-radius:20px; padding:18px; box-shadow:0 10px 26px rgba(15,23,42,.05);}


.nav-section-title {
  font-size: 12px;
  letter-spacing: .05em;
  text-transform: uppercase;
  color: #64748b;
  margin: 10px 0 6px 0;
}
.footer-links {
  margin-top: 34px;
  padding: 18px;
  border-radius: 18px;
  background: rgba(255,255,255,.72);
  border: 1px solid rgba(15,23,42,.08);
}
.footer-links-title {font-size: 13px; color:#64748b; margin-bottom: 8px;}


.mobile-hero-mini {
  padding: 20px; border-radius: 22px;
  background: linear-gradient(135deg,#0f172a 0%,#1e40af 62%,#0f766e 100%);
  color:#fff; box-shadow:0 18px 46px rgba(15,23,42,.16); margin-bottom:14px;
}
.mobile-hero-mini h2 {font-size:28px; line-height:1.15; margin:0 0 8px 0;}
.mobile-hero-mini p {font-size:15px; line-height:1.65; color:rgba(255,255,255,.9); margin:0;}
.mobile-report-card {
  border-radius: 20px; padding: 16px; background:#fff;
  border:1px solid #e2e8f0; box-shadow:0 10px 26px rgba(15,23,42,.06);
  margin-bottom: 12px;
}
.mobile-report-card .kpi {font-size:26px; font-weight:800; color:#0f172a; margin:4px 0;}
.mobile-report-card .label {font-size:13px; color:#64748b;}
.mobile-cta-row {display:flex; gap:8px; flex-wrap:wrap; margin:8px 0 12px 0;}
.mobile-cta {padding:8px 11px; border-radius:999px; background:#eef6ff; border:1px solid #bfdbfe; color:#1d4ed8; font-size:13px;}
.share-card-preview {
  border-radius:22px; padding:22px; color:#fff;
  background:linear-gradient(135deg,#111827,#1d4ed8,#0f766e);
  box-shadow:0 20px 50px rgba(15,23,42,.20); margin-bottom:14px;
}
.share-card-preview h3 {font-size:28px; margin:0 0 8px 0;}
.share-card-preview p {font-size:15px; line-height:1.7; color:rgba(255,255,255,.92);}
@media (max-width: 640px) {
  .mobile-hero-mini h2 {font-size:24px;}
  .mobile-report-card .kpi {font-size:24px;}
  .share-card-preview h3 {font-size:24px;}
  .stButton button {min-height: 44px;}
  div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea {font-size:16px !important;}
}

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
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS behavior_events (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_email TEXT,
          event_type TEXT,
          page TEXT,
          scenario TEXT,
          detail TEXT,
          created_at TEXT
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS recommendation_snapshots (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_email TEXT,
          top_scenario TEXT,
          reason TEXT,
          score REAL,
          created_at TEXT
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS feedback_tasks (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          source_feedback_id INTEGER,
          title TEXT,
          category TEXT,
          scenario TEXT,
          priority_score INTEGER,
          status TEXT DEFAULT '待处理',
          ai_reason TEXT,
          created_at TEXT
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS user_demands (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          source_feedback_id INTEGER,
          demand_type TEXT,
          scenario TEXT,
          description TEXT,
          priority_score INTEGER,
          created_at TEXT
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS iteration_plans (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          title TEXT,
          plan_text TEXT,
          created_at TEXT
        )
        """
    )

    c.execute(
        """
        CREATE TABLE IF NOT EXISTS feedback_task_notes (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          task_id INTEGER,
          note TEXT,
          operator TEXT,
          created_at TEXT
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS feedback_task_status_history (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          task_id INTEGER,
          old_status TEXT,
          new_status TEXT,
          operator TEXT,
          created_at TEXT
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS iteration_retrospectives (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          batch_name TEXT,
          completed_items TEXT,
          tests_summary TEXT,
          issues_found TEXT,
          next_actions TEXT,
          created_at TEXT
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS upload_error_events (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_email TEXT,
          file_name TEXT,
          error_type TEXT,
          error_message TEXT,
          repair_suggestion TEXT,
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

# Batch 63：更细的字段别名库，重点强化电商售后与高校就业场景
FIELD_ALIASES.update({
    "日期": FIELD_ALIASES.get("日期", []) + ["售后申请时间", "退款申请时间", "工单创建时间", "创建时间", "提交时间", "完结时间", "完成时间"],
    "门店": FIELD_ALIASES.get("门店", []) + ["店铺名称", "店铺名", "网店", "门店编码", "商家名称"],
    "渠道": FIELD_ALIASES.get("渠道", []) + ["平台名称", "销售平台", "售后渠道", "订单来源", "来源平台", "店铺渠道"],
    "金额": FIELD_ALIASES.get("金额", []) + ["订单金额", "实付金额", "应收金额", "成交价", "支付总额", "结算金额"],
    "退款金额": FIELD_ALIASES.get("退款金额", []) + ["退款金额(元)", "申请退款金额", "实际退款金额", "退赔金额", "售后退款金额", "退款/赔付金额", "退还金额"],
    "订单号": FIELD_ALIASES.get("订单号", []) + ["订单编号", "售后编号", "售后工单号", "退款单号", "退货单号", "平台订单号", "子订单号", "主订单号"],
    "商品": FIELD_ALIASES.get("商品", []) + ["商品标题", "商品编码", "SKU编码", "SKU名称", "货品名称", "产品名称", "商品ID", "款号"],
    "售后类型": FIELD_ALIASES.get("售后类型", []) + ["售后类别", "退款类型", "退货类型", "服务类型", "问题类型", "业务类型"],
    "退款原因": FIELD_ALIASES.get("退款原因", []) + ["原因", "退换原因", "申请原因", "问题原因", "客户反馈原因", "投诉类型", "售后备注"],
    "处理状态": FIELD_ALIASES.get("处理状态", []) + ["状态", "退款状态", "售后处理状态", "工单处理状态", "是否完结", "完结状态", "当前状态"],
    "客服": ["客服", "客服人员", "处理人", "处理客服", "跟进人", "售后专员", "负责人"],
    "处理时长": ["处理时长", "处理小时", "完成时长", "工单时长", "售后时长", "处理耗时", "完结耗时"],
    "响应时长": ["响应时长", "首次响应时长", "首响时长", "响应耗时", "首次回复时长"],
    "赔付金额": ["赔付金额", "补偿金额", "补贴金额", "平台补贴", "商家赔付", "赔偿金额"],
    "学院": FIELD_ALIASES.get("学院", []) + ["学校", "分院", "学院名称", "院部"],
    "就业状态": FIELD_ALIASES.get("就业状态", []) + ["落实状态", "毕业落实去向", "去向类型", "当前去向", "就业落实情况", "是否落实"],
    "实习单位": ["实习单位", "实习企业", "实习公司", "实践单位", "单位名称", "企业名称"],
    "就业单位": ["就业单位", "签约单位", "录用单位", "工作单位", "入职单位", "用人单位"],
    "岗位": ["岗位", "职位", "岗位名称", "就业岗位", "实习岗位", "职务"],
    "行业": ["行业", "就业行业", "单位行业", "所属行业", "行业类别"],
    "地区": ["地区", "城市", "就业地区", "工作地点", "单位所在地", "省市"],
})

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
    data, _, _ = read_uploaded_files_with_logs(files)
    return data


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


def metric_explanations(result: Dict[str, Any]) -> pd.DataFrame:
    trust = result.get("trust", 0)
    issue_count = len(result.get("issues", []))
    rows = result.get("rows", 0)
    total = result.get("total", 0.0)
    level = "可信" if trust >= 80 else "需复核" if trust >= 60 else "不建议直接使用"
    return pd.DataFrame([
        {"指标": "记录数", "当前值": rows, "AI解释": "本次纳入分析的有效数据行数。行数过少时，结论只能作为初步参考。", "建议动作": "如果是正式报告，请确认是否已经上传全部文件。"},
        {"指标": "关键金额合计", "当前值": f"{total:,.2f}", "AI解释": "系统根据识别到的金额、退款金额或薪资字段计算出的汇总值。不同场景下含义不同。", "建议动作": "核对金额字段是否映射正确，必要时补充字段别名。"},
        {"指标": "问题数", "当前值": issue_count, "AI解释": "问题数越多，说明字段缺失、空值或格式异常越多。", "建议动作": "优先下载问题清单，将问题发给数据提交人修正。"},
        {"指标": "数据可信度", "当前值": f"{trust}/100（{level}）", "AI解释": "综合字段完整度、异常数量和金额可解析情况得出的辅助评分。", "建议动作": "80分以上可进入汇报草稿；60-79分建议复核；低于60分不建议直接用于正式决策。"},
    ])


def auto_feedback_category(text: str) -> str:
    t = (text or "").lower()
    rules = [
        ("上传/文件问题", ["上传", "文件", "excel", "csv", "word", "pdf", "zip", "打不开", "读取"]),
        ("AI结果问题", ["ai", "模型", "回答", "评语", "摘要", "幻觉", "不准"]),
        ("模板/字段建议", ["模板", "字段", "映射", "场景", "列名", "表头"]),
        ("报告/下载问题", ["报告", "下载", "导出", "zip", "excel", "清单"]),
        ("界面体验", ["界面", "按钮", "导航", "不好看", "卡", "慢", "回弹"]),
    ]
    for name, kws in rules:
        if any(k in t for k in kws):
            return name
    return "其他"


def upload_repair_tips(error_logs: List[Dict[str, str]]) -> pd.DataFrame:
    """把上传错误转成用户可自助修复的操作建议。"""
    if not error_logs:
        return pd.DataFrame(columns=["文件名", "问题类型", "可能原因", "自助修复建议", "建议优先级"])
    rows = []
    for e in error_logs:
        fname = e.get("文件名", "未知文件")
        msg = str(e.get("错误", ""))
        low = msg.lower()
        if any(x in low for x in ["unicode", "codec", "encoding", "decode"]):
            row = {"文件名": fname, "问题类型": "CSV编码异常", "可能原因": "CSV不是UTF-8编码，常见于Excel导出的GBK/GB18030文件。", "自助修复建议": "用Excel打开后另存为 .xlsx，或另存为 UTF-8 CSV 后重新上传。", "建议优先级": "高"}
        elif any(x in low for x in ["excel", "workbook", "file is not a zip", "badzip", "openpyxl"]):
            row = {"文件名": fname, "问题类型": "Excel文件结构异常", "可能原因": "文件可能损坏、不是标准xlsx、含复杂合并单元格或加密。", "自助修复建议": "用Excel重新打开，取消合并单元格，另存为新的 .xlsx 文件后再上传。", "建议优先级": "高"}
        elif any(x in low for x in ["permission", "access", "denied"]):
            row = {"文件名": fname, "问题类型": "文件权限异常", "可能原因": "文件可能被占用，或浏览器没有读取权限。", "自助修复建议": "关闭正在打开该文件的Excel/Word/PDF，再重新选择上传。", "建议优先级": "中"}
        elif any(x in low for x in ["empty", "no columns", "no data"]):
            row = {"文件名": fname, "问题类型": "空文件或无表头", "可能原因": "文件没有有效数据，或第一行不是表头。", "自助修复建议": "确认第一行为字段名，第二行开始为数据；删除空行空列后重试。", "建议优先级": "高"}
        elif any(x in low for x in ["unsupported", "not supported", "extension"]):
            row = {"文件名": fname, "问题类型": "格式暂不支持", "可能原因": "上传了非Excel/CSV或非作业批改支持格式。", "自助修复建议": "数据分析请上传 .xlsx/.csv；作业批改请上传 .txt/.docx/.pdf/.zip。", "建议优先级": "中"}
        else:
            row = {"文件名": fname, "问题类型": "文件结构或格式异常", "可能原因": "表头、编码、格式或文件内容不符合结构化分析要求。", "自助修复建议": "保留一张结构化表，第一行为表头；删除说明行、合并单元格、空白列后重试。", "建议优先级": "中"}
        rows.append(row)
    return pd.DataFrame(rows)


def _read_csv_robust(raw: bytes) -> pd.DataFrame:
    last_error = None
    for enc in ["utf-8-sig", "utf-8", "gb18030", "gbk"]:
        for sep in [",", "	", ";", None]:
            try:
                if sep is None:
                    return pd.read_csv(io.BytesIO(raw), encoding=enc, sep=None, engine="python")
                return pd.read_csv(io.BytesIO(raw), encoding=enc, sep=sep)
            except Exception as e:
                last_error = e
    raise last_error or ValueError("CSV读取失败")


def _read_excel_robust(raw: bytes, file_name: str) -> pd.DataFrame:
    suffix = Path(file_name).suffix.lower()
    if suffix not in [".xlsx", ".xls", ".xlsm"]:
        raise ValueError(f"unsupported extension {suffix}")
    try:
        return pd.read_excel(io.BytesIO(raw), engine="openpyxl" if suffix in [".xlsx", ".xlsm"] else None)
    except Exception as e:
        raise ValueError(f"Excel读取失败：{e}")


def _log_upload_error(file_name: str, error_type: str, error_message: str, suggestion: str):
    try:
        conn = db_conn()
        conn.execute(
            "INSERT INTO upload_error_events(user_email, file_name, error_type, error_message, repair_suggestion, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (current_email(), file_name, error_type, error_message, suggestion, datetime.now().isoformat())
        )
        conn.commit(); conn.close()
    except Exception:
        pass


def read_uploaded_files_with_logs(files: List[Any]):
    frames, logs, errors = [], [], []
    if not files:
        return pd.DataFrame(), pd.DataFrame(columns=["文件名","状态","行数","列数","错误","建议"]), pd.DataFrame(columns=["文件名","问题类型","可能原因","自助修复建议","建议优先级"])
    for f in files:
        fname = getattr(f, "name", "unknown")
        try:
            raw = f.getvalue() if hasattr(f, "getvalue") else f.read()
            if not raw:
                raise ValueError("empty file")
            suffix = Path(fname).suffix.lower()
            if suffix == ".csv":
                df = _read_csv_robust(raw)
            elif suffix in [".xlsx", ".xls", ".xlsm"]:
                df = _read_excel_robust(raw, fname)
            else:
                raise ValueError(f"unsupported extension {suffix}")
            if df.empty or len(df.columns) == 0:
                raise ValueError("empty or no columns")
            df.columns = [str(c).strip() if str(c).strip() else f"未命名列_{i+1}" for i, c in enumerate(df.columns)]
            df["来源文件"] = fname
            frames.append(df)
            logs.append({"文件名": fname, "状态": "读取成功", "行数": len(df), "列数": len(df.columns), "错误": "", "建议": "可继续分析"})
        except Exception as e:
            err = {"文件名": fname, "错误": str(e)}
            errors.append(err)
            tips = upload_repair_tips([err])
            suggestion = tips.iloc[0]["自助修复建议"] if len(tips) else "检查文件结构后重试"
            issue_type = tips.iloc[0]["问题类型"] if len(tips) else "读取失败"
            _log_upload_error(fname, issue_type, str(e), suggestion)
            logs.append({"文件名": fname, "状态": "读取失败", "行数": 0, "列数": 0, "错误": str(e), "建议": suggestion})
    data = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    return data, pd.DataFrame(logs), upload_repair_tips(errors)


def make_assignment_sample_report_zip() -> bytes:
    students = ["李明", "王婷", "陈宇", "赵悦", "周航", "黄琳"]
    scores = [91, 86, 73, 58, 94, 61]
    rows = []
    for name, score in zip(students, scores):
        level = "优秀" if score >= 85 else "良好" if score >= 75 else "及格" if score >= 60 else "需重点辅导"
        sim = "疑似雷同：与赵悦相似度82%" if name == "陈宇" else "无明显雷同"
        history = "表扬：多次高分，表现稳定" if score >= 90 else "警告：连续低分，建议跟进" if score < 60 else "正常"
        rows.append({"学生": name, "作业类型": "课程论文", "得分": score, "等级": level, "雷同标注": sim, "历史表现": history, "AI评语": f"该生本次作业为{level}，建议继续完善论证、案例和结构表达。"})
    df = pd.DataFrame(rows)
    summary = pd.DataFrame([{
        "班级": "演示班级", "平均分": df["得分"].mean(), "优秀人数": int((df["得分"]>=85).sum()), "低分风险人数": int((df["得分"]<60).sum()), "疑似雷同数量": int(df["雷同标注"].str.contains("疑似").sum())
    }])
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="AI批改结果", index=False)
        summary.to_excel(writer, sheet_name="班级分析", index=False)
        pd.DataFrame([{ "指标": "平均分", "解释": "反映班级整体作业完成质量。"}, {"指标": "疑似雷同", "解释": "仅为辅助筛查，需要教师人工复核。"}]).to_excel(writer, sheet_name="指标解释", index=False)
    zbuf = io.BytesIO()
    with zipfile.ZipFile(zbuf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("AI作业批改完整样例报告.xlsx", out.getvalue())
        z.writestr("AI作业批改摘要.txt", "本样例展示了AI辅助评分、深度评语、疑似雷同标注、历史表现提醒和班级风险分析。")
    return zbuf.getvalue()

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




def log_event(event_type: str, page: str = "", scenario: str = "", detail: Optional[Dict[str, Any]] = None):
    """Record lightweight product usage events for recommendation strategy and UX improvement."""
    try:
        conn = db_conn()
        conn.execute(
            "INSERT INTO behavior_events(user_email, event_type, page, scenario, detail, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (current_email() if is_logged_in() else "guest", event_type, page or st.session_state.get("page", ""), scenario or "", json.dumps(detail or {}, ensure_ascii=False), datetime.now().isoformat()),
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


def load_behavior_events(limit: int = 500) -> pd.DataFrame:
    try:
        conn = db_conn()
        df = pd.read_sql_query("SELECT * FROM behavior_events ORDER BY created_at DESC LIMIT ?", conn, params=(limit,))
        conn.close()
        return df
    except Exception:
        return pd.DataFrame(columns=["id", "user_email", "event_type", "page", "scenario", "detail", "created_at"])


def safe_read_analysis_history() -> pd.DataFrame:
    try:
        conn = db_conn()
        df = pd.read_sql_query("SELECT * FROM analysis_history ORDER BY created_at DESC", conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame(columns=["scenario", "rows_count", "trust_score", "issue_count", "created_at"])


def scenario_recommendation_scores() -> pd.DataFrame:
    hist = safe_read_analysis_history()
    events = load_behavior_events(1000)
    rows = []
    for s in SCENARIOS:
        name = s["name"]
        h = hist[hist.get("scenario", pd.Series(dtype=str)).astype(str) == name] if not hist.empty else pd.DataFrame()
        e = events[events.get("scenario", pd.Series(dtype=str)).astype(str) == name] if not events.empty else pd.DataFrame()
        usage_count = len(h) + len(e)
        avg_trust = float(h["trust_score"].mean()) if not h.empty and "trust_score" in h else 78.0
        avg_issues = float(h["issue_count"].mean()) if not h.empty and "issue_count" in h else 1.5
        recency_bonus = min(8, len(h.head(3)) * 2) if not h.empty else 0
        strategic_bonus = 10 if any(k in name for k in ["电商", "高校", "作业"]) else 4
        score = usage_count * 4 + avg_trust * 0.45 - avg_issues * 3 + recency_bonus + strategic_bonus
        if "电商" in name:
            reason = "适合互联网/电商团队，能直接处理退换货、售后工单、客服效率和商品风险。"
        elif "高校" in name:
            reason = "适合院系、就业办和辅导员，能输出就业率、未就业清单和院系汇总。"
        elif "作业" in name:
            reason = "适合教师减轻批改压力，能输出评分、评语、雷同风险和班级预警。"
        elif usage_count > 0:
            reason = "用户已经使用过该场景，建议继续深化模板和报告表现。"
        else:
            reason = "作为通用补充模板，可根据用户上传字段进一步推荐。"
        rows.append({"场景": name, "分类": s["category"], "推荐分": round(score, 2), "历史使用": usage_count, "平均可信度": round(avg_trust, 1), "平均问题数": round(avg_issues, 1), "推荐理由": reason})
    return pd.DataFrame(rows).sort_values("推荐分", ascending=False).reset_index(drop=True)


def generate_product_optimization_suggestions() -> pd.DataFrame:
    events = load_behavior_events(1000)
    hist = safe_read_analysis_history()
    suggestions = []
    if events.empty and hist.empty:
        suggestions.append({"优先级": "P0", "问题/机会": "真实行为数据不足", "建议动作": "继续引导用户先使用样例报告、再上传真实文件，并鼓励提交反馈。", "依据": "暂无行为数据"})
    else:
        page_counts = events["page"].value_counts().to_dict() if not events.empty and "page" in events else {}
        scenario_counts = hist["scenario"].value_counts().to_dict() if not hist.empty and "scenario" in hist else {}
        if scenario_counts:
            top_scene = max(scenario_counts, key=scenario_counts.get)
            suggestions.append({"优先级": "P0", "问题/机会": f"{top_scene} 使用最多", "建议动作": "优先打磨该场景的样例报告、字段修复向导和AI摘要。", "依据": f"历史分析 {scenario_counts[top_scene]} 次"})
        if "样例报告库" not in page_counts:
            suggestions.append({"优先级": "P1", "问题/机会": "样例报告访问不足", "建议动作": "在首页和首次使用向导中进一步突出样例报告入口。", "依据": "页面访问行为"})
        if not hist.empty and hist["issue_count"].mean() >= 3:
            suggestions.append({"优先级": "P0", "问题/机会": "用户上传数据问题偏多", "建议动作": "强化字段缺失修复向导、表头检测和文件结构提示。", "依据": f"平均问题数 {hist['issue_count'].mean():.1f}"})
        if not hist.empty and hist["trust_score"].mean() < 75:
            suggestions.append({"优先级": "P0", "问题/机会": "数据可信度偏低", "建议动作": "增加上传前模板校验、缺字段提醒和样例字段对照表。", "依据": f"平均可信度 {hist['trust_score'].mean():.1f}"})
        if len(suggestions) < 3:
            suggestions.append({"优先级": "P1", "问题/机会": "AI Agent 使用路径可继续缩短", "建议动作": "在报告页加入‘让AI解释本页结果’和‘生成汇报话术’按钮。", "依据": "产品体验评审"})
    return pd.DataFrame(suggestions)


def automated_usage_report_text() -> str:
    events = load_behavior_events(1000)
    hist = safe_read_analysis_history()
    total_events = len(events)
    total_analysis = len(hist)
    top_scene = hist["scenario"].value_counts().idxmax() if not hist.empty and "scenario" in hist and len(hist["scenario"].dropna()) else "暂无"
    avg_trust = hist["trust_score"].mean() if not hist.empty and "trust_score" in hist else 0
    avg_issues = hist["issue_count"].mean() if not hist.empty and "issue_count" in hist else 0
    return f"""Aurevia 智策云自动化使用报告

1. 行为事件总数：{total_events}
2. 历史分析次数：{total_analysis}
3. 当前最常用场景：{top_scene}
4. 平均数据可信度：{avg_trust:.1f}
5. 平均问题数：{avg_issues:.1f}

产品判断：
- 如果最常用场景集中在电商/高校/作业批改，说明核心方向正在形成。
- 如果平均问题数偏高，应继续优化上传前字段提示和修复向导。
- 如果样例报告访问较少，应在首页增加样例报告引导。
- 如果AI中心访问较高，应继续加强AI解释、推荐和客服能力。
"""

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
TOP_NAV_PAGES = ["手机端优化", "App与桌面版", "桌面版启动页", "移动端体验", "PWA安装引导"]
CORE_NAV_PAGES = ["首页", "首次使用向导", "工作台", "场景配置向导", "样例报告库", "模板中心", "成果分享中心", "用户案例库", "传播分析", "AI推荐策略", "交互图表", "体验数据分析", "AI智能中心", "AI作业批改"]
FOOTER_NAV_PAGES = ["一人公司运营中枢", "产品优化中心", "隐私与数据", "协议与政策", "上架前检查", "系统后台", "反馈"]
NAV_PAGES = TOP_NAV_PAGES + CORE_NAV_PAGES + FOOTER_NAV_PAGES

def set_page(page: str):
    st.session_state.page = page
    log_event("page_view", page=page)
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
        st.markdown("<div class='nav-section-title'>应用入口</div>", unsafe_allow_html=True)
        for page in TOP_NAV_PAGES:
            active = "● " if st.session_state.page == page else "○ "
            if st.button(active + page, key=f"nav_top_{page}", use_container_width=True):
                set_page(page)

        st.markdown("---")
        st.markdown("<div class='nav-section-title'>核心功能服务</div>", unsafe_allow_html=True)
        for page in CORE_NAV_PAGES:
            active = "● " if st.session_state.page == page else "○ "
            if st.button(active + page, key=f"nav_core_{page}", use_container_width=True):
                set_page(page)

        st.markdown("---")
        st.caption(f"客服邮箱：{CONTACT_EMAIL}")
        st.caption("辅助入口已移到页面底部，避免左侧导航过载。")


def render_bottom_utility_links():
    st.markdown("<div class='footer-links'>", unsafe_allow_html=True)
    st.markdown("<div class='footer-links-title'>辅助入口 / 管理与政策</div>", unsafe_allow_html=True)
    cols = st.columns(len(FOOTER_NAV_PAGES))
    for col, page in zip(cols, FOOTER_NAV_PAGES):
        with col:
            if st.button(page, key=f"footer_nav_{page}", use_container_width=True):
                set_page(page)
    st.markdown(f"<div class='small'>联系客服：{CONTACT_EMAIL}｜核心功能免费开放，辅助页面统一放在底部，减少主导航干扰。</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)



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
    st.markdown("#### AI 解释每个指标")
    st.dataframe(metric_explanations(result), use_container_width=True)
    st.markdown("#### 字段识别")
    st.dataframe(result["field_map"], use_container_width=True)
    if len(result["issues"]):
        st.markdown("#### 问题清单")
        st.dataframe(result["issues"], use_container_width=True)
    with st.expander("查看原始数据", expanded=False):
        st.dataframe(df, use_container_width=True)
    report_zip = make_report_zip(df, scenario, result)
    st.download_button("下载报告包 ZIP", data=report_zip, file_name=f"Aurevia_{scenario['name']}_报告包.zip", mime="application/zip", use_container_width=True, key=f"download_report_zip_{scenario['name']}")


def record_history(scenario: str, result: Dict[str, Any]):
    log_event("analysis_completed", scenario=scenario, detail={"rows": result.get("rows"), "trust": result.get("trust"), "issues": len(result.get("issues", []))})
    if not is_logged_in():
        return
    conn = db_conn()
    conn.execute("INSERT INTO analysis_history(user_email, scenario, rows_count, trust_score, issue_count, created_at) VALUES (?, ?, ?, ?, ?, ?)", (current_email(), scenario, result["rows"], result["trust"], len(result["issues"]), datetime.now().isoformat()))
    conn.commit()
    conn.close()




def render_first_success_guide():
    st.markdown("## 首次使用向导")
    st.markdown("<div class='infobox'>目标：让新用户不用摸索，5分钟内完成第一次成功体验。</div>", unsafe_allow_html=True)
    steps = pd.DataFrame([
        {"步骤": "1. 选择场景", "要做什么": "从电商售后、高校就业、AI作业批改等场景中选一个。", "成功标准": "知道自己要解决的问题属于哪个模板。"},
        {"步骤": "2. 先看样例", "要做什么": "进入样例报告库，先下载完整样例报告。", "成功标准": "看到产品最终能输出什么。"},
        {"步骤": "3. 上传自己的文件", "要做什么": "上传结构化 Excel / CSV，第一行尽量是表头。", "成功标准": "系统能识别字段并生成结果。"},
        {"步骤": "4. 查看问题清单", "要做什么": "先处理缺字段、空值、金额异常、状态缺失等问题。", "成功标准": "知道数据哪里需要修。"},
        {"步骤": "5. 下载报告包", "要做什么": "下载 Excel 报告、摘要和问题清单。", "成功标准": "能把报告用于复盘、汇报或沟通。"},
        {"步骤": "6. 提交反馈", "要做什么": "告诉我们哪里卡住、哪里不够好。", "成功标准": "产品能继续按真实问题优化。"},
    ])
    st.dataframe(steps, use_container_width=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("去样例报告库", use_container_width=True):
            set_page("样例报告库")
    with c2:
        if st.button("去工作台上传", use_container_width=True):
            set_page("工作台")
    with c3:
        if st.button("去反馈", use_container_width=True):
            set_page("反馈")


def sample_report_card(title: str, scenario_keyword: str, desc: str):
    scenario = next(s for s in SCENARIOS if scenario_keyword in s["name"])
    df = demo_data(scenario["name"])
    result = analyze_df(df, scenario)
    st.markdown(f"### {title}")
    st.write(desc)
    render_result(df, scenario, result)


def render_sample_reports():
    st.markdown("## 样例报告库")
    st.markdown("<div class='successbox'>无需准备数据，直接查看完整样例报告。它的作用是让用户先看见价值，再上传真实文件。</div>", unsafe_allow_html=True)
    tabs = st.tabs(["电商售后完整样例报告", "高校就业完整样例报告", "AI作业批改完整样例报告"])
    with tabs[0]:
        sample_report_card("电商售后完整样例报告", "电商", "覆盖退款原因分布、商品售后表现、客服处理效率、高风险工单和问题清单。")
    with tabs[1]:
        sample_report_card("高校就业完整样例报告", "高校", "覆盖实习单位汇总、就业去向、专业/班级就业率、薪资区间和未就业清单。")
    with tabs[2]:
        st.markdown("### AI作业批改完整样例报告")
        st.write("覆盖评分、深度评语、疑似雷同标注、历史表现提醒和班级风险分析。")
        st.download_button("下载 AI 作业批改完整样例报告包", data=make_assignment_sample_report_zip(), file_name="AI作业批改完整样例报告包.zip", mime="application/zip", use_container_width=True, key="sample_grading_report_zip")
        demo = pd.DataFrame([
            {"学生": "李明", "得分": 91, "等级": "优秀", "历史表现": "表扬：多次高分", "AI评语": "结构完整，论证充分，可作为优秀样例。"},
            {"学生": "陈宇", "得分": 73, "等级": "及格", "历史表现": "正常", "AI评语": "观点基本清晰，但案例支撑不足。"},
            {"学生": "赵悦", "得分": 58, "等级": "需重点辅导", "历史表现": "警告：连续低分", "AI评语": "结构不完整，反思不足，建议教师重点跟进。"},
        ])
        st.dataframe(demo, use_container_width=True)


def render_privacy_data():
    st.markdown("## 隐私说明与数据删除")
    st.markdown("<div class='infobox'>你的产品涉及学生作业、就业数据、电商订单和经营数据，因此隐私说明必须清楚、克制、可执行。</div>", unsafe_allow_html=True)
    st.markdown("""
### 我们建议对用户明确说明
- 上传文件仅用于当前分析与报告生成。
- 不建议上传身份证号、银行卡号、详细住址等与分析无关的敏感信息。
- AI 批改结果仅作为教师辅助参考，不替代教师最终判断。
- 如用户要求删除数据，应提供明确的删除入口。
""")
    if not is_logged_in():
        st.warning("请先登录，才能删除账号相关数据。访客模式下可直接刷新页面清空临时结果。")
        return
    if st.button("清空当前会话分析结果", use_container_width=True):
        st.session_state.last_result = None
        st.session_state.last_df = None
        st.session_state.last_scenario = None
        st.success("当前会话分析结果已清空。")
    if st.button("删除我的历史分析记录和反馈", use_container_width=True):
        conn = db_conn()
        email = current_email()
        conn.execute("DELETE FROM analysis_history WHERE user_email=?", (email,))
        conn.execute("DELETE FROM feedback WHERE user_email=?", (email,))
        conn.execute("DELETE FROM ai_settings WHERE user_email=?", (email,))
        conn.commit()
        conn.close()
        st.success("已删除你的历史分析记录、反馈和AI设置。账号本身仍保留，如需删除账号请联系管理员。")


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
            log_event("demo_analysis", page="工作台", scenario=scenario["name"], detail={"rows": len(df)})
            st.session_state.last_df = df
            st.session_state.last_result = result
            st.session_state.last_scenario = scenario
            record_history(scenario["name"], result)
            st.rerun()
    with c2:
        uploaded = st.file_uploader("上传 Excel / CSV，可多选", type=["xlsx", "csv"], accept_multiple_files=True)
        if st.button("分析上传文件", use_container_width=True):
            if uploaded:
                df, upload_log, repair_tips = read_uploaded_files_with_logs(uploaded)
                st.session_state.upload_log = upload_log
                st.session_state.repair_tips = repair_tips
                if len(df):
                    result = analyze_df(df, scenario)
                    st.session_state.last_df = df
                    st.session_state.last_result = result
                    st.session_state.last_scenario = scenario
                    record_history(scenario["name"], result)
                    st.rerun()
                else:
                    st.warning("上传文件未能成功读取，请查看下方自助修复提示。")
            else:
                st.warning("请先上传文件，或直接使用演示数据。")
    if st.session_state.get("upload_log") is not None:
        with st.expander("上传文件日志", expanded=False):
            st.dataframe(st.session_state.upload_log, use_container_width=True)
    if st.session_state.get("repair_tips") is not None and len(st.session_state.repair_tips):
        st.markdown("#### 上传错误自助修复提示")
        st.dataframe(st.session_state.repair_tips, use_container_width=True)
    if st.session_state.last_result is not None:
        render_result(st.session_state.last_df, st.session_state.last_scenario, st.session_state.last_result)


def render_templates():
    st.markdown("## 模板中心")
    rec_df = scenario_recommendation_scores()
    if not rec_df.empty:
        top = rec_df.iloc[0]
        st.markdown(f"<div class='infobox'>AI 推荐优先尝试：<b>{top['场景']}</b>。理由：{top['推荐理由']}</div>", unsafe_allow_html=True)
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



def extract_text_from_docx(raw: bytes) -> str:
    try:
        from docx import Document
        doc = Document(io.BytesIO(raw))
        return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    except Exception as e:
        raise ValueError(f"Word解析失败：{e}")


def extract_text_from_pdf(raw: bytes) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(raw))
        texts = []
        for page in reader.pages[:80]:
            try:
                texts.append(page.extract_text() or "")
            except Exception:
                pass
        return "\n".join(texts).strip()
    except Exception as e:
        raise ValueError(f"PDF解析失败：{e}")


def extract_assignment_documents(uploaded_files: List[Any]) -> List[Dict[str, str]]:
    """支持 txt / docx / pdf / zip 的作业文本抽取。"""
    docs = []
    for f in uploaded_files or []:
        fname = getattr(f, "name", "unknown")
        raw = f.getvalue() if hasattr(f, "getvalue") else f.read()
        suffix = Path(fname).suffix.lower()
        try:
            if suffix == ".txt":
                text = raw.decode("utf-8", errors="ignore")
                docs.append({"学生": Path(fname).stem, "文件名": fname, "文本": text, "状态": "成功", "错误": ""})
            elif suffix == ".docx":
                docs.append({"学生": Path(fname).stem, "文件名": fname, "文本": extract_text_from_docx(raw), "状态": "成功", "错误": ""})
            elif suffix == ".pdf":
                docs.append({"学生": Path(fname).stem, "文件名": fname, "文本": extract_text_from_pdf(raw), "状态": "成功", "错误": ""})
            elif suffix == ".zip":
                with zipfile.ZipFile(io.BytesIO(raw)) as z:
                    for name in z.namelist():
                        if name.endswith("/") or name.startswith("__MACOSX"):
                            continue
                        sub_suffix = Path(name).suffix.lower()
                        if sub_suffix not in [".txt", ".docx", ".pdf"]:
                            continue
                        sub_raw = z.read(name)
                        if sub_suffix == ".txt":
                            text = sub_raw.decode("utf-8", errors="ignore")
                        elif sub_suffix == ".docx":
                            text = extract_text_from_docx(sub_raw)
                        else:
                            text = extract_text_from_pdf(sub_raw)
                        docs.append({"学生": Path(name).stem, "文件名": name, "文本": text, "状态": "成功", "错误": ""})
            else:
                docs.append({"学生": Path(fname).stem, "文件名": fname, "文本": "", "状态": "失败", "错误": "暂不支持该文件格式"})
        except Exception as e:
            docs.append({"学生": Path(fname).stem, "文件名": fname, "文本": "", "状态": "失败", "错误": str(e)})
    return docs


def detect_assignment_similarity(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    from difflib import SequenceMatcher
    pairs = []
    valid = [r for r in rows if str(r.get("文本", "")).strip()]
    for i in range(len(valid)):
        for j in range(i + 1, len(valid)):
            a, b = valid[i], valid[j]
            ta, tb = a.get("文本", "")[:5000], b.get("文本", "")[:5000]
            sim = SequenceMatcher(None, ta, tb).ratio()
            if sim >= 0.72:
                pairs.append({"学生A": a.get("学生"), "学生B": b.get("学生"), "相似度": round(sim * 100, 2), "标注": "疑似雷同，建议教师人工复核"})
    return pd.DataFrame(pairs) if pairs else pd.DataFrame(columns=["学生A", "学生B", "相似度", "标注"])


def save_grading_history(rows: List[Dict[str, Any]], assignment_type: str):
    try:
        conn = db_conn()
        for r in rows:
            conn.execute(
                "INSERT INTO grading_history(student, assignment_type, score, level, similarity_note, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (str(r.get("学生/文件", "")), assignment_type, float(r.get("得分", 0)), str(r.get("等级", "")), str(r.get("雷同风险", "")), datetime.now().isoformat())
            )
        conn.commit(); conn.close()
    except Exception:
        pass


def historical_performance_label(student: str, current_score: float) -> str:
    try:
        conn = db_conn()
        hist = pd.read_sql_query("SELECT score FROM grading_history WHERE student=? ORDER BY created_at DESC LIMIT 3", conn, params=(student,))
        conn.close()
        scores = hist["score"].tolist() if not hist.empty else []
        scores = [float(x) for x in scores if x is not None]
        if len(scores) >= 2 and all(s >= 85 for s in scores) and current_score >= 85:
            return "表扬：该生历史表现稳定较好，可作为优秀样例。"
        if len(scores) >= 2 and all(s < 60 for s in scores) and current_score < 60:
            return "警告：该生连续低分，建议教师重点辅导。"
        if scores and current_score > max(scores):
            return "进步：本次表现较历史记录有提升。"
        return "正常：暂无明显长期风险。"
    except Exception:
        return "正常：暂无历史记录。"



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
    st.markdown("<div class='infobox'>本功能用于辅助教师初筛、生成评语、识别疑似雷同和统计班级表现。正式成绩仍建议教师复核。</div>", unsafe_allow_html=True)

    c1, c2 = st.columns([1, 1], gap="large")
    with c1:
        assignment_type = st.selectbox("作业类型", ["通用文字作业", "课程论文", "实习报告", "实验报告", "读书报告", "代码说明文档"])
        rubric = st.text_area("评分标准细则", placeholder="例如：结构完整20分；观点清晰20分；案例和数据30分；反思总结20分；格式规范10分。", height=120)
    with c2:
        st.markdown("### 批改稳定性说明")
        st.markdown("""
        - 支持 `.txt / .docx / .pdf / .zip`
        - ZIP 中可包含多份学生作业
        - PDF 文字提取受文件质量影响，扫描件可能需要 OCR 后再上传
        - 雷同识别为辅助筛查，不等同正式学术查重
        """)
    uploaded = st.file_uploader("上传作业文件或ZIP作业包", type=["txt", "docx", "pdf", "zip"], accept_multiple_files=True)
    if st.button("开始批改", use_container_width=True):
        if not uploaded:
            st.warning("请先上传作业文件。")
            return
        docs = extract_assignment_documents(uploaded)
        extract_log = pd.DataFrame([{k: v for k, v in d.items() if k != "文本"} for d in docs])
        with st.expander("文件解析日志", expanded=False):
            st.dataframe(extract_log, use_container_width=True)
        success_docs = [d for d in docs if d.get("状态") == "成功" and str(d.get("文本", "")).strip()]
        if not success_docs:
            st.error("没有成功解析的作业文本。请查看文件解析日志，并尝试转换为 .docx 或 .txt 后重新上传。")
            return

        sim_df = detect_assignment_similarity(success_docs)
        sim_notes = {}
        for _, r in sim_df.iterrows():
            sim_notes.setdefault(r["学生A"], []).append(f"与 {r['学生B']} 相似度 {r['相似度']}%")
            sim_notes.setdefault(r["学生B"], []).append(f"与 {r['学生A']} 相似度 {r['相似度']}%")

        rows = []
        for d in success_docs:
            res = score_assignment_text(d["文本"], rubric)
            student = d["学生"]
            plagiarism = "；".join(sim_notes.get(student, [])) or "未发现明显雷同"
            hist_label = historical_performance_label(student, res["得分"])
            rows.append({
                "学生/文件": student,
                "文件名": d["文件名"],
                "作业类型": assignment_type,
                "得分": res["得分"],
                "等级": res["等级"],
                "字数": res["字数"],
                "雷同风险": plagiarism,
                "历史表现标注": hist_label,
                "命中要点": res["命中要点"],
                "AI批改意见": res["评语"],
            })
        df = pd.DataFrame(rows)
        save_grading_history(rows, assignment_type)

        st.markdown("### 批改结果")
        st.dataframe(df, use_container_width=True)
        if not sim_df.empty:
            st.markdown("### 疑似雷同检测")
            st.dataframe(sim_df, use_container_width=True)
            st.warning("雷同检测仅为辅助筛查，正式判断需要教师人工复核。")

        summary = pd.DataFrame([{
            "作业数量": len(df),
            "平均分": round(df["得分"].mean(), 2),
            "优秀人数": int((df["得分"] >= 85).sum()),
            "低分风险人数": int((df["得分"] < 60).sum()),
            "疑似雷同人数": int(df["雷同风险"].ne("未发现明显雷同").sum()),
            "建议": "优先复核疑似雷同和低分作业；对连续高分学生给予表扬。"
        }])
        st.markdown("### 班级分析")
        st.dataframe(summary, use_container_width=True)

        out = io.BytesIO()
        with pd.ExcelWriter(out, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="AI批改结果", index=False)
            summary.to_excel(writer, sheet_name="班级分析", index=False)
            sim_df.to_excel(writer, sheet_name="雷同检测", index=False)
            extract_log.to_excel(writer, sheet_name="文件解析日志", index=False)
            pd.DataFrame([{"评分标准": rubric, "作业类型": assignment_type}]).to_excel(writer, sheet_name="评分设置", index=False)
        st.download_button("下载批改结果 Excel", out.getvalue(), "AI作业批改结果.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True, key="download_grading_batch63")


def render_feedback():
    st.markdown("## 用户反馈")
    st.markdown("<div class='infobox'>你的反馈会进入产品优化中心，用于生成修复任务、优先级和下一轮迭代计划。</div>", unsafe_allow_html=True)
    quick = st.selectbox("常见问题快捷选择", ["手动填写", "上传失败", "AI回答不准", "字段识别不准", "报告下载失败", "手机端不好用", "作业批改不稳定", "高校就业报告看不懂", "电商售后字段不够"])
    default_text = "" if quick == "手动填写" else f"我遇到的问题是：{quick}。请协助优化。"
    content = st.text_area("反馈内容", value=default_text, height=180, placeholder="例如：上传文件失败、AI回答不准、模板字段不够、报告下载有问题、界面导航卡顿……")
    suggested = auto_feedback_category(content) if content.strip() else "其他"
    st.caption(f"系统自动分类建议：{suggested}")
    categories = ["上传/文件问题", "AI结果问题", "模板/字段建议", "报告/下载问题", "界面体验", "其他"]
    category = st.selectbox("反馈类型", categories, index=categories.index(suggested) if suggested in categories else 5)
    scenario = st.selectbox("关联场景", ["不确定 / 通用", "电商退款 / 售后工单汇总", "高校教务 / 实习 / 就业数据汇总", "AI 作业批改", "移动端 / PWA", "桌面版"])
    if st.button("提交反馈", use_container_width=True):
        if content.strip():
            full_content = f"[关联场景：{scenario}] {content}"
            conn = db_conn()
            conn.execute("INSERT INTO feedback(user_email, category, content, created_at) VALUES (?, ?, ?, ?)", (current_email(), category, full_content, datetime.now().isoformat()))
            conn.commit()
            conn.close()
            st.success("反馈已提交，并已进入产品优化闭环。")
            st.info("如果是阻断性问题，也可以直接联系：" + CONTACT_EMAIL)
        else:
            st.warning("请填写反馈内容。")
    st.markdown("### 反馈后会发生什么")
    st.markdown("""
    1. 系统自动分类反馈。  
    2. 产品优化中心会生成任务和优先级。  
    3. 每批迭代后会生成复盘报告。  
    4. 高优先级问题会优先进入下一批修复。  
    """)
    st.info(f"遇到无法解决的问题，也可以联系：{CONTACT_EMAIL}")


def render_admin():
    st.markdown("## 系统后台")
    if not is_logged_in() or current_email() != CONTACT_EMAIL:
        st.warning("仅管理员可访问后台。")
        return
    tab1, tab2, tab3, tab4 = st.tabs(["用户", "反馈", "分析记录", "行为数据"])
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
    with tab4:
        try:
            events = pd.read_sql_query("SELECT * FROM behavior_events ORDER BY created_at DESC LIMIT 500", conn)
            st.dataframe(events, use_container_width=True)
        except Exception:
            st.info("暂无行为数据。")
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
Batch 51 已落实：免费版体验打磨 + 样例报告库 + 用户首次成功路径优化
- 电商售后、高校就业、AI作业批改三个完整样例报告
- 首次使用向导
- AI解释每个指标
- 反馈自动分类
- 上传错误自助修复提示
- 隐私说明与数据删除入口
        """
    )



# ============================================================
# Batch 52：三大核心场景深度打磨
# ============================================================

def inspect_file_structure(df: pd.DataFrame) -> pd.DataFrame:
    """增强上传文件结构检测：帮助用户在分析前发现表格结构问题。"""
    rows = []
    total_rows, total_cols = len(df), len(df.columns)
    duplicated = [c for c in df.columns[df.columns.duplicated()].tolist()]
    empty_cols = [c for c in df.columns if df[c].isna().all()]
    unnamed_cols = [c for c in df.columns if str(c).lower().startswith('unnamed') or str(c).strip()==""]
    null_ratio = float(df.isna().mean().mean()) if total_cols else 1.0
    numeric_cols = []
    for c in df.columns:
        s = pd.to_numeric(df[c], errors='coerce')
        if s.notna().sum() >= max(1, int(total_rows * 0.6)):
            numeric_cols.append(c)
    checks = [
        ("表格行数", total_rows, "正常" if total_rows > 0 else "异常", "至少应包含1行有效数据。"),
        ("表格列数", total_cols, "正常" if total_cols >= 2 else "需复核", "建议至少包含2列以上结构化字段。"),
        ("重复列名", len(duplicated), "需复核" if duplicated else "正常", "如存在重复列名，请修改为唯一表头。"),
        ("空白列", len(empty_cols), "需清理" if empty_cols else "正常", "删除全空列，可提升字段识别准确率。"),
        ("未命名列", len(unnamed_cols), "需清理" if unnamed_cols else "正常", "通常由空表头、合并单元格或导出格式异常造成。"),
        ("总体空值比例", f"{null_ratio*100:.1f}%", "需复核" if null_ratio > 0.25 else "正常", "空值比例过高会影响汇总和诊断。"),
        ("疑似数值列", len(numeric_cols), "正常" if numeric_cols else "需复核", "金额、薪资、时长、库存等字段应能被解析为数字。"),
    ]
    for item, value, status, suggestion in checks:
        rows.append({"检测项": item, "当前值": value, "状态": status, "建议": suggestion})
    return pd.DataFrame(rows)


def ecommerce_deep_analysis(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    reason_col = find_col(df, "退款原因")
    product_col = find_col(df, "商品")
    channel_col = find_col(df, "渠道")
    status_col = find_col(df, "处理状态")
    amount_col = find_col(df, "退款金额") or find_col(df, "金额")
    service_col = find_col(df, "客服") or find_col(df, "销售人员")
    duration_col = find_col(df, "处理时长")
    response_col = find_col(df, "响应时长")
    compensation_col = find_col(df, "赔付金额")
    order_col = find_col(df, "订单号")
    amount = pd.to_numeric(df[amount_col], errors="coerce").fillna(0) if amount_col else pd.Series([0]*len(df))
    compensation = pd.to_numeric(df[compensation_col], errors="coerce").fillna(0) if compensation_col else pd.Series([0]*len(df))
    outputs = {}
    base = df.copy()
    base["_退款金额"] = amount
    base["_赔付金额"] = compensation
    base["_售后净损失"] = base["_退款金额"] + base["_赔付金额"]

    if reason_col:
        outputs["退款原因深度分析"] = base.groupby(reason_col, dropna=False).agg(
            工单数=(reason_col,"count"),
            退款金额=("_退款金额","sum"),
            赔付金额=("_赔付金额","sum"),
            售后净损失=("_售后净损失","sum")
        ).reset_index().sort_values(["售后净损失","工单数"], ascending=False)
    if product_col:
        risk = base.groupby(product_col, dropna=False).agg(
            售后次数=(product_col,"count"),
            退款金额=("_退款金额","sum"),
            售后净损失=("_售后净损失","sum")
        ).reset_index()
        risk["风险等级"] = pd.cut(risk["售后净损失"].rank(method="first"), bins=[0, max(1, len(risk)*0.5), max(2, len(risk)*0.8), len(risk)+1], labels=["低","中","高"])
        outputs["商品售后风险排行"] = risk.sort_values(["售后净损失","售后次数"], ascending=False)
    if channel_col:
        outputs["渠道售后表现"] = base.groupby(channel_col, dropna=False).agg(
            售后工单=(channel_col,"count"),
            退款金额=("_退款金额","sum"),
            赔付金额=("_赔付金额","sum"),
            售后净损失=("_售后净损失","sum")
        ).reset_index().sort_values("售后净损失", ascending=False)
    if service_col:
        tmp = base.copy()
        aggs = {"处理工单": (service_col, "count"), "涉及退款": ("_退款金额", "sum"), "售后净损失": ("_售后净损失","sum")}
        if duration_col:
            tmp["_处理时长"] = pd.to_numeric(tmp[duration_col], errors="coerce")
            aggs["平均处理时长"] = ("_处理时长", "mean")
        if response_col:
            tmp["_响应时长"] = pd.to_numeric(tmp[response_col], errors="coerce")
            aggs["平均响应时长"] = ("_响应时长", "mean")
        outputs["客服处理效率"] = tmp.groupby(service_col, dropna=False).agg(**aggs).reset_index()
    # 高风险工单：金额高、超时、响应慢、状态未完结
    high = base.copy()
    flags = []
    if status_col:
        flags.append(high[status_col].astype(str).str.contains("超时|处理中|未处理|待处理|待审核|未完结|申诉", regex=True, na=False))
    if duration_col:
        flags.append(pd.to_numeric(high[duration_col], errors="coerce").fillna(0) >= 48)
    if response_col:
        flags.append(pd.to_numeric(high[response_col], errors="coerce").fillna(0) >= 12)
    threshold = max(300, high["_售后净损失"].quantile(0.8) if len(high) else 300)
    flags.append(high["_售后净损失"] >= threshold)
    mask = flags[0] if flags else pd.Series([False]*len(high))
    for flg in flags[1:]:
        mask = mask | flg
    risk = high[mask].copy()
    if len(risk):
        risk["风险标注"] = "高金额/响应慢/处理超时/未完结，建议优先复核"
        show_cols = [c for c in [order_col, product_col, channel_col, reason_col, status_col, service_col, amount_col, compensation_col, duration_col, response_col, "风险标注"] if c]
        outputs["高风险售后工单"] = risk[show_cols] if show_cols else risk
    else:
        outputs["高风险售后工单"] = pd.DataFrame([{"结论":"未识别到明显高风险工单"}])
    # 字段口径建议，帮助用户补字段
    outputs["电商字段口径建议"] = pd.DataFrame([
        {"字段": "订单号", "用途": "识别同一笔交易/售后工单", "建议": "平台订单号、退款单号、售后工单号都可映射为订单号。"},
        {"字段": "退款金额", "用途": "计算退款损失", "建议": "优先使用实际退款金额；若只有申请金额，需在报告中标注口径。"},
        {"字段": "赔付金额", "用途": "识别额外补偿成本", "建议": "建议单独保留，不要与退款金额混在一起。"},
        {"字段": "响应时长/处理时长", "用途": "评估客服效率", "建议": "单位建议统一为小时。"},
        {"字段": "处理状态", "用途": "识别未完结/超时工单", "建议": "建议规范为已完成、处理中、待处理、超时。"},
    ])
    return outputs


def education_deep_analysis(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    college_col = find_col(df, "学院")
    major_col = find_col(df, "专业")
    class_col = find_col(df, "班级")
    status_col = find_col(df, "就业状态")
    salary_col = find_col(df, "薪资")
    unit_col = find_col(df, "实习单位") or find_col(df, "就业单位")
    industry_col = find_col(df, "行业")
    name_col = find_col(df, "姓名")
    outputs = {}
    def is_done(s):
        return s.astype(str).str.contains("已就业|升学|实习|签约|录用|创业", regex=True, na=False)
    if status_col:
        outputs["就业去向统计"] = df[status_col].astype(str).value_counts(dropna=False).reset_index().rename(columns={"index":"就业状态", status_col:"人数"})
    group_fields = [c for c in [college_col, major_col, class_col] if c]
    if status_col and group_fields:
        tmp = df.copy()
        tmp["_已落实"] = is_done(tmp[status_col]).astype(int)
        if salary_col:
            tmp["_薪资"] = pd.to_numeric(tmp[salary_col], errors="coerce").fillna(0)
            outputs["专业班级就业率"] = tmp.groupby(group_fields, dropna=False).agg(学生数=(status_col,"count"),已落实人数=("_已落实","sum"),平均薪资=("_薪资","mean")).reset_index()
        else:
            outputs["专业班级就业率"] = tmp.groupby(group_fields, dropna=False).agg(学生数=(status_col,"count"),已落实人数=("_已落实","sum")).reset_index()
        outputs["专业班级就业率"]["落实率"] = outputs["专业班级就业率"]["已落实人数"] / outputs["专业班级就业率"]["学生数"].clip(lower=1)
    if industry_col:
        outputs["岗位行业分布"] = df[industry_col].astype(str).value_counts(dropna=False).reset_index().rename(columns={"index":"行业", industry_col:"人数"})
    if unit_col:
        outputs["实习就业单位汇总"] = df[unit_col].astype(str).value_counts(dropna=False).reset_index().rename(columns={"index":"单位", unit_col:"人数"})
    if salary_col:
        salary = pd.to_numeric(df[salary_col], errors="coerce").fillna(0)
        bins = [-1,0,3000,5000,8000,12000,20000,10**9]
        labels = ["未填写/无薪资","0-3000","3000-5000","5000-8000","8000-12000","12000-20000","20000+"]
        outputs["薪资区间统计"] = pd.cut(salary, bins=bins, labels=labels).value_counts().sort_index().reset_index().rename(columns={"index":"薪资区间", salary_col:"人数", "count":"人数"})
    if status_col:
        mask = df[status_col].astype(str).str.contains("待就业|未就业|未落实|暂无", regex=True, na=False)
        cols = [c for c in [college_col, major_col, class_col, name_col, status_col, unit_col, industry_col, salary_col] if c]
        outputs["未就业学生清单"] = df.loc[mask, cols] if cols else df.loc[mask]
    if college_col and status_col:
        tmp = df.copy()
        tmp["_已落实"] = is_done(tmp[status_col]).astype(int)
        outputs["院系汇总报告"] = tmp.groupby(college_col, dropna=False).agg(学生数=(status_col,"count"),已落实人数=("_已落实","sum")).reset_index()
        outputs["院系汇总报告"]["落实率"] = outputs["院系汇总报告"]["已落实人数"] / outputs["院系汇总报告"]["学生数"].clip(lower=1)
    # Batch 63：增加更适合院系汇报的可读性摘要
    if status_col:
        total_students = len(df)
        done_count = int(is_done(df[status_col]).sum())
        pending_count = int(df[status_col].astype(str).str.contains("待就业|未就业|未落实|暂无", regex=True, na=False).sum())
        salary_value = ""
        if salary_col:
            _salary_series = pd.to_numeric(df[salary_col], errors="coerce")
            salary_value = round(_salary_series.dropna().mean(), 2) if _salary_series.notna().any() else ""
        outputs["院系报告可读摘要"] = pd.DataFrame([
            {"项目": "总学生数", "数值": total_students, "解释": "本次纳入统计的学生总数。", "建议": "确认是否覆盖所有班级/专业。"},
            {"项目": "已落实人数", "数值": done_count, "解释": "包含已就业、升学、实习、签约、录用、创业等状态。", "建议": "建议与院系就业台账复核口径。"},
            {"项目": "待帮扶人数", "数值": pending_count, "解释": "待就业、未就业、未落实等需要重点跟进。", "建议": "建议辅导员建立一对一帮扶记录。"},
            {"项目": "平均薪资", "数值": salary_value, "解释": "仅基于已填写薪资的数据计算。", "建议": "薪资不是唯一质量指标，应结合行业、岗位和地区综合判断。"},
        ])
    return outputs


def grading_deep_report() -> Dict[str, pd.DataFrame]:
    rows = [
        {"学生":"李明","得分":92,"等级":"优秀","雷同风险":"低","历史趋势":"连续高分","教师提示":"可表扬，建议鼓励其分享写作结构。"},
        {"学生":"王婷","得分":86,"等级":"优秀","雷同风险":"低","历史趋势":"稳定提升","教师提示":"表现较好，可关注其案例深度。"},
        {"学生":"陈宇","得分":72,"等级":"及格","雷同风险":"中","历史趋势":"波动","教师提示":"建议人工复核雷同段落并提醒改进。"},
        {"学生":"赵悦","得分":55,"等级":"需重点辅导","雷同风险":"高","历史趋势":"连续低分","教师提示":"建议单独沟通，明确作业结构和评分标准。"},
        {"学生":"周航","得分":94,"等级":"优秀","雷同风险":"低","历史趋势":"连续高分","教师提示":"可表扬，适合作为优秀样例。"},
    ]
    df = pd.DataFrame(rows)
    summary = pd.DataFrame([{
        "平均分": round(df["得分"].mean(),2),
        "优秀人数": int((df["得分"]>=85).sum()),
        "低分风险人数": int((df["得分"]<60).sum()),
        "中高雷同风险人数": int(df["雷同风险"].isin(["中","高"]).sum()),
        "建议": "优先复核高雷同风险与连续低分学生，表扬连续高分学生。"
    }])
    trend = pd.DataFrame([
        {"学生":"李明","上次":88,"本次":92,"趋势":"提升"},
        {"学生":"王婷","上次":80,"本次":86,"趋势":"提升"},
        {"学生":"陈宇","上次":76,"本次":72,"趋势":"下降"},
        {"学生":"赵悦","上次":58,"本次":55,"趋势":"连续低分"},
        {"学生":"周航","上次":91,"本次":94,"趋势":"稳定优秀"},
    ])
    return {"AI批改深度结果": df, "班级学习风险预警": summary, "作业批改历史趋势": trend}


def make_presentation_talk(scenario: Dict[str, Any], result: Dict[str, Any], deep_outputs: Dict[str, pd.DataFrame]) -> str:
    trust = result.get("trust", 0)
    rows = result.get("rows", 0)
    issue_count = len(result.get("issues", []))
    lines = [
        f"各位好，本次汇报基于“{scenario['name']}”场景，共纳入 {rows} 条数据。",
        f"系统给出的数据可信度为 {trust}/100，问题清单中识别出 {issue_count} 项需要复核的内容。",
    ]
    if "电商" in scenario["name"]:
        lines += [
            "从售后数据看，建议重点关注退款原因集中项、高退款金额商品、处理超时工单和客服处理效率。",
            "下一步建议：先处理高风险工单，再复核高频退货商品，最后优化客服响应流程。",
        ]
    elif "高校" in scenario["name"]:
        lines += [
            "从就业与实习数据看，建议重点关注未落实学生、专业/班级就业率差异、薪资区间分布和实习单位集中度。",
            "下一步建议：对未就业学生建立帮扶台账，对优质实习单位进行长期合作维护。",
        ]
    elif "作业" in scenario["name"]:
        lines += [
            "从作业批改结果看，建议重点关注连续低分学生和疑似雷同内容，同时对连续高分学生给予表扬。",
            "下一步建议：教师复核高风险样本，并针对共性问题统一讲解评分标准。",
        ]
    else:
        lines.append("建议先复核字段映射和问题清单，再将报告用于正式汇报。")
    return "\n".join(lines)


def analyze_df(df: pd.DataFrame, scenario: Dict[str, Any]) -> Dict[str, Any]:
    field_map = map_fields(df, scenario["required"])
    structure_report = inspect_file_structure(df)
    missing = field_map[field_map["状态"] == "缺失"]["标准字段"].tolist()
    rows = len(df)
    money_col = find_col(df, "金额") or find_col(df, "退款金额") or find_col(df, "薪资")
    total = 0.0
    if money_col:
        total = pd.to_numeric(df[money_col], errors="coerce").fillna(0).sum()
    structure_penalty = int((structure_report["状态"].astype(str).isin(["需复核","需清理","异常"]).sum()) * 4)
    issue_count = int(len(missing) * 3) + structure_penalty
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
        if reason_col and len(df):
            top_reason = df[reason_col].astype(str).value_counts().idxmax()
            summary_lines.append(f"最高频退款/售后原因是：{top_reason}，建议优先复核对应商品、渠道和客服处理流程。")
    if "高校" in scenario["name"]:
        status_col = find_col(df, "就业状态")
        if status_col and len(df):
            done = df[status_col].astype(str).str.contains("已就业|升学|实习|签约|录用|创业", regex=True).sum()
            rate = done / max(rows, 1) * 100
            summary_lines.append(f"就业/升学/实习等已落实人数 {done} 人，落实率约 {rate:.1f}%。")
    issues = [{"级别": "高", "问题类型": "缺失必需字段", "问题详情": f"缺少字段：{m}", "建议处理": f"补充 {m} 字段或建立字段别名映射。"} for m in missing]
    for _, r in structure_report.iterrows():
        if r["状态"] in ["需复核","需清理","异常"]:
            issues.append({"级别":"中", "问题类型":"文件结构问题", "问题详情": f"{r['检测项']}：{r['当前值']}，状态：{r['状态']}", "建议处理": r["建议"]})
    issue_df = pd.DataFrame(issues) if issues else pd.DataFrame(columns=["级别", "问题类型", "问题详情", "建议处理"])
    deep_outputs = {}
    if "电商" in scenario["name"]:
        deep_outputs = ecommerce_deep_analysis(df)
    elif "高校" in scenario["name"]:
        deep_outputs = education_deep_analysis(df)
    elif "作业" in scenario["name"]:
        deep_outputs = grading_deep_report()
    result = {"field_map": field_map, "structure_report": structure_report, "trust": trust, "summary": "\n".join(summary_lines), "issues": issue_df, "total": total, "rows": rows, "deep_outputs": deep_outputs}
    result["talk_script"] = make_presentation_talk(scenario, result, deep_outputs)
    return result


def make_report_zip(df: pd.DataFrame, scenario: Dict[str, Any], result: Dict[str, Any]) -> bytes:
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="原始数据", index=False)
        result["field_map"].to_excel(writer, sheet_name="字段识别", index=False)
        result.get("structure_report", pd.DataFrame()).to_excel(writer, sheet_name="文件结构检测", index=False)
        result["issues"].to_excel(writer, sheet_name="问题清单", index=False)
        metric_explanations(result).to_excel(writer, sheet_name="指标解释", index=False)
        pd.DataFrame([{"场景": scenario["name"], "记录数": result["rows"], "合计值": result["total"], "数据可信度": result["trust"], "摘要": result["summary"], "汇报话术": result.get("talk_script", "")}]).to_excel(writer, sheet_name="分析摘要", index=False)
        for name, sheet_df in result.get("deep_outputs", {}).items():
            safe_name = str(name)[:31]
            sheet_df.to_excel(writer, sheet_name=safe_name, index=False)
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("深度分析报告.xlsx", excel_buffer.getvalue())
        z.writestr("AI经营_就业_批改摘要.txt", result["summary"])
        z.writestr("AI自动生成汇报话术.txt", result.get("talk_script", ""))
        z.writestr("问题清单.csv", result["issues"].to_csv(index=False).encode("utf-8-sig"))
        z.writestr("文件结构检测.csv", result.get("structure_report", pd.DataFrame()).to_csv(index=False).encode("utf-8-sig"))
    return zip_buffer.getvalue()


def render_visual_summary(result: Dict[str, Any], scenario: Dict[str, Any]):
    st.markdown("#### 样例报告视觉总览")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"<div class='metric-card'><h2>{result['rows']}</h2><p>纳入记录</p></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='metric-card'><h2>{result['trust']}</h2><p>数据可信度</p></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='metric-card'><h2>{len(result['issues'])}</h2><p>待复核问题</p></div>", unsafe_allow_html=True)
    st.markdown("#### AI 自动生成汇报话术")
    st.success(result.get("talk_script", "暂无汇报话术。"))


def render_result(df: pd.DataFrame, scenario: Dict[str, Any], result: Dict[str, Any]):
    render_visual_summary(result, scenario)
    st.markdown("#### AI / 规则诊断摘要")
    st.info(result["summary"])
    tabs = st.tabs(["核心指标解释", "深度分析", "字段与结构检测", "问题清单", "原始数据"])
    with tabs[0]:
        st.dataframe(metric_explanations(result), use_container_width=True)
    with tabs[1]:
        deep_outputs = result.get("deep_outputs", {})
        if deep_outputs:
            for name, sheet_df in deep_outputs.items():
                st.markdown(f"##### {name}")
                st.dataframe(sheet_df, use_container_width=True)
        else:
            st.write("该场景暂无深度分析表。")
    with tabs[2]:
        st.markdown("##### 字段识别")
        st.dataframe(result["field_map"], use_container_width=True)
        st.markdown("##### 文件结构检测")
        st.dataframe(result.get("structure_report", pd.DataFrame()), use_container_width=True)
    with tabs[3]:
        if len(result["issues"]):
            st.dataframe(result["issues"], use_container_width=True)
        else:
            st.success("暂无明显问题。")
    with tabs[4]:
        st.dataframe(df, use_container_width=True)
    report_zip = make_report_zip(df, scenario, result)
    st.download_button("下载深度报告包 ZIP", data=report_zip, file_name=f"Aurevia_{scenario['name']}_深度报告包.zip", mime="application/zip", use_container_width=True, key=f"download_b52_report_zip_{scenario['name']}")


def render_sample_reports():
    st.markdown("## 样例报告库")
    st.markdown("<div class='successbox'>Batch 54 已保留三大核心场景深度分析，并新增指标解释库、图表化样例、场景配置向导、PWA 与桌面封装方案。</div>", unsafe_allow_html=True)
    tabs = st.tabs(["电商售后深度样例报告", "高校就业深度样例报告", "AI作业批改深度样例报告"])
    with tabs[0]:
        sample_report_card("电商售后深度样例报告", "电商", "覆盖退款原因、商品风险、渠道售后、客服效率、高风险工单、结构检测和汇报话术。")
    with tabs[1]:
        sample_report_card("高校就业深度样例报告", "高校", "覆盖就业去向、专业班级就业率、行业分布、薪资区间、未就业清单、院系报告和汇报话术。")
    with tabs[2]:
        st.markdown("### AI作业批改深度样例报告")
        st.write("覆盖深度评分、雷同风险、历史趋势、学生成长画像、班级风险预警和教师汇报话术。")
        deep = grading_deep_report()
        for name, df in deep.items():
            st.markdown(f"#### {name}")
            st.dataframe(df, use_container_width=True)
        st.download_button("下载 AI 作业批改完整样例报告包", data=make_assignment_sample_report_zip(), file_name="AI作业批改深度样例报告包.zip", mime="application/zip", use_container_width=True, key="b52_sample_grading_report_zip")




# ----------------------------
# Batch 53/54: 指标解释库、场景配置向导、App/桌面封装方案
# ----------------------------
SCENE_METRIC_LIBRARY = {
    "电商": [
        {"指标": "退款金额", "解释": "反映售后退款规模。金额高不一定代表经营差，但需要结合退款原因和商品分析。", "建议": "优先检查高退款商品和高频退款原因。"},
        {"指标": "退款原因占比", "解释": "用于判断售后问题是集中在质量、物流、尺码、体验还是客服流程。", "建议": "原因集中时，优先做专项改进。"},
        {"指标": "客服处理时长", "解释": "衡量售后响应和结案效率，处理过慢会影响用户满意度。", "建议": "对超时工单设置优先级和处理 SLA。"},
        {"指标": "高风险工单", "解释": "通常包含高金额退款、超时未完结、重复投诉或原因缺失等问题。", "建议": "先处理高金额、高超时、高投诉的工单。"},
    ],
    "高校": [
        {"指标": "就业落实率", "解释": "反映班级、专业或院系学生就业、升学、实习等去向落实情况。", "建议": "低落实率专业需要优先辅导和资源跟进。"},
        {"指标": "未就业学生数", "解释": "用于识别需要重点帮扶的学生群体。", "建议": "生成未就业清单，分配辅导员跟进。"},
        {"指标": "薪资区间", "解释": "反映就业质量的参考维度，但不能单独代表培养质量。", "建议": "结合岗位、行业、地区一起分析。"},
        {"指标": "实习单位集中度", "解释": "反映实习资源是否过度集中或是否形成稳定合作单位。", "建议": "对高频实习单位建立长期合作。"},
    ],
    "作业": [
        {"指标": "平均得分", "解释": "反映班级整体作业完成质量。", "建议": "结合低分学生和评分维度进一步分析。"},
        {"指标": "雷同风险", "解释": "用于辅助筛查作业相似度较高的情况，不等同正式学术查重。", "建议": "对高风险学生进行人工复核。"},
        {"指标": "历史趋势", "解释": "观察学生连续表现，识别稳定优秀或持续低分。", "建议": "对持续优秀者表扬，对连续低分者重点辅导。"},
        {"指标": "教师评语", "解释": "辅助老师快速形成个性化反馈，减少重复劳动。", "建议": "正式给分前由教师确认和修订。"},
    ],
}


def infer_scene_from_columns(columns) -> str:
    text = " ".join([str(c) for c in columns])
    candidates = []
    rules = [
        ("电商退款 / 售后工单汇总", ["退款", "售后", "工单", "客服", "商品", "订单", "赔付"]),
        ("高校教务 / 实习 / 就业数据汇总", ["学院", "专业", "班级", "就业", "实习", "薪资", "学号"]),
        ("AI 作业批改", ["学生", "作业", "评分", "评语", "雷同", "题目"]),
        ("门店 / 渠道销售日报", ["门店", "渠道", "销售", "订单", "实收", "佣金"]),
        ("库存盘点差异", ["库存", "盘点", "盘亏", "盘盈", "SKU"]),
    ]
    for name, kws in rules:
        score = sum(1 for k in kws if k in text)
        if score:
            candidates.append((score, name, "、".join([k for k in kws if k in text])))
    if not candidates:
        return "暂未识别到明确场景。建议选择“模板中心”查看字段要求，或让 AI Agent 根据字段帮你推荐。"
    candidates.sort(reverse=True)
    score, name, hits = candidates[0]
    return f"推荐场景：{name}\n命中字段线索：{hits}\n建议：先使用该模板分析，再根据问题清单修复缺失字段。"


def field_repair_guide(scenario: Dict[str, Any], field_map: pd.DataFrame) -> pd.DataFrame:
    missing = field_map[field_map["状态"] == "缺失"]["标准字段"].tolist() if len(field_map) else []
    rows = []
    for f in missing:
        rows.append({
            "缺失字段": f,
            "为什么重要": "这是该场景进行稳定分析和生成报告所需的关键字段。",
            "修复方式": f"在 Excel 中新增“{f}”列，或把已有相近列名映射为“{f}”。",
            "可接受示例": "请参考模板说明页或样例报告库中的字段示例。",
        })
    if not rows:
        rows.append({"缺失字段": "无", "为什么重要": "必需字段识别完整。", "修复方式": "可以进入分析和报告输出。", "可接受示例": "无需修复。"})
    return pd.DataFrame(rows)


def audience_talk_script(scenario: Dict[str, Any], result: Dict[str, Any]) -> pd.DataFrame:
    name = scenario.get("name", "当前场景")
    rows = result.get("rows", 0)
    trust = result.get("trust", 0)
    issues = len(result.get("issues", []))
    return pd.DataFrame([
        {"对象": "老板 / 管理层", "话术": f"本次基于{name}纳入{rows}条数据，数据可信度为{trust}/100。建议优先关注影响结果可信度的{issues}项问题，并据此安排下一步经营或管理动作。"},
        {"对象": "老师 / 教务人员", "话术": f"本次分析可作为教学、就业或作业管理的辅助材料。建议先查看问题清单与风险学生/待就业学生，再由老师进行最终判断。"},
        {"对象": "运营 / 执行团队", "话术": f"请先处理字段缺失、空值和异常记录，再根据高风险项逐条复核。报告可用于周会、复盘或跨部门沟通。"},
    ])


def render_scene_config_wizard():
    st.markdown("## 场景配置向导")
    st.markdown("<div class='successbox'>目标：用户上传文件后，系统自动推荐场景、解释缺失字段，并生成老板/老师/运营不同版本的话术。</div>", unsafe_allow_html=True)
    files = st.file_uploader("上传一个 Excel / CSV，系统将先做结构检测和场景推荐", type=["xlsx", "csv"], accept_multiple_files=True, key="wizard_upload")
    if st.button("开始智能配置", use_container_width=True):
        if not files:
            st.warning("请先上传文件，或到样例报告库查看演示。")
            return
        df, upload_log, repair_tips = read_uploaded_files_with_logs(files)
        if not len(df):
            st.error("未能成功读取文件。")
            st.dataframe(upload_log, use_container_width=True)
            st.dataframe(repair_tips, use_container_width=True)
            return
        st.session_state.wizard_df = df
        st.session_state.wizard_recommendation = infer_scene_from_columns(df.columns)
        # choose most likely scenario by text
        rec = st.session_state.wizard_recommendation
        scenario = next((s for s in SCENARIOS if s["name"] in rec), SCENARIOS[0])
        result = analyze_df(df, scenario)
        st.session_state.wizard_scenario = scenario
        st.session_state.wizard_result = result
    if st.session_state.get("wizard_df") is not None:
        st.markdown("### 自动推荐场景")
        st.info(st.session_state.get("wizard_recommendation"))
        result = st.session_state.wizard_result
        scenario = st.session_state.wizard_scenario
        st.markdown("### 字段缺失修复向导")
        st.dataframe(field_repair_guide(scenario, result["field_map"]), use_container_width=True)
        st.markdown("### AI 生成不同对象汇报话术")
        st.dataframe(audience_talk_script(scenario, result), use_container_width=True)
        st.markdown("### 场景独立指标解释库")
        scene_key = "电商" if "电商" in scenario["name"] else "高校" if "高校" in scenario["name"] else "作业" if "作业" in scenario["name"] else "电商"
        st.dataframe(pd.DataFrame(SCENE_METRIC_LIBRARY[scene_key]), use_container_width=True)
        st.markdown("### 图表化概览")
        try:
            st.bar_chart(pd.DataFrame({"指标": ["记录数", "可信度", "问题数"], "值": [result["rows"], result["trust"], len(result["issues"])]}).set_index("指标"))
        except Exception:
            st.write("当前数据暂不适合图表展示。")


def render_app_delivery_plan():
    st.markdown("## App 与桌面版上线方案（Batch 55 增强）")
    st.markdown("<div class='infobox'>这不是继续堆功能，而是把产品从网页试用版推进到可安装、可在手机上使用的产品形态。</div>", unsafe_allow_html=True)
    st.markdown("### 当前判断")
    st.write("现在已经可以通过网页在电脑和手机浏览器中使用。要变成真正 App / 桌面安装包，建议分三步推进：")
    roadmap = pd.DataFrame([
        {"阶段": "1. 移动端 PWA", "目标": "手机浏览器打开并添加到主屏幕", "交付物": "manifest、service worker、移动端布局说明", "难度": "低", "建议时间": "现在即可做"},
        {"阶段": "2. Windows 桌面壳", "目标": "把网页封装成 .exe 桌面应用", "交付物": "Electron wrapper、build 脚本、安装包说明", "难度": "中", "建议时间": "1-2周内可试用"},
        {"阶段": "3. 正式手机 App", "目标": "上架应用商店或企业内部分发", "交付物": "React Native/Flutter/Capacitor 项目、隐私合规、应用审核材料", "难度": "高", "建议时间": "产品稳定后"},
    ])
    st.dataframe(roadmap, use_container_width=True)
    st.markdown("### 桌面可执行文件方案")
    st.write("本开发包已提供增强版 `desktop/electron-wrapper`，包含启动页、网络加载提示和线上地址自动打开逻辑，可把当前 Streamlit 线上地址包装为 Windows 桌面程序。")
    st.code("""
cd desktop/electron-wrapper
npm install
npm run build
# 生成文件在 desktop/electron-wrapper/dist/
""", language="bash")
    st.markdown("### 手机 PWA 方案")
    st.write("本开发包已提供 `mobile_pwa/manifest.webmanifest` 和 `mobile_pwa/service-worker.js`。正式接入时建议放到官网静态目录中，并在 HTML 中注册。")
    st.markdown("### 重要边界")
    st.warning("Streamlit Cloud 本身适合快速试用和演示。如果要正式做手机 App 与桌面安装包，后续应逐步迁移到更标准的前端架构，例如 React / Next.js + 后端 API。")


def render_desktop_launch_page():
    st.markdown("## 桌面版专属启动页")
    st.markdown("<div class='infobox'>目标：让 Windows 桌面版打开后不像网页套壳，而像一个真正的桌面应用。</div>", unsafe_allow_html=True)

    c1, c2 = st.columns([1.25, 1], gap="large")
    with c1:
        st.markdown("""
        <div class='hero'>
          <div class='chip'>Desktop App Preview</div>
          <h1>Aurevia 智策云<br>桌面版启动中心</h1>
          <p>双击桌面图标后先展示品牌启动页，再自动打开线上工作台。适合给试用用户和老师/运营人员使用。</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("### 桌面版推荐流程")
        steps = [
            ("1. 启动页", "展示品牌、网络状态、客服邮箱与版本号。"),
            ("2. 自动打开线上地址", "默认打开 https://orbiretail-saas.streamlit.app/。"),
            ("3. 异常处理", "如果网络异常，提示用户检查网络或联系 2790569814@qq.com。"),
            ("4. 长期方向", "后续可加入本地缓存、离线说明、自动更新和崩溃日志。"),
        ]
        for title, desc in steps:
            st.markdown(f"<div class='step-card'><b>{title}</b><br><span class='small'>{desc}</span></div>", unsafe_allow_html=True)
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 桌面版状态")
        st.write("本开发包已包含增强后的 Electron 桌面封装文件：")
        st.code("desktop/electron-wrapper/", language="text")
        st.write("Windows 打包入口：")
        st.code("build_desktop_windows.bat", language="text")
        st.write("开发预览入口：")
        st.code("run_desktop_dev.bat", language="text")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### 桌面版打包步骤")
    st.code("""
cd desktop/electron-wrapper
npm install
npm run build
# 生成安装包在 desktop/electron-wrapper/dist/
""", language="bash")
    st.warning("正式分发前建议做：Windows 11 测试、杀毒误报测试、安装/卸载测试、桌面快捷方式测试、首次启动测试。")


def render_mobile_experience_page():
    st.markdown("## 移动端体验优化")
    st.markdown("<div class='infobox'>目标：让手机浏览器打开后能快速看懂、能查看报告、能知道如何上传或下载。</div>", unsafe_allow_html=True)

    st.markdown("### 手机端报告卡片示例")
    cards = [
        ("电商售后", "退款金额 52,430 元", "高风险工单 12 条", "建议先处理高金额退款和响应超时工单。"),
        ("高校就业", "落实率 80.26%", "待就业 15 人", "建议重点跟进低落实率专业和未就业学生清单。"),
        ("AI 作业批改", "平均分 82.4", "疑似雷同 3 份", "建议复核雷同作业并关注连续低分学生。"),
    ]
    cols = st.columns(3)
    for col, (title, kpi, risk, advice) in zip(cols, cards):
        with col:
            st.markdown(
                f"""
                <div class='mobile-card'>
                  <span class='report-chip'>手机报告</span>
                  <h3>{title}</h3>
                  <p><b>{kpi}</b></p>
                  <p>{risk}</p>
                  <p class='small'>{advice}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("### 移动端上传提示")
    st.markdown("""
    - 手机端适合查看报告、提交反馈、使用 AI Agent、查看样例结果。
    - 大文件上传建议在电脑端完成，尤其是 ZIP 作业包、多个 Excel 或大 PDF。
    - 手机上传前建议确认文件格式为 `.xlsx`、`.csv`、`.docx`、`.pdf` 或 `.zip`。
    - 如果手机上传失败，建议改用电脑上传，或把文件另存为标准格式后重试。
    """)

    st.markdown("### 手机端产品原则")
    st.dataframe(pd.DataFrame([
        {"原则": "少表格，多卡片", "说明": "手机屏幕不适合横向大表格，应优先展示摘要卡片。"},
        {"原则": "先结论，再明细", "说明": "先展示AI摘要、风险和建议，再允许用户展开明细。"},
        {"原则": "下载为辅，查看为主", "说明": "手机端重点看摘要，完整报告下载更适合电脑端。"},
        {"原则": "上传需提示", "说明": "大文件、ZIP、PDF批改应明确建议电脑端使用。"},
    ]), use_container_width=True)


def render_pwa_install_guide():
    st.markdown("## PWA 安装引导")
    st.markdown("<div class='infobox'>PWA 是当前最稳的手机轻应用路线：不用立刻上架应用商店，也能让用户添加到主屏幕。</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 用户手机上怎么安装")
        st.markdown("""
        **iPhone / Safari**
        1. 打开 `https://orbiretail-saas.streamlit.app/`
        2. 点击分享按钮
        3. 选择“添加到主屏幕”
        4. 命名为“Aurevia 智策云”

        **Android / Chrome**
        1. 打开网址
        2. 点击右上角菜单
        3. 选择“添加到主屏幕”或“安装应用”
        4. 从桌面图标进入
        """)
    with c2:
        st.markdown("### 开发侧要做什么")
        st.markdown("""
        本包已提供：
        ```text
        mobile_pwa/manifest.webmanifest
        mobile_pwa/service-worker.js
        mobile_pwa/pwa_integration.html
        ```
        若后续建设独立官网或 React 前端，应把这些文件接入静态站点。
        """)

    st.markdown("### PWA 边界")
    st.warning("Streamlit Cloud 可以被手机浏览器访问，但完整 PWA 能力更适合在独立前端或官网中实现。当前版本属于 PWA 准备方案，不是正式应用商店 App。")


def render_legal_pages():
    st.markdown("## 隐私政策 / 用户协议正式页面")
    st.markdown("<div class='infobox'>本页用于产品正式试用前的合规基础说明。内容是产品草案，正式对外发布前建议再做专业审阅。</div>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["隐私政策草案", "用户协议草案"])
    with tab1:
        st.markdown("""
        ### 隐私政策草案

        **1. 我们处理哪些数据**  
        用户可能上传 Excel、CSV、Word、PDF、ZIP 作业包等文件。文件中可能包含订单、售后、学生、就业、作业、薪资、门店经营等信息。

        **2. 数据用途**  
        上传数据仅用于完成用户选择的分析、批改、摘要生成、问题识别和报告导出。

        **3. 敏感数据提醒**  
        如果文件中包含身份证号、手机号、薪资、学生作业、就业去向等敏感内容，建议用户先脱敏后上传。

        **4. 数据删除**  
        用户可以在“隐私与数据”页面清空当前会话数据、删除历史记录、删除反馈和 AI 设置。

        **5. AI 使用边界**  
        AI 结果用于辅助分析和辅助批改，不替代人工最终判断。涉及成绩、处分、就业质量判断时，应由教师或负责人复核。

        **6. 联系方式**  
        如需删除数据或反馈问题，请联系：2790569814@qq.com
        """)
    with tab2:
        st.markdown("""
        ### 用户协议草案

        **1. 产品用途**  
        Aurevia 智策云用于结构化数据分析、报告生成、AI 辅助批改和效率提升。

        **2. 用户责任**  
        用户应保证上传数据来源合法，并对数据内容、授权范围和使用目的负责。

        **3. 结果边界**  
        系统输出的分析、评分、建议和报告属于辅助结果，不构成法律、财务、教学或管理上的最终结论。

        **4. 禁止用途**  
        不得上传违法数据、侵犯他人隐私的数据或用于欺诈、歧视、非法监控等目的。

        **5. 反馈与支持**  
        遇到无法解决的问题，可联系：2790569814@qq.com
        """)


def render_app_store_checklist():
    st.markdown("## App 上架前检查清单")
    st.markdown("<div class='infobox'>当前阶段建议先做网页 + PWA + 桌面壳。正式手机 App 上架应在产品稳定、隐私和数据流程更成熟后进行。</div>", unsafe_allow_html=True)

    checklist = pd.DataFrame([
        {"类别": "产品稳定性", "检查项": "核心场景能连续完成，不频繁报错或回弹", "状态": "需要持续验证"},
        {"类别": "隐私合规", "检查项": "隐私政策、用户协议、数据删除机制、敏感数据提示", "状态": "本批已提供草案"},
        {"类别": "账号体系", "检查项": "登录、注册、找回、用户数据隔离", "状态": "MVP阶段"},
        {"类别": "AI边界", "检查项": "说明AI为辅助，不替代老师/运营/财务最终判断", "状态": "已加入说明"},
        {"类别": "上传能力", "检查项": "手机端大文件上传稳定性与错误提示", "状态": "建议继续测试"},
        {"类别": "报告查看", "检查项": "手机端摘要卡片、关键指标、下载提示", "状态": "本批增强"},
        {"类别": "应用材料", "检查项": "应用名称、图标、截图、介绍文案、客服邮箱", "状态": "需要准备"},
        {"类别": "分发路线", "检查项": "先PWA/桌面版，后正式App上架", "状态": "推荐路线"},
    ])
    st.dataframe(checklist, use_container_width=True)

    st.markdown("### 建议路线")
    st.markdown("""
    1. 先稳定网页版本和 PWA 体验。  
    2. 打包 Windows 桌面版给小范围用户试用。  
    3. 收集手机端使用反馈，判断是否真的需要正式 App。  
    4. 再决定使用 Flutter / React Native / Capacitor 开发正式移动端。  
    """)




def render_ai_recommendation_strategy():
    st.markdown("## AI 模型自动推荐策略迭代")
    st.markdown("<div class='infobox'>本页根据用户行为、历史分析记录、数据可信度和问题数量，动态调整场景模板推荐顺序。</div>", unsafe_allow_html=True)
    rec = scenario_recommendation_scores()
    top = rec.iloc[0].to_dict() if not rec.empty else {}
    if top:
        st.markdown(f"""
        <div class='recommend-card'>
          <h2>当前优先推荐：{top.get('场景')}</h2>
          <p>{top.get('推荐理由')}</p>
          <p>推荐分：{top.get('推荐分')}｜平均可信度：{top.get('平均可信度')}｜历史使用：{top.get('历史使用')}</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("### 推荐策略评分表")
    st.dataframe(rec, use_container_width=True)
    st.markdown("### 推荐策略如何迭代")
    st.markdown("""
    - 用户经常选择的模板会提高推荐分。
    - 数据可信度高、问题少的模板会优先推荐。
    - 电商、高校、AI作业批改作为当前核心方向，会获得适度战略加权。
    - 如果某个场景平均问题数偏高，系统会建议优先完善字段修复向导。
    """)
    if st.button("生成一次推荐快照", use_container_width=True):
        if top:
            try:
                conn = db_conn()
                conn.execute("INSERT INTO recommendation_snapshots(user_email, top_scenario, reason, score, created_at) VALUES (?, ?, ?, ?, ?)", (current_email() if is_logged_in() else "guest", top.get("场景"), top.get("推荐理由"), float(top.get("推荐分", 0)), datetime.now().isoformat()))
                conn.commit(); conn.close()
                log_event("recommendation_snapshot", page="AI推荐策略", scenario=top.get("场景"), detail={"score": top.get("推荐分")})
                st.success("推荐快照已保存。")
            except Exception as e:
                st.error(f"保存失败：{e}")


def render_interactive_charts():
    st.markdown("## 高级交互图表")
    st.markdown("<div class='infobox'>图表用于让手机端和桌面端用户快速理解数据。当前采用“图表 + 指标选择”的交互方式，确保在 Streamlit 环境下稳定可用。</div>", unsafe_allow_html=True)
    hist = safe_read_analysis_history()
    if hist.empty:
        st.info("暂无真实历史数据，已展示演示交互图表。")
        hist = pd.DataFrame([
            {"scenario": "电商退款 / 售后工单汇总", "rows_count": 128, "trust_score": 86, "issue_count": 4, "created_at": datetime.now().isoformat()},
            {"scenario": "高校教务 / 实习 / 就业数据汇总", "rows_count": 76, "trust_score": 82, "issue_count": 6, "created_at": datetime.now().isoformat()},
            {"scenario": "AI 作业批改", "rows_count": 38, "trust_score": 79, "issue_count": 3, "created_at": datetime.now().isoformat()},
        ])
    summary = hist.groupby("scenario", as_index=False).agg(分析次数=("scenario", "count"), 平均可信度=("trust_score", "mean"), 平均问题数=("issue_count", "mean"), 平均记录数=("rows_count", "mean"))
    summary["平均可信度"] = summary["平均可信度"].round(1)
    summary["平均问题数"] = summary["平均问题数"].round(1)
    summary["平均记录数"] = summary["平均记录数"].round(1)
    st.markdown("### 场景表现总览")
    if px is not None:
        fig = px.bar(summary, x="scenario", y="平均可信度", color="平均问题数", hover_data=["分析次数", "平均记录数"], title="场景平均可信度与问题数")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.bar_chart(summary.set_index("scenario")[["平均可信度"]])
    selected = st.selectbox("点击 / 选择一个场景查看详细解释", summary["scenario"].tolist())
    row = summary[summary["scenario"] == selected].iloc[0].to_dict()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("分析次数", int(row["分析次数"]))
    c2.metric("平均可信度", row["平均可信度"])
    c3.metric("平均问题数", row["平均问题数"])
    c4.metric("平均记录数", row["平均记录数"])
    st.markdown("### 指标解释与建议")
    st.dataframe(pd.DataFrame([
        {"指标": "平均可信度", "解释": "越高表示字段完整、异常少、数据结构更稳定。", "建议": "低于75时应优先修复字段和表头结构。"},
        {"指标": "平均问题数", "解释": "反映每次分析中发现的缺字段、空值、格式错误等问题。", "建议": "问题数偏高时应强化上传前模板说明和字段修复向导。"},
        {"指标": "分析次数", "解释": "代表用户对该场景的使用频率。", "建议": "高频场景优先做深度报告、样例和AI话术。"},
        {"指标": "平均记录数", "解释": "反映场景单次处理数据规模。", "建议": "记录数高的场景应优化上传体验和报告下载速度。"},
    ]), use_container_width=True)


def render_user_experience_analytics():
    st.markdown("## 用户体验数据分析")
    st.markdown("<div class='infobox'>本页把用户操作转化为产品优化建议。它不是监控用户隐私，而是帮助你判断产品哪里最值得继续打磨。</div>", unsafe_allow_html=True)
    events = load_behavior_events(1000)
    hist = safe_read_analysis_history()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("行为事件", len(events))
    m2.metric("分析次数", len(hist))
    m3.metric("平均可信度", f"{hist['trust_score'].mean():.1f}" if not hist.empty else "0")
    m4.metric("平均问题数", f"{hist['issue_count'].mean():.1f}" if not hist.empty else "0")
    tab1, tab2, tab3, tab4 = st.tabs(["行为看板", "产品优化建议", "自动化使用报告", "原始数据"])
    with tab1:
        if events.empty:
            st.info("暂无行为数据。你可以点击页面、生成样例、上传文件后再回来查看。")
        else:
            page_counts = events["page"].replace("", "未记录页面").value_counts().reset_index()
            page_counts.columns = ["页面", "次数"]
            event_counts = events["event_type"].value_counts().reset_index()
            event_counts.columns = ["事件类型", "次数"]
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### 页面访问")
                if px is not None:
                    st.plotly_chart(px.bar(page_counts, x="页面", y="次数", title="页面访问次数"), use_container_width=True)
                else:
                    st.bar_chart(page_counts.set_index("页面"))
            with c2:
                st.markdown("#### 事件类型")
                if px is not None:
                    st.plotly_chart(px.pie(event_counts, names="事件类型", values="次数", title="行为事件构成"), use_container_width=True)
                else:
                    st.bar_chart(event_counts.set_index("事件类型"))
    with tab2:
        suggestions = generate_product_optimization_suggestions()
        st.dataframe(suggestions, use_container_width=True)
        st.download_button("下载产品优化建议 CSV", suggestions.to_csv(index=False).encode("utf-8-sig"), file_name="Aurevia_产品优化建议.csv", mime="text/csv", use_container_width=True, key="download_ux_suggestions")
    with tab3:
        report = automated_usage_report_text()
        st.text_area("自动化使用报告", value=report, height=320)
        st.download_button("下载自动化使用报告 TXT", report.encode("utf-8"), file_name="Aurevia_自动化使用报告.txt", mime="text/plain", use_container_width=True, key="download_usage_report")
    with tab4:
        st.markdown("#### 行为事件")
        st.dataframe(events, use_container_width=True)
        st.markdown("#### 分析历史")
        st.dataframe(hist, use_container_width=True)




# ============================================================
# Batch 62：真实用户反馈闭环 + 产品优化任务看板 + AI 迭代计划
# ============================================================

FEEDBACK_TASK_STATUS = ["待处理", "处理中", "已完成", "暂缓", "需更多反馈"]


def feedback_priority_score(category: str, content: str) -> int:
    """把用户反馈转成可执行优先级。分数越高越应该先处理。"""
    text = (content or "").lower()
    score = 40
    category_weight = {
        "上传/文件问题": 22,
        "AI结果问题": 20,
        "报告/下载问题": 18,
        "界面体验": 14,
        "模板/字段建议": 13,
        "其他": 8,
    }
    score += category_weight.get(category, 8)
    critical_words = ["打不开", "不能用", "报错", "闪退", "崩溃", "无法上传", "无法下载", "数据丢失", "隐私", "泄露", "批改错误", "分数不准"]
    high_value_words = ["高校", "作业", "电商", "售后", "就业", "报告", "手机", "桌面", "ai", "模板", "字段"]
    if any(w in text for w in critical_words):
        score += 28
    if any(w in text for w in high_value_words):
        score += 10
    if len(text) >= 80:
        score += 6
    return max(0, min(100, score))


def infer_feedback_scenario(content: str) -> str:
    text = (content or "").lower()
    rules = [
        ("电商退款 / 售后工单汇总", ["电商", "售后", "退款", "退货", "客服", "工单"]),
        ("高校教务 / 实习 / 就业数据汇总", ["高校", "就业", "实习", "院系", "学生", "班级", "专业"]),
        ("AI 作业批改", ["作业", "批改", "评分", "雷同", "抄袭", "评语"]),
        ("移动端 / PWA", ["手机", "移动", "pwa", "主屏幕", "浏览器"]),
        ("桌面版", ["桌面", "安装包", "exe", "electron", "启动"]),
        ("通用体验", ["界面", "导航", "按钮", "首页", "慢", "卡"]),
    ]
    for name, kws in rules:
        if any(k in text for k in kws):
            return name
    return "通用体验"


def task_title_from_feedback(category: str, content: str) -> str:
    short = (content or "").strip().replace("\n", " ")
    if len(short) > 28:
        short = short[:28] + "…"
    if not short:
        short = "未填写具体反馈"
    return f"[{category}] {short}"


def task_reason(category: str, content: str, score: int) -> str:
    scenario = infer_feedback_scenario(content)
    if score >= 85:
        level = "阻断级：影响用户完成核心任务，应优先修复。"
    elif score >= 70:
        level = "高优先级：影响首次成功体验或核心场景质量。"
    elif score >= 55:
        level = "中优先级：影响体验稳定性，建议排入近期版本。"
    else:
        level = "观察项：继续收集更多反馈后再决定。"
    return f"场景：{scenario}；判断：{level}"


def load_feedback_df() -> pd.DataFrame:
    try:
        conn = db_conn()
        df = pd.read_sql_query("SELECT * FROM feedback ORDER BY created_at DESC", conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame(columns=["id", "user_email", "category", "content", "created_at"])


def load_feedback_tasks_df() -> pd.DataFrame:
    try:
        conn = db_conn()
        df = pd.read_sql_query("SELECT * FROM feedback_tasks ORDER BY priority_score DESC, created_at DESC", conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame(columns=["id", "source_feedback_id", "title", "category", "scenario", "priority_score", "status", "ai_reason", "created_at"])


def create_tasks_from_feedback() -> int:
    fb = load_feedback_df()
    if fb.empty:
        return 0
    conn = db_conn()
    created = 0
    existing = pd.read_sql_query("SELECT COALESCE(source_feedback_id, -1) AS source_feedback_id FROM feedback_tasks", conn)
    existing_ids = set(existing["source_feedback_id"].astype(int).tolist()) if not existing.empty else set()
    for _, row in fb.iterrows():
        fid = int(row.get("id", 0))
        if fid in existing_ids:
            continue
        cat = row.get("category", "其他") or auto_feedback_category(row.get("content", ""))
        content = row.get("content", "") or ""
        scenario = infer_feedback_scenario(content)
        score = feedback_priority_score(cat, content)
        title = task_title_from_feedback(cat, content)
        reason = task_reason(cat, content, score)
        conn.execute(
            "INSERT INTO feedback_tasks(source_feedback_id, title, category, scenario, priority_score, status, ai_reason, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (fid, title, cat, scenario, score, "待处理", reason, datetime.now().isoformat()),
        )
        created += 1
    conn.commit()
    conn.close()
    return created


def create_demands_from_feedback() -> int:
    fb = load_feedback_df()
    if fb.empty:
        return 0
    conn = db_conn()
    created = 0
    existing = pd.read_sql_query("SELECT COALESCE(source_feedback_id, -1) AS source_feedback_id FROM user_demands", conn)
    existing_ids = set(existing["source_feedback_id"].astype(int).tolist()) if not existing.empty else set()
    for _, row in fb.iterrows():
        fid = int(row.get("id", 0))
        if fid in existing_ids:
            continue
        content = row.get("content", "") or ""
        cat = row.get("category", "其他") or auto_feedback_category(content)
        scenario = infer_feedback_scenario(content)
        score = feedback_priority_score(cat, content)
        if cat in ["模板/字段建议", "AI结果问题"]:
            dtype = "功能增强"
        elif cat in ["上传/文件问题", "报告/下载问题"]:
            dtype = "稳定性修复"
        elif cat == "界面体验":
            dtype = "体验优化"
        else:
            dtype = "待判断"
        conn.execute(
            "INSERT INTO user_demands(source_feedback_id, demand_type, scenario, description, priority_score, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (fid, dtype, scenario, content[:500], score, datetime.now().isoformat()),
        )
        created += 1
    conn.commit()
    conn.close()
    return created


def load_user_demands_df() -> pd.DataFrame:
    try:
        conn = db_conn()
        df = pd.read_sql_query("SELECT * FROM user_demands ORDER BY priority_score DESC, created_at DESC", conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame(columns=["id", "source_feedback_id", "demand_type", "scenario", "description", "priority_score", "created_at"])


def feedback_stats_by_scenario() -> pd.DataFrame:
    tasks = load_feedback_tasks_df()
    if tasks.empty:
        return pd.DataFrame(columns=["场景", "反馈任务数", "平均优先级", "待处理数", "最高优先级"])
    grp = tasks.groupby("scenario", as_index=False).agg(
        反馈任务数=("id", "count"),
        平均优先级=("priority_score", "mean"),
        最高优先级=("priority_score", "max"),
        待处理数=("status", lambda s: int((s == "待处理").sum())),
    )
    grp = grp.rename(columns={"scenario": "场景"})
    grp["平均优先级"] = grp["平均优先级"].round(1)
    return grp.sort_values(["最高优先级", "反馈任务数"], ascending=False)


def generate_iteration_plan_text() -> str:
    tasks = load_feedback_tasks_df()
    demands = load_user_demands_df()
    hist = safe_read_analysis_history()
    if tasks.empty and demands.empty:
        return "当前暂无足够真实反馈。建议先引导用户完成样例报告、上传真实文件并提交反馈，再生成迭代计划。"
    top_tasks = tasks.head(8).to_dict("records") if not tasks.empty else []
    top_scene = "暂无"
    if not tasks.empty:
        top_scene = tasks["scenario"].value_counts().index[0]
    avg_trust = hist["trust_score"].mean() if not hist.empty else 0
    avg_issues = hist["issue_count"].mean() if not hist.empty else 0
    lines = []
    lines.append("# Aurevia 智策云｜AI 自动生成迭代计划")
    lines.append("")
    lines.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"当前反馈重点场景：{top_scene}")
    lines.append(f"历史分析平均可信度：{avg_trust:.1f}；平均问题数：{avg_issues:.1f}")
    lines.append("")
    lines.append("## 一、下一轮优先级判断")
    if top_tasks:
        for i, t in enumerate(top_tasks[:5], 1):
            lines.append(f"{i}. {t.get('title')}｜优先级 {t.get('priority_score')}｜{t.get('ai_reason')}")
    else:
        lines.append("暂无任务。")
    lines.append("")
    lines.append("## 二、建议拆成 3 个开发方向")
    lines.append("1. 稳定性修复：优先处理上传失败、下载失败、页面报错、AI返回异常。")
    lines.append("2. 场景深度打磨：优先打磨反馈最多的场景，让一个场景真正解决问题。")
    lines.append("3. 首次成功体验：继续缩短用户从进入页面到生成第一份报告的路径。")
    lines.append("")
    lines.append("## 三、建议下一批验收标准")
    lines.append("- 用户能在 1 分钟内看到样例报告价值。")
    lines.append("- 上传失败时能看到明确修复建议。")
    lines.append("- AI 能解释主要指标和异常问题。")
    lines.append("- 反馈能自动归类并进入任务看板。")
    lines.append("- 每个高优先级问题都有状态、负责人或下一步动作。")
    return "\n".join(lines)


def save_iteration_plan(plan_text: str) -> None:
    conn = db_conn()
    conn.execute("INSERT INTO iteration_plans(title, plan_text, created_at) VALUES (?, ?, ?)", ("AI自动生成迭代计划", plan_text, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def render_product_iteration_center():
    st.markdown("## 产品优化中心")
    st.markdown("<div class='infobox'>本页把真实用户反馈、行为数据和历史分析结果转成可执行任务，避免产品迭代只凭感觉。</div>", unsafe_allow_html=True)
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["反馈闭环", "任务看板", "用户需求池", "场景痛点统计", "AI迭代计划", "迭代复盘"])

    with tab1:
        st.markdown("### 真实用户反馈闭环")
        fb = load_feedback_df()
        if fb.empty:
            st.info("暂无用户反馈。建议先在底部“反馈”入口收集真实用户问题。")
        else:
            view = fb.copy()
            view["自动优先级"] = view.apply(lambda r: feedback_priority_score(r.get("category", "其他"), r.get("content", "")), axis=1)
            view["关联场景"] = view["content"].apply(infer_feedback_scenario)
            st.dataframe(view, use_container_width=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("从反馈生成优化任务", use_container_width=True):
                n = create_tasks_from_feedback()
                st.success(f"已生成 {n} 条新优化任务。")
                st.rerun()
        with c2:
            if st.button("从反馈抽取用户需求", use_container_width=True):
                n = create_demands_from_feedback()
                st.success(f"已抽取 {n} 条新用户需求。")
                st.rerun()

    with tab2:
        st.markdown("### 产品优化任务看板")
        tasks = load_feedback_tasks_df()
        if tasks.empty:
            st.info("暂无任务。请先从反馈生成任务。")
        else:
            status_filter = st.multiselect("筛选状态", FEEDBACK_TASK_STATUS, default=FEEDBACK_TASK_STATUS)
            shown = tasks[tasks["status"].isin(status_filter)] if status_filter else tasks
            st.dataframe(shown, use_container_width=True)
            st.download_button("下载任务看板 CSV", shown.to_csv(index=False).encode("utf-8-sig"), file_name="Aurevia_产品优化任务看板.csv", mime="text/csv", use_container_width=True, key="download_feedback_tasks")
            st.markdown("#### 手动更新任务状态与人工备注")
            task_ids = shown["id"].tolist()
            if task_ids:
                tid = st.selectbox("选择任务 ID", task_ids)
                current_row = tasks[tasks["id"] == int(tid)].iloc[0].to_dict()
                old_status = current_row.get("status", "待处理")
                new_status = st.selectbox("新状态", FEEDBACK_TASK_STATUS, index=FEEDBACK_TASK_STATUS.index(old_status) if old_status in FEEDBACK_TASK_STATUS else 0)
                manual_note = st.text_area("人工备注", placeholder="例如：已复现；需要用户提供样例文件；本批已修复；暂缓原因……", height=90)
                cstat1, cstat2 = st.columns(2)
                with cstat1:
                    if st.button("更新状态并记录", use_container_width=True):
                        conn = db_conn()
                        conn.execute("UPDATE feedback_tasks SET status=? WHERE id=?", (new_status, int(tid)))
                        conn.execute("INSERT INTO feedback_task_status_history(task_id, old_status, new_status, operator, created_at) VALUES (?, ?, ?, ?, ?)", (int(tid), old_status, new_status, current_email(), datetime.now().isoformat()))
                        if manual_note.strip():
                            conn.execute("INSERT INTO feedback_task_notes(task_id, note, operator, created_at) VALUES (?, ?, ?, ?)", (int(tid), manual_note.strip(), current_email(), datetime.now().isoformat()))
                        conn.commit(); conn.close()
                        st.success("任务状态和备注已记录。")
                        st.rerun()
                with cstat2:
                    if st.button("仅添加备注", use_container_width=True):
                        if manual_note.strip():
                            conn = db_conn()
                            conn.execute("INSERT INTO feedback_task_notes(task_id, note, operator, created_at) VALUES (?, ?, ?, ?)", (int(tid), manual_note.strip(), current_email(), datetime.now().isoformat()))
                            conn.commit(); conn.close()
                            st.success("人工备注已添加。")
                            st.rerun()
                        else:
                            st.warning("请先填写备注。")
                with st.expander("查看该任务状态变更与备注", expanded=False):
                    conn = db_conn()
                    h = pd.read_sql_query("SELECT old_status, new_status, operator, created_at FROM feedback_task_status_history WHERE task_id=? ORDER BY created_at DESC", conn, params=(int(tid),))
                    n = pd.read_sql_query("SELECT note, operator, created_at FROM feedback_task_notes WHERE task_id=? ORDER BY created_at DESC", conn, params=(int(tid),))
                    conn.close()
                    st.markdown("##### 状态变更记录")
                    st.dataframe(h, use_container_width=True)
                    st.markdown("##### 人工备注")
                    st.dataframe(n, use_container_width=True)

    with tab3:
        st.markdown("### 用户需求池")
        demands = load_user_demands_df()
        if demands.empty:
            st.info("暂无需求。可以从反馈中抽取。")
        else:
            st.dataframe(demands, use_container_width=True)
            st.download_button("下载用户需求池 CSV", demands.to_csv(index=False).encode("utf-8-sig"), file_name="Aurevia_用户需求池.csv", mime="text/csv", use_container_width=True, key="download_demands")

    with tab4:
        st.markdown("### 按场景统计用户痛点")
        stats = feedback_stats_by_scenario()
        if stats.empty:
            st.info("暂无可统计的任务数据。")
        else:
            st.dataframe(stats, use_container_width=True)
            if px is not None:
                st.plotly_chart(px.bar(stats, x="场景", y="反馈任务数", color="平均优先级", title="场景反馈任务数与平均优先级"), use_container_width=True)
            else:
                st.bar_chart(stats.set_index("场景")[["反馈任务数"]])
            st.markdown("#### 解读")
            top = stats.iloc[0].to_dict()
            st.info(f"当前最值得优先关注的场景是：{top['场景']}。反馈任务数 {top['反馈任务数']}，平均优先级 {top['平均优先级']}。建议先打磨该场景的上传、字段识别、AI解释和报告下载体验。")

    with tab5:
        st.markdown("### AI 自动生成下一轮迭代计划")
        plan_text = generate_iteration_plan_text()
        st.text_area("迭代计划草案", value=plan_text, height=430)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("保存本次迭代计划", use_container_width=True):
                save_iteration_plan(plan_text)
                st.success("迭代计划已保存。")
        with c2:
            st.download_button("下载迭代计划 TXT", plan_text.encode("utf-8"), file_name="Aurevia_AI自动迭代计划.txt", mime="text/plain", use_container_width=True, key="download_iteration_plan")


    with tab6:
        st.markdown("### 每批迭代完成后的复盘报告")
        st.markdown("<div class='infobox'>复盘不是形式，而是判断本批是否真正解决用户问题。建议每一批上线后都记录：做了什么、测了什么、发现了什么、下一步做什么。</div>", unsafe_allow_html=True)
        batch_name = st.text_input("批次名称", value="Batch 63：核心场景修复与稳定性增强")
        completed_items = st.text_area("本批完成事项", value="上传失败问题集中修复；AI作业批改稳定性增强；电商售后字段映射细化；高校就业报告可读性增强；手机端反馈入口优化；产品优化中心加入人工备注；任务状态变更记录。", height=120)
        tests_summary = st.text_area("测试摘要", value="已进行Python语法编译检查；上传错误修复逻辑检查；作业批改文本抽取逻辑检查；电商/高校深度分析函数检查；任务备注与状态记录表结构检查。", height=110)
        issues_found = st.text_area("发现的问题与处理", value="如用户真实上传的PDF为扫描件，当前仍需OCR；Streamlit Cloud对超大文件仍受平台限制；正式桌面版打包需在Windows环境实测。", height=110)
        next_actions = st.text_area("下一步建议", value="继续收集真实用户上传失败样例；补OCR方案；优化作业批改的教师复核流程；将电商字段映射做成可编辑字典。", height=110)
        if st.button("保存复盘报告", use_container_width=True):
            conn = db_conn()
            conn.execute("INSERT INTO iteration_retrospectives(batch_name, completed_items, tests_summary, issues_found, next_actions, created_at) VALUES (?, ?, ?, ?, ?, ?)", (batch_name, completed_items, tests_summary, issues_found, next_actions, datetime.now().isoformat()))
            conn.commit(); conn.close()
            st.success("复盘报告已保存。")
        report = f"""# {batch_name} 复盘报告

## 本批完成事项
{completed_items}

## 测试摘要
{tests_summary}

## 发现的问题与处理
{issues_found}

## 下一步建议
{next_actions}

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        st.download_button("下载本批复盘报告", report.encode("utf-8"), file_name="Aurevia_Batch63_复盘报告.md", mime="text/markdown", use_container_width=True, key="download_batch63_retrospective")
        conn = db_conn()
        saved = pd.read_sql_query("SELECT batch_name, created_at FROM iteration_retrospectives ORDER BY created_at DESC LIMIT 20", conn)
        conn.close()
        if not saved.empty:
            st.markdown("#### 已保存复盘记录")
            st.dataframe(saved, use_container_width=True)



def render_one_person_operator_os():
    st.markdown("## 一人公司运营中枢")
    st.markdown("<div class='infobox'>本页不是普通功能页，而是你的个人产品运营操作台：把产品、设计、文案、研究、运营和迭代放进一个闭环里，确保你一个人也能稳步管理。</div>", unsafe_allow_html=True)

    st.markdown("### 1. 关键结论：当前步骤需要加强的地方")
    checks = pd.DataFrame([
        {"检查项": "窄赛道聚焦", "当前判断": "仍然偏宽", "加强动作": "先聚焦电商售后、高校就业、AI作业批改三个核心场景", "优先级": "P0"},
        {"检查项": "真实痛点", "当前判断": "已有样例，但真实用户验证不足", "加强动作": "每周至少找3名目标用户完成一次真实任务", "优先级": "P0"},
        {"检查项": "用户主动传播", "当前判断": "还缺可分享交付物", "加强动作": "为每个场景生成可截图分享的成果卡片和汇报话术", "优先级": "P0"},
        {"检查项": "AI提升效率", "当前判断": "已有AI Agent，但运营侧自动化不足", "加强动作": "让AI自动生成内容选题、用户访谈问题、迭代计划和复盘报告", "优先级": "P1"},
        {"检查项": "数据反馈闭环", "当前判断": "已有行为和反馈记录", "加强动作": "建立每周固定复盘和指标阈值，不达标就调整产品", "优先级": "P0"},
    ])
    st.dataframe(checks, use_container_width=True)

    st.markdown("### 2. 一人公司每周工作节奏")
    weekly = pd.DataFrame([
        {"星期": "周一", "主题": "产品复盘", "动作": "看反馈、行为数据、上传失败和用户卡点", "交付物": "本周优化优先级"},
        {"星期": "周二", "主题": "核心场景打磨", "动作": "只修最影响首次成功的1-2个问题", "交付物": "小版本修复"},
        {"星期": "周三", "主题": "用户访谈", "动作": "联系3个老师/运营/电商用户，让他们跑样例或真实数据", "交付物": "访谈记录"},
        {"星期": "周四", "主题": "内容增长", "动作": "发布1篇案例文案或1条短视频脚本", "交付物": "可分享内容"},
        {"星期": "周五", "主题": "AI运营自动化", "动作": "让AI生成迭代复盘、下周计划、客服FAQ和推广话术", "交付物": "运营周报"},
        {"星期": "周末", "主题": "轻量测试", "动作": "自己从注册到样例报告跑一遍，记录卡点", "交付物": "产品体验清单"},
    ])
    st.dataframe(weekly, use_container_width=True)

    st.markdown("### 3. 30 / 60 / 90 天执行路线")
    roadmap = pd.DataFrame([
        {"阶段": "0-30天", "目标": "证明产品真的有用", "关键动作": "聚焦三大场景，确保样例报告和真实上传流程稳定", "衡量指标": "首次成功率≥70%，3个真实用户完成任务"},
        {"阶段": "31-60天", "目标": "让用户愿意复用", "关键动作": "做分享卡片、汇报话术、反馈闭环，围绕真实卡点迭代", "衡量指标": "复用用户≥5人，至少2个场景被反复使用"},
        {"阶段": "61-90天", "目标": "形成独特定位", "关键动作": "确定最强窄赛道和核心传播话术，做案例库", "衡量指标": "形成3个可公开案例，用户主动推荐/转发"},
    ])
    st.dataframe(roadmap, use_container_width=True)

    st.markdown("### 4. 增长内容选题库")
    topics = pd.DataFrame([
        {"目标用户": "电商客服主管", "标题": "一个售后Excel，3分钟看出哪个商品最容易退货", "形式": "图文/短视频", "传播点": "高频痛点+直观结果"},
        {"目标用户": "高校辅导员", "标题": "就业数据别再手动汇总，AI自动生成未就业学生清单", "形式": "案例截图", "传播点": "省时间+可交付"},
        {"目标用户": "高校老师", "标题": "50份作业批改到崩溃？先让AI做初筛和评语", "形式": "短视频", "传播点": "老师真实痛点"},
        {"目标用户": "门店运营", "标题": "日报不是给老板看的表，而是找问题的雷达", "形式": "图文", "传播点": "经营判断"},
        {"目标用户": "个人开发者", "标题": "我如何一个人把Excel工具做成AI效率平台", "形式": "复盘文章", "传播点": "一人公司故事"},
    ])
    st.dataframe(topics, use_container_width=True)

    st.markdown("### 5. 每周必须看的指标")
    metrics = pd.DataFrame([
        {"指标": "首次成功率", "定义": "用户是否完成样例/上传/报告下载任一完整流程", "警戒线": "<60%", "动作": "简化首页和首次使用路径"},
        {"指标": "上传失败率", "定义": "上传失败事件 / 上传尝试", "警戒线": ">20%", "动作": "优先修复文件读取和结构提示"},
        {"指标": "样例报告点击率", "定义": "样例报告访问 / 首页访问", "警戒线": "<30%", "动作": "把样例入口放到首屏"},
        {"指标": "AI使用率", "定义": "AI Agent使用事件 / 总用户", "警戒线": "<25%", "动作": "增加示例指令和场景化AI按钮"},
        {"指标": "反馈提交数", "定义": "每周真实反馈数量", "警戒线": "<5条", "动作": "在结果页加入更醒目的反馈入口"},
    ])
    st.dataframe(metrics, use_container_width=True)

    st.markdown("### 6. 执行按钮")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("生成本周运营周报", use_container_width=True):
            report = """Aurevia 智策云｜本周运营周报\n\n1. 本周重点：聚焦三大核心场景，先提升首次成功率。\n2. 重点检查：上传失败、样例报告点击、AI Agent使用、用户反馈。\n3. 下周动作：找3名真实用户跑一次完整流程，优先修复阻断问题。\n4. 内容增长：发布1个电商售后或高校就业真实案例。\n"""
            st.download_button("下载运营周报", report, file_name="Aurevia_本周运营周报.txt", mime="text/plain", use_container_width=True)
    with c2:
        if st.button("生成用户访谈提纲", use_container_width=True):
            guide = """用户访谈提纲\n\n1. 你平时最耗时的数据/批改/报告工作是什么？\n2. 你第一次打开产品时是否知道下一步做什么？\n3. 样例报告是否让你明白产品价值？\n4. 上传自己的文件时卡在哪里？\n5. 生成的报告是否能直接用于工作？\n6. 如果只能保留一个功能，你希望保留什么？\n7. 你愿不愿意推荐给同事？为什么？\n"""
            st.download_button("下载访谈提纲", guide, file_name="Aurevia_用户访谈提纲.txt", mime="text/plain", use_container_width=True)
    with c3:
        if st.button("生成下一批迭代建议", use_container_width=True):
            plan = """下一批迭代建议\n\n优先级P0：\n- 修复上传失败和文件结构识别问题。\n- 三大核心场景报告再压缩到一屏可懂。\n- 增加可分享成果卡片。\n\n优先级P1：\n- AI自动生成推广文案。\n- AI根据用户反馈生成任务优先级。\n- 手机端样例报告视觉继续优化。\n"""
            st.download_button("下载迭代建议", plan, file_name="Aurevia_下一批迭代建议.txt", mime="text/plain", use_container_width=True)



def render_mobile_optimized_experience():
    st.markdown("## 手机端完整优化版")
    st.markdown("<div class='mobile-hero-mini'><h2>手机上也能一屏看懂结果</h2><p>本页用于验证手机端体验：入口更短、报告卡片更清楚、AI输入更适合触屏、大文件上传有明确提示。建议你用手机打开线上网址后重点测试本页。</p></div>", unsafe_allow_html=True)

    st.markdown("### 手机端核心入口")
    c1, c2 = st.columns(2)
    with c1:
        st.button("查看样例报告", use_container_width=True)
        st.button("打开 AI Agent", use_container_width=True)
    with c2:
        st.button("上传文件分析", use_container_width=True)
        st.button("提交使用反馈", use_container_width=True)

    st.markdown("### 一屏报告卡片")
    cards = [
        ("电商售后", "退款金额", "52,430 元", "发现 12 条高风险售后工单，建议优先处理高金额退款和响应超时。"),
        ("高校就业", "就业落实率", "80.26%", "15 名学生仍待跟进，建议按专业和班级拆分帮扶。"),
        ("AI作业批改", "班级平均分", "82.4", "3 份作业存在中高雷同风险，建议教师二次复核。"),
    ]
    cols = st.columns(3)
    for col, (scene, label, value, advice) in zip(cols, cards):
        with col:
            st.markdown(f"""
            <div class='mobile-report-card'>
              <div class='label'>{scene}</div>
              <div class='kpi'>{value}</div>
              <div class='label'>{label}</div>
              <p style='line-height:1.65;color:#475569;'>{advice}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("### 移动端上传提示")
    st.markdown("<div class='warnbox'>手机端更适合查看报告、使用 AI、提交反馈。大文件、ZIP 作业包、多个 Excel 批量上传建议在电脑端完成；如果必须手机上传，请优先上传小文件并等待处理完成。</div>", unsafe_allow_html=True)
    st.markdown("### AI Agent 手机输入示例")
    prompt = st.text_area("在手机上输入你的问题", placeholder="例如：帮我分析这份电商售后报告最应该关注什么？", height=120, key="mobile_ai_prompt")
    if st.button("生成手机端 AI 示例回复", use_container_width=True):
        st.markdown("<div class='ai-msg'>建议优先查看：①退款原因占比最高项；②商品售后风险排行；③高金额退款工单；④客服响应时长。若你上传真实数据，我会进一步生成可直接汇报的话术。</div>", unsafe_allow_html=True)


def render_share_growth_center():
    st.markdown("## 成果分享中心")
    st.markdown("<div class='infobox'>目标：让用户的分析成果天然适合截图、转发和复盘，而不是生硬邀请好友。</div>", unsafe_allow_html=True)
    scene = st.selectbox("选择分享场景", ["电商售后", "高校就业", "AI作业批改"], key="share_scene")
    sample = {
        "电商售后": ("哪个商品最容易退？", "用一份售后表，3分钟发现高风险商品和高金额退款工单。"),
        "高校就业": ("未就业学生一键筛出", "就业数据不再手动汇总，院系报告自动生成。"),
        "AI作业批改": ("50份作业先让AI初筛", "自动评分、评语、雷同风险和班级趋势，一次生成。"),
    }[scene]
    st.markdown(f"""
    <div class='share-card-preview'>
      <h3>{sample[0]}</h3>
      <p>{sample[1]}</p>
      <p>适合分享到：朋友圈 / 小红书 / 公众号 / 班级群 / 运营复盘群</p>
    </div>
    """, unsafe_allow_html=True)
    captions = pd.DataFrame([
        {"平台":"小红书", "文案":"今天用 Aurevia 智策云把一份复杂表格直接生成了问题清单和汇报摘要，终于不用手动整理到崩溃。"},
        {"平台":"公众号", "文案":"一份结构化Excel背后，藏着用户真正的经营/教学痛点。AI不是替代人，而是先把重复劳动处理掉。"},
        {"平台":"朋友圈", "文案":"试了一个数据分析小工具，上传表格就能生成摘要和问题清单，挺适合老师/运营/电商售后。"},
    ])
    st.dataframe(captions, use_container_width=True)
    st.download_button("下载传播文案 CSV", captions.to_csv(index=False).encode("utf-8-sig"), file_name="Aurevia_传播文案.csv", mime="text/csv", use_container_width=True)


def render_user_case_library():
    st.markdown("## 用户案例库")
    st.markdown("<div class='infobox'>案例库用于给新用户快速展示产品价值。现阶段先用样例案例，后续替换为真实匿名案例。</div>", unsafe_allow_html=True)
    cases = pd.DataFrame([
        {"场景":"电商售后", "用户":"电商运营", "痛点":"售后表字段乱、退款原因难统计", "结果":"生成退款原因排行、商品风险排行、高风险工单", "节省时间":"约2小时/周"},
        {"场景":"高校就业", "用户":"辅导员", "痛点":"就业去向、实习单位、未就业名单要反复汇总", "结果":"生成专业就业率、未就业清单、院系汇报摘要", "节省时间":"约半天/次"},
        {"场景":"AI作业批改", "用户":"课程老师", "痛点":"作业太多、评语重复、雷同难初筛", "结果":"生成评分表、评语、雷同风险、班级趋势", "节省时间":"约3小时/批"},
    ])
    st.dataframe(cases, use_container_width=True)
    st.markdown("### 案例推荐给新用户的原则")
    st.write("优先推荐：痛点清晰、结果直观、报告可截图、用户愿意转发的案例。")


def render_share_analytics():
    st.markdown("## 传播分析")
    st.markdown("<div class='infobox'>当前是轻量模拟统计，后续可接入真实分享链接和 UTM 参数。</div>", unsafe_allow_html=True)
    df = pd.DataFrame([
        {"内容":"电商售后分享卡", "分享次数":12, "点击次数":48, "转化注册":3, "推荐动作":"继续优化电商字段映射和短视频脚本"},
        {"内容":"高校就业案例", "分享次数":9, "点击次数":40, "转化注册":4, "推荐动作":"优先找辅导员和就业办试用"},
        {"内容":"AI作业批改卡", "分享次数":15, "点击次数":63, "转化注册":6, "推荐动作":"制作老师批改前后对比案例"},
    ])
    st.dataframe(df, use_container_width=True)
    try:
        st.bar_chart(df.set_index("内容")[["分享次数", "点击次数", "转化注册"]])
    except Exception:
        pass
    st.markdown("### AI 文案策略优化建议")
    st.markdown("- 如果点击高但注册低：优化落地页首屏和立即体验入口。\n- 如果分享少：说明分享卡不够有冲击力，需要突出前后对比。\n- 如果转化集中在某个场景：优先深挖该场景，不要平均发力。")


# ----------------------------
# Main
# ----------------------------
def main():
    sidebar()
    page = st.session_state.page
    if st.session_state.get("last_logged_page") != page:
        log_event("page_view", page=page)
        st.session_state.last_logged_page = page
    if page == "首页":
        render_home()
    elif page == "首次使用向导":
        render_first_success_guide()
    elif page == "工作台":
        render_workspace()
    elif page == "场景配置向导":
        render_scene_config_wizard()
    elif page == "样例报告库":
        render_sample_reports()
    elif page == "模板中心":
        render_templates()
    elif page == "手机端优化":
        render_mobile_optimized_experience()
    elif page == "成果分享中心":
        render_share_growth_center()
    elif page == "用户案例库":
        render_user_case_library()
    elif page == "传播分析":
        render_share_analytics()
    elif page == "AI推荐策略":
        render_ai_recommendation_strategy()
    elif page == "交互图表":
        render_interactive_charts()
    elif page == "体验数据分析":
        render_user_experience_analytics()
    elif page == "AI智能中心":
        render_ai_center()
    elif page == "AI作业批改":
        render_grading()
    elif page == "一人公司运营中枢":
        render_one_person_operator_os()
    elif page == "产品优化中心":
        render_product_iteration_center()
    elif page == "隐私与数据":
        render_privacy_data()
    elif page == "App与桌面版":
        render_app_delivery_plan()
    elif page == "桌面版启动页":
        render_desktop_launch_page()
    elif page == "移动端体验":
        render_mobile_experience_page()
    elif page == "PWA安装引导":
        render_pwa_install_guide()
    elif page == "协议与政策":
        render_legal_pages()
    elif page == "上架前检查":
        render_app_store_checklist()
    elif page == "系统后台":
        render_admin()
    elif page == "反馈":
        render_feedback()
    render_audit() if page == "首页" else None
    render_bottom_utility_links()
    st.markdown(f"<div class='footer'>© 2026 {APP_NAME}｜免费开放核心功能｜联系：{CONTACT_EMAIL}</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
