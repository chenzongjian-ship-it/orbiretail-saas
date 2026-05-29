# -*- coding: utf-8 -*-
"""
OrbiRetail 奥比零售云 - Batch 37
样例数据体验 + 用户引导 + 首次成功路径优化 + P1 能力

交付内容：
1. 批量上传
2. 模板说明页
3. 样例数据体验
4. 经营诊断摘要
5. 下载问题清单
6. 报告包下载
7. 用户反馈入口
8. 首次成功路径优化
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import io
import json
import math
import os
import re
import secrets
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st


APP_NAME = "OrbiRetail 奥比零售云"
APP_VERSION = "Batch 37 样例体验与引导优化版"
TRIAL_DAYS = 7
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "saas_data"
USERS_FILE = DATA_DIR / "users.json"
FEEDBACK_FILE = DATA_DIR / "feedback.jsonl"
DATA_DIR.mkdir(exist_ok=True)


# -----------------------------------------------------------------------------
# 页面配置与样式
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="OrbiRetail 奥比零售云",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def inject_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --orbi-navy: #0f172a;
            --orbi-blue: #2563eb;
            --orbi-cyan: #14b8a6;
            --orbi-slate: #334155;
            --orbi-muted: #64748b;
            --orbi-bg: #f8fafc;
            --orbi-card: #ffffff;
            --orbi-border: #e2e8f0;
        }
        .stApp {
            background:
                radial-gradient(circle at 8% 8%, rgba(37,99,235,.10), transparent 28%),
                radial-gradient(circle at 92% 12%, rgba(20,184,166,.12), transparent 24%),
                linear-gradient(180deg, #f8fafc 0%, #eef4ff 48%, #f8fafc 100%);
            color: var(--orbi-navy);
        }
        .block-container {
            padding-top: 2.0rem;
            padding-bottom: 3.2rem;
            max-width: 1380px;
        }
        div[data-testid="stHeader"] {
            background: rgba(248,250,252,.66);
            backdrop-filter: blur(18px);
        }
        .orbi-hero {
            position: relative;
            overflow: hidden;
            border-radius: 30px;
            padding: 42px 48px;
            color: white;
            background: linear-gradient(135deg, #020617 0%, #1d4ed8 52%, #0f766e 100%);
            box-shadow: 0 26px 76px rgba(15,23,42,.22);
            margin-bottom: 24px;
        }
        .orbi-hero:after {
            content: "";
            position: absolute;
            right: -135px;
            top: -130px;
            width: 380px;
            height: 380px;
            border-radius: 999px;
            background: rgba(255,255,255,.11);
        }
        .orbi-hero h1 {
            font-size: 44px;
            line-height: 1.12;
            margin: 0 0 14px 0;
            letter-spacing: -.045em;
            color: #fff;
        }
        .orbi-hero p {
            font-size: 17px;
            opacity: .92;
            margin: 0;
            max-width: 920px;
        }
        .orbi-pill-row {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 24px;
        }
        .orbi-pill {
            padding: 7px 12px;
            border-radius: 999px;
            background: rgba(255,255,255,.14);
            border: 1px solid rgba(255,255,255,.20);
            color: #fff;
            font-size: 13px;
        }
        .orbi-card {
            border: 1px solid rgba(226,232,240,.92);
            background: rgba(255,255,255,.90);
            backdrop-filter: blur(16px);
            border-radius: 22px;
            padding: 22px;
            box-shadow: 0 14px 34px rgba(15,23,42,.08);
            height: 100%;
        }
        .orbi-card h3, .orbi-card h4 {
            margin-top: 0;
            color: #0f172a;
        }
        .orbi-muted { color: #64748b; font-size: 14px; line-height: 1.65; }
        .orbi-small { color: #64748b; font-size: 12.5px; line-height: 1.55; }
        .orbi-section-title {
            margin: 18px 0 10px 0;
            font-size: 24px;
            font-weight: 850;
            letter-spacing: -.035em;
            color: #0f172a;
        }
        .orbi-section-subtitle {
            margin: -4px 0 18px 0;
            color: #64748b;
            font-size: 15px;
        }
        .step-card {
            border-radius: 20px;
            background: #fff;
            border: 1px solid #e2e8f0;
            padding: 18px;
            box-shadow: 0 12px 28px rgba(15,23,42,.06);
            height: 100%;
        }
        .step-num {
            width: 30px; height: 30px;
            display: inline-flex; align-items:center; justify-content:center;
            border-radius: 10px;
            background: #eff6ff;
            color: #1d4ed8;
            font-weight: 800;
            margin-right: 8px;
        }
        .template-card {
            border: 1px solid #e2e8f0;
            border-radius: 20px;
            background: #fff;
            padding: 18px;
            min-height: 250px;
            box-shadow: 0 10px 24px rgba(15,23,42,.055);
        }
        .template-card .icon { font-size: 28px; margin-bottom: 8px; }
        .template-card .name {
            font-size: 18px;
            font-weight: 850;
            color: #0f172a;
            margin-bottom: 6px;
        }
        .template-card .tag {
            display: inline-block;
            font-size: 12px;
            padding: 4px 9px;
            border-radius: 999px;
            background: #eff6ff;
            color: #1d4ed8;
            margin-bottom: 10px;
        }
        .template-card .desc {
            color: #475569;
            font-size: 13.5px;
            min-height: 54px;
            margin-bottom: 10px;
        }
        .template-card .output { color: #0f766e; font-size: 13px; }
        .metric-card {
            border-radius: 22px;
            padding: 20px 20px 18px 20px;
            background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
            border: 1px solid #e2e8f0;
            box-shadow: 0 12px 28px rgba(15,23,42,.07);
            height: 100%;
        }
        .metric-label { color: #64748b; font-size: 13px; margin-bottom: 10px; }
        .metric-value {
            color: #0f172a;
            font-size: 28px;
            font-weight: 850;
            letter-spacing: -.04em;
        }
        .metric-note { color: #0f766e; margin-top: 8px; font-size: 12.5px; }
        .trust-good { color: #059669; font-weight: 850; }
        .trust-mid { color: #d97706; font-weight: 850; }
        .trust-bad { color: #dc2626; font-weight: 850; }
        .diagnosis-box {
            border-left: 5px solid #2563eb;
            background: rgba(255,255,255,.94);
            border-radius: 18px;
            padding: 18px 20px;
            box-shadow: 0 10px 24px rgba(15,23,42,.055);
            margin-bottom: 12px;
        }
        .diagnosis-title { font-weight: 850; color:#0f172a; margin-bottom:5px; }
        .diagnosis-desc { color:#475569; font-size:14px; line-height:1.65; }
        .login-shell {
            display: grid;
            grid-template-columns: 1.18fr .82fr;
            gap: 26px;
            align-items: stretch;
            margin-top: 16px;
        }
        .login-brand {
            border-radius: 30px;
            color: white;
            padding: 48px;
            background:
                radial-gradient(circle at 82% 16%, rgba(20,184,166,.30), transparent 28%),
                linear-gradient(135deg, #020617 0%, #1e3a8a 54%, #0f766e 100%);
            min-height: 620px;
            box-shadow: 0 30px 80px rgba(15,23,42,.24);
        }
        .login-brand h1 {
            font-size: 50px;
            line-height: 1.06;
            color: #fff;
            letter-spacing: -.055em;
            margin: 20px 0 18px 0;
        }
        .login-brand .lead {
            font-size: 18px;
            line-height: 1.7;
            color: rgba(255,255,255,.88);
            max-width: 740px;
        }
        .login-kpis {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 14px;
            margin-top: 34px;
        }
        .login-kpi {
            border-radius: 18px;
            padding: 18px;
            background: rgba(255,255,255,.10);
            border: 1px solid rgba(255,255,255,.18);
        }
        .login-kpi strong { display:block; font-size: 23px; color:#fff; margin-bottom: 5px; }
        .login-kpi span { color: rgba(255,255,255,.78); font-size: 12.5px; }
        .login-form-card {
            border-radius: 30px;
            background: rgba(255,255,255,.93);
            border: 1px solid #e2e8f0;
            padding: 30px;
            box-shadow: 0 22px 58px rgba(15,23,42,.15);
            min-height: 620px;
        }
        .brand-mark {
            display: inline-flex;
            align-items: center;
            gap: 12px;
            font-weight: 850;
            letter-spacing: -.03em;
            font-size: 18px;
            color: #fff;
        }
        .brand-dot {
            width: 38px; height: 38px; border-radius: 14px;
            background: linear-gradient(135deg, #60a5fa, #2dd4bf);
            display:flex; align-items:center; justify-content:center;
            box-shadow: 0 12px 30px rgba(20,184,166,.34);
        }
        @media (max-width: 980px) {
            .login-shell { grid-template-columns: 1fr; }
            .login-brand { min-height: auto; padding: 32px; }
            .login-brand h1 { font-size: 38px; }
            .login-kpis { grid-template-columns: 1fr; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_css()


# -----------------------------------------------------------------------------
# 用户、登录与试用
# -----------------------------------------------------------------------------
def load_users() -> Dict[str, Any]:
    if USERS_FILE.exists():
        try:
            return json.loads(USERS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_users(users: Dict[str, Any]) -> None:
    USERS_FILE.write_text(json.dumps(users, ensure_ascii=False, indent=2), encoding="utf-8")


def password_hash(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120_000).hex()


def register_user(email: str, password: str, company: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    email = email.strip().lower()
    users = load_users()
    if not email or "@" not in email:
        return False, None, "请输入有效邮箱。"
    if len(password) < 6:
        return False, None, "密码至少 6 位。"
    if email in users:
        return False, None, "该邮箱已经注册，请直接登录。"
    now = dt.datetime.now()
    salt = secrets.token_hex(12)
    user = {
        "email": email,
        "company": company.strip() or "未命名企业",
        "salt": salt,
        "password_hash": password_hash(password, salt),
        "created_at": now.isoformat(),
        "trial_start": now.isoformat(),
        "trial_end": (now + dt.timedelta(days=TRIAL_DAYS)).isoformat(),
        "plan": "Trial",
    }
    users[email] = user
    save_users(users)
    return True, user, "注册成功，已开通 7 天试用。"


def authenticate(email: str, password: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    email = email.strip().lower()
    users = load_users()
    user = users.get(email)
    if not user:
        return False, None, "账号不存在。"
    if password_hash(password, user["salt"]) != user["password_hash"]:
        return False, None, "密码错误。"
    return True, user, "登录成功。"


def trial_days_left(user: Dict[str, Any]) -> int:
    end = dt.datetime.fromisoformat(user["trial_end"])
    seconds = (end - dt.datetime.now()).total_seconds()
    if seconds <= 0:
        return 0
    return int(math.ceil(seconds / 86400))


def is_trial_active(user: Dict[str, Any]) -> bool:
    return dt.datetime.now() <= dt.datetime.fromisoformat(user["trial_end"])


def logout() -> None:
    for key in ["auth", "user", "selected_template", "analysis_result", "demo_started"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()


# -----------------------------------------------------------------------------
# 场景模板中心
# -----------------------------------------------------------------------------
TEMPLATES: List[Dict[str, Any]] = [
    {
        "id": "retail_daily",
        "icon": "🏪",
        "name": "门店 / 渠道销售日报",
        "category": "零售经营",
        "tagline": "门店日报、平台结算、退款佣金自动对齐",
        "for_who": "门店运营、区域经理、财务结算",
        "inputs": "门店销售日报、渠道结算日报、退款明细、佣金表",
        "outputs": "销售汇总、渠道差异、退款冲销、净销售额、经营诊断",
        "saving": "每日 30-90 分钟",
        "required": ["date", "store", "channel", "amount"],
        "dimensions": ["date", "store", "channel"],
        "value_field": "amount",
        "sample_steps": ["上传门店销售日报", "系统识别渠道与金额", "检查退款 / 佣金 / 优惠", "下载日报分析包"],
    },
    {
        "id": "boss_daily",
        "icon": "📌",
        "name": "老板经营日报",
        "category": "零售经营",
        "tagline": "给老板看的一页经营结论，不再只给明细表",
        "for_who": "老板、总经理、区域负责人",
        "inputs": "门店日报、渠道日报、成本费用、退款佣金",
        "outputs": "收入、利润、亏损门店、异常渠道、建议动作",
        "saving": "每日 20-60 分钟",
        "required": ["date", "store", "amount"],
        "dimensions": ["date", "store"],
        "value_field": "amount",
        "sample_steps": ["上传门店日报", "系统汇总关键指标", "生成经营诊断", "下载老板摘要"],
    },
    {
        "id": "platform_settlement",
        "icon": "🧾",
        "name": "平台结算对账",
        "category": "财务对账",
        "tagline": "订单、平台结算、到账金额自动核对",
        "for_who": "财务、渠道运营、结算人员",
        "inputs": "门店订单、平台结算单、银行流水",
        "outputs": "未结算订单、结算差异、手续费差异、到账差异",
        "saving": "每周 2-5 小时",
        "required": ["order_id", "amount"],
        "dimensions": ["channel", "store"],
        "value_field": "amount",
        "sample_steps": ["上传平台订单与结算数据", "识别订单号与金额", "发现结算差异", "下载对账问题清单"],
    },
    {
        "id": "supplier_recon",
        "icon": "🤝",
        "name": "供应商对账",
        "category": "财务对账",
        "tagline": "采购订单、入库、发票、付款自动比对",
        "for_who": "财务、采购、供应链",
        "inputs": "采购订单、入库单、发票、付款记录",
        "outputs": "匹配项、金额不一致、仅订单存在、仅发票存在",
        "saving": "每月 3-8 小时",
        "required": ["supplier", "amount"],
        "dimensions": ["supplier"],
        "value_field": "amount",
        "sample_steps": ["上传供应商明细", "识别供应商和金额", "汇总差异", "下载对账报告"],
    },
    {
        "id": "monthly_expense",
        "icon": "💼",
        "name": "月度费用汇总",
        "category": "财务对账",
        "tagline": "部门费用、项目费用、员工报销自动汇总质检",
        "for_who": "财务、行政、部门助理",
        "inputs": "部门费用表、员工报销表、项目费用表",
        "outputs": "费用汇总、异常金额、重复报销、部门排名",
        "saving": "每月 2-6 小时",
        "required": ["department", "month", "expense_category", "amount"],
        "dimensions": ["department", "month", "expense_category"],
        "value_field": "amount",
        "sample_steps": ["上传费用明细", "识别部门和费用类别", "自动汇总", "下载费用报告"],
    },
    {
        "id": "sales_performance",
        "icon": "📈",
        "name": "销售业绩分析",
        "category": "销售运营",
        "tagline": "区域、人员、产品、客户维度业绩自动排名",
        "for_who": "销售运营、销售经理、业务负责人",
        "inputs": "销售明细、销售人员表、区域表、产品表",
        "outputs": "销售排名、区域排名、产品排名、同比环比",
        "saving": "每周 1-4 小时",
        "required": ["salesperson", "amount"],
        "dimensions": ["region", "salesperson", "product"],
        "value_field": "amount",
        "sample_steps": ["上传销售明细", "识别销售人员和区域", "自动排名", "下载销售简报"],
    },
    {
        "id": "inventory_check",
        "icon": "📦",
        "name": "库存盘点差异",
        "category": "库存供应链",
        "tagline": "系统库存与实际盘点自动比对，快速定位盘盈盘亏",
        "for_who": "仓储、门店、供应链、财务",
        "inputs": "系统库存、实际盘点表、出入库记录",
        "outputs": "盘盈、盘亏、异常商品、差异金额",
        "saving": "每次盘点 2-10 小时",
        "required": ["product", "system_qty", "actual_qty"],
        "dimensions": ["store", "product"],
        "value_field": "diff_qty",
        "sample_steps": ["上传系统库存和盘点结果", "识别商品和数量", "计算差异", "下载盘点差异表"],
    },
    {
        "id": "payroll_check",
        "icon": "👥",
        "name": "考勤工资核对",
        "category": "人事行政",
        "tagline": "考勤、请假、工资自动核对，减少人工复算",
        "for_who": "人事、行政、薪酬专员",
        "inputs": "考勤表、请假表、工资表",
        "outputs": "应发差异、缺勤异常、请假异常、工资核对表",
        "saving": "每月 2-6 小时",
        "required": ["employee", "month", "salary_actual"],
        "dimensions": ["department", "employee", "month"],
        "value_field": "salary_actual",
        "sample_steps": ["上传工资 / 考勤表", "识别员工和月份", "核对工资字段", "下载核对清单"],
    },
]

CATEGORIES = ["全部", "零售经营", "财务对账", "销售运营", "库存供应链", "人事行政"]

FIELD_ALIASES: Dict[str, List[str]] = {
    "date": ["日期", "业务日期", "销售日期", "下单日期", "支付时间", "结算日期", "Date"],
    "month": ["月份", "月", "统计月份", "所属月份", "Month"],
    "store": ["门店", "门店名称", "店铺", "店名", "门店编码", "Store"],
    "channel": ["渠道", "平台", "销售渠道", "结算渠道", "Channel", "Platform"],
    "order_id": ["订单号", "单号", "交易号", "业务单号", "OrderID", "Order No"],
    "amount": ["金额", "销售额", "实收金额", "结算金额", "支付金额", "订单金额", "收入", "Amount", "Sales"],
    "refund_amount": ["退款金额", "退款", "退货金额", "Refund"],
    "commission": ["佣金", "平台佣金", "服务费", "手续费", "Commission", "Fee"],
    "discount": ["优惠金额", "折扣金额", "优惠", "平台补贴", "门店优惠", "Discount"],
    "net_amount": ["净销售额", "净收入", "净额", "Net Amount", "Net Sales"],
    "supplier": ["供应商", "供应商名称", "Vendor", "Supplier"],
    "department": ["部门", "部门名称", "所属部门", "Department"],
    "expense_category": ["费用类别", "类别", "费用分类", "科目", "Category"],
    "salesperson": ["销售人员", "业务员", "销售", "Salesperson"],
    "region": ["区域", "大区", "地区", "Region"],
    "product": ["商品", "产品", "品名", "SKU", "Product"],
    "system_qty": ["系统库存", "账面库存", "系统数量", "System Qty"],
    "actual_qty": ["实际库存", "盘点库存", "实盘数量", "Actual Qty"],
    "diff_qty": ["差异数量", "库存差异", "Diff Qty"],
    "employee": ["员工", "员工姓名", "姓名", "Employee"],
    "salary_actual": ["实发工资", "应发工资", "工资", "薪资", "Salary"],
    "salary_expected": ["预计工资", "核算工资", "Expected Salary"],
    "source_file": ["来源文件", "文件名", "Source File"],
}

FIELD_LABELS = {
    "date": "日期",
    "month": "月份",
    "store": "门店",
    "channel": "渠道",
    "order_id": "订单号",
    "amount": "金额 / 销售额",
    "refund_amount": "退款金额",
    "commission": "平台佣金 / 服务费",
    "discount": "优惠 / 折扣",
    "net_amount": "净销售额",
    "supplier": "供应商",
    "department": "部门",
    "expense_category": "费用类别",
    "salesperson": "销售人员",
    "region": "区域",
    "product": "商品 / 产品",
    "system_qty": "系统库存",
    "actual_qty": "实际库存",
    "diff_qty": "差异数量",
    "employee": "员工",
    "salary_actual": "实发 / 应发工资",
    "salary_expected": "预计工资",
    "source_file": "来源文件",
}


# -----------------------------------------------------------------------------
# 数据处理
# -----------------------------------------------------------------------------
def normalize_text(value: Any) -> str:
    text = str(value).strip().lower()
    text = re.sub(r"[\s\-_/()（）【】\[\].,，。:：]+", "", text)
    return text


def detect_fields(columns: List[str]) -> Dict[str, Optional[str]]:
    normalized_cols = {col: normalize_text(col) for col in columns}
    result: Dict[str, Optional[str]] = {key: None for key in FIELD_ALIASES}
    for field, aliases in FIELD_ALIASES.items():
        normalized_aliases = [normalize_text(a) for a in aliases]
        for col, norm_col in normalized_cols.items():
            if norm_col in normalized_aliases:
                result[field] = col
                break
        if result[field]:
            continue
        for col, norm_col in normalized_cols.items():
            for alias in normalized_aliases:
                if len(alias) >= 2 and (alias in norm_col or norm_col in alias):
                    result[field] = col
                    break
            if result[field]:
                break
    return result


def read_uploaded_file(uploaded_file: Any) -> pd.DataFrame:
    if uploaded_file.name.lower().endswith(".csv"):
        try:
            return pd.read_csv(uploaded_file)
        except UnicodeDecodeError:
            uploaded_file.seek(0)
            return pd.read_csv(uploaded_file, encoding="gbk")
    return pd.read_excel(uploaded_file)


def read_uploaded_files(uploaded_files: List[Any]) -> Tuple[pd.DataFrame, List[Dict[str, Any]]]:
    frames = []
    logs = []
    for f in uploaded_files:
        try:
            df = read_uploaded_file(f)
            df.columns = [str(c).strip() for c in df.columns]
            df["来源文件"] = f.name
            frames.append(df)
            logs.append({"文件名": f.name, "状态": "成功", "行数": len(df), "列数": len(df.columns)})
        except Exception as exc:
            logs.append({"文件名": getattr(f, "name", "未知文件"), "状态": "失败", "行数": 0, "列数": 0, "错误": str(exc)})
    if not frames:
        return pd.DataFrame(), logs
    return pd.concat(frames, ignore_index=True, sort=False), logs


def to_number(series: pd.Series) -> pd.Series:
    cleaned = series.astype(str).str.replace(",", "", regex=False)
    cleaned = cleaned.str.replace("¥", "", regex=False).str.replace("￥", "", regex=False)
    cleaned = cleaned.str.replace("元", "", regex=False).str.replace(" ", "", regex=False)
    cleaned = cleaned.replace({"nan": None, "None": None, "": None})
    return pd.to_numeric(cleaned, errors="coerce")


def build_issues(df: pd.DataFrame, mapping: Dict[str, Optional[str]], template: Dict[str, Any]) -> pd.DataFrame:
    issues: List[Dict[str, Any]] = []
    for field in template["required"]:
        if not mapping.get(field):
            issues.append({
                "级别": "ERROR",
                "问题类型": "缺少必需字段",
                "问题详情": f"当前模板需要字段：{FIELD_LABELS.get(field, field)}",
                "建议处理": "请检查表头，或在导出数据中补充该字段。",
                "行号": "-",
                "来源文件": "全部",
            })

    for field, col in mapping.items():
        if col and col in df.columns:
            null_count = int(df[col].isna().sum())
            if null_count > 0:
                issues.append({
                    "级别": "WARNING",
                    "问题类型": "存在空值",
                    "问题详情": f"字段 {FIELD_LABELS.get(field, field)} / {col} 有 {null_count} 个空值。",
                    "建议处理": "建议补齐空值，或确认这些记录是否应排除。",
                    "行号": "多行",
                    "来源文件": "多文件" if "来源文件" in df.columns else "当前文件",
                })

    amount_col = mapping.get(template.get("value_field")) or mapping.get("amount") or mapping.get("salary_actual")
    if amount_col and amount_col in df.columns:
        amount = to_number(df[amount_col])
        invalid_count = int(amount.isna().sum())
        if invalid_count > 0:
            issues.append({
                "级别": "WARNING",
                "问题类型": "金额无法解析",
                "问题详情": f"字段 {amount_col} 有 {invalid_count} 行无法转换成数字。",
                "建议处理": "请删除金额中的文字说明，保留数字、负号和小数点。",
                "行号": "多行",
                "来源文件": "多文件" if "来源文件" in df.columns else "当前文件",
            })
        negative_count = int((amount < 0).sum())
        if negative_count > 0:
            issues.append({
                "级别": "INFO",
                "问题类型": "负数金额",
                "问题详情": f"字段 {amount_col} 中有 {negative_count} 行负数，可能是退款或冲销。",
                "建议处理": "如属于退款/冲销，建议保留；如不是，请复核。",
                "行号": "多行",
                "来源文件": "多文件" if "来源文件" in df.columns else "当前文件",
            })

    order_col = mapping.get("order_id")
    if order_col and order_col in df.columns:
        duplicates = int(df[order_col].duplicated().sum())
        if duplicates > 0:
            issues.append({
                "级别": "WARNING",
                "问题类型": "订单号重复",
                "问题详情": f"发现 {duplicates} 行重复订单号。",
                "建议处理": "请确认是拆单、退款记录，还是重复录入。",
                "行号": "多行",
                "来源文件": "多文件" if "来源文件" in df.columns else "当前文件",
            })

    return pd.DataFrame(issues)


def trust_score(df: pd.DataFrame, mapping: Dict[str, Optional[str]], template: Dict[str, Any], issues_df: pd.DataFrame) -> Tuple[int, str, str, pd.DataFrame]:
    score = 100
    details: List[Dict[str, Any]] = []

    missing_required = [f for f in template["required"] if not mapping.get(f)]
    if missing_required:
        penalty = min(45, len(missing_required) * 15)
        score -= penalty
        details.append({"检查项": "必需字段", "结果": f"缺少 {len(missing_required)} 个必需字段", "扣分": penalty})
    else:
        details.append({"检查项": "必需字段", "结果": "完整", "扣分": 0})

    if df.empty:
        score -= 40
        details.append({"检查项": "数据行数", "结果": "无有效数据", "扣分": 40})
    else:
        null_ratio = float(df.isna().sum().sum()) / max(1, df.shape[0] * df.shape[1])
        penalty = int(min(20, null_ratio * 80))
        score -= penalty
        details.append({"检查项": "空值比例", "结果": f"{null_ratio:.1%}", "扣分": penalty})

    amount_col = mapping.get(template.get("value_field")) or mapping.get("amount") or mapping.get("salary_actual")
    if amount_col and amount_col in df.columns:
        amount = to_number(df[amount_col])
        invalid_ratio = float(amount.isna().sum()) / max(1, len(amount))
        penalty = int(min(20, invalid_ratio * 60))
        score -= penalty
        details.append({"检查项": "金额可解析性", "结果": f"异常 {invalid_ratio:.1%}", "扣分": penalty})
    else:
        score -= 20
        details.append({"检查项": "金额字段", "结果": "未识别", "扣分": 20})

    error_count = 0 if issues_df.empty else int((issues_df.get("级别", pd.Series(dtype=str)) == "ERROR").sum())
    warning_count = 0 if issues_df.empty else int((issues_df.get("级别", pd.Series(dtype=str)) == "WARNING").sum())
    penalty = min(20, error_count * 8 + warning_count * 2)
    score -= penalty
    details.append({"检查项": "问题清单", "结果": f"ERROR {error_count} / WARNING {warning_count}", "扣分": penalty})

    score = max(0, min(100, score))
    if score >= 85:
        level = "可信"
        css = "trust-good"
    elif score >= 65:
        level = "需复核"
        css = "trust-mid"
    else:
        level = "不可直接使用"
        css = "trust-bad"
    return score, level, css, pd.DataFrame(details)


def analyze_dataframe(df: pd.DataFrame, template: Dict[str, Any], file_logs: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    mapping = detect_fields(list(df.columns))
    issues_df = build_issues(df, mapping, template)

    value_field = template.get("value_field", "amount")
    value_col = mapping.get(value_field) or mapping.get("amount") or mapping.get("salary_actual")

    analysis_df = df.copy()
    if value_col and value_col in analysis_df.columns:
        analysis_df["_分析金额"] = to_number(analysis_df[value_col]).fillna(0)
    elif value_field == "diff_qty":
        system_col = mapping.get("system_qty")
        actual_col = mapping.get("actual_qty")
        if system_col and actual_col and system_col in analysis_df.columns and actual_col in analysis_df.columns:
            analysis_df["_分析金额"] = to_number(analysis_df[actual_col]).fillna(0) - to_number(analysis_df[system_col]).fillna(0)
        else:
            analysis_df["_分析金额"] = 0
    else:
        analysis_df["_分析金额"] = 0

    net_components: Dict[str, float] = {}
    net_amount = analysis_df["_分析金额"].copy()
    for field, label in [("refund_amount", "退款金额"), ("commission", "平台佣金"), ("discount", "优惠金额")]:
        col = mapping.get(field)
        if col and col in analysis_df.columns:
            numeric = to_number(analysis_df[col]).fillna(0)
            net_components[label] = float(numeric.sum())
            net_amount = net_amount - numeric
    analysis_df["_净额"] = net_amount

    group_cols = []
    for field in template.get("dimensions", []):
        col = mapping.get(field)
        if col and col in analysis_df.columns and col not in group_cols:
            group_cols.append(col)
    if "来源文件" in analysis_df.columns and len(analysis_df["来源文件"].dropna().unique()) > 1 and "来源文件" not in group_cols:
        group_cols = ["来源文件"] + group_cols

    if group_cols:
        summary = (
            analysis_df.groupby(group_cols, dropna=False)
            .agg(记录数=("_净额", "count"), 合计金额=("_分析金额", "sum"), 净额=("_净额", "sum"), 平均金额=("_净额", "mean"))
            .reset_index()
            .sort_values("净额", ascending=False)
        )
    else:
        summary = pd.DataFrame({
            "记录数": [len(analysis_df)],
            "合计金额": [float(analysis_df["_分析金额"].sum())],
            "净额": [float(analysis_df["_净额"].sum())],
            "平均金额": [float(analysis_df["_净额"].mean()) if len(analysis_df) else 0],
        })

    score, level, css, trust_details = trust_score(df, mapping, template, issues_df)

    metrics = {
        "records": int(len(df)),
        "columns": int(len(df.columns)),
        "total_amount": float(analysis_df["_分析金额"].sum()),
        "net_amount": float(analysis_df["_净额"].sum()),
        "avg_amount": float(analysis_df["_净额"].mean()) if len(analysis_df) else 0.0,
        "issue_count": int(len(issues_df)),
        "recognized_fields": int(sum(1 for v in mapping.values() if v)),
        "trust_score": score,
        "trust_level": level,
        "trust_css": css,
        "net_components": net_components,
        "file_count": int(len(file_logs or [])) or int(analysis_df["来源文件"].nunique()) if "来源文件" in analysis_df.columns else 1,
    }

    field_rows = []
    for field, label in FIELD_LABELS.items():
        original_col = mapping.get(field)
        field_rows.append({
            "标准字段": label,
            "系统字段": field,
            "识别到的原始列": original_col or "未识别",
            "状态": "已识别" if original_col else "未识别",
        })
    field_df = pd.DataFrame(field_rows)
    insights = generate_insights(template, metrics, issues_df, summary)
    actions = generate_action_recommendations(template, metrics, issues_df, summary)

    return {
        "raw": df,
        "analysis_df": analysis_df,
        "mapping": mapping,
        "field_df": field_df,
        "issues_df": issues_df,
        "summary": summary,
        "metrics": metrics,
        "trust_details": trust_details,
        "insights": insights,
        "actions": actions,
        "template": template,
        "file_logs": file_logs or [],
    }


def fmt_money(value: float) -> str:
    try:
        return f"¥{value:,.2f}"
    except Exception:
        return "¥0.00"


def generate_insights(template: Dict[str, Any], metrics: Dict[str, Any], issues_df: pd.DataFrame, summary: pd.DataFrame) -> List[str]:
    insights: List[str] = []
    if metrics["trust_score"] >= 85:
        insights.append("本次数据可信度较高，可以作为经营分析的初步依据。")
    elif metrics["trust_score"] >= 65:
        insights.append("本次数据可用于初步分析，但建议先复核问题清单中的异常项。")
    else:
        insights.append("本次数据存在较多风险，建议修正字段或异常数据后再用于正式汇报。")
    if metrics["issue_count"] > 0:
        insights.append(f"系统发现 {metrics['issue_count']} 条字段、空值或金额相关问题，请优先处理 ERROR 和 WARNING。")
    if metrics.get("file_count", 1) > 1:
        insights.append(f"本次批量读取 {metrics['file_count']} 个文件，已合并为统一口径进行分析。")
    if not summary.empty and "净额" in summary.columns and len(summary) > 1:
        top_row = summary.iloc[0]
        dim_cols = [c for c in summary.columns if c not in ["记录数", "合计金额", "净额", "平均金额"]]
        dim_desc = " / ".join(str(top_row[c]) for c in dim_cols[:3])
        insights.append(f"当前净额最高的分组是：{dim_desc}，净额为 {fmt_money(float(top_row['净额']))}。")
    if template["id"] in ["retail_daily", "platform_settlement", "boss_daily"]:
        if metrics["net_components"]:
            insights.append("已识别退款、佣金或优惠字段，系统已按净额口径进行经营指标计算。")
        else:
            insights.append("未识别退款、佣金或优惠字段；如实际存在平台费用，建议补充后再分析净利润。")
    elif template["id"] == "inventory_check":
        insights.append("库存差异建议结合商品金额进一步计算盘盈盘亏价值，便于财务复核。")
    elif template["id"] == "payroll_check":
        insights.append("工资核对结果建议由人事和财务共同复核，避免因考勤口径不同导致误判。")
    return insights


def generate_action_recommendations(template: Dict[str, Any], metrics: Dict[str, Any], issues_df: pd.DataFrame, summary: pd.DataFrame) -> List[Dict[str, str]]:
    actions: List[Dict[str, str]] = []
    if metrics["trust_score"] < 85:
        actions.append({"优先级": "高", "建议动作": "先处理问题清单", "说明": "字段缺失、金额无法解析或空值过多会直接影响经营结论。"})
    if metrics["issue_count"] > 0:
        actions.append({"优先级": "高", "建议动作": "下载问题清单并回传给提交人", "说明": "优先修正 ERROR 和 WARNING，再重新上传分析。"})
    if template["id"] in ["retail_daily", "platform_settlement", "boss_daily"] and not metrics["net_components"]:
        actions.append({"优先级": "中", "建议动作": "补充退款、佣金、优惠字段", "说明": "只有销售额不代表真实利润，补充费用字段后结果更接近经营口径。"})
    if not summary.empty and "净额" in summary.columns and len(summary) > 1:
        bottom = summary.sort_values("净额", ascending=True).head(1).iloc[0]
        dim_cols = [c for c in summary.columns if c not in ["记录数", "合计金额", "净额", "平均金额"]]
        dim_desc = " / ".join(str(bottom[c]) for c in dim_cols[:3])
        actions.append({"优先级": "中", "建议动作": "复核低净额分组", "说明": f"建议关注净额较低的分组：{dim_desc}。"})
    if not actions:
        actions.append({"优先级": "正常", "建议动作": "可进入报告下载", "说明": "当前数据质量较好，可下载报告用于内部复核或汇报。"})
    return actions


def make_report_bytes(result: Dict[str, Any]) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        result["raw"].to_excel(writer, sheet_name="原始数据", index=False)
        result["summary"].to_excel(writer, sheet_name="汇总结果", index=False)
        result["field_df"].to_excel(writer, sheet_name="字段识别", index=False)
        result["issues_df"].to_excel(writer, sheet_name="问题清单", index=False)
        result["trust_details"].to_excel(writer, sheet_name="数据可信度", index=False)
        pd.DataFrame(result.get("file_logs", [])).to_excel(writer, sheet_name="上传文件日志", index=False)
        pd.DataFrame(result["actions"]).to_excel(writer, sheet_name="建议动作", index=False)
        metrics_df = pd.DataFrame([
            {"指标": "文件数", "值": result["metrics"].get("file_count", 1)},
            {"指标": "记录数", "值": result["metrics"]["records"]},
            {"指标": "识别字段数", "值": result["metrics"]["recognized_fields"]},
            {"指标": "合计金额", "值": result["metrics"]["total_amount"]},
            {"指标": "净额", "值": result["metrics"]["net_amount"]},
            {"指标": "问题数", "值": result["metrics"]["issue_count"]},
            {"指标": "数据可信度评分", "值": result["metrics"]["trust_score"]},
            {"指标": "数据可信度等级", "值": result["metrics"]["trust_level"]},
        ])
        metrics_df.to_excel(writer, sheet_name="经营指标", index=False)
        template_df = pd.DataFrame([
            {"项目": "模板名称", "内容": result["template"]["name"]},
            {"项目": "适合用户", "内容": result["template"]["for_who"]},
            {"项目": "输入", "内容": result["template"]["inputs"]},
            {"项目": "输出", "内容": result["template"]["outputs"]},
            {"项目": "预计节省时间", "内容": result["template"]["saving"]},
        ])
        template_df.to_excel(writer, sheet_name="模板说明", index=False)
        pd.DataFrame({"经营诊断": result["insights"]}).to_excel(writer, sheet_name="经营诊断", index=False)
    return output.getvalue()


def make_summary_text(result: Dict[str, Any]) -> str:
    metrics = result["metrics"]
    lines = [
        f"OrbiRetail 奥比零售云 - {result['template']['name']} 经营摘要",
        "",
        f"文件数：{metrics.get('file_count', 1)}",
        f"记录数：{metrics['records']}",
        f"合计金额：{fmt_money(metrics['total_amount'])}",
        f"净额：{fmt_money(metrics['net_amount'])}",
        f"数据可信度：{metrics['trust_score']} / 100（{metrics['trust_level']}）",
        f"问题数量：{metrics['issue_count']}",
        "",
        "经营诊断：",
    ]
    for item in result["insights"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("建议动作：")
    for action in result["actions"]:
        lines.append(f"- [{action['优先级']}] {action['建议动作']}：{action['说明']}")
    return "\n".join(lines)


def make_issue_list_csv(result: Dict[str, Any]) -> bytes:
    df = result["issues_df"]
    if df.empty:
        df = pd.DataFrame([{"级别": "INFO", "问题类型": "无明显问题", "问题详情": "当前未发现明显问题", "建议处理": "可以下载分析报告", "行号": "-"}])
    return df.to_csv(index=False).encode("utf-8-sig")


def make_template_guide_text(template: Dict[str, Any]) -> str:
    lines = [
        f"模板说明：{template['name']}",
        "",
        f"场景分类：{template['category']}",
        f"适合用户：{template['for_who']}",
        f"建议输入：{template['inputs']}",
        f"输出结果：{template['outputs']}",
        f"预计节省：{template['saving']}",
        "",
        "必需字段：",
    ]
    for field in template["required"]:
        aliases = "、".join(FIELD_ALIASES.get(field, []))
        lines.append(f"- {FIELD_LABELS.get(field, field)}：可识别列名示例：{aliases}")
    lines.append("")
    lines.append("建议流程：")
    for i, step in enumerate(template.get("sample_steps", []), 1):
        lines.append(f"{i}. {step}")
    return "\n".join(lines)


def make_report_package(result: Dict[str, Any]) -> bytes:
    buf = io.BytesIO()
    filename_stem = safe_filename(result["template"]["name"])
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"OrbiRetail_{filename_stem}_分析报告.xlsx", make_report_bytes(result))
        zf.writestr(f"OrbiRetail_{filename_stem}_问题清单.csv", make_issue_list_csv(result))
        zf.writestr(f"OrbiRetail_{filename_stem}_经营摘要.txt", make_summary_text(result).encode("utf-8"))
        zf.writestr(f"OrbiRetail_{filename_stem}_模板说明.txt", make_template_guide_text(result["template"]).encode("utf-8"))
        if result.get("file_logs"):
            zf.writestr("上传文件日志.csv", pd.DataFrame(result["file_logs"]).to_csv(index=False).encode("utf-8-sig"))
    return buf.getvalue()


def safe_filename(value: str) -> str:
    return re.sub(r"[^0-9A-Za-z\u4e00-\u9fff_-]+", "_", value)


# -----------------------------------------------------------------------------
# 样例数据
# -----------------------------------------------------------------------------
def build_demo_data(template: Dict[str, Any]) -> pd.DataFrame:
    today = dt.date.today()
    if template["id"] in ["retail_daily", "boss_daily", "platform_settlement"]:
        return pd.DataFrame({
            "日期": [today, today, today, today, today],
            "门店": ["上海人民广场店", "上海人民广场店", "杭州西湖店", "南京新街口店", "杭州西湖店"],
            "渠道": ["美团", "饿了么", "线下POS", "美团", "京东到家"],
            "订单号": ["A1001", "A1002", "A1003", "A1004", "A1005"],
            "实收金额": [1250.5, 980.0, 1530.0, 760.0, 1320.0],
            "退款金额": [0, 80, 0, 0, 120],
            "平台佣金": [85.0, 65.0, 0, 52.0, 75.0],
            "优惠金额": [35.0, 20.0, 10.0, 15.0, 30.0],
        })
    if template["id"] == "supplier_recon":
        return pd.DataFrame({
            "供应商": ["华东食品", "华东食品", "优鲜供应链", "城市饮品"],
            "订单号": ["PO1001", "PO1002", "PO1003", "PO1004"],
            "金额": [5200, 3100, 7800, 2200],
            "日期": [today, today, today, today],
        })
    if template["id"] == "monthly_expense":
        return pd.DataFrame({
            "部门": ["运营部", "财务部", "销售部", "行政部"],
            "月份": [today.strftime("%Y-%m")] * 4,
            "费用类别": ["差旅费", "办公费", "招待费", "房租水电"],
            "金额": [2300, 800, 4500, 12000],
        })
    if template["id"] == "sales_performance":
        return pd.DataFrame({
            "区域": ["华东", "华南", "华北", "华东"],
            "销售人员": ["张三", "李四", "王五", "赵六"],
            "产品": ["A商品", "B商品", "A商品", "C商品"],
            "销售额": [36000, 42000, 28000, 51000],
        })
    if template["id"] == "inventory_check":
        return pd.DataFrame({
            "门店": ["上海人民广场店", "杭州西湖店", "南京新街口店", "上海人民广场店"],
            "商品": ["A商品", "A商品", "B商品", "C商品"],
            "系统库存": [100, 80, 120, 60],
            "实际库存": [96, 82, 110, 60],
        })
    return pd.DataFrame({
        "部门": ["一店", "二店", "三店"],
        "员工": ["张三", "李四", "王五"],
        "月份": [today.strftime("%Y-%m")] * 3,
        "实发工资": [6800, 7200, 6500],
        "预计工资": [6800, 7000, 6500],
    })


def build_demo_batch(template: Dict[str, Any]) -> List[pd.DataFrame]:
    df = build_demo_data(template)
    if len(df) <= 2:
        return [df]
    mid = max(1, len(df) // 2)
    a = df.iloc[:mid].copy()
    b = df.iloc[mid:].copy()
    return [a, b]


# -----------------------------------------------------------------------------
# 反馈
# -----------------------------------------------------------------------------
def save_feedback(user: Dict[str, Any], payload: Dict[str, Any]) -> None:
    record = {
        "created_at": dt.datetime.now().isoformat(),
        "email": user.get("email", ""),
        "company": user.get("company", ""),
        **payload,
    }
    with FEEDBACK_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


# -----------------------------------------------------------------------------
# UI 组件
# -----------------------------------------------------------------------------
def render_login_page() -> None:
    st.markdown(
        """
        <div class="login-shell">
            <div class="login-brand">
                <div class="brand-mark"><div class="brand-dot">◉</div><span>OrbiRetail 奥比零售云</span></div>
                <h1>零售经营数据，一键汇总、对账、诊断。</h1>
                <div class="lead">
                    上传门店、渠道、财务 Excel，自动生成销售汇总、对账差异、利润分析和经营报告。
                    让门店、区域、财务和老板每天都能看清真正的经营结果。
                </div>
                <div class="orbi-pill-row">
                    <div class="orbi-pill">7 天免费试用</div>
                    <div class="orbi-pill">一键样例体验</div>
                    <div class="orbi-pill">批量上传</div>
                    <div class="orbi-pill">报告包下载</div>
                    <div class="orbi-pill">经营诊断摘要</div>
                </div>
                <div class="login-kpis">
                    <div class="login-kpi"><strong>8</strong><span>核心业务场景模板</span></div>
                    <div class="login-kpi"><strong>1分钟</strong><span>样例数据快速体验</span></div>
                    <div class="login-kpi"><strong>4步</strong><span>首次成功路径</span></div>
                </div>
            </div>
            <div class="login-form-card">
                <h2 style="margin:0 0 8px 0; letter-spacing:-.03em;">进入经营数据工作台</h2>
                <p class="orbi-muted">注册即开通 7 天试用。建议先用样例数据体验完整流程，再上传自己的 Excel。</p>
        """,
        unsafe_allow_html=True,
    )
    tab_login, tab_register = st.tabs(["登录", "注册 7 天试用"])
    with tab_login:
        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("邮箱", placeholder="name@company.com")
            password = st.text_input("密码", type="password", placeholder="请输入密码")
            submitted = st.form_submit_button("登录工作台", use_container_width=True)
        if submitted:
            ok, user, msg = authenticate(email, password)
            if ok and user:
                st.session_state["auth"] = True
                st.session_state["user"] = user
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
    with tab_register:
        with st.form("register_form", clear_on_submit=False):
            company = st.text_input("公司 / 门店名称", placeholder="例如：小作坊零售 / 华东一区")
            email = st.text_input("注册邮箱", placeholder="name@company.com")
            password = st.text_input("设置密码", type="password", placeholder="至少 6 位")
            submitted = st.form_submit_button("注册并直接进入工作台", use_container_width=True)
        if submitted:
            ok, user, msg = register_user(email, password, company)
            if ok and user:
                st.session_state["auth"] = True
                st.session_state["user"] = user
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
    st.markdown(
        """
                <div style="margin-top:22px; padding:14px 16px; border-radius:16px; background:#f8fafc; border:1px solid #e2e8f0;">
                    <div style="font-weight:700; color:#0f172a; margin-bottom:4px;">首次体验建议</div>
                    <div class="orbi-small">注册后点击“启动样例体验”，不用准备文件，也能看到字段识别、经营指标、问题清单和报告包下载。</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_top_hero(user: Dict[str, Any]) -> None:
    days = trial_days_left(user)
    st.markdown(
        f"""
        <div class="orbi-hero">
            <h1>经营数据分析工作台</h1>
            <p>选择场景模板，上传一个或多个 Excel / CSV，系统自动完成字段识别、数据汇总、异常提示、经营诊断和报告包下载。</p>
            <div class="orbi-pill-row">
                <div class="orbi-pill">账号：{user['email']}</div>
                <div class="orbi-pill">公司：{user.get('company','')}</div>
                <div class="orbi-pill">套餐：{user.get('plan','Trial')}</div>
                <div class="orbi-pill">试用剩余：{days} 天</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_first_success_path(has_template: bool, has_data: bool, has_result: bool) -> None:
    st.markdown("<div class='orbi-section-title'>首次成功路径</div>", unsafe_allow_html=True)
    progress = int(sum([has_template, has_data, has_result, has_result]) / 4 * 100)
    st.progress(progress / 100, text=f"当前完成度：{progress}%")
    cols = st.columns(4)
    steps = [
        ("1", "选择场景", "从模板中心选择业务问题", has_template),
        ("2", "样例或上传", "先体验样例，或上传自己的文件", has_data),
        ("3", "查看诊断", "确认经营指标和可信度", has_result),
        ("4", "下载报告", "下载问题清单或报告包", has_result),
    ]
    for col, (num, title, desc, ok) in zip(cols, steps):
        with col:
            status = "✅ 已完成" if ok else "⏳ 待完成"
            st.markdown(
                f"""
                <div class="step-card">
                    <div><span class="step-num">{num}</span><b>{title}</b></div>
                    <div class="orbi-muted" style="margin-top:10px;">{desc}</div>
                    <div class="orbi-small" style="margin-top:12px;">{status}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_template_center() -> None:
    st.markdown("<div class='orbi-section-title'>模板中心</div>", unsafe_allow_html=True)
    st.markdown("<div class='orbi-section-subtitle'>选择业务场景后，系统会按对应字段、指标和输出口径进行分析。</div>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 2])
    with c1:
        selected_category = st.selectbox("场景分类", CATEGORIES, index=0)
    with c2:
        keyword = st.text_input("搜索模板", placeholder="例如：门店、对账、库存、工资、销售")
    filtered = []
    for template in TEMPLATES:
        if selected_category != "全部" and template["category"] != selected_category:
            continue
        if keyword.strip():
            text = " ".join(str(template.get(k, "")) for k in ["name", "category", "tagline", "for_who", "inputs", "outputs"])
            if keyword.strip().lower() not in text.lower():
                continue
        filtered.append(template)
    if not filtered:
        st.warning("没有匹配的模板，请换一个关键词。")
        return
    for i in range(0, len(filtered), 4):
        cols = st.columns(4)
        for col, template in zip(cols, filtered[i : i + 4]):
            with col:
                st.markdown(
                    f"""
                    <div class="template-card">
                        <div class="icon">{template['icon']}</div>
                        <div class="name">{template['name']}</div>
                        <div class="tag">{template['category']}</div>
                        <div class="desc">{template['tagline']}</div>
                        <div class="orbi-small">适合：{template['for_who']}</div>
                        <div class="output">输出：{template['outputs']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("选择此模板", key=f"select_{template['id']}", use_container_width=True):
                    st.session_state["selected_template"] = template
                    st.session_state["analysis_result"] = None
                    st.success(f"已选择：{template['name']}")
                    st.rerun()


def render_template_details(template: Dict[str, Any]) -> None:
    st.markdown("<div class='orbi-section-title'>模板说明页</div>", unsafe_allow_html=True)
    tabs = st.tabs(["模板价值", "字段要求", "样例流程", "输出说明"])
    with tabs[0]:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"<div class='orbi-card'><h4>{template['icon']} {template['name']}</h4><div class='orbi-muted'>{template['tagline']}</div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='orbi-card'><h4>适合用户</h4><div class='orbi-muted'>{template['for_who']}</div></div>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<div class='orbi-card'><h4>需要上传</h4><div class='orbi-muted'>{template['inputs']}</div></div>", unsafe_allow_html=True)
        with c4:
            st.markdown(f"<div class='orbi-card'><h4>预计节省</h4><div class='orbi-muted'>{template['saving']}</div></div>", unsafe_allow_html=True)
    with tabs[1]:
        rows = []
        for field in template["required"]:
            rows.append({"必需字段": FIELD_LABELS.get(field, field), "可识别表头示例": "、".join(FIELD_ALIASES.get(field, []))})
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    with tabs[2]:
        for i, step in enumerate(template.get("sample_steps", []), 1):
            st.info(f"{i}. {step}")
    with tabs[3]:
        st.markdown(f"**输出结果：** {template['outputs']}")
        st.markdown("系统会生成：Excel 分析报告、问题清单、经营摘要、模板说明和报告包 ZIP。")


def render_metrics(result: Dict[str, Any]) -> None:
    metrics = result["metrics"]
    st.markdown("<div class='orbi-section-title'>经营指标卡片</div>", unsafe_allow_html=True)
    cols = st.columns(6)
    cards = [
        ("文件数", f"{metrics.get('file_count', 1):,}", "本次读取的文件数量"),
        ("记录数", f"{metrics['records']:,}", "已读取的业务明细行数"),
        ("合计金额", fmt_money(metrics["total_amount"]), "原始金额口径"),
        ("净额", fmt_money(metrics["net_amount"]), "扣除退款/佣金/优惠后的口径"),
        ("问题数", f"{metrics['issue_count']:,}", "字段、空值、金额、重复等异常"),
        ("数据可信度", f"{metrics['trust_score']} / 100", metrics["trust_level"]),
    ]
    for col, (label, value, note) in zip(cols, cards):
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-note">{note}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_diagnosis_summary(result: Dict[str, Any]) -> None:
    st.markdown("### 经营诊断摘要")
    for insight in result["insights"]:
        st.markdown(f"<div class='diagnosis-box'><div class='diagnosis-title'>诊断</div><div class='diagnosis-desc'>{insight}</div></div>", unsafe_allow_html=True)
    st.markdown("### 建议动作")
    for action in result["actions"]:
        st.markdown(f"<div class='diagnosis-box'><div class='diagnosis-title'>{action['优先级']} · {action['建议动作']}</div><div class='diagnosis-desc'>{action['说明']}</div></div>", unsafe_allow_html=True)


def render_analysis_workspace(template: Dict[str, Any]) -> None:
    st.markdown("<div class='orbi-section-title'>上传与分析</div>", unsafe_allow_html=True)
    st.markdown("<div class='orbi-section-subtitle'>支持批量上传 .xlsx / .csv。第一行为表头。没有文件时，先用样例数据体验完整流程。</div>", unsafe_allow_html=True)

    c1, c2 = st.columns([2, 1])
    with c1:
        uploaded_files = st.file_uploader("批量上传 Excel / CSV 文件", type=["xlsx", "csv"], accept_multiple_files=True)
    with c2:
        demo = st.button("启动样例数据体验", use_container_width=True)
        demo_batch = st.button("启动批量样例体验", use_container_width=True)

    df: Optional[pd.DataFrame] = None
    source_name = ""
    file_logs: List[Dict[str, Any]] = []

    if demo:
        df = build_demo_data(template)
        df["来源文件"] = f"{template['name']}_样例数据.xlsx"
        source_name = f"{template['name']}_样例数据.xlsx"
        file_logs = [{"文件名": source_name, "状态": "成功", "行数": len(df), "列数": len(df.columns)}]
        st.session_state["demo_started"] = True
        st.info("已生成样例数据，可直接查看分析结果。")
    elif demo_batch:
        frames = []
        for idx, frame in enumerate(build_demo_batch(template), 1):
            name = f"{template['name']}_样例文件{idx}.xlsx"
            frame = frame.copy()
            frame["来源文件"] = name
            frames.append(frame)
            file_logs.append({"文件名": name, "状态": "成功", "行数": len(frame), "列数": len(frame.columns)})
        df = pd.concat(frames, ignore_index=True, sort=False)
        source_name = "批量样例数据"
        st.session_state["demo_started"] = True
        st.info("已生成批量样例数据，可体验多文件合并分析。")
    elif uploaded_files:
        df, file_logs = read_uploaded_files(uploaded_files)
        source_name = f"{len(uploaded_files)} 个上传文件"

    if df is None:
        st.info("请选择模板并上传文件，或点击“启动样例数据体验”。")
        return
    if df.empty:
        st.warning("文件中没有有效数据。")
        return

    result = analyze_dataframe(df, template, file_logs=file_logs)
    result["source_name"] = source_name
    st.session_state["analysis_result"] = result
    st.success(f"已完成分析：{source_name}")

    render_metrics(result)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["上传日志", "字段识别", "汇总结果", "经营诊断摘要", "问题清单", "报告下载"])
    with tab1:
        st.markdown("### 上传文件日志")
        st.dataframe(pd.DataFrame(file_logs), use_container_width=True)
        st.dataframe(df.head(50), use_container_width=True)
    with tab2:
        st.markdown("### 上传后字段识别")
        st.dataframe(result["field_df"], use_container_width=True)
        missing_required = [f for f in template["required"] if not result["mapping"].get(f)]
        if missing_required:
            st.warning("当前模板缺少以下必需字段：" + "、".join(FIELD_LABELS.get(f, f) for f in missing_required))
        else:
            st.success("模板必需字段已识别完整。")
    with tab3:
        st.markdown("### 汇总结果")
        st.dataframe(result["summary"], use_container_width=True)
    with tab4:
        render_diagnosis_summary(result)
        score = result["metrics"]["trust_score"]
        level = result["metrics"]["trust_level"]
        st.markdown(f"### 数据可信度评分：{score} / 100（{level}）")
        st.dataframe(result["trust_details"], use_container_width=True)
    with tab5:
        st.markdown("### 问题清单")
        if result["issues_df"].empty:
            st.success("没有发现明显字段、金额或重复异常。")
        else:
            st.dataframe(result["issues_df"], use_container_width=True)
        st.download_button(
            "下载问题清单 CSV",
            data=make_issue_list_csv(result),
            file_name=f"OrbiRetail_{safe_filename(template['name'])}_问题清单.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with tab6:
        st.markdown("### 报告下载区")
        report_bytes = make_report_bytes(result)
        text_report = make_summary_text(result)
        issue_csv = make_issue_list_csv(result)
        package_bytes = make_report_package(result)
        filename_stem = safe_filename(template["name"])
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.download_button("下载 Excel 分析报告", data=report_bytes, file_name=f"OrbiRetail_{filename_stem}_分析报告.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        with c2:
            st.download_button("下载 经营摘要 TXT", data=text_report.encode("utf-8"), file_name=f"OrbiRetail_{filename_stem}_经营摘要.txt", mime="text/plain", use_container_width=True)
        with c3:
            st.download_button("下载问题清单 CSV", data=issue_csv, file_name=f"OrbiRetail_{filename_stem}_问题清单.csv", mime="text/csv", use_container_width=True)
        with c4:
            st.download_button("下载报告包 ZIP", data=package_bytes, file_name=f"OrbiRetail_{filename_stem}_报告包.zip", mime="application/zip", use_container_width=True)


def render_feedback(user: Dict[str, Any]) -> None:
    st.markdown("<div class='orbi-section-title'>用户反馈入口</div>", unsafe_allow_html=True)
    with st.expander("提交反馈 / 试用问题 / 功能建议", expanded=False):
        with st.form("feedback_form", clear_on_submit=True):
            feedback_type = st.selectbox("反馈类型", ["使用卡点", "模板建议", "数据结果问题", "界面体验", "付费意愿", "其他"])
            rating = st.slider("整体满意度", 1, 5, 4)
            contact = st.text_input("联系方式（可选）", placeholder="微信 / 手机 / 邮箱")
            content = st.text_area("反馈内容", placeholder="请描述你遇到的问题、希望新增的模板或愿意付费的场景。", height=120)
            submitted = st.form_submit_button("提交反馈", use_container_width=True)
        if submitted:
            if not content.strip():
                st.warning("请填写反馈内容。")
            else:
                save_feedback(user, {"反馈类型": feedback_type, "满意度": rating, "联系方式": contact, "反馈内容": content})
                st.success("反馈已记录。后续可用于优化模板、界面和收费版本。")


def render_workspace() -> None:
    user = st.session_state["user"]
    render_top_hero(user)

    template = st.session_state.get("selected_template") or TEMPLATES[0]
    st.session_state["selected_template"] = template
    has_result = bool(st.session_state.get("analysis_result"))
    render_first_success_path(has_template=True, has_data=bool(st.session_state.get("demo_started") or has_result), has_result=has_result)

    render_template_center()
    template = st.session_state.get("selected_template") or TEMPLATES[0]
    render_template_details(template)
    render_analysis_workspace(template)
    render_feedback(user)

    st.markdown("---")
    c1, c2, c3 = st.columns([1, 1, 4])
    with c1:
        if st.button("退出登录", use_container_width=True):
            logout()
    with c2:
        st.caption(f"{APP_VERSION}")


def main() -> None:
    if "auth" not in st.session_state:
        st.session_state["auth"] = False
    if not st.session_state.get("auth"):
        render_login_page()
        return
    user = st.session_state.get("user")
    if not user:
        logout()
        return
    if not is_trial_active(user):
        st.error("你的 7 天试用已结束。请升级正式版后继续使用。")
        st.info("正式版将支持更多文件量、团队账号、正式数据库和报告包功能。")
        if st.button("退出登录"):
            logout()
        return
    render_workspace()


if __name__ == "__main__":
    main()
