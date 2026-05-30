# -*- coding: utf-8 -*-
"""
OrbiRetail 奥比零售云 - Batch 44 AI Agent 真实大模型接入 + 教育智能化增强

新增：
1. 支付系统雏形
2. 团队账号
3. 角色权限
4. 正式数据库雏形（SQLite，生产建议 PostgreSQL）
5. 企业私有化说明与部署文件下载
6. API 接入雏形
7. 手机端报告查看
"""
from __future__ import annotations

import base64
import datetime as dt
import hashlib
import hmac
import io
import json
import os
import re
import math
import secrets
import sqlite3
import textwrap
import zipfile
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st

APP_NAME = "OrbiRetail 奥比零售云"
APP_VERSION = "Batch 44 AI Agent 真实大模型接入 + 教育智能化增强"
TRIAL_DAYS = 10
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "saas_data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = Path(os.getenv("ORBIRETAIL_DB_PATH", DATA_DIR / "orbiretail.db"))
CONTACT_EMAIL = "2790569814@qq.com"
MEMBER_PRICE_MONTH = 19
MEMBER_PRICE_YEAR = 199

# -----------------------------------------------------------------------------
# Streamlit page
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="OrbiRetail 奥比零售云",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# -----------------------------------------------------------------------------
# CSS
# -----------------------------------------------------------------------------
def inject_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --orbi-navy: #0f172a;
            --orbi-blue: #2563eb;
            --orbi-cyan: #14b8a6;
            --orbi-muted: #64748b;
            --orbi-border: #e2e8f0;
            --orbi-bg: #f8fafc;
            --orbi-card: rgba(255,255,255,.90);
        }
        .stApp {
            background:
                radial-gradient(circle at 8% 8%, rgba(37,99,235,.11), transparent 26%),
                radial-gradient(circle at 92% 4%, rgba(20,184,166,.14), transparent 22%),
                linear-gradient(180deg, #f8fafc 0%, #eef4ff 45%, #f8fafc 100%);
            color: var(--orbi-navy);
        }
        div[data-testid="stHeader"] {
            background: rgba(248,250,252,.70);
            backdrop-filter: blur(18px);
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 4rem;
            max-width: 1380px;
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
            font-size: clamp(32px, 5vw, 52px);
            line-height: 1.08;
            margin: 0 0 16px 0;
            letter-spacing: -.045em;
            color: #fff;
        }
        .orbi-hero p {
            font-size: 17px;
            opacity: .92;
            margin: 0;
            max-width: 920px;
        }
        .orbi-pill-row { display:flex; gap:10px; flex-wrap:wrap; margin-top:24px; }
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
            background: rgba(255,255,255,.92);
            backdrop-filter: blur(16px);
            border-radius: 22px;
            padding: 22px;
            box-shadow: 0 14px 34px rgba(15,23,42,.08);
            height: 100%;
        }
        .orbi-card h3, .orbi-card h4 { margin-top: 0; color: #0f172a; }
        .orbi-muted { color: #64748b; font-size: 14px; line-height: 1.65; }
        .orbi-small { color: #64748b; font-size: 12.5px; line-height: 1.55; }
        .orbi-section-title {
            margin: 18px 0 10px 0;
            font-size: 24px;
            font-weight: 850;
            letter-spacing: -.035em;
            color: #0f172a;
        }
        .orbi-section-subtitle { margin: -4px 0 18px 0; color: #64748b; font-size: 15px; }
        .template-card {
            border: 1px solid #e2e8f0;
            border-radius: 20px;
            background: #fff;
            padding: 18px;
            min-height: 250px;
            box-shadow: 0 10px 24px rgba(15,23,42,.055);
        }
        .template-card .icon { font-size: 28px; margin-bottom: 8px; }
        .template-card .name { font-size: 18px; font-weight: 850; color: #0f172a; margin-bottom: 6px; }
        .template-card .tag {
            display: inline-block;
            font-size: 12px;
            padding: 4px 9px;
            border-radius: 999px;
            background: #eff6ff;
            color: #1d4ed8;
            margin-bottom: 10px;
        }
        .metric-card {
            border-radius: 22px;
            padding: 20px 20px 18px 20px;
            background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
            border: 1px solid #e2e8f0;
            box-shadow: 0 12px 28px rgba(15,23,42,.07);
            height: 100%;
        }
        .metric-label { color: #64748b; font-size: 13px; margin-bottom: 10px; }
        .metric-value { color: #0f172a; font-size: 28px; font-weight: 900; letter-spacing: -.04em; }
        .trust-good { color: #047857; font-weight: 900; }
        .trust-mid { color: #b45309; font-weight: 900; }
        .trust-bad { color: #b91c1c; font-weight: 900; }
        .notice-box {
            border-radius: 20px;
            padding: 18px 20px;
            background: linear-gradient(135deg, #eff6ff 0%, #ecfeff 100%);
            border: 1px solid #bfdbfe;
            color: #0f172a;
        }
        .success-box {
            border-radius: 20px;
            padding: 18px 20px;
            background: linear-gradient(135deg, #ecfdf5 0%, #f0fdfa 100%);
            border: 1px solid #a7f3d0;
            color: #064e3b;
        }
        .danger-box {
            border-radius: 20px;
            padding: 18px 20px;
            background: linear-gradient(135deg, #fef2f2 0%, #fff7ed 100%);
            border: 1px solid #fecaca;
            color: #7f1d1d;
        }
        .topbar {
            border-radius: 20px;
            padding: 14px 18px;
            background: rgba(255,255,255,.92);
            border: 1px solid #e2e8f0;
            box-shadow: 0 12px 28px rgba(15,23,42,.05);
        }
        .role-badge {
            display:inline-block;
            padding: 4px 9px;
            border-radius:999px;
            background:#eff6ff;
            color:#1d4ed8;
            font-size:12px;
            font-weight:800;
        }
        .plan-badge {
            display:inline-block;
            padding: 4px 9px;
            border-radius:999px;
            background:#ecfdf5;
            color:#047857;
            font-size:12px;
            font-weight:800;
        }
        .contact-strip {
            border-radius: 18px;
            padding: 14px 18px;
            margin: 14px 0 18px 0;
            background: linear-gradient(135deg, #fff7ed 0%, #eff6ff 100%);
            border: 1px solid #fed7aa;
            color: #0f172a;
            box-shadow: 0 10px 24px rgba(15,23,42,.055);
        }
        .contact-strip b { color:#1d4ed8; }
        .admin-table-note { font-size:12px; color:#64748b; margin-top:6px; }
        .mobile-report-card {
            border-radius: 22px;
            padding: 20px;
            background: #fff;
            border: 1px solid #e2e8f0;
            box-shadow: 0 16px 32px rgba(15,23,42,.08);
            margin-bottom: 14px;
        }
        @media (max-width: 768px) {
            .orbi-hero { padding: 28px 24px; border-radius: 22px; }
            .orbi-hero h1 { font-size: 31px; }
            .block-container { padding-left: 1rem; padding-right: 1rem; }
            .metric-value { font-size: 24px; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# Database
# -----------------------------------------------------------------------------
def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def now_iso() -> str:
    return dt.datetime.now().replace(microsecond=0).isoformat()


def today_iso() -> str:
    return dt.date.today().isoformat()


def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return digest, salt


def verify_password(password: str, digest: str, salt: str) -> bool:
    new_digest, _ = hash_password(password, salt)
    return hmac.compare_digest(new_digest, digest)


def init_db() -> None:
    conn = db()
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            plan TEXT NOT NULL DEFAULT 'trial',
            trial_start TEXT NOT NULL,
            trial_end TEXT NOT NULL,
            subscription_status TEXT NOT NULL DEFAULT 'trialing',
            subscription_end TEXT,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'admin',
            status TEXT NOT NULL DEFAULT 'active',
            created_at TEXT NOT NULL,
            FOREIGN KEY(company_id) REFERENCES companies(id)
        );
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS payment_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            plan TEXT NOT NULL,
            billing_cycle TEXT NOT NULL,
            payment_method TEXT NOT NULL,
            amount INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL,
            paid_at TEXT,
            note TEXT,
            FOREIGN KEY(company_id) REFERENCES companies(id)
        );
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            token_hash TEXT NOT NULL,
            token_preview TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            created_at TEXT NOT NULL,
            last_used_at TEXT,
            FOREIGN KEY(company_id) REFERENCES companies(id)
        );
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            template_id TEXT NOT NULL,
            template_name TEXT NOT NULL,
            report_title TEXT NOT NULL,
            trust_score INTEGER NOT NULL,
            total_rows INTEGER NOT NULL,
            total_amount REAL NOT NULL,
            net_amount REAL NOT NULL,
            issue_count INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            summary_json TEXT NOT NULL,
            FOREIGN KEY(company_id) REFERENCES companies(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(company_id) REFERENCES companies(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS payment_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payment_request_id INTEGER,
            provider TEXT NOT NULL,
            event_type TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            verify_status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL,
            FOREIGN KEY(payment_request_id) REFERENCES payment_requests(id)
        );
        CREATE TABLE IF NOT EXISTS db_migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'planned',
            applied_at TEXT,
            note TEXT
        );
        CREATE TABLE IF NOT EXISTS admin_audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            target_type TEXT,
            target_id TEXT,
            detail TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS assignment_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            student_name TEXT NOT NULL,
            assignment_title TEXT NOT NULL,
            assignment_type TEXT NOT NULL,
            score REAL NOT NULL,
            level TEXT NOT NULL,
            similarity_flag TEXT NOT NULL DEFAULT '正常',
            praise_or_warning TEXT,
            created_at TEXT NOT NULL,
            feedback_json TEXT NOT NULL,
            FOREIGN KEY(company_id) REFERENCES companies(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        """
    )
    conn.commit()
    conn.close()


init_db()


# -----------------------------------------------------------------------------
# Commercial plans and roles
# -----------------------------------------------------------------------------
PLANS: Dict[str, Dict[str, Any]] = {
    "free": {
        "name": "免费版",
        "price_month": 0,
        "price_year": 0,
        "stores": 1,
        "members": 1,
        "files_per_run": 3,
        "api": False,
        "private_deploy": False,
        "desc": "长期免费，适合样例体验、单门店轻量汇总和基础报告下载。",
    },
    "member": {
        "name": "会员版",
        "price_month": MEMBER_PRICE_MONTH,
        "price_year": MEMBER_PRICE_YEAR,
        "stores": 20,
        "members": 10,
        "files_per_run": 100,
        "api": True,
        "private_deploy": True,
        "desc": "高性价比会员，开放批量上传、全部模板、报告包、团队协作、API 接入和私有化资料。",
    },
    # 兼容旧版本数据库中的套餐值，统一映射为会员能力。
    "trial": {
        "name": "会员版试用",
        "price_month": 0,
        "price_year": 0,
        "stores": 20,
        "members": 10,
        "files_per_run": 100,
        "api": True,
        "private_deploy": True,
        "desc": "注册后 10 天会员能力体验，到期后可继续使用免费版或升级会员版。",
    },
    "standard": {
        "name": "会员版",
        "price_month": MEMBER_PRICE_MONTH,
        "price_year": MEMBER_PRICE_YEAR,
        "stores": 20,
        "members": 10,
        "files_per_run": 100,
        "api": True,
        "private_deploy": True,
        "desc": "兼容旧标准版，已合并为会员版。",
    },
    "professional": {
        "name": "会员版",
        "price_month": MEMBER_PRICE_MONTH,
        "price_year": MEMBER_PRICE_YEAR,
        "stores": 20,
        "members": 10,
        "files_per_run": 100,
        "api": True,
        "private_deploy": True,
        "desc": "兼容旧专业版，已合并为会员版。",
    },
    "enterprise": {
        "name": "会员版",
        "price_month": MEMBER_PRICE_MONTH,
        "price_year": MEMBER_PRICE_YEAR,
        "stores": 20,
        "members": 10,
        "files_per_run": 100,
        "api": True,
        "private_deploy": True,
        "desc": "兼容旧企业版，已合并为会员版。",
    },
}

PUBLIC_PLANS = ["free", "member"]
PAYMENT_PROVIDERS = ["微信支付", "支付宝", "Stripe", "企业转账"]
PAYMENT_WEBHOOKS = {
    "微信支付": "/payment/webhook/wechat",
    "支付宝": "/payment/webhook/alipay",
    "Stripe": "/payment/webhook/stripe",
    "企业转账": "/payment/manual/transfer",
}

ROLES: Dict[str, Dict[str, Any]] = {
    "admin": {
        "name": "管理员",
        "permissions": ["analyze", "download", "team", "billing", "api", "private", "feedback", "mobile"],
        "desc": "管理企业账号、成员、套餐、API 和全部报告。",
    },
    "finance": {
        "name": "财务",
        "permissions": ["analyze", "download", "feedback", "mobile"],
        "desc": "可上传对账数据、查看财务报告、下载问题清单。",
    },
    "operations": {
        "name": "运营",
        "permissions": ["analyze", "download", "feedback", "mobile"],
        "desc": "可分析门店、销售、库存和渠道数据。",
    },
    "owner": {
        "name": "老板/管理层",
        "permissions": ["download", "feedback", "mobile"],
        "desc": "只看老板报告、经营摘要和手机端看板。",
    },
    "analyst": {
        "name": "分析员",
        "permissions": ["analyze", "download", "feedback", "mobile"],
        "desc": "可做数据分析和报告导出，无成员和账单权限。",
    },
}


def role_name(role: str) -> str:
    return ROLES.get(role, {}).get("name", role)


def has_perm(user: sqlite3.Row, permission: str) -> bool:
    return permission in ROLES.get(user["role"], {}).get("permissions", [])


# -----------------------------------------------------------------------------
# Templates
# -----------------------------------------------------------------------------
TEMPLATES: List[Dict[str, Any]] = [
    {
        "id": "retail_daily",
        "name": "门店 / 渠道销售日报",
        "category": "零售经营",
        "icon": "🏪",
        "target": "门店运营、区域经理、财务结算",
        "input": "门店销售日报、渠道结算日报、退款明细、佣金表",
        "output": "销售汇总、渠道差异、退款冲销、经营诊断",
        "save_time": "每日 30-90 分钟",
        "required": ["日期", "门店", "渠道", "金额"],
        "group_by": ["日期", "门店", "渠道"],
        "desc": "适合每天汇总各门店、各平台渠道销售数据，自动检查退款、佣金和优惠字段。",
    },
    {
        "id": "ecommerce_after_sales",
        "name": "电商退款 / 售后工单汇总",
        "category": "互联网电商",
        "icon": "🛒",
        "target": "电商运营、客服主管、店铺负责人、售后团队",
        "input": "售后工单、退款明细、退换货明细、赔付记录、客服处理记录",
        "output": "退换货趋势、退款原因分布、商品售后表现、客服处理效率、高风险工单、优化建议",
        "save_time": "每周 2-8 小时",
        "required": ["订单号", "商品", "售后类型", "退款原因", "处理状态", "退款金额"],
        "group_by": ["渠道", "店铺", "退款原因", "售后类型"],
        "desc": "面向互联网电商公司，自动汇总退换货、退款和售后工单，识别高风险商品、异常退款原因和客服处理效率问题。",
    },
    {
        "id": "higher_education_career",
        "name": "高校教务 / 实习 / 就业数据汇总",
        "category": "高校教育",
        "icon": "🎓",
        "target": "高校院系、教务办、就业办、学生工作办公室、实习管理老师",
        "input": "学生基础信息、实习记录、就业去向、岗位薪资、行业地区、未就业跟进表",
        "output": "实习单位汇总、就业去向统计、专业/班级就业率、岗位行业分布、薪资区间、未就业学生清单、院系汇总报告",
        "save_time": "每学期 4-12 小时",
        "required": ["学院", "专业", "班级", "姓名", "就业状态"],
        "group_by": ["学院", "专业", "班级", "就业状态"],
        "desc": "面向高校院系和就业管理场景，自动汇总学生实习、就业去向、行业岗位、薪资区间和未就业学生清单，并生成院系汇总报告。",
    },
    {
        "id": "boss_daily",
        "name": "老板经营日报",
        "category": "零售经营",
        "icon": "📌",
        "target": "老板、总经理、区域负责人",
        "input": "销售日报、成本表、渠道结算数据",
        "output": "收入、净额、异常门店、建议动作",
        "save_time": "每日 20-60 分钟",
        "required": ["日期", "门店", "金额"],
        "group_by": ["日期", "门店"],
        "desc": "把复杂 Excel 转成老板能直接看的经营摘要，突出异常和下一步动作。",
    },
    {
        "id": "platform_settlement",
        "name": "平台结算对账",
        "category": "财务对账",
        "icon": "💳",
        "target": "财务、渠道运营",
        "input": "门店订单、平台结算单、银行流水",
        "output": "未结算订单、结算差异、手续费差异",
        "save_time": "每周 2-4 小时",
        "required": ["日期", "渠道", "订单号", "金额"],
        "group_by": ["日期", "渠道"],
        "desc": "适合检查平台结算金额与门店订单金额是否一致。",
    },
    {
        "id": "supplier_recon",
        "name": "供应商对账",
        "category": "财务对账",
        "icon": "🧾",
        "target": "财务、采购、门店后勤",
        "input": "采购订单、入库单、发票、付款记录",
        "output": "匹配项、金额不一致、仅订单存在、付款差异",
        "save_time": "每月 3-8 小时",
        "required": ["供应商", "订单号", "金额"],
        "group_by": ["供应商"],
        "desc": "适合供应商月结、采购核对和发票差异检查。",
    },
    {
        "id": "expense_monthly",
        "name": "月度费用汇总",
        "category": "财务对账",
        "icon": "💰",
        "target": "财务、行政、部门助理",
        "input": "部门费用表、员工报销表、项目费用表",
        "output": "费用汇总、异常金额、重复报销、部门排名",
        "save_time": "每月 2-6 小时",
        "required": ["部门", "类别", "金额"],
        "group_by": ["部门", "类别"],
        "desc": "适合把多部门费用表自动合并，并输出问题清单。",
    },
    {
        "id": "sales_performance",
        "name": "销售业绩分析",
        "category": "销售运营",
        "icon": "📈",
        "target": "销售运营、区域经理、销售主管",
        "input": "销售明细、销售人员表、区域表、产品表",
        "output": "销售排名、区域排名、产品排名、趋势摘要",
        "save_time": "每周 1-3 小时",
        "required": ["销售人员", "区域", "金额"],
        "group_by": ["区域", "销售人员"],
        "desc": "适合快速生成销售人员、区域和产品维度的业绩分析。",
    },
    {
        "id": "inventory_check",
        "name": "库存盘点差异",
        "category": "库存供应链",
        "icon": "📦",
        "target": "库存、门店、供应链负责人",
        "input": "系统库存、实际盘点表、出入库记录",
        "output": "盘盈、盘亏、异常商品、差异金额",
        "save_time": "每次盘点 2-5 小时",
        "required": ["商品", "系统库存", "盘点库存"],
        "group_by": ["商品"],
        "desc": "适合门店盘点后快速识别库存差异和差异金额。",
    },
    {
        "id": "payroll_check",
        "name": "考勤工资核对",
        "category": "人事行政",
        "icon": "👥",
        "target": "人事、行政、薪酬专员",
        "input": "考勤表、请假表、工资表",
        "output": "应发差异、缺勤异常、请假异常、工资核对表",
        "save_time": "每月 2-5 小时",
        "required": ["员工", "月份", "工资"],
        "group_by": ["员工", "月份"],
        "desc": "适合核对考勤、请假和工资发放数据。",
    },
]

FIELD_ALIASES: Dict[str, List[str]] = {
    "日期": ["日期", "销售日期", "下单时间", "支付时间", "结算日期", "date", "Date"],
    "月份": ["月份", "月", "统计月份", "期间", "Month"],
    "门店": ["门店", "店铺", "门店名称", "店名", "Store", "store"],
    "区域": ["区域", "大区", "城市", "Region"],
    "渠道": ["渠道", "平台", "销售渠道", "来源平台", "店铺平台", "电商平台", "Channel"],
    "店铺": ["店铺", "店铺名称", "网店", "电商店铺", "门店", "Store", "Shop"],
    "订单号": ["订单号", "单号", "交易号", "业务单号", "售后单号", "工单号", "OrderID", "order_id", "TicketID"],
    "金额": ["金额", "销售额", "实收金额", "结算金额", "付款金额", "费用金额", "应发工资", "工资", "Amount", "amount"],
    "退款金额": ["退款金额", "退款", "退货金额", "退款费用", "售后金额", "Refund", "refund_amount"],
    "赔付金额": ["赔付金额", "赔偿金额", "补偿金额", "赔付", "Compensation"],
    "售后类型": ["售后类型", "工单类型", "退换货类型", "服务类型", "类型", "TicketType"],
    "退款原因": ["退款原因", "退货原因", "售后原因", "投诉原因", "原因", "Reason"],
    "处理状态": ["处理状态", "工单状态", "售后状态", "状态", "Status"],
    "响应时长": ["响应时长", "首次响应时长", "响应小时", "响应时间", "ResponseHours"],
    "处理时长": ["处理时长", "完成时长", "处理小时", "完结时长", "CloseHours"],
    "客服": ["客服", "客服人员", "处理人", "负责人", "Agent"],
    "平台佣金": ["平台佣金", "佣金", "服务费", "手续费", "Commission"],
    "优惠金额": ["优惠金额", "折扣金额", "平台补贴", "优惠券", "Discount"],
    "供应商": ["供应商", "供应商名称", "Vendor", "Supplier"],
    "部门": ["部门", "部门名称", "所属部门", "Dept"],
    "类别": ["类别", "费用类别", "分类", "项目类别", "Category"],
    "销售人员": ["销售人员", "销售", "业务员", "Sales"],
    "商品": ["商品", "商品名称", "产品", "SKU", "Product"],
    "系统库存": ["系统库存", "账面库存", "库存数量", "SystemStock"],
    "盘点库存": ["盘点库存", "实际库存", "实盘数量", "CountedStock"],
    "员工": ["员工", "员工姓名", "姓名", "Employee"],
    "工资": ["工资", "应发工资", "实发工资", "Salary"],
    "学院": ["学院", "院系", "二级学院", "所属学院", "学院名称", "College", "Faculty"],
    "专业": ["专业", "专业名称", "培养专业", "Major"],
    "班级": ["班级", "班级名称", "行政班", "Class"],
    "学号": ["学号", "学生编号", "StudentID", "student_id"],
    "姓名": ["姓名", "学生", "学生姓名", "Name", "StudentName"],
    "实习单位": ["实习单位", "实习企业", "实习公司", "单位名称", "Employer", "Company"],
    "就业单位": ["就业单位", "签约单位", "录用单位", "工作单位", "Employer"],
    "就业状态": ["就业状态", "去向", "毕业去向", "就业去向", "是否就业", "状态", "EmploymentStatus"],
    "岗位": ["岗位", "职位", "岗位名称", "Job", "Position"],
    "行业": ["行业", "所属行业", "就业行业", "Industry"],
    "薪资": ["薪资", "月薪", "薪酬", "税前薪资", "实习薪资", "Salary"],
    "地区": ["地区", "城市", "就业地区", "工作地点", "Region", "City"],
    "升学单位": ["升学单位", "升学院校", "读研学校", "录取院校"],
}


# -----------------------------------------------------------------------------
# Auth and company helpers
# -----------------------------------------------------------------------------
def create_company_and_user(company: str, email: str, password: str) -> Optional[str]:
    conn = db()
    cur = conn.cursor()
    existing = cur.execute("SELECT id FROM users WHERE email=?", (email.strip().lower(),)).fetchone()
    if existing:
        conn.close()
        return "该邮箱已注册。"
    start = dt.datetime.now()
    end = start + dt.timedelta(days=TRIAL_DAYS)
    cur.execute(
        "INSERT INTO companies(name, plan, trial_start, trial_end, subscription_status, created_at) VALUES(?,?,?,?,?,?)",
        (company.strip() or "未命名企业", "member", start.isoformat(), end.isoformat(), "trialing", now_iso()),
    )
    company_id = cur.lastrowid
    digest, salt = hash_password(password)
    cur.execute(
        "INSERT INTO users(company_id,email,password_hash,salt,role,status,created_at) VALUES(?,?,?,?,?,?,?)",
        (company_id, email.strip().lower(), digest, salt, "admin", "active", now_iso()),
    )
    conn.commit()
    conn.close()
    return None


def login_user(email: str, password: str) -> Tuple[Optional[str], Optional[str]]:
    conn = db()
    row = conn.execute("SELECT * FROM users WHERE email=? AND status='active'", (email.strip().lower(),)).fetchone()
    if not row:
        conn.close()
        return None, "邮箱或密码错误。"
    if not verify_password(password, row["password_hash"], row["salt"]):
        conn.close()
        return None, "邮箱或密码错误。"
    token = secrets.token_urlsafe(32)
    expires = (dt.datetime.now() + dt.timedelta(days=30)).isoformat()
    conn.execute(
        "INSERT INTO sessions(token,user_id,created_at,expires_at) VALUES(?,?,?,?)",
        (token, row["id"], now_iso(), expires),
    )
    conn.commit()
    conn.close()
    return token, None


def get_query_token() -> Optional[str]:
    try:
        token = st.query_params.get("token")
        if isinstance(token, list):
            return token[0] if token else None
        return token
    except Exception:
        try:
            params = st.experimental_get_query_params()
            token = params.get("token", [None])[0]
            return token
        except Exception:
            return None


def set_query_token(token: str) -> None:
    try:
        st.query_params["token"] = token
    except Exception:
        try:
            st.experimental_set_query_params(token=token)
        except Exception:
            pass


def clear_query_token() -> None:
    try:
        if "token" in st.query_params:
            del st.query_params["token"]
    except Exception:
        try:
            st.experimental_set_query_params()
        except Exception:
            pass


def get_current_context() -> Tuple[Optional[sqlite3.Row], Optional[sqlite3.Row]]:
    token = st.session_state.get("token") or get_query_token()
    if not token:
        return None, None
    conn = db()
    sess = conn.execute("SELECT * FROM sessions WHERE token=?", (token,)).fetchone()
    if not sess:
        conn.close()
        return None, None
    if dt.datetime.fromisoformat(sess["expires_at"]) < dt.datetime.now():
        conn.execute("DELETE FROM sessions WHERE token=?", (token,))
        conn.commit()
        conn.close()
        return None, None
    user = conn.execute("SELECT * FROM users WHERE id=? AND status='active'", (sess["user_id"],)).fetchone()
    if not user:
        conn.close()
        return None, None
    company = conn.execute("SELECT * FROM companies WHERE id=?", (user["company_id"],)).fetchone()
    conn.close()
    st.session_state["token"] = token
    return user, company


def trial_days_left(company: sqlite3.Row) -> int:
    if company["subscription_status"] == "active":
        return 9999
    end = dt.datetime.fromisoformat(company["trial_end"])
    return max(0, (end.date() - dt.date.today()).days)


def company_access_allowed(company: sqlite3.Row) -> bool:
    # Batch 40：试用到期后不再一刀切阻断。用户仍可使用免费版能力，
    # 这样更符合“产品先有用、价格高性价比”的策略。
    return True


def current_plan(company: sqlite3.Row) -> Dict[str, Any]:
    if company["subscription_status"] == "active":
        return PLANS.get(company["plan"], PLANS["member"])
    if company["subscription_status"] == "trialing" and trial_days_left(company) > 0:
        return PLANS["trial"]
    return PLANS["free"]


# -----------------------------------------------------------------------------
# Analysis helpers
# -----------------------------------------------------------------------------
def find_field(columns: List[str], standard: str) -> Optional[str]:
    normalized = {str(c).strip().lower(): c for c in columns}
    for alias in FIELD_ALIASES.get(standard, [standard]):
        key = str(alias).strip().lower()
        if key in normalized:
            return normalized[key]
    for c in columns:
        c_str = str(c).strip().lower()
        for alias in FIELD_ALIASES.get(standard, [standard]):
            alias_l = str(alias).strip().lower()
            if alias_l and alias_l in c_str:
                return c
    return None


def to_number(series: pd.Series) -> pd.Series:
    if series is None:
        return pd.Series(dtype="float64")
    cleaned = series.astype(str).str.replace(",", "", regex=False).str.replace("￥", "", regex=False).str.replace("元", "", regex=False)
    return pd.to_numeric(cleaned, errors="coerce").fillna(0)


def sample_dataframe(template: Dict[str, Any], batch: bool = False) -> pd.DataFrame:
    base_dates = pd.date_range(dt.date.today() - dt.timedelta(days=6), periods=7, freq="D")
    rows: List[Dict[str, Any]] = []
    if template["id"] == "ecommerce_after_sales":
        shops = ["天猫旗舰店", "抖音小店", "京东自营店"]
        channels = ["天猫", "抖音", "京东"]
        products = ["无线耳机A1", "智能手表S2", "保温杯B3", "运动鞋K9", "充电宝P6"]
        reasons = ["质量问题", "尺码/规格不符", "物流破损", "七天无理由", "描述不符"]
        statuses = ["已完结", "处理中", "待买家补充", "已关闭"]
        types = ["仅退款", "退货退款", "换货", "赔付"]
        agents = ["小陈", "小王", "小李", "小周"]
        for i, day in enumerate(base_dates):
            for j, shop in enumerate(shops):
                product = products[(i + j) % len(products)]
                reason = reasons[(i + 2*j) % len(reasons)]
                status = statuses[(i + j) % len(statuses)]
                refund = 89 + i * 13 + j * 37
                close_hours = 6 + (i % 4) * 8 + j * 3
                rows.append({
                    "申请日期": day.date().isoformat(),
                    "店铺": shop,
                    "渠道": channels[j],
                    "订单号": f"EC{i:02d}{j:02d}{1000+i*j}",
                    "商品": product,
                    "售后类型": types[(i + j) % len(types)],
                    "退款原因": reason,
                    "处理状态": status,
                    "退款金额": refund,
                    "赔付金额": 20 if types[(i + j) % len(types)] == "赔付" else 0,
                    "响应时长": 1 + (i + j) % 6,
                    "处理时长": close_hours,
                    "客服": agents[(i + j) % len(agents)],
                    "备注": "样例数据"
                })
        # 加入两条有问题的样例，帮助用户看到问题清单价值
        rows.append({"申请日期": base_dates[-1].date().isoformat(), "店铺": "抖音小店", "渠道": "抖音", "订单号": "EC-RISK-001", "商品": "无线耳机A1", "售后类型": "退货退款", "退款原因": "", "处理状态": "处理中", "退款金额": 1280, "赔付金额": 0, "响应时长": 15, "处理时长": 78, "客服": "小陈", "备注": "高金额且超时"})
        rows.append({"申请日期": base_dates[-1].date().isoformat(), "店铺": "京东自营店", "渠道": "京东", "订单号": "", "商品": "智能手表S2", "售后类型": "仅退款", "退款原因": "描述不符", "处理状态": "", "退款金额": "abc", "赔付金额": 0, "响应时长": 2, "处理时长": 8, "客服": "小李", "备注": "字段异常"})
    elif template["id"] == "higher_education_career":
        colleges = ["信息工程学院", "经济管理学院", "智能制造学院"]
        majors = ["软件工程", "电子商务", "机械设计制造"]
        classes = ["2026届1班", "2026届2班"]
        statuses = ["已就业", "已就业", "升学", "待就业", "自由职业", "实习中"]
        industries = ["互联网", "教育培训", "智能制造", "金融服务", "跨境电商"]
        regions = ["杭州", "上海", "深圳", "南京", "洛阳"]
        jobs = ["数据运营", "软件开发", "产品助理", "教务运营", "电商运营", "机械工程师"]
        companies = ["星云科技", "洛阳智造", "云杉教育", "河洛电商", "蓝海数据"]
        idx = 0
        for ci, college in enumerate(colleges):
            for mi, major in enumerate(majors):
                for cls in classes:
                    for n in range(5 if batch else 3):
                        status = statuses[(idx + ci + mi + n) % len(statuses)]
                        salary = 0 if status in ["待就业", "升学"] else 4200 + (idx % 9) * 650
                        rows.append({
                            "学院": college,
                            "专业": major,
                            "班级": cls,
                            "学号": f"2026{ci}{mi}{n:03d}",
                            "姓名": f"学生{idx+1:03d}",
                            "实习单位": companies[(idx+n) % len(companies)],
                            "就业单位": "" if status in ["待就业", "升学"] else companies[(idx+1) % len(companies)],
                            "就业状态": status,
                            "岗位": jobs[(idx+n) % len(jobs)],
                            "行业": industries[(idx+mi) % len(industries)],
                            "薪资": salary,
                            "地区": regions[(idx+ci) % len(regions)],
                            "备注": "样例数据"
                        })
                        idx += 1
        rows.append({"学院": "信息工程学院", "专业": "软件工程", "班级": "2026届1班", "学号": "", "姓名": "学生异常A", "实习单位": "", "就业单位": "", "就业状态": "待就业", "岗位": "", "行业": "", "薪资": 0, "地区": "", "备注": "缺少学号与实习单位"})
    elif template["id"] in {"retail_daily", "boss_daily", "platform_settlement"}:
        stores = ["上海人民广场店", "杭州西湖店", "南京新街口店"]
        channels = ["美团", "饿了么", "线下POS"]
        for i, day in enumerate(base_dates):
            for store in stores:
                for channel in channels:
                    amount = 3600 + i * 180 + len(store) * 12 + len(channel) * 35
                    rows.append({
                        "日期": day.date().isoformat(),
                        "门店": store,
                        "渠道": channel,
                        "订单号": f"ORD{i}{stores.index(store)}{channels.index(channel)}",
                        "金额": amount,
                        "退款金额": 80 if channel == "美团" and i % 3 == 0 else 0,
                        "平台佣金": round(amount * (0.055 if channel != "线下POS" else 0.012), 2),
                        "优惠金额": 120 if channel == "饿了么" and i % 2 == 0 else 30,
                    })
    elif template["id"] == "supplier_recon":
        suppliers = ["星河食品", "华东包装", "新鲜冷链"]
        for i, supplier in enumerate(suppliers * (3 if batch else 2)):
            rows.append({"供应商": supplier, "订单号": f"PO-2026-{1000+i}", "金额": 8000 + i * 650, "类别": "采购", "日期": today_iso()})
    elif template["id"] == "expense_monthly":
        depts = ["销售部", "运营部", "财务部", "行政部"]
        cats = ["差旅费", "办公费", "招待费"]
        for i, dept in enumerate(depts):
            for cat in cats:
                rows.append({"部门": dept, "类别": cat, "金额": 1200 + i * 350 + len(cat) * 80, "月份": dt.date.today().strftime("%Y-%m")})
    elif template["id"] == "sales_performance":
        names = ["李雷", "韩梅梅", "王强", "赵敏"]
        regions = ["华东", "华南"]
        for i, name in enumerate(names):
            for region in regions:
                rows.append({"销售人员": name, "区域": region, "金额": 28000 + i * 4200 + len(region) * 500, "月份": dt.date.today().strftime("%Y-%m")})
    elif template["id"] == "inventory_check":
        products = ["招牌套餐", "儿童套餐", "咖啡", "果汁", "纸袋"]
        for i, product in enumerate(products):
            rows.append({"商品": product, "系统库存": 500 - i * 35, "盘点库存": 492 - i * 30, "金额": 1000 + i * 120})
    elif template["id"] == "payroll_check":
        employees = ["张三", "李四", "王五", "赵六"]
        for i, emp in enumerate(employees):
            rows.append({"员工": emp, "月份": dt.date.today().strftime("%Y-%m"), "工资": 7800 + i * 500, "部门": "门店运营"})
    df = pd.DataFrame(rows)
    if batch:
        df2 = df.copy()
        if "来源文件" not in df.columns:
            df["来源文件"] = "样例文件A.xlsx"
            df2["来源文件"] = "样例文件B.xlsx"
        return pd.concat([df, df2], ignore_index=True)
    return df


def detect_fields(df: pd.DataFrame, template: Dict[str, Any]) -> pd.DataFrame:
    rows = []
    for std in sorted(set(template.get("required", []) + template.get("group_by", []) + list(FIELD_ALIASES.keys()))):
        found = find_field(list(df.columns), std)
        if found:
            status = "已识别"
        elif std in template.get("required", []):
            status = "缺失必需字段"
        else:
            status = "未识别"
        rows.append({"标准字段": std, "识别到的原始列": found or "", "状态": status})
    return pd.DataFrame(rows)


def analyze_ecommerce_after_sales(df: pd.DataFrame, template: Dict[str, Any]) -> Dict[str, Any]:
    """电商退换货 / 售后工单专用分析。保持返回结构与通用分析一致。"""
    if df.empty:
        raise ValueError("上传文件没有可分析的数据。")
    cols = list(df.columns)
    field_map = {std: find_field(cols, std) for std in FIELD_ALIASES.keys()}
    required_missing = [f for f in template.get("required", []) if not find_field(cols, f)]
    issues: List[Dict[str, Any]] = []
    for field in required_missing:
        issues.append({"级别": "ERROR", "问题类型": "缺少必需字段", "问题详情": f"缺少字段：{field}", "建议处理": "检查平台导出列名，或在字段字典中增加别名。", "行号": "", "来源文件": ""})

    df_clean = df.copy()
    refund_col = field_map.get("退款金额")
    comp_col = field_map.get("赔付金额")
    response_col = field_map.get("响应时长")
    close_col = field_map.get("处理时长")
    status_col = field_map.get("处理状态")
    reason_col = field_map.get("退款原因")
    order_col = field_map.get("订单号")
    product_col = field_map.get("商品")
    channel_col = field_map.get("渠道")
    shop_col = field_map.get("店铺") or field_map.get("门店")
    type_col = field_map.get("售后类型")
    agent_col = field_map.get("客服")

    df_clean["__refund"] = to_number(df_clean[refund_col]) if refund_col else 0
    df_clean["__compensation"] = to_number(df_clean[comp_col]) if comp_col else 0
    df_clean["__after_sales_amount"] = df_clean["__refund"] + df_clean["__compensation"]
    df_clean["__response_hours"] = to_number(df_clean[response_col]) if response_col else 0
    df_clean["__close_hours"] = to_number(df_clean[close_col]) if close_col else 0
    if status_col:
        status_text = df_clean[status_col].astype(str)
        df_clean["__is_closed"] = status_text.str.contains("完结|完成|关闭|已关闭|已完结", regex=True)
    else:
        df_clean["__is_closed"] = False

    for idx, row in df_clean.iterrows():
        line_no = int(idx) + 2
        source_file = row.get("来源文件", "")
        for field in template.get("required", []):
            col = find_field(cols, field)
            if col and (pd.isna(row[col]) or str(row[col]).strip() == ""):
                issues.append({"级别": "WARNING", "问题类型": "必填值为空", "问题详情": f"字段 {field} 为空", "建议处理": "补齐后再统计，避免售后归因不准确。", "行号": line_no, "来源文件": source_file})
        if refund_col and pd.isna(pd.to_numeric(str(row.get(refund_col, "")).replace(",", "").replace("￥", ""), errors="coerce")):
            issues.append({"级别": "WARNING", "问题类型": "退款金额异常", "问题详情": f"退款金额无法解析：{row.get(refund_col)}", "建议处理": "请改为纯数字金额。", "行号": line_no, "来源文件": source_file})
        if float(row.get("__close_hours", 0) or 0) > 48 and not bool(row.get("__is_closed", False)):
            issues.append({"级别": "WARNING", "问题类型": "工单处理超时", "问题详情": "处理时长超过 48 小时且未完结", "建议处理": "优先跟进该工单，避免差评或平台处罚。", "行号": line_no, "来源文件": source_file})
        if float(row.get("__refund", 0) or 0) >= 1000:
            issues.append({"级别": "WARNING", "问题类型": "高金额退款", "问题详情": f"退款金额较高：{float(row.get('__refund',0)):,.2f}", "建议处理": "建议复核商品、原因和订单凭证。", "行号": line_no, "来源文件": source_file})
        if response_col and float(row.get("__response_hours", 0) or 0) > 12:
            issues.append({"级别": "WARNING", "问题类型": "首次响应慢", "问题详情": "首次响应时长超过 12 小时", "建议处理": "检查客服排班和自动回复策略。", "行号": line_no, "来源文件": source_file})

    group_cols = [c for c in [channel_col, shop_col, reason_col, type_col] if c]
    if group_cols:
        summary = df_clean.groupby(group_cols, dropna=False).agg(
            工单数=("__after_sales_amount", "count"),
            退款金额合计=("__refund", "sum"),
            赔付金额合计=("__compensation", "sum"),
            售后金额合计=("__after_sales_amount", "sum"),
            平均响应时长=("__response_hours", "mean"),
            平均处理时长=("__close_hours", "mean"),
            完结率=("__is_closed", "mean"),
        ).reset_index()
        summary["完结率"] = (summary["完结率"] * 100).round(2)
    else:
        summary = pd.DataFrame({
            "工单数": [len(df_clean)],
            "退款金额合计": [df_clean["__refund"].sum()],
            "赔付金额合计": [df_clean["__compensation"].sum()],
            "售后金额合计": [df_clean["__after_sales_amount"].sum()],
        })

    extra_sheets: Dict[str, pd.DataFrame] = {}
    if reason_col:
        extra_sheets["退款原因分布"] = df_clean.groupby(reason_col, dropna=False).agg(工单数=("__refund", "count"), 退款金额=("__refund", "sum"), 平均处理时长=("__close_hours", "mean")).reset_index().sort_values("工单数", ascending=False)
    if channel_col:
        extra_sheets["渠道售后汇总"] = df_clean.groupby(channel_col, dropna=False).agg(工单数=("__refund", "count"), 退款金额=("__refund", "sum"), 赔付金额=("__compensation", "sum"), 平均处理时长=("__close_hours", "mean")).reset_index().sort_values("退款金额", ascending=False)
    if product_col:
        extra_sheets["商品售后表现"] = df_clean.groupby(product_col, dropna=False).agg(工单数=("__refund", "count"), 退款金额=("__refund", "sum"), 高金额退款数=("__refund", lambda x: int((x >= 1000).sum()))).reset_index().sort_values("工单数", ascending=False)
    if agent_col:
        extra_sheets["客服工单效率"] = df_clean.groupby(agent_col, dropna=False).agg(工单数=("__refund", "count"), 平均响应时长=("__response_hours", "mean"), 平均处理时长=("__close_hours", "mean"), 完结率=("__is_closed", "mean")).reset_index()
        extra_sheets["客服工单效率"]["完结率"] = (extra_sheets["客服工单效率"]["完结率"] * 100).round(2)
    high_risk = df_clean[(df_clean["__refund"] >= 1000) | ((df_clean["__close_hours"] > 48) & (~df_clean["__is_closed"])) | (df_clean["__response_hours"] > 12)].copy()
    if not high_risk.empty:
        keep_cols = [c for c in [order_col, product_col, channel_col, shop_col, reason_col, status_col, refund_col, response_col, close_col, agent_col, "来源文件"] if c and c in high_risk.columns]
        extra_sheets["高风险工单"] = high_risk[keep_cols].head(500)

    issue_df = pd.DataFrame(issues) if issues else pd.DataFrame(columns=["级别", "问题类型", "问题详情", "建议处理", "行号", "来源文件"])
    field_df = detect_fields(df, template)
    total_refund = float(df_clean["__refund"].sum())
    total_comp = float(df_clean["__compensation"].sum())
    total_after_sales = float(df_clean["__after_sales_amount"].sum())
    close_rate = float(df_clean["__is_closed"].mean() * 100) if len(df_clean) else 0.0
    avg_close = float(df_clean["__close_hours"].mean()) if len(df_clean) else 0.0
    risk_count = len(high_risk)
    required_score = max(0, 100 - len(required_missing) * 20)
    issue_score = max(0, 100 - len(issue_df) * 2.5)
    close_score = 100 if avg_close <= 24 else 85 if avg_close <= 48 else 60
    trust_score = int(round(required_score * 0.42 + issue_score * 0.38 + close_score * 0.20))
    trust_level = "可信" if not required_missing and trust_score >= 82 else "需复核" if trust_score >= 65 else "不可直接使用"

    top_reason = "暂无"
    if reason_col and not df_clean.empty:
        try:
            top_reason = str(df_clean[reason_col].value_counts(dropna=False).index[0])
        except Exception:
            pass
    top_product = "暂无"
    if product_col and not df_clean.empty:
        try:
            top_product = str(df_clean[product_col].value_counts(dropna=False).index[0])
        except Exception:
            pass
    diagnosis = [
        f"本次共处理 {len(df_clean)} 条售后/退换货记录，退款金额 {total_refund:,.2f}，赔付金额 {total_comp:,.2f}。",
        f"工单完结率约 {close_rate:.2f}%，平均处理时长 {avg_close:.2f} 小时。",
        f"最高频退款原因是：{top_reason}；售后出现次数最多的商品是：{top_product}。",
        f"数据可信度为 {trust_score}/100，判断为：{trust_level}。",
    ]
    if risk_count:
        diagnosis.append(f"系统识别到 {risk_count} 条高风险工单，请优先处理高金额退款、超时未完结和响应慢问题。")
    else:
        diagnosis.append("未发现明显高风险售后工单，可进入常规复盘。")
    recommendations = [
        "先查看高风险工单，优先处理高金额退款和超时未完结工单。",
        "按退款原因分布定位商品质量、物流、描述不符等主要问题。",
        "按商品售后表现筛选高退货商品，联动商品、运营和客服团队复盘。",
        "按客服工单效率检查响应时长和处理时长，优化排班和SOP。",
    ]
    metrics = {
        "记录数": len(df_clean),
        "金额合计": total_after_sales,
        "净额": -total_after_sales,
        "问题数": len(issue_df),
        "数据可信度": trust_score,
        "可信等级": trust_level,
        "退款金额": total_refund,
        "赔付金额": total_comp,
        "完结率": round(close_rate, 2),
        "高风险工单": risk_count,
    }
    return {
        "template": template,
        "raw": df,
        "field_detection": field_df,
        "summary": summary,
        "issues": issue_df,
        "metrics": metrics,
        "diagnosis": diagnosis,
        "recommendations": recommendations,
        "extra_sheets": extra_sheets,
        "created_at": now_iso(),
    }


def _employment_positive(status: Any) -> bool:
    text = str(status).strip()
    return any(k in text for k in ["已就业", "签约", "升学", "创业", "自由职业", "实习中", "录用", "已落实"])


def analyze_higher_education_career(df: pd.DataFrame, template: Dict[str, Any]) -> Dict[str, Any]:
    """高校教务 / 实习 / 就业数据汇总专用分析。"""
    if df.empty:
        raise ValueError("上传文件没有可分析的数据。")
    cols = list(df.columns)
    field_map = {std: find_field(cols, std) for std in FIELD_ALIASES.keys()}
    required_missing = [f for f in template.get("required", []) if not find_field(cols, f)]
    issues: List[Dict[str, Any]] = []
    for field in required_missing:
        issues.append({"级别": "ERROR", "问题类型": "缺少必需字段", "问题详情": f"缺少字段：{field}", "建议处理": "请检查院系统计表列名，或在字段字典中补充别名。", "行号": "", "来源文件": ""})

    df_clean = df.copy()
    college_col = field_map.get("学院")
    major_col = field_map.get("专业")
    class_col = field_map.get("班级")
    name_col = field_map.get("姓名") or field_map.get("员工")
    sid_col = field_map.get("学号")
    internship_col = field_map.get("实习单位")
    employer_col = field_map.get("就业单位") or internship_col
    status_col = field_map.get("就业状态")
    job_col = field_map.get("岗位")
    industry_col = field_map.get("行业")
    salary_col = field_map.get("薪资") or field_map.get("工资")
    region_col = field_map.get("地区") or field_map.get("区域")

    if status_col:
        df_clean["__employed_flag"] = df_clean[status_col].apply(_employment_positive)
    else:
        df_clean["__employed_flag"] = False
    if salary_col:
        df_clean["__salary"] = to_number(df_clean[salary_col])
    else:
        df_clean["__salary"] = 0

    # 行级质检
    for idx, row in df_clean.iterrows():
        for field, col in [("学院", college_col), ("专业", major_col), ("班级", class_col), ("姓名", name_col), ("就业状态", status_col)]:
            if col and (pd.isna(row.get(col)) or str(row.get(col)).strip() == ""):
                issues.append({"级别": "WARNING", "问题类型": "高校关键字段为空", "问题详情": f"字段 {field} 为空", "建议处理": "补齐后再进入院系统计或就业率核算。", "行号": int(idx)+2, "来源文件": row.get("来源文件", "")})
        if sid_col and str(row.get(sid_col, "")).strip() == "":
            issues.append({"级别": "WARNING", "问题类型": "学号为空", "问题详情": "学号为空，可能影响学生追踪和去重。", "建议处理": "建议补充学号或学生唯一编号。", "行号": int(idx)+2, "来源文件": row.get("来源文件", "")})
        if status_col and str(row.get(status_col, "")).strip() in ["待就业", "未就业", "未落实"]:
            issues.append({"级别": "INFO", "问题类型": "未就业学生", "问题详情": f"学生 {row.get(name_col, '')} 当前状态为 {row.get(status_col, '')}", "建议处理": "纳入就业帮扶跟进名单。", "行号": int(idx)+2, "来源文件": row.get("来源文件", "")})

    # 汇总维度
    group_fields = [c for c in [college_col, major_col, class_col, status_col] if c]
    if group_fields:
        summary = df_clean.groupby(group_fields, dropna=False).agg(
            学生数=("__employed_flag", "count"),
            已落实人数=("__employed_flag", "sum"),
            平均薪资=("__salary", "mean"),
        ).reset_index()
        summary["就业落实率"] = (summary["已落实人数"] / summary["学生数"] * 100).round(2)
    else:
        summary = pd.DataFrame({"学生数": [len(df_clean)], "已落实人数": [int(df_clean["__employed_flag"].sum())]})
        summary["就业落实率"] = (summary["已落实人数"] / summary["学生数"] * 100).round(2)

    def safe_group(col: Optional[str], name: str) -> pd.DataFrame:
        if not col:
            return pd.DataFrame({name: [], "人数": []})
        return df_clean.groupby(col, dropna=False).size().reset_index(name="人数").rename(columns={col: name}).sort_values("人数", ascending=False)

    internship_summary = safe_group(internship_col, "实习单位")
    status_summary = safe_group(status_col, "就业去向")
    industry_summary = safe_group(industry_col, "行业")
    job_summary = safe_group(job_col, "岗位")
    region_summary = safe_group(region_col, "地区")

    # 专业 / 班级就业率
    rate_fields = [c for c in [college_col, major_col, class_col] if c]
    if rate_fields:
        employment_rate = df_clean.groupby(rate_fields, dropna=False).agg(
            学生数=("__employed_flag", "count"),
            已落实人数=("__employed_flag", "sum"),
            平均薪资=("__salary", "mean"),
        ).reset_index()
        employment_rate["就业落实率"] = (employment_rate["已落实人数"] / employment_rate["学生数"] * 100).round(2)
    else:
        employment_rate = summary.copy()

    # 薪资区间
    salary_bins = [-1, 0, 3000, 5000, 8000, 12000, 20000, 10**9]
    salary_labels = ["未填写/无薪资", "0-3000", "3000-5000", "5000-8000", "8000-12000", "12000-20000", "20000+"]
    df_clean["__salary_band"] = pd.cut(df_clean["__salary"], bins=salary_bins, labels=salary_labels)
    salary_band = df_clean.groupby("__salary_band", dropna=False).size().reset_index(name="人数").rename(columns={"__salary_band": "薪资区间"})

    # 未就业学生清单
    if status_col:
        unemployed_mask = df_clean[status_col].astype(str).str.contains("待就业|未就业|未落实", regex=True, na=False)
    else:
        unemployed_mask = pd.Series([False] * len(df_clean))
    cols_for_unemployed = [c for c in [college_col, major_col, class_col, sid_col, name_col, status_col, job_col, industry_col, region_col] if c]
    unemployed = df_clean.loc[unemployed_mask, cols_for_unemployed].copy() if cols_for_unemployed else pd.DataFrame()

    # 院系汇总报告
    if college_col:
        college_report = df_clean.groupby(college_col, dropna=False).agg(
            学生数=("__employed_flag", "count"),
            已落实人数=("__employed_flag", "sum"),
            平均薪资=("__salary", "mean"),
        ).reset_index().rename(columns={college_col: "学院"})
        college_report["就业落实率"] = (college_report["已落实人数"] / college_report["学生数"] * 100).round(2)
    else:
        college_report = pd.DataFrame()

    issue_df = pd.DataFrame(issues) if issues else pd.DataFrame(columns=["级别", "问题类型", "问题详情", "建议处理", "行号", "来源文件"])
    field_df = detect_fields(df, template)
    required_score = max(0, 100 - len(required_missing) * 20)
    issue_score = max(0, 100 - len(issue_df) * 2)
    trust_score = int(round(required_score * 0.55 + issue_score * 0.45))
    if required_missing:
        trust_level = "不可直接使用"
    elif trust_score >= 82:
        trust_level = "可信"
    elif trust_score >= 65:
        trust_level = "需复核"
    else:
        trust_level = "不可直接使用"

    total_students = len(df_clean)
    employed_count = int(df_clean["__employed_flag"].sum())
    employment_rate_total = round(employed_count / total_students * 100, 2) if total_students else 0
    avg_salary = float(df_clean.loc[df_clean["__salary"] > 0, "__salary"].mean()) if (df_clean["__salary"] > 0).any() else 0.0
    top_industry = industry_summary.iloc[0, 0] if not industry_summary.empty else "暂无"
    top_employer = internship_summary.iloc[0, 0] if not internship_summary.empty else "暂无"
    diagnosis = [
        f"本次共处理 {total_students} 名学生数据，就业/升学/实习等已落实人数 {employed_count}，总体落实率 {employment_rate_total}%。",
        f"平均薪资约 {avg_salary:,.2f} 元；样本最多的行业是：{top_industry}。",
        f"实习/就业单位出现频次最高的是：{top_employer}。",
        f"数据可信度为 {trust_score}/100，判断为：{trust_level}。",
    ]
    if len(unemployed) > 0:
        diagnosis.append(f"系统识别到 {len(unemployed)} 名待就业/未落实学生，建议纳入院系就业帮扶跟进。")
    recommendations = [
        "优先核对未就业学生清单，补充联系方式、求职意向和帮扶状态。",
        "按专业/班级就业落实率排序，定位需要重点跟进的班级。",
        "结合岗位和行业分布，调整实习基地和就业推荐方向。",
        "薪资区间统计适合作为就业质量分析参考，不建议单独作为教学质量评价依据。",
    ]
    metrics = {
        "记录数": total_students,
        "金额合计": avg_salary,
        "净额": employment_rate_total,
        "问题数": len(issue_df),
        "数据可信度": trust_score,
        "可信等级": trust_level,
        "就业落实率": employment_rate_total,
        "平均薪资": avg_salary,
    }
    return {
        "template": template,
        "raw": df,
        "field_detection": field_df,
        "summary": summary,
        "issues": issue_df,
        "metrics": metrics,
        "diagnosis": diagnosis,
        "recommendations": recommendations,
        "extra_sheets": {
            "实习单位汇总": internship_summary,
            "就业去向统计": status_summary,
            "专业班级就业率": employment_rate,
            "岗位行业分布": pd.concat([industry_summary.assign(类型="行业").rename(columns={"行业":"名称"}), job_summary.assign(类型="岗位").rename(columns={"岗位":"名称"})], ignore_index=True) if not job_summary.empty or not industry_summary.empty else pd.DataFrame(),
            "薪资区间统计": salary_band,
            "未就业学生清单": unemployed,
            "院系汇总报告": college_report,
            "地区分布": region_summary,
        },
        "created_at": now_iso(),
    }


def analyze_dataframe(df: pd.DataFrame, template: Dict[str, Any]) -> Dict[str, Any]:
    if template.get("id") == "higher_education_career":
        return analyze_higher_education_career(df, template)
    if template.get("id") == "ecommerce_after_sales":
        return analyze_ecommerce_after_sales(df, template)
    if df.empty:
        raise ValueError("上传文件没有可分析的数据。")
    field_map = {std: find_field(list(df.columns), std) for std in FIELD_ALIASES.keys()}
    required_missing = [f for f in template.get("required", []) if not find_field(list(df.columns), f)]
    issues: List[Dict[str, Any]] = []
    for field in required_missing:
        issues.append({"级别": "ERROR", "问题类型": "缺少必需字段", "问题详情": f"缺少字段：{field}", "建议处理": "检查列名或使用模板说明中的标准字段。", "行号": "", "来源文件": ""})
    amount_col = field_map.get("金额")
    refund_col = field_map.get("退款金额")
    commission_col = field_map.get("平台佣金")
    discount_col = field_map.get("优惠金额")
    df_clean = df.copy()
    if amount_col:
        df_clean["__amount"] = to_number(df_clean[amount_col])
    else:
        df_clean["__amount"] = 0
    df_clean["__refund"] = to_number(df_clean[refund_col]) if refund_col else 0
    df_clean["__commission"] = to_number(df_clean[commission_col]) if commission_col else 0
    df_clean["__discount"] = to_number(df_clean[discount_col]) if discount_col else 0
    df_clean["__net"] = df_clean["__amount"] - df_clean["__refund"] - df_clean["__commission"] - df_clean["__discount"]
    for idx, row in df_clean.iterrows():
        for field in template.get("required", []):
            col = find_field(list(df_clean.columns), field)
            if col and (pd.isna(row[col]) or str(row[col]).strip() == ""):
                issues.append({"级别": "WARNING", "问题类型": "必填值为空", "问题详情": f"字段 {field} 为空", "建议处理": "补齐后再复核。", "行号": int(idx) + 2, "来源文件": row.get("来源文件", "")})
        if amount_col and pd.isna(pd.to_numeric(str(row.get(amount_col, "")).replace(",", "").replace("￥", ""), errors="coerce")):
            issues.append({"级别": "WARNING", "问题类型": "金额格式异常", "问题详情": f"金额无法解析：{row.get(amount_col)}", "建议处理": "请改为纯数字金额。", "行号": int(idx) + 2, "来源文件": row.get("来源文件", "")})
    group_fields: List[str] = []
    for std in template.get("group_by", []):
        found = find_field(list(df_clean.columns), std)
        if found:
            group_fields.append(found)
    if group_fields:
        summary = df_clean.groupby(group_fields, dropna=False).agg(
            记录数=("__amount", "count"),
            金额合计=("__amount", "sum"),
            净额合计=("__net", "sum"),
            退款合计=("__refund", "sum"),
            佣金合计=("__commission", "sum"),
            优惠合计=("__discount", "sum"),
        ).reset_index()
    else:
        summary = pd.DataFrame({"记录数": [len(df_clean)], "金额合计": [df_clean["__amount"].sum()], "净额合计": [df_clean["__net"].sum()]})
    issue_df = pd.DataFrame(issues) if issues else pd.DataFrame(columns=["级别", "问题类型", "问题详情", "建议处理", "行号", "来源文件"])
    field_df = detect_fields(df, template)
    required_score = max(0, 100 - len(required_missing) * 22)
    issue_score = max(0, 100 - len(issue_df) * 3)
    amount_score = 100 if amount_col else 70
    trust_score = int(round(required_score * 0.45 + issue_score * 0.35 + amount_score * 0.20))
    if required_missing:
        trust_level = "不可直接使用"
    elif trust_score >= 82:
        trust_level = "可信"
    elif trust_score >= 65:
        trust_level = "需复核"
    else:
        trust_level = "不可直接使用"
    total_amount = float(df_clean["__amount"].sum())
    net_amount = float(df_clean["__net"].sum())
    top_line = "暂无分组结果"
    if not summary.empty and "净额合计" in summary.columns:
        top_row = summary.sort_values("净额合计", ascending=False).iloc[0].to_dict()
        dims = [str(top_row.get(f, "")) for f in group_fields if f in top_row]
        top_line = " / ".join([d for d in dims if d]) or "整体数据"
    diagnosis = [
        f"本次共处理 {len(df_clean)} 行数据，金额合计 {total_amount:,.2f}，净额 {net_amount:,.2f}。",
        f"数据可信度为 {trust_score}/100，判断为：{trust_level}。",
        f"当前净额最高的分组是：{top_line}。",
    ]
    if len(issue_df) > 0:
        diagnosis.append(f"系统发现 {len(issue_df)} 条问题，请优先下载问题清单并复核。")
    else:
        diagnosis.append("未发现明显字段缺失或金额异常，可以进入下一步经营复核。")
    recommendations = [
        "先核对问题清单中的缺失字段和金额异常。",
        "将分析报告发给财务或运营负责人复核。",
        "如果数据来自多个平台，建议启用平台结算对账模板。",
    ]
    metrics = {
        "记录数": len(df_clean),
        "金额合计": total_amount,
        "净额": net_amount,
        "问题数": len(issue_df),
        "数据可信度": trust_score,
        "可信等级": trust_level,
    }
    return {
        "template": template,
        "raw": df,
        "field_detection": field_df,
        "summary": summary,
        "issues": issue_df,
        "metrics": metrics,
        "diagnosis": diagnosis,
        "recommendations": recommendations,
        "created_at": now_iso(),
    }


def make_excel_report(result: Dict[str, Any]) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        result["raw"].to_excel(writer, index=False, sheet_name="原始数据")
        result["summary"].to_excel(writer, index=False, sheet_name="汇总结果")
        result["field_detection"].to_excel(writer, index=False, sheet_name="字段识别")
        result["issues"].to_excel(writer, index=False, sheet_name="问题清单")
        pd.DataFrame([result["metrics"]]).to_excel(writer, index=False, sheet_name="经营指标")
        pd.DataFrame({"经营诊断": result["diagnosis"]}).to_excel(writer, index=False, sheet_name="经营诊断")
        pd.DataFrame({"建议动作": result["recommendations"]}).to_excel(writer, index=False, sheet_name="建议动作")
        for sheet_name, extra_df in result.get("extra_sheets", {}).items():
            safe_name = str(sheet_name)[:31] or "专题分析"
            extra_df.to_excel(writer, index=False, sheet_name=safe_name)
        pd.DataFrame([{
            "模板": result["template"]["name"],
            "分类": result["template"]["category"],
            "适合用户": result["template"]["target"],
            "输入": result["template"]["input"],
            "输出": result["template"]["output"],
        }]).to_excel(writer, index=False, sheet_name="模板说明")
    return buffer.getvalue()


def make_issue_csv(result: Dict[str, Any]) -> bytes:
    return result["issues"].to_csv(index=False).encode("utf-8-sig")


def make_summary_text(result: Dict[str, Any]) -> bytes:
    lines = [
        f"OrbiRetail 奥比零售云 - 经营摘要",
        f"生成时间：{result['created_at']}",
        f"场景模板：{result['template']['name']}",
        "",
        "核心指标：",
    ]
    for k, v in result["metrics"].items():
        lines.append(f"- {k}: {v}")
    lines.append("\n经营诊断：")
    for item in result["diagnosis"]:
        lines.append(f"- {item}")
    lines.append("\n建议动作：")
    for item in result["recommendations"]:
        lines.append(f"- {item}")
    return "\n".join(lines).encode("utf-8")


def make_report_zip(result: Dict[str, Any]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("OrbiRetail_分析报告.xlsx", make_excel_report(result))
        z.writestr("问题清单.csv", make_issue_csv(result))
        z.writestr("经营摘要.txt", make_summary_text(result))
        z.writestr("模板说明.txt", f"{result['template']['name']}\n{result['template']['desc']}\n输入：{result['template']['input']}\n输出：{result['template']['output']}")
        if result.get("extra_sheets"):
            z.writestr("专题分析说明.txt", "本报告包含电商售后专题分析，如退款原因分布、渠道售后汇总、商品售后表现、客服工单效率和高风险工单。")
    return buf.getvalue()


def save_report_record(user: sqlite3.Row, company: sqlite3.Row, result: Dict[str, Any]) -> int:
    conn = db()
    cur = conn.cursor()
    metrics = result["metrics"]
    cur.execute(
        """INSERT INTO reports(company_id,user_id,template_id,template_name,report_title,trust_score,total_rows,total_amount,net_amount,issue_count,created_at,summary_json)
           VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            company["id"],
            user["id"],
            result["template"]["id"],
            result["template"]["name"],
            f"{result['template']['name']} - {today_iso()}",
            int(metrics["数据可信度"]),
            int(metrics["记录数"]),
            float(metrics["金额合计"]),
            float(metrics["净额"]),
            int(metrics["问题数"]),
            now_iso(),
            json.dumps({"metrics": metrics, "diagnosis": result["diagnosis"], "recommendations": result["recommendations"]}, ensure_ascii=False),
        ),
    )
    rid = cur.lastrowid
    conn.commit()
    conn.close()
    return rid


# -----------------------------------------------------------------------------
# Rendering helpers
# -----------------------------------------------------------------------------
def money(v: Any) -> str:
    try:
        return f"¥{float(v):,.2f}"
    except Exception:
        return str(v)


def render_metric_cards(metrics: Dict[str, Any]) -> None:
    cols = st.columns(5)
    items = [
        ("记录数", f"{metrics.get('记录数', 0):,}"),
        ("金额合计", money(metrics.get("金额合计", 0))),
        ("净额", money(metrics.get("净额", 0))),
        ("问题数", f"{metrics.get('问题数', 0):,}"),
        ("数据可信度", f"{metrics.get('数据可信度', 0)} / 100"),
    ]
    for col, (label, value) in zip(cols, items):
        with col:
            st.markdown(f"<div class='metric-card'><div class='metric-label'>{label}</div><div class='metric-value'>{value}</div></div>", unsafe_allow_html=True)


def render_topbar(user: sqlite3.Row, company: sqlite3.Row) -> None:
    plan = current_plan(company)
    left, mid, right = st.columns([2.2, 2.3, 1.0])
    with left:
        st.markdown(
            f"""
            <div class='topbar'>
            <b>{APP_NAME}</b><br>
            <span class='orbi-small'>{company['name']} · {user['email']}</span><br><span class='orbi-small'>遇到问题请联系：{CONTACT_EMAIL}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with mid:
        days = trial_days_left(company)
        trial_txt = "正式版" if company["subscription_status"] == "active" else f"试用剩余 {days} 天"
        st.markdown(
            f"""
            <div class='topbar'>
            <span class='plan-badge'>{plan['name']}</span>
            <span class='role-badge'>{role_name(user['role'])}</span>
            <span class='orbi-small'> {trial_txt}</span><br>
            <span class='orbi-small'>成员上限 {plan['members']} · 单次文件上限 {plan['files_per_run']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        if st.button("退出登录", key="logout_btn", use_container_width=True):
            st.session_state.pop("token", None)
            clear_query_token()
            st.rerun()


def selected_template() -> Dict[str, Any]:
    tid = st.session_state.get("selected_template_id", "retail_daily")
    return next((t for t in TEMPLATES if t["id"] == tid), TEMPLATES[0])


# -----------------------------------------------------------------------------
# Login page
# -----------------------------------------------------------------------------
def render_login_page() -> None:
    inject_css()
    left, right = st.columns([1.35, 0.9], gap="large")
    with left:
        st.markdown(
            """
            <div class='orbi-hero'>
                <h1>从经营数据到高校作业，用 AI 帮你把重复工作自动化。</h1>
                <p>上传门店、财务、电商售后、高校就业 Excel，自动完成汇总、对账、诊断和报告。新版新增高校教务/实习/就业数据汇总，以及 Word/PDF/ZIP 作业包 AI 批改能力。</p>
                <div class='orbi-pill-row'>
                    <span class='orbi-pill'>10 天会员能力试用</span>
                    <span class='orbi-pill'>免费版 + 低价会员版</span>
                    <span class='orbi-pill'>角色权限</span>
                    <span class='orbi-pill'>API 接入</span>
                    <span class='orbi-pill'>手机报告</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        a, b, c = st.columns(3)
        for col, title, text in [
            (a, "10 个场景", "新增高校就业与 AI 作业批改，覆盖零售、电商、财务、教育、库存、人事。"),
            (b, "1 分钟", "样例数据快速体验完整流程。"),
            (c, "高性价比", "免费版长期可用，会员版低价解锁完整能力。"),
        ]:
            with col:
                st.markdown(f"<div class='orbi-card'><h3>{title}</h3><div class='orbi-muted'>{text}</div></div>", unsafe_allow_html=True)
    with right:
        st.markdown("<div class='orbi-card'>", unsafe_allow_html=True)
        tab_login, tab_register = st.tabs(["登录", "注册 10 天试用"])
        with tab_login:
            email = st.text_input("邮箱", placeholder="name@company.com", key="login_email")
            password = st.text_input("密码", type="password", placeholder="请输入密码", key="login_password")
            if st.button("登录工作台", key="login_submit", use_container_width=True):
                token, err = login_user(email, password)
                if err:
                    st.error(err)
                else:
                    st.session_state["token"] = token
                    set_query_token(token)
                    st.success("登录成功，正在进入工作台。")
                    st.rerun()
        with tab_register:
            company = st.text_input("公司 / 门店名称", placeholder="例如：小作坊连锁", key="reg_company")
            email = st.text_input("注册邮箱", placeholder="name@company.com", key="reg_email")
            password = st.text_input("设置密码", type="password", placeholder="至少 6 位", key="reg_password")
            if st.button("注册并开启 10 天试用", key="reg_submit", use_container_width=True):
                if len(password) < 6:
                    st.error("密码至少 6 位。")
                elif "@" not in email:
                    st.error("请输入有效邮箱。")
                else:
                    err = create_company_and_user(company, email, password)
                    if err:
                        st.error(err)
                    else:
                        token, err2 = login_user(email, password)
                        if err2:
                            st.error(err2)
                        else:
                            st.session_state["token"] = token
                            set_query_token(token)
                            st.success("注册成功，已自动开通 10 天会员能力试用。")
                            st.rerun()
        st.markdown("<div class='orbi-small'>当前为商业版 MVP。遇到无法解决的问题，请联系：2790569814@qq.com。正式付费前建议接入真实支付回调和 PostgreSQL 数据库。</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Workspace pages
# -----------------------------------------------------------------------------
def render_template_picker() -> None:
    st.markdown("<div class='orbi-section-title'>选择业务场景模板</div>", unsafe_allow_html=True)
    categories = ["全部"] + sorted({t["category"] for t in TEMPLATES})
    c1, c2 = st.columns([1, 2])
    with c1:
        cat = st.selectbox("场景分类", categories, key="tpl_cat")
    with c2:
        kw = st.text_input("搜索模板", placeholder="例如：门店、对账、库存、工资", key="tpl_kw")
    filtered = []
    for t in TEMPLATES:
        hay = " ".join([t["name"], t["category"], t["target"], t["input"], t["output"], t["desc"]])
        if cat != "全部" and t["category"] != cat:
            continue
        if kw and kw.strip().lower() not in hay.lower():
            continue
        filtered.append(t)
    cols = st.columns(4)
    for i, t in enumerate(filtered):
        with cols[i % 4]:
            st.markdown(
                f"""
                <div class='template-card'>
                    <div class='icon'>{t['icon']}</div>
                    <div class='name'>{t['name']}</div>
                    <span class='tag'>{t['category']}</span>
                    <div class='orbi-muted'>{t['desc']}</div>
                    <div class='orbi-small'><b>输入：</b>{t['input']}</div>
                    <div class='orbi-small'><b>输出：</b>{t['output']}</div>
                    <div class='orbi-small'><b>预计节省：</b>{t['save_time']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("选择此模板", key=f"select_tpl_{t['id']}", use_container_width=True):
                st.session_state["selected_template_id"] = t["id"]
                st.success(f"已选择：{t['name']}")
                st.rerun()


def render_template_detail(template: Dict[str, Any]) -> None:
    with st.expander("模板说明页", expanded=False):
        st.markdown(f"### {template['icon']} {template['name']}")
        st.write(template["desc"])
        st.markdown(f"**适合用户：** {template['target']}")
        st.markdown(f"**建议输入：** {template['input']}")
        st.markdown(f"**输出结果：** {template['output']}")
        st.markdown("**必需字段：** " + "、".join(template.get("required", [])))
        st.markdown("**默认汇总维度：** " + "、".join(template.get("group_by", [])))


def read_uploaded_files(files: List[Any], max_files: int) -> Tuple[pd.DataFrame, pd.DataFrame]:
    logs: List[Dict[str, Any]] = []
    frames: List[pd.DataFrame] = []
    if len(files) > max_files:
        raise ValueError(f"当前套餐单次最多允许上传 {max_files} 个文件。")
    for f in files:
        try:
            if f.name.lower().endswith(".csv"):
                df = pd.read_csv(f)
            else:
                df = pd.read_excel(f)
            df["来源文件"] = f.name
            frames.append(df)
            logs.append({"文件名": f.name, "状态": "成功", "行数": len(df), "列数": len(df.columns), "错误信息": ""})
        except Exception as e:
            logs.append({"文件名": getattr(f, "name", "未知"), "状态": "失败", "行数": 0, "列数": 0, "错误信息": str(e)})
    if not frames:
        return pd.DataFrame(), pd.DataFrame(logs)
    return pd.concat(frames, ignore_index=True), pd.DataFrame(logs)


def render_result(user: sqlite3.Row, company: sqlite3.Row, result: Dict[str, Any]) -> None:
    metrics = result["metrics"]
    st.markdown("<div class='orbi-section-title'>分析结果</div>", unsafe_allow_html=True)
    render_metric_cards(metrics)
    score = int(metrics.get("数据可信度", 0))
    level = metrics.get("可信等级", "需复核")
    st.progress(max(0, min(score, 100)) / 100)
    css_class = "trust-good" if score >= 82 else "trust-mid" if score >= 65 else "trust-bad"
    st.markdown(f"<div class='notice-box'><b>数据可信度：</b><span class='{css_class}'>{score}/100 · {level}</span></div>", unsafe_allow_html=True)
    st.markdown("#### 经营诊断摘要")
    for item in result["diagnosis"]:
        st.markdown(f"- {item}")
    st.markdown("#### 建议动作")
    for item in result["recommendations"]:
        st.markdown(f"- {item}")
    t1, t2, t3, t4 = st.tabs(["汇总结果", "字段识别", "问题清单", "原始数据"])
    with t1:
        st.dataframe(result["summary"], use_container_width=True)
    with t2:
        st.dataframe(result["field_detection"], use_container_width=True)
    with t3:
        st.dataframe(result["issues"], use_container_width=True)
    with t4:
        st.dataframe(result["raw"].head(300), use_container_width=True)
    if result.get("extra_sheets"):
        st.markdown("#### 专题分析")
        for sheet_name, extra_df in result.get("extra_sheets", {}).items():
            with st.expander(sheet_name, expanded=False):
                st.dataframe(extra_df, use_container_width=True)
    st.markdown("<div class='orbi-section-title'>报告下载区</div>", unsafe_allow_html=True)
    filename_stem = f"OrbiRetail_{result['template']['id']}_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.download_button("下载 Excel 分析报告", data=make_excel_report(result), file_name=f"{filename_stem}_分析报告.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key=f"dl_excel_{filename_stem}", use_container_width=True)
    with c2:
        st.download_button("下载问题清单 CSV", data=make_issue_csv(result), file_name=f"{filename_stem}_问题清单.csv", mime="text/csv", key=f"dl_issue_{filename_stem}", use_container_width=True)
    with c3:
        st.download_button("下载经营摘要 TXT", data=make_summary_text(result), file_name=f"{filename_stem}_经营摘要.txt", mime="text/plain", key=f"dl_txt_{filename_stem}", use_container_width=True)
    with c4:
        st.download_button("下载报告包 ZIP", data=make_report_zip(result), file_name=f"{filename_stem}_报告包.zip", mime="application/zip", key=f"dl_zip_{filename_stem}", use_container_width=True)
    if "saved_report_id" not in result:
        rid = save_report_record(user, company, result)
        result["saved_report_id"] = rid
        st.session_state["analysis_result"] = result



# -----------------------------------------------------------------------------
# Batch 44: AI provider adapters and intelligent analysis helpers
# -----------------------------------------------------------------------------
AI_PROVIDER_DEFAULTS: Dict[str, Dict[str, str]] = {
    "openai": {
        "label": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",
        "key_env": "OPENAI_API_KEY",
    },
    "qwen": {
        "label": "通义千问 / 阿里云百炼",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-plus",
        "key_env": "DASHSCOPE_API_KEY",
    },
    "zhipu": {
        "label": "智谱 GLM",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "model": "glm-4-flash",
        "key_env": "ZHIPU_API_KEY",
    },
    "deepseek": {
        "label": "DeepSeek",
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-chat",
        "key_env": "DEEPSEEK_API_KEY",
    },
}


def _secret_or_env(name: str, default: str = "") -> str:
    """Read AI configuration from Streamlit secrets, session input, or environment."""
    try:
        value = st.secrets.get(name)  # type: ignore[attr-defined]
        if value:
            return str(value)
    except Exception:
        pass
    if st.session_state.get(name):
        return str(st.session_state.get(name))
    return os.getenv(name, default)


def get_ai_runtime_config() -> Dict[str, str]:
    provider = str(st.session_state.get("AI_PROVIDER", _secret_or_env("ORBI_AI_PROVIDER", "rules"))).lower().strip()
    if provider not in AI_PROVIDER_DEFAULTS:
        provider = "rules"
    if provider == "rules":
        return {"provider": "rules", "label": "本地规则模式", "base_url": "", "model": "", "api_key": ""}
    d = AI_PROVIDER_DEFAULTS[provider]
    api_key = _secret_or_env(d["key_env"], "")
    base_url = _secret_or_env(f"{provider.upper()}_BASE_URL", d["base_url"]).rstrip("/")
    model = _secret_or_env(f"{provider.upper()}_MODEL", d["model"])
    return {"provider": provider, "label": d["label"], "base_url": base_url, "model": model, "api_key": api_key}


def ai_provider_ready() -> bool:
    cfg = get_ai_runtime_config()
    return bool(cfg.get("provider") != "rules" and cfg.get("api_key"))


def call_chat_completion(system_prompt: str, user_prompt: str, temperature: float = 0.25, max_tokens: int = 900) -> Tuple[Optional[str], str]:
    """Call an OpenAI-compatible chat completion endpoint. Falls back safely when unconfigured."""
    cfg = get_ai_runtime_config()
    if cfg.get("provider") == "rules":
        return None, "当前为本地规则模式，未调用外部大模型。"
    if not cfg.get("api_key"):
        return None, f"未配置 {cfg.get('label')} API Key。请在 AI 智能中心临时输入，或在 Streamlit Secrets/环境变量中配置。"
    payload = {
        "model": cfg["model"],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    url = cfg["base_url"].rstrip("/") + "/chat/completions"
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {cfg['api_key']}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            raw = resp.read().decode("utf-8")
        obj = json.loads(raw)
        content = obj.get("choices", [{}])[0].get("message", {}).get("content")
        if not content:
            return None, "大模型返回为空，已改用本地规则结果。"
        return str(content).strip(), "ok"
    except urllib.error.HTTPError as exc:
        try:
            detail = exc.read().decode("utf-8")[:600]
        except Exception:
            detail = str(exc)
        return None, f"大模型接口 HTTP 错误：{exc.code}；{detail}"
    except Exception as exc:
        return None, f"大模型接口调用失败：{exc}"


def result_brief_for_ai(result: Optional[Dict[str, Any]], max_rows: int = 12) -> str:
    if not result:
        return "当前还没有分析结果。请先启动样例体验或上传数据进行分析。"
    lines = [
        f"场景模板：{result.get('template', {}).get('name', '')}",
        f"分类：{result.get('template', {}).get('category', '')}",
        "核心指标：" + json.dumps(result.get("metrics", {}), ensure_ascii=False),
        "经营诊断：" + "；".join(result.get("diagnosis", [])[:5]),
        "建议动作：" + "；".join(result.get("recommendations", [])[:5]),
    ]
    issues = result.get("issues")
    if isinstance(issues, pd.DataFrame) and not issues.empty:
        lines.append("问题清单样例：" + issues.head(max_rows).to_json(orient="records", force_ascii=False))
    summary = result.get("summary")
    if isinstance(summary, pd.DataFrame) and not summary.empty:
        lines.append("汇总样例：" + summary.head(max_rows).to_json(orient="records", force_ascii=False))
    return "\n".join(lines)


def fallback_business_insight(result: Optional[Dict[str, Any]]) -> str:
    if not result:
        return "请先运行一次样例体验或上传数据分析。AI 会基于已生成的经营指标、问题清单和汇总表给出分析。"
    m = result.get("metrics", {})
    trust = m.get("数据可信度", 0)
    issue_count = int(m.get("问题数", 0) or 0)
    net = float(m.get("净额", 0) or 0)
    total = float(m.get("金额合计", 0) or 0)
    level = m.get("可信等级", "需复核")
    parts = [
        f"当前数据可信度为 {trust}/100，系统判断为：{level}。",
        f"本次记录数 {m.get('记录数', 0)}，金额合计 {total:,.2f}，净额 {net:,.2f}。",
    ]
    if issue_count > 0:
        parts.append(f"系统发现 {issue_count} 条问题。建议先处理缺失字段、金额异常、状态缺失和高风险记录，再用于正式汇报。")
    else:
        parts.append("未发现明显字段或金额异常，可以作为初步经营分析依据。")
    if result.get("template", {}).get("id") == "ecommerce_after_sales":
        parts.append("电商售后场景建议重点关注：高退款商品、处理超时工单、退款原因集中度、客服响应时长和赔付金额。")
    elif result.get("template", {}).get("id") == "higher_education_career":
        parts.append("高校就业场景建议重点关注：未就业学生清单、专业/班级就业落实率、行业岗位匹配和薪资区间分布。")
    else:
        parts.append("建议下载报告包，与财务、运营或管理层共同复核后再进入下一步决策。")
    parts.append("未来趋势判断：当前为规则型预测，请结合历史周期数据继续验证。若后续连续录入多期数据，系统可生成更稳定的趋势判断。")
    return "\n".join(parts)


def generate_ai_business_analysis(result: Optional[Dict[str, Any]], user_question: str = "") -> str:
    sys = "你是OrbiRetail奥比零售云的企业经营分析AI。请基于用户上传的数据摘要，给出当前状况、风险、未来趋势和可执行建议。不要虚构未提供的数据。输出中文，结构清晰。"
    prompt = result_brief_for_ai(result) + "\n\n用户问题：" + (user_question or "请分析当前状况，并预测未来趋势，提出建议。")
    ans, status = call_chat_completion(sys, prompt, temperature=0.2, max_tokens=1000)
    return ans or (fallback_business_insight(result) + f"\n\n（{status}）")


def generate_ai_field_mapping(result: Optional[Dict[str, Any]]) -> str:
    if not result:
        return "请先上传数据或启动样例体验，AI 才能根据列名生成字段映射建议。"
    cols = list(result.get("raw", pd.DataFrame()).columns)
    template = result.get("template", {})
    current = result.get("field_detection")
    prompt = "模板要求：" + json.dumps({"name": template.get("name"), "required": template.get("required"), "group_by": template.get("group_by")}, ensure_ascii=False) + "\n上传列名：" + json.dumps([str(c) for c in cols], ensure_ascii=False)
    if isinstance(current, pd.DataFrame):
        prompt += "\n当前识别：" + current.to_json(orient="records", force_ascii=False)
    sys = "你是字段映射助手。请把用户上传的列名映射到标准字段，并指出缺失字段、冲突字段和建议修改列名。输出表格化中文说明。"
    ans, status = call_chat_completion(sys, prompt, temperature=0.1, max_tokens=900)
    if ans:
        return ans
    missing = []
    for f in template.get("required", []):
        if not find_field(cols, f):
            missing.append(f)
    return "字段映射建议：\n" + "\n".join([f"- `{c}`：请根据模板说明确认是否可映射为标准字段。" for c in cols[:20]]) + (f"\n缺失必需字段：{', '.join(missing)}" if missing else "\n必需字段基本完整。") + f"\n\n（{status}）"


def generate_ai_anomaly_explanation(result: Optional[Dict[str, Any]]) -> str:
    if not result:
        return "请先运行分析，AI 才能解释异常问题。"
    issues = result.get("issues")
    if not isinstance(issues, pd.DataFrame) or issues.empty:
        return "当前没有明显异常。建议继续关注数据可信度、金额口径和上传文件来源是否完整。"
    prompt = "问题清单：" + issues.head(80).to_json(orient="records", force_ascii=False) + "\n请解释这些异常可能产生的原因、影响和处理顺序。"
    sys = "你是数据质检与业务异常解释助手。请把技术问题翻译成业务人员能理解的原因、影响和处理动作。"
    ans, status = call_chat_completion(sys, prompt, temperature=0.15, max_tokens=900)
    if ans:
        return ans
    by_type = issues["问题类型"].value_counts().to_dict() if "问题类型" in issues.columns else {}
    return "异常解释：\n" + "\n".join([f"- {k}：{v} 条。建议优先复核相关列名、金额格式和必填值。" for k, v in by_type.items()]) + f"\n\n（{status}）"


def generate_ai_customer_reply(result: Optional[Dict[str, Any]], tone: str = "专业友好") -> str:
    prompt = result_brief_for_ai(result) + f"\n请生成一段{tone}的客服回复，说明分析结果、问题和下一步建议。"
    sys = "你是SaaS产品客服与客户成功顾问。请输出简洁、专业、可直接发送给客户的中文回复。"
    ans, status = call_chat_completion(sys, prompt, temperature=0.35, max_tokens=700)
    if ans:
        return ans
    return "您好，系统已完成本次数据分析。建议您先查看经营指标、数据可信度和问题清单，再下载报告包用于内部复核。如字段识别或结果有疑问，请把上传文件列名、模板名称和问题截图发送给我们，我们会协助定位。" + f"\n\n（{status}）"


def generate_ai_report_config(result: Optional[Dict[str, Any]]) -> str:
    if not result:
        return "请先运行一次分析，系统会根据当前场景生成报告配置建议。"
    template = result.get("template", {})
    base = {
        "报告标题": f"{template.get('name', '经营分析')}报告",
        "建议章节": ["核心指标", "数据可信度", "汇总结果", "异常问题", "AI经营摘要", "建议动作", "附录：原始数据"],
        "重点图表": ["趋势图", "Top5排行", "原因分布", "问题类型分布"],
        "下载内容": ["Excel分析报告", "问题清单CSV", "经营摘要TXT", "报告包ZIP"],
    }
    if template.get("id") == "ecommerce_after_sales":
        base["建议章节"] = ["售后概览", "退款原因分布", "商品售后表现", "客服效率", "高风险工单", "整改建议"]
    elif template.get("id") == "higher_education_career":
        base["建议章节"] = ["院系就业概览", "专业/班级就业率", "实习单位分布", "岗位行业分布", "薪资区间", "未就业帮扶清单", "AI分析摘要"]
    prompt = json.dumps(base, ensure_ascii=False) + "\n请把它整理成一份更适合业务汇报的报告配置。"
    sys = "你是报表配置专家。请输出适合当前业务场景的报告标题、章节顺序、图表建议、下载文件建议和展示重点。"
    ans, status = call_chat_completion(sys, prompt, temperature=0.2, max_tokens=850)
    return ans or (json.dumps(base, ensure_ascii=False, indent=2) + f"\n\n（{status}）")


def recommend_template_by_text(text: str) -> Dict[str, Any]:
    lower = (text or "").lower()
    scores = []
    for t in TEMPLATES:
        words = " ".join([t.get("name", ""), t.get("category", ""), t.get("target", ""), t.get("input", ""), t.get("output", ""), t.get("desc", "")]).lower()
        score = 0
        for token in re.findall(r"[\u4e00-\u9fffA-Za-z0-9]+", lower):
            if token and token in words:
                score += 2 if len(token) >= 2 else 1
        scores.append((score, t))
    scores.sort(key=lambda x: x[0], reverse=True)
    return scores[0][1] if scores else TEMPLATES[0]


def parse_rubric_criteria(rubric: str, assignment_type: str = "") -> pd.DataFrame:
    text = rubric or "结构完整20分，内容准确30分，分析深入30分，表达规范20分。"
    parts = re.split(r"[;；\n]+", text)
    rows = []
    for i, part in enumerate(parts):
        part = part.strip(" ，,。\t")
        if not part:
            continue
        m = re.search(r"(\d+(?:\.\d+)?)\s*分", part)
        score = float(m.group(1)) if m else None
        name = re.sub(r"\d+(?:\.\d+)?\s*分", "", part).strip(" ：:") or f"评分项{i+1}"
        rows.append({"评分项": name[:40], "分值": score if score is not None else "未标注", "说明": part})
    if not rows:
        rows = [{"评分项": "内容质量", "分值": "未标注", "说明": text[:120]}]
    return pd.DataFrame(rows)


def growth_profiles_dataframe(company_id: int) -> pd.DataFrame:
    conn = db()
    rows = conn.execute("SELECT student_name, score, level, similarity_flag, praise_or_warning, created_at FROM assignment_history WHERE company_id=? ORDER BY created_at", (company_id,)).fetchall()
    conn.close()
    if not rows:
        return pd.DataFrame(columns=["学生", "批改次数", "平均分", "最高分", "最低分", "高分次数", "低分次数", "成长趋势", "画像标签"])
    df = pd.DataFrame([dict(r) for r in rows])
    out = []
    for stu, g in df.groupby("student_name"):
        scores = g["score"].astype(float).tolist()
        trend = "稳定"
        if len(scores) >= 2:
            diff = scores[-1] - scores[0]
            if diff >= 8:
                trend = "明显进步"
            elif diff <= -8:
                trend = "明显下滑"
        tag = "正常"
        avg = sum(scores) / len(scores)
        if avg >= 85 and len(scores) >= 2:
            tag = "持续优秀，建议表扬"
        elif avg < 65 and len(scores) >= 2:
            tag = "持续低分，建议重点辅导"
        elif trend == "明显进步":
            tag = "进步明显，建议正向激励"
        out.append({"学生": stu, "批改次数": len(scores), "平均分": round(avg, 1), "最高分": max(scores), "最低分": min(scores), "高分次数": sum(s >= 85 for s in scores), "低分次数": sum(s < 60 for s in scores), "成长趋势": trend, "画像标签": tag})
    return pd.DataFrame(out).sort_values(["低分次数", "平均分"], ascending=[False, True])


def grading_trend_dataframe(company_id: int) -> pd.DataFrame:
    conn = db()
    rows = conn.execute("SELECT assignment_title, assignment_type, score, created_at FROM assignment_history WHERE company_id=?", (company_id,)).fetchall()
    conn.close()
    if not rows:
        return pd.DataFrame(columns=["日期", "作业类型", "批改数", "平均分", "低分数"])
    df = pd.DataFrame([dict(r) for r in rows])
    df["日期"] = pd.to_datetime(df["created_at"], errors="coerce").dt.date.astype(str)
    return df.groupby(["日期", "assignment_type"], dropna=False).agg(批改数=("score", "count"), 平均分=("score", "mean"), 低分数=("score", lambda s: int((pd.Series(s).astype(float) < 60).sum()))).reset_index().rename(columns={"assignment_type": "作业类型"})


def class_risk_dataframe(company_id: int) -> pd.DataFrame:
    profiles = growth_profiles_dataframe(company_id)
    if profiles.empty:
        return pd.DataFrame(columns=["风险类型", "学生", "风险说明", "建议动作"])
    rows = []
    for _, r in profiles.iterrows():
        if str(r.get("画像标签", "")).startswith("持续低分"):
            rows.append({"风险类型": "持续低分", "学生": r["学生"], "风险说明": f"平均分 {r['平均分']}，低分次数 {r['低分次数']}。", "建议动作": "建议教师单独反馈学习方法，安排补交/重做或辅导。"})
        elif r.get("成长趋势") == "明显下滑":
            rows.append({"风险类型": "成绩下滑", "学生": r["学生"], "风险说明": "近期分数较首次批改明显下降。", "建议动作": "建议查看最近作业主题、出勤和提交质量。"})
    return pd.DataFrame(rows) if rows else pd.DataFrame([{"风险类型": "暂无明显风险", "学生": "", "风险说明": "当前历史记录未发现连续低分或明显下滑学生。", "建议动作": "继续积累批改记录，定期查看趋势。"}])


def generate_teacher_comment(row: Dict[str, Any], rubric: str = "") -> str:
    prompt = "学生作业批改结果：" + json.dumps(row, ensure_ascii=False) + "\n评分标准：" + (rubric or "未提供") + "\n请生成教师可直接使用的评语，包含优点、问题和下一步建议。"
    sys = "你是高校教师助教AI。请生成温和、具体、可执行的中文作业评语，不要过度夸大，不要给出无法验证的事实。"
    ans, status = call_chat_completion(sys, prompt, temperature=0.35, max_tokens=550)
    if ans:
        return ans
    return f"该同学本次作业得分为 {row.get('得分', '')}，等级为 {row.get('等级', '')}。总体完成了基本要求，但仍建议结合评分标准进一步完善结构、论据和表达规范。请重点查看批改意见中的不足，并在下次作业中改进。\n\n（{status}）"

def ai_agent_reply(message: str, user: sqlite3.Row, company: sqlite3.Row) -> str:
    msg_raw = (message or "").strip()
    msg = msg_raw.lower()
    current_result = st.session_state.get("analysis_result")
    # 智能动作：基于当前分析结果做解释、预测、摘要和配置建议。
    if any(k in msg for k in ["当前状况", "怎么样", "好不好", "经营情况", "现状", "预测", "未来", "建议", "利润", "亏损"]):
        return generate_ai_business_analysis(current_result, msg_raw)
    if any(k in msg for k in ["字段映射", "列名", "识别字段", "缺字段", "映射建议"]):
        return generate_ai_field_mapping(current_result)
    if any(k in msg for k in ["异常", "为什么", "解释问题", "报错原因", "问题清单"]):
        return generate_ai_anomaly_explanation(current_result)
    if any(k in msg for k in ["客服回复", "回复客户", "怎么跟客户说", "售后回复"]):
        return generate_ai_customer_reply(current_result)
    if any(k in msg for k in ["报告配置", "报告怎么做", "生成报告配置", "章节"]):
        return generate_ai_report_config(current_result)
    if any(k in msg for k in ["就业数据", "就业率", "实习", "未就业", "院系", "班级就业"]):
        # 如果已有高校分析结果，则优先基于数据问答；否则推荐模板。
        if current_result and current_result.get("template", {}).get("id") == "higher_education_career":
            return generate_ai_business_analysis(current_result, msg_raw)
    tpl_map = {
        "ecommerce_after_sales": ["电商", "退款", "售后", "退货", "换货", "工单", "客服", "投诉", "赔付"],
        "retail_daily": ["门店", "渠道", "日报", "零售", "销售日报"],
        "platform_settlement": ["结算", "平台对账", "到账", "手续费", "银行流水"],
        "inventory_check": ["库存", "盘点", "盘盈", "盘亏", "补货"],
        "expense_monthly": ["费用", "报销", "部门", "月度"],
        "sales_performance": ["销售", "业绩", "区域", "排名"],
        "payroll_check": ["考勤", "工资", "请假", "人事"],
        "supplier_recon": ["供应商", "采购", "发票", "付款"],
        "higher_education_career": ["高校", "教务", "实习", "就业", "院系", "学生", "专业", "班级", "薪资", "未就业"],
    }
    for tid, kws in tpl_map.items():
        if any(k in msg for k in kws):
            tpl = next((t for t in TEMPLATES if t["id"] == tid), None)
            if tpl:
                st.session_state["selected_template_id"] = tid
                return (
                    f"我建议你使用【{tpl['name']}】模板。\n\n"
                    f"适合用户：{tpl['target']}\n"
                    f"建议上传：{tpl['input']}\n"
                    f"系统输出：{tpl['output']}\n"
                    f"必需字段：{'、'.join(tpl.get('required', []))}\n\n"
                    "你可以先点击“立即启动样例数据体验”，确认结果，再上传自己的 Excel/CSV。"
                )
    if any(k in msg for k in ["怎么用", "不会", "流程", "新手", "开始"]):
        return "新用户建议按 4 步操作：1）选择业务模板；2）先启动样例数据体验；3）查看经营诊断和问题清单；4）再上传自己的 Excel 并下载报告包。"
    if any(k in msg for k in ["上传", "文件", "excel", "csv", "批量"]):
        return "上传建议：第一行必须是表头；支持 .xlsx 和 .csv；可批量上传。系统会自动合并文件并生成来源文件日志。若字段没有被识别，请按模板说明补充列名。"
    if any(k in msg for k in ["下载", "报告", "问题清单", "zip"]):
        return "分析完成后，在“报告下载区”可以下载 Excel 分析报告、问题清单 CSV、经营摘要 TXT 和报告包 ZIP。问题清单适合发给提交数据的人进行修改。"
    if any(k in msg for k in ["付费", "会员", "价格", "套餐"]):
        return f"当前产品主张高性价比：免费版可长期轻量使用；会员版 ¥{MEMBER_PRICE_MONTH}/月或 ¥{MEMBER_PRICE_YEAR}/年，解锁批量上传、全部模板、报告包、团队协作、API 和手机报告。"
    if any(k in msg for k in ["批改", "作业", "评分", "论文", "雷同", "抄袭", "查重", "评语"]):
        return "你可以进入【AI作业批改】页，上传 Word / PDF / TXT / ZIP 作业包，并输入或上传评分细则。Batch 44 支持真实大模型深度评语、评分标准解析、学生成长画像、班级风险预警和一键生成教师评语。"
    if any(k in msg for k in ["客服", "联系", "报错", "闪退", "失败", "问题"]):
        return f"如果页面报错或结果异常，请先截图并记录使用的模板、上传文件列名和操作步骤。也可以直接联系：{CONTACT_EMAIL}。我会优先建议你下载问题清单和报告包，便于定位。"
    # 如果配置了真实大模型，把未命中的问题交给大模型回答；否则使用规则答案。
    if ai_provider_ready():
        sys = "你是OrbiRetail奥比零售云的AI Agent，负责产品客服、模板推荐、数据分析解释和教育场景助手。请基于产品能力回答，不要承诺无法完成的功能。"
        prompt = "产品能力包括：零售/电商/财务/库存/人事/高校就业数据分析、AI作业批改、字段映射、问题清单、经营摘要、报告包下载、会员版。用户问题：" + msg_raw
        ans, _ = call_chat_completion(sys, prompt, temperature=0.25, max_tokens=800)
        if ans:
            return ans
    rec = recommend_template_by_text(msg_raw)
    return f"我可以帮你选择模板、解释字段、指导上传、分析当前结果、预测趋势、生成报告配置，也可以作为客服记录问题。根据你的描述，我初步推荐【{rec['name']}】模板。你也可以直接告诉我：要分析什么文件、希望输出什么报告。"

def render_ai_agent(user: sqlite3.Row, company: sqlite3.Row) -> None:
    st.markdown(
        """
        <div class='ai-agent-box'>
          <div class='ai-agent-title'>🤖 OrbiRetail AI Agent 智能助手</div>
          <div class='orbi-muted'>告诉我你要解决的问题。我可以推荐模板、解释异常、生成经营摘要、预测趋势、生成客服回复，并在配置 API Key 后调用真实大模型。</div>
          <span class='ai-agent-chip'>模板推荐</span><span class='ai-agent-chip'>字段映射</span><span class='ai-agent-chip'>异常解释</span><span class='ai-agent-chip'>趋势预测</span><span class='ai-agent-chip'>客服回复</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    cfg = get_ai_runtime_config()
    status_text = "本地规则模式" if cfg.get("provider") == "rules" else f"{cfg.get('label')} · 模型 {cfg.get('model')}"
    if cfg.get("provider") != "rules" and not cfg.get("api_key"):
        status_text += " · 未配置 API Key"
    st.caption(f"AI 当前模式：{status_text}")
    quick_cols = st.columns(4)
    quick_prompts = [
        "根据当前数据分析经营状况并预测未来",
        "生成字段映射建议",
        "解释问题清单里的异常",
        "我要批改学生作业并生成教师评语",
    ]
    for i, prompt in enumerate(quick_prompts):
        with quick_cols[i]:
            if st.button(prompt, key=f"ai_quick_{i}", use_container_width=True):
                st.session_state["ai_input_text"] = prompt
                st.session_state["ai_last_answer"] = ai_agent_reply(prompt, user, company)
                st.rerun()
    with st.form("ai_agent_form", clear_on_submit=False):
        msg = st.text_input("向 AI Agent 发送需求或问题", value=st.session_state.get("ai_input_text", ""), placeholder="例如：分析当前店铺状况、预测未来趋势、生成客服回复、解析评分标准", key="ai_input_box")
        submitted = st.form_submit_button("发送给 AI Agent", use_container_width=True)
        if submitted:
            st.session_state["ai_input_text"] = msg
            st.session_state["ai_last_answer"] = ai_agent_reply(msg, user, company)
    if st.session_state.get("ai_last_answer"):
        st.markdown(f"<div class='ai-answer'>{st.session_state['ai_last_answer']}</div>", unsafe_allow_html=True)


def render_ai_intelligence_center(user: sqlite3.Row, company: sqlite3.Row) -> None:
    st.markdown("<div class='orbi-section-title'>AI 智能中心</div>", unsafe_allow_html=True)
    st.markdown("<div class='orbi-section-subtitle'>配置真实大模型 API，并对当前分析结果进行深度问答、趋势预测、字段映射、异常解释和报告配置生成。</div>", unsafe_allow_html=True)
    cfg = get_ai_runtime_config()
    with st.expander("AI 接入配置（OpenAI / 通义千问 / 智谱 / DeepSeek）", expanded=True):
        provider_options = {"rules": "本地规则模式（无需API Key）", "openai": "OpenAI", "qwen": "通义千问 / 阿里云百炼", "zhipu": "智谱 GLM", "deepseek": "DeepSeek"}
        current_provider = str(st.session_state.get("AI_PROVIDER", _secret_or_env("ORBI_AI_PROVIDER", "rules"))).lower()
        if current_provider not in provider_options:
            current_provider = "rules"
        provider = st.selectbox("AI 提供商", list(provider_options.keys()), index=list(provider_options.keys()).index(current_provider), format_func=lambda x: provider_options[x], key="AI_PROVIDER_SELECT")
        st.session_state["AI_PROVIDER"] = provider
        if provider != "rules":
            defaults = AI_PROVIDER_DEFAULTS[provider]
            c1, c2 = st.columns([1, 1])
            with c1:
                api_key = st.text_input("API Key（仅本次会话临时保存；正式部署建议放到 Streamlit Secrets）", value=st.session_state.get(defaults["key_env"], ""), type="password", key=f"{provider}_api_key_input")
                if api_key:
                    st.session_state[defaults["key_env"]] = api_key
            with c2:
                model = st.text_input("模型名称", value=_secret_or_env(f"{provider.upper()}_MODEL", defaults["model"]), key=f"{provider}_model_input")
                st.session_state[f"{provider.upper()}_MODEL"] = model
            base_url = st.text_input("Base URL", value=_secret_or_env(f"{provider.upper()}_BASE_URL", defaults["base_url"]), key=f"{provider}_base_url_input")
            st.session_state[f"{provider.upper()}_BASE_URL"] = base_url
            st.caption("提示：通义千问、智谱和 DeepSeek 均按 OpenAI 兼容 Chat Completions 格式预留接入。")
        else:
            st.info("当前使用本地规则模式，所有 AI 功能会以可控规则输出，不调用外部大模型。")
    result = st.session_state.get("analysis_result")
    if not result:
        st.warning("当前还没有分析结果。建议先在工作台点击样例体验或上传数据，再使用 AI 智能分析。")
    else:
        st.markdown("#### 基于当前分析结果的一键 AI 能力")
        cols = st.columns(3)
        actions = [
            ("ai_business_summary", "生成经营摘要 / 当前状况分析", lambda: generate_ai_business_analysis(result)),
            ("ai_future_prediction", "预测未来趋势并给出建议", lambda: generate_ai_business_analysis(result, "请重点预测未来趋势和风险，并提出下一步建议。")),
            ("ai_field_mapping", "生成字段映射建议", lambda: generate_ai_field_mapping(result)),
            ("ai_anomaly_explain", "解释异常问题", lambda: generate_ai_anomaly_explanation(result)),
            ("ai_customer_reply", "生成客服回复草稿", lambda: generate_ai_customer_reply(result)),
            ("ai_report_config", "生成报告配置建议", lambda: generate_ai_report_config(result)),
        ]
        for i, (key, label, fn) in enumerate(actions):
            with cols[i % 3]:
                if st.button(label, key=key, use_container_width=True):
                    st.session_state[f"{key}_answer"] = fn()
        for key, label, _ in actions:
            val = st.session_state.get(f"{key}_answer")
            if val:
                with st.expander(label, expanded=True):
                    st.markdown(f"<div class='ai-answer'>{val}</div>", unsafe_allow_html=True)
        st.markdown("#### AI 问答")
        q = st.text_area("围绕当前数据提问", placeholder="例如：哪个店铺风险最大？为什么退款金额偏高？高校哪个专业就业率需要重点关注？", height=100, key="ai_data_question")
        if st.button("向 AI 提问", key="ask_ai_about_data", use_container_width=True):
            st.session_state["ai_data_answer"] = generate_ai_business_analysis(result, q)
        if st.session_state.get("ai_data_answer"):
            st.markdown(f"<div class='ai-answer'>{st.session_state['ai_data_answer']}</div>", unsafe_allow_html=True)
    st.markdown("#### 教育场景智能化")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("班级学习风险预警", key="ai_class_risk_btn", use_container_width=True):
            st.session_state["ai_class_risk_df"] = class_risk_dataframe(company["id"])
    with c2:
        if st.button("学生成长画像", key="ai_growth_profile_btn", use_container_width=True):
            st.session_state["ai_growth_df"] = growth_profiles_dataframe(company["id"])
    with c3:
        if st.button("作业批改历史趋势", key="ai_grading_trend_btn", use_container_width=True):
            st.session_state["ai_trend_df"] = grading_trend_dataframe(company["id"])
    if st.session_state.get("ai_class_risk_df") is not None:
        with st.expander("班级学习风险预警", expanded=True):
            st.dataframe(st.session_state["ai_class_risk_df"], use_container_width=True)
    if st.session_state.get("ai_growth_df") is not None:
        with st.expander("学生成长画像", expanded=True):
            st.dataframe(st.session_state["ai_growth_df"], use_container_width=True)
    if st.session_state.get("ai_trend_df") is not None:
        with st.expander("作业批改历史趋势", expanded=True):
            st.dataframe(st.session_state["ai_trend_df"], use_container_width=True)

def render_workbench(user: sqlite3.Row, company: sqlite3.Row) -> None:
    if not company_access_allowed(company):
        st.markdown("<div class='danger-box'><b>10 天试用已结束。</b>你仍可继续使用免费版轻量能力；如需批量上传、全部模板、报告包和 API，请升级会员版。</div>", unsafe_allow_html=True)
        return
    template = selected_template()
    st.markdown("<div class='orbi-section-title'>经营数据分析工作台</div>", unsafe_allow_html=True)
    st.markdown("<div class='orbi-section-subtitle'>先用样例体验，再上传自己的 Excel。系统会自动识别字段、生成汇总、问题清单、经营诊断和报告包。</div>", unsafe_allow_html=True)
    render_ai_agent(user, company)
    st.markdown(
        f"<div class='success-box'><b>当前模板：</b>{template['icon']} {template['name']} · {template['category']}<br><span class='orbi-small'>{template['desc']}</span></div>",
        unsafe_allow_html=True,
    )
    st.write("")
    a, b = st.columns(2)
    with a:
        if st.button("立即启动样例数据体验", key="sample_single", use_container_width=True):
            df = sample_dataframe(template, batch=False)
            result = analyze_dataframe(df, template)
            st.session_state["analysis_result"] = result
            st.success("样例数据体验已完成。")
            st.rerun()
    with b:
        if st.button("立即启动批量样例体验", key="sample_batch", use_container_width=True):
            df = sample_dataframe(template, batch=True)
            result = analyze_dataframe(df, template)
            st.session_state["analysis_result"] = result
            st.success("批量样例体验已完成。")
            st.rerun()
    render_template_detail(template)
    st.markdown("#### 上传自己的 Excel / CSV")
    plan = current_plan(company)
    if not has_perm(user, "analyze"):
        st.warning("当前角色没有上传和分析权限。请联系管理员。")
    else:
        uploaded = st.file_uploader(
            f"支持批量上传，当前套餐单次最多 {plan['files_per_run']} 个文件。",
            type=["xlsx", "csv"],
            accept_multiple_files=True,
            key="uploaded_files",
        )
        if uploaded:
            try:
                df, logs = read_uploaded_files(uploaded, plan["files_per_run"])
                st.markdown("上传文件日志")
                st.dataframe(logs, use_container_width=True)
                if not df.empty and st.button("开始分析上传数据", key="analyze_uploaded", use_container_width=True):
                    result = analyze_dataframe(df, template)
                    st.session_state["analysis_result"] = result
                    st.rerun()
            except Exception as e:
                st.error(f"上传或读取失败：{e}")
    result = st.session_state.get("analysis_result")
    if result:
        render_result(user, company, result)


# -----------------------------------------------------------------------------
# AI assignment grading helpers
# -----------------------------------------------------------------------------
def _simple_tokens(text: str) -> set:
    words = re.findall(r"[\u4e00-\u9fff]{2,}|[A-Za-z0-9_]{3,}", text.lower())
    return set(words)


def _safe_read_text_file(uploaded: Any) -> str:
    data = uploaded.getvalue()
    name = getattr(uploaded, "name", "").lower()
    if name.endswith(".txt"):
        return data.decode("utf-8", errors="ignore")
    if name.endswith(".docx"):
        try:
            from docx import Document
            doc = Document(io.BytesIO(data))
            return "\n".join(p.text for p in doc.paragraphs)
        except Exception as exc:
            return f"[DOCX 解析失败：{exc}]"
    if name.endswith(".pdf"):
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(data))
            texts = []
            for page in reader.pages[:80]:
                texts.append(page.extract_text() or "")
            return "\n".join(texts)
        except Exception as exc:
            return f"[PDF 解析失败：{exc}]"
    return data.decode("utf-8", errors="ignore")


def extract_assignment_submissions(files: List[Any]) -> List[Dict[str, Any]]:
    submissions: List[Dict[str, Any]] = []
    for f in files:
        name = getattr(f, "name", "uploaded")
        lower = name.lower()
        if lower.endswith(".zip"):
            try:
                z = zipfile.ZipFile(io.BytesIO(f.getvalue()))
                for member in z.namelist():
                    if member.startswith("__MACOSX/") or member.endswith("/"):
                        continue
                    if not member.lower().endswith((".docx", ".pdf", ".txt")):
                        continue
                    raw = z.read(member)
                    fake = type("UploadedLike", (), {"name": Path(member).name, "getvalue": lambda self, raw=raw: raw})()
                    text = _safe_read_text_file(fake)
                    student = Path(member).stem.split("_")[0].split("-")[0].strip() or Path(member).stem
                    submissions.append({"文件名": member, "学生": student, "文本": text, "字数": len(text)})
            except Exception as exc:
                submissions.append({"文件名": name, "学生": Path(name).stem, "文本": f"[ZIP 解析失败：{exc}]", "字数": 0})
        else:
            text = _safe_read_text_file(f)
            student = Path(name).stem.split("_")[0].split("-")[0].strip() or Path(name).stem
            submissions.append({"文件名": name, "学生": student, "文本": text, "字数": len(text)})
    return submissions


def rubric_keywords(rubric: str, assignment_type: str) -> List[str]:
    base = ["结构", "观点", "论证", "案例", "数据", "反思", "结论"]
    type_map = {
        "课程论文": ["摘要", "文献", "引用", "研究", "分析", "结论"],
        "实习报告": ["单位", "岗位", "任务", "收获", "问题", "改进"],
        "实验报告": ["目的", "步骤", "数据", "结果", "分析", "误差"],
        "读书报告": ["作者", "主题", "观点", "摘录", "感悟", "评价"],
        "代码说明文档": ["需求", "设计", "接口", "测试", "异常", "部署"],
    }
    text_words = re.findall(r"[\u4e00-\u9fff]{2,}|[A-Za-z0-9_]{3,}", rubric)
    words = base + type_map.get(assignment_type, []) + text_words[:40]
    # 去重但保持顺序
    seen, out = set(), []
    for w in words:
        if w not in seen:
            seen.add(w); out.append(w)
    return out


def compute_similarity(submissions: List[Dict[str, Any]]) -> Dict[Tuple[int, int], float]:
    sims: Dict[Tuple[int, int], float] = {}
    token_sets = [_simple_tokens(s.get("文本", "")) for s in submissions]
    for i in range(len(submissions)):
        for j in range(i + 1, len(submissions)):
            a, b = token_sets[i], token_sets[j]
            if not a or not b:
                sims[(i, j)] = 0.0
            else:
                sims[(i, j)] = len(a & b) / max(1, len(a | b))
    return sims


def grade_submission_text(text: str, rubric: str, assignment_type: str, max_score: int, use_llm: bool = False) -> Tuple[float, str, str, str]:
    kws = rubric_keywords(rubric, assignment_type)
    text_l = text.lower()
    keyword_hits = sum(1 for k in kws if str(k).lower() in text_l)
    length = len(text.strip())
    length_score = min(30, length / 40)  # 1200字左右接近满分
    keyword_score = min(35, keyword_hits / max(6, len(kws) * 0.35) * 35)
    structure_hits = sum(1 for k in ["一、", "二、", "三、", "1.", "2.", "结论", "总结", "参考", "反思"] if k in text)
    structure_score = min(20, structure_hits * 4)
    clarity_score = 15 if len(set(text.strip())) > 60 else 8
    raw = length_score + keyword_score + structure_score + clarity_score
    score = round(max(0, min(max_score, raw / 100 * max_score)), 1)
    if score >= max_score * 0.85:
        level = "优秀"
    elif score >= max_score * 0.70:
        level = "良好"
    elif score >= max_score * 0.60:
        level = "合格"
    else:
        level = "需改进"
    strengths = []
    if keyword_hits >= 6:
        strengths.append("覆盖了较多评分要点")
    if structure_score >= 12:
        strengths.append("结构较清晰")
    if length_score >= 20:
        strengths.append("内容较充实")
    if not strengths:
        strengths.append("已提交基本内容")
    improvements = []
    if keyword_hits < 5:
        improvements.append("需补充评分细则中的关键要点")
    if structure_score < 8:
        improvements.append("建议增加标题层级、结论或反思段落")
    if length_score < 15:
        improvements.append("内容偏短，建议补充案例、数据或过程说明")
    if not improvements:
        improvements.append("可进一步提升论证深度和案例质量")
    comment = f"等级：{level}。优点：{'；'.join(strengths)}。改进建议：{'；'.join(improvements)}。"
    if use_llm and ai_provider_ready():
        sys = "你是高校课程助教AI。请根据作业文本、评分细则和初评分生成深度评语，内容包括：优点、不足、可执行改进建议、是否需要教师重点复核。不要虚构引用和事实。"
        prompt = f"作业类型：{assignment_type}\n满分：{max_score}\n初评分：{score}\n等级：{level}\n命中要点：{'、'.join(kws[:20])}\n评分细则：{rubric[:3000]}\n作业正文节选：{text[:6000]}"
        ans, _status = call_chat_completion(sys, prompt, temperature=0.25, max_tokens=850)
        if ans:
            comment = ans.strip()
    return score, level, comment, "、".join(kws[:12])

def student_history_note(company_id: int, student: str, current_score: float, max_score: int) -> str:
    conn = db()
    rows = conn.execute("SELECT score, level, created_at FROM assignment_history WHERE company_id=? AND student_name=? ORDER BY id DESC LIMIT 8", (company_id, student)).fetchall()
    conn.close()
    if not rows:
        return "首次记录"
    high = sum(1 for r in rows if float(r["score"]) >= max_score * 0.85)
    low = sum(1 for r in rows if float(r["score"]) < max_score * 0.60)
    avg = sum(float(r["score"]) for r in rows) / len(rows)
    if high >= 2 and current_score >= max_score * 0.80:
        return f"表扬：该生历史表现稳定较好，近{len(rows)}次均分约 {avg:.1f}。"
    if low >= 2 or current_score < max_score * 0.55:
        return f"警告：该生存在连续低分风险，近{len(rows)}次均分约 {avg:.1f}，建议重点辅导。"
    return f"历史参考：近{len(rows)}次均分约 {avg:.1f}。"


def run_assignment_grading(user: sqlite3.Row, company: sqlite3.Row, files: List[Any], assignment_title: str, assignment_type: str, rubric: str, max_score: int, use_llm_comments: bool = False) -> Dict[str, Any]:
    submissions = extract_assignment_submissions(files)
    sims = compute_similarity(submissions)
    similarity_flags = {i: [] for i in range(len(submissions))}
    for (i, j), sim in sims.items():
        if sim >= 0.72:
            similarity_flags[i].append(f"与 {submissions[j]['学生']} 相似度 {sim:.2%}")
            similarity_flags[j].append(f"与 {submissions[i]['学生']} 相似度 {sim:.2%}")
    rows = []
    conn = db()
    for idx, sub in enumerate(submissions):
        text = sub.get("文本", "")
        score, level, comment, used_kws = grade_submission_text(text, rubric, assignment_type, max_score, use_llm_comments)
        sim_flag = "；".join(similarity_flags.get(idx, [])) or "正常"
        hist_note = student_history_note(company["id"], sub["学生"], score, max_score)
        if sim_flag != "正常":
            level = level + "（需查重复核）"
        rows.append({
            "学生": sub["学生"],
            "文件名": sub["文件名"],
            "作业类型": assignment_type,
            "得分": score,
            "等级": level,
            "字数": sub.get("字数", 0),
            "雷同抄袭标注": sim_flag,
            "历史表现标注": hist_note,
            "AI批改意见": comment,
            "命中评分要点": used_kws,
        })
        conn.execute(
            "INSERT INTO assignment_history(company_id,user_id,student_name,assignment_title,assignment_type,score,level,similarity_flag,praise_or_warning,created_at,feedback_json) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            (company["id"], user["id"], sub["学生"], assignment_title, assignment_type, float(score), level, sim_flag, hist_note, now_iso(), json.dumps({"comment": comment, "keywords": used_kws, "llm": bool(use_llm_comments and ai_provider_ready())}, ensure_ascii=False)),
        )
    conn.commit(); conn.close()
    result_df = pd.DataFrame(rows)
    sim_rows = []
    for (i, j), sim in sims.items():
        sim_rows.append({"学生A": submissions[i]["学生"], "学生B": submissions[j]["学生"], "相似度": round(sim, 4), "标注": "疑似雷同" if sim >= 0.72 else "正常"})
    sim_df = pd.DataFrame(sim_rows)
    rubric_df = parse_rubric_criteria(rubric, assignment_type)
    growth_df = growth_profiles_dataframe(company["id"])
    trend_df = grading_trend_dataframe(company["id"])
    risk_df = class_risk_dataframe(company["id"])
    return {"results": result_df, "similarity": sim_df, "rubric": rubric, "rubric_df": rubric_df, "growth_profiles": growth_df, "grading_trends": trend_df, "class_risks": risk_df, "assignment_title": assignment_title, "assignment_type": assignment_type, "created_at": now_iso(), "llm_comments": bool(use_llm_comments and ai_provider_ready())}

def make_assignment_report_excel(grading: Dict[str, Any]) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        grading["results"].to_excel(writer, index=False, sheet_name="AI批改结果")
        grading["similarity"].to_excel(writer, index=False, sheet_name="雷同抄袭检测")
        grading.get("rubric_df", pd.DataFrame()).to_excel(writer, index=False, sheet_name="评分标准解析")
        grading.get("growth_profiles", pd.DataFrame()).to_excel(writer, index=False, sheet_name="学生成长画像")
        grading.get("grading_trends", pd.DataFrame()).to_excel(writer, index=False, sheet_name="批改历史趋势")
        grading.get("class_risks", pd.DataFrame()).to_excel(writer, index=False, sheet_name="班级风险预警")
        pd.DataFrame([{"作业标题": grading["assignment_title"], "作业类型": grading["assignment_type"], "生成时间": grading["created_at"], "是否启用真实大模型评语": grading.get("llm_comments", False), "评分细则": grading["rubric"][:3000]}]).to_excel(writer, index=False, sheet_name="评分设置")
    return buf.getvalue()

def render_assignment_grading_page(user: sqlite3.Row, company: sqlite3.Row) -> None:
    st.markdown("<div class='orbi-section-title'>AI 作业批改</div>", unsafe_allow_html=True)
    st.markdown("<div class='orbi-section-subtitle'>支持上传 Word / PDF / TXT / ZIP 作业包。Batch 44 新增真实大模型深度评语、评分标准自动解析、班级学习风险预警、学生成长画像和教师一键评语。</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='notice-box'><b>说明：</b>当前为规则增强型 AI 批改 MVP，适合初筛、统计和辅助批改。重要课程成绩仍建议教师复核。遇到问题请联系：{CONTACT_EMAIL}</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.2, 1, 1])
    with c1:
        assignment_title = st.text_input("作业标题", value="课程作业", key="assign_title")
    with c2:
        assignment_type = st.selectbox("作业类型", ["通用文字作业", "课程论文", "实习报告", "实验报告", "读书报告", "代码说明文档"], key="assign_type")
    with c3:
        max_score = st.number_input("满分", min_value=10, max_value=150, value=100, step=5, key="assign_max")
    rubric_text = st.text_area("评分标准细则（可直接输入）", placeholder="例如：结构完整20分，观点清晰20分，案例和数据30分，反思总结20分，格式规范10分。", height=140, key="assign_rubric")
    rubric_file = st.file_uploader("也可以上传评分标准文件（Word/PDF/TXT）", type=["docx", "pdf", "txt"], key="rubric_file")
    if rubric_file:
        extra = _safe_read_text_file(rubric_file)
        rubric_text = (rubric_text + "\n" + extra).strip()
        st.success("已读取评分标准文件。")
    rubric_preview = parse_rubric_criteria(rubric_text, assignment_type)
    with st.expander("AI 评分标准自动解析预览", expanded=False):
        st.dataframe(rubric_preview, use_container_width=True)
    use_llm_comments = st.checkbox("启用真实大模型深度评语（需要在 AI 智能中心配置 API Key）", value=False, key="assign_use_llm_comments")
    files = st.file_uploader("上传学生作业（可多选 Word/PDF/TXT，也可上传 ZIP 作业包）", type=["docx", "pdf", "txt", "zip"], accept_multiple_files=True, key="assignment_files")
    if st.button("开始 AI 批改作业", key="run_assignment_grading", use_container_width=True):
        if not files:
            st.error("请先上传学生作业文件。")
        else:
            rubric = rubric_text.strip() or "结构完整、内容准确、观点清晰、案例充分、反思到位、格式规范。"
            try:
                grading = run_assignment_grading(user, company, files, assignment_title, assignment_type, rubric, int(max_score), bool(use_llm_comments))
                st.session_state["assignment_grading"] = grading
                st.success("AI 批改已完成。")
            except Exception as exc:
                st.error(f"批改失败：{exc}")
    grading = st.session_state.get("assignment_grading")
    if grading:
        results = grading["results"]
        st.markdown("#### 批改结果汇总")
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.metric("作业份数", len(results))
        with m2: st.metric("平均分", round(float(results["得分"].mean()), 1) if not results.empty else 0)
        with m3: st.metric("疑似雷同", int((results["雷同抄袭标注"] != "正常").sum()) if not results.empty else 0)
        with m4: st.metric("需重点关注", int(results["历史表现标注"].astype(str).str.contains("警告").sum()) if not results.empty else 0)
        st.dataframe(results, use_container_width=True)
        with st.expander("雷同抄袭检测详情", expanded=False):
            st.dataframe(grading["similarity"], use_container_width=True)
        with st.expander("评分标准自动解析", expanded=False):
            st.dataframe(grading.get("rubric_df", pd.DataFrame()), use_container_width=True)
        with st.expander("学生成长画像", expanded=False):
            st.dataframe(grading.get("growth_profiles", pd.DataFrame()), use_container_width=True)
        with st.expander("班级学习风险预警", expanded=True):
            st.dataframe(grading.get("class_risks", pd.DataFrame()), use_container_width=True)
        with st.expander("作业批改历史趋势", expanded=False):
            st.dataframe(grading.get("grading_trends", pd.DataFrame()), use_container_width=True)
        if not results.empty:
            st.markdown("#### 教师一键生成评语")
            student_options = results["学生"].astype(str).tolist()
            selected_student = st.selectbox("选择学生", student_options, key="teacher_comment_student")
            selected_row = results[results["学生"].astype(str) == selected_student].iloc[0].to_dict()
            if st.button("生成教师评语", key="generate_teacher_comment", use_container_width=True):
                st.session_state["teacher_comment"] = generate_teacher_comment(selected_row, grading.get("rubric", ""))
            if st.session_state.get("teacher_comment"):
                st.markdown(f"<div class='ai-answer'>{st.session_state['teacher_comment']}</div>", unsafe_allow_html=True)
        st.download_button("下载 AI 作业批改数据分析表格", data=make_assignment_report_excel(grading), file_name=f"OrbiRetail_AI作业批改_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="download_assignment_report", use_container_width=True)


# -----------------------------------------------------------------------------
# Team and permissions
# -----------------------------------------------------------------------------
def render_team_page(user: sqlite3.Row, company: sqlite3.Row) -> None:
    st.markdown("<div class='orbi-section-title'>团队账号与角色权限</div>", unsafe_allow_html=True)
    if not has_perm(user, "team"):
        st.warning("当前角色没有管理团队权限。")
        return
    plan = current_plan(company)
    conn = db()
    members = conn.execute("SELECT id,email,role,status,created_at FROM users WHERE company_id=? ORDER BY id", (company["id"],)).fetchall()
    st.info(f"当前套餐成员上限：{plan['members']}，当前成员数：{len(members)}")
    st.dataframe(pd.DataFrame([dict(m) | {"角色名称": role_name(m["role"])} for m in members]), use_container_width=True)
    st.markdown("#### 新增团队成员")
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        new_email = st.text_input("成员邮箱", key="team_email")
    with c2:
        new_role = st.selectbox("角色", list(ROLES.keys()), format_func=role_name, key="team_role")
    with c3:
        active = st.selectbox("状态", ["active", "disabled"], format_func=lambda x: "启用" if x == "active" else "禁用", key="team_status")
    if st.button("创建成员账号", key="create_member", use_container_width=True):
        if len(members) >= plan["members"]:
            st.error("当前套餐成员数量已达上限。")
        elif "@" not in new_email:
            st.error("请输入有效邮箱。")
        else:
            existing = conn.execute("SELECT id FROM users WHERE email=?", (new_email.strip().lower(),)).fetchone()
            if existing:
                st.error("该邮箱已存在。")
            else:
                temp_pwd = "Orbi" + secrets.token_hex(3)
                digest, salt = hash_password(temp_pwd)
                conn.execute(
                    "INSERT INTO users(company_id,email,password_hash,salt,role,status,created_at) VALUES(?,?,?,?,?,?,?)",
                    (company["id"], new_email.strip().lower(), digest, salt, new_role, active, now_iso()),
                )
                conn.commit()
                st.success(f"已创建成员。临时密码：{temp_pwd}，请让成员首次登录后修改密码（正式版需补密码修改页）。")
                st.rerun()
    with st.expander("角色权限说明", expanded=True):
        st.dataframe(pd.DataFrame([{"角色": v["name"], "权限": "、".join(v["permissions"]), "说明": v["desc"]} for k, v in ROLES.items()]), use_container_width=True)
    conn.close()


# -----------------------------------------------------------------------------
# Billing and payment
# -----------------------------------------------------------------------------
def render_billing_page(user: sqlite3.Row, company: sqlite3.Row) -> None:
    st.markdown("<div class='orbi-section-title'>正式支付接入准备与会员升级</div>", unsafe_allow_html=True)
    if not has_perm(user, "billing"):
        st.warning("当前角色没有查看或管理订阅权限。")
        return
    plan = current_plan(company)
    days = trial_days_left(company)
    st.markdown(
        f"""
        <div class='notice-box'>
        <b>当前能力：</b>{plan['name']} · <b>状态：</b>{company['subscription_status']} · <b>试用剩余：</b>{days} 天<br>
        <span class='orbi-small'>我们将套餐收敛为免费版和会员版，价格保持低门槛，优先让用户觉得产品真的有用、值得长期使用。</span><br>
        <span class='orbi-small'>遇到支付或使用问题，请联系：<b>{CONTACT_EMAIL}</b></span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### 套餐选择")
    cols = st.columns(2)
    for col, pid in zip(cols, PUBLIC_PLANS):
        p = PLANS[pid]
        price_line = "¥0" if pid == "free" else f"¥{MEMBER_PRICE_MONTH}/月 · ¥{MEMBER_PRICE_YEAR}/年"
        with col:
            st.markdown(
                f"""
                <div class='orbi-card'>
                    <h3>{p['name']}</h3>
                    <div class='metric-value'>{price_line}</div>
                    <div class='orbi-muted'>{p['desc']}</div>
                    <div class='orbi-small'>门店上限：{p['stores']}</div>
                    <div class='orbi-small'>成员上限：{p['members']}</div>
                    <div class='orbi-small'>单次文件上限：{p['files_per_run']}</div>
                    <div class='orbi-small'>API：{'支持' if p['api'] else '不支持'}</div>
                    <div class='orbi-small'>私有化资料：{'支持' if p['private_deploy'] else '不支持'}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if pid == "member" and st.button("选择会员版", key="choose_plan_member", use_container_width=True):
                st.session_state["chosen_plan"] = "member"
            if pid == "free" and st.button("切换/保留免费版", key="choose_plan_free", use_container_width=True):
                conn = db()
                conn.execute("UPDATE companies SET plan=?, subscription_status=? WHERE id=?", ("free", "free", company["id"]))
                conn.commit()
                conn.close()
                st.success("已切换为免费版。你仍可继续使用基础能力。")
                st.rerun()

    st.markdown("#### 生成会员付款申请")
    c1, c2, c3 = st.columns(3)
    with c1:
        selected_plan = st.selectbox("套餐", ["member"], format_func=lambda x: PLANS[x]["name"], key="bill_plan")
    with c2:
        cycle = st.selectbox("周期", ["monthly", "yearly"], format_func=lambda x: {"monthly": "月付", "yearly": "年付"}[x], key="bill_cycle")
    with c3:
        method = st.selectbox("支付方式", PAYMENT_PROVIDERS, key="bill_method")
    amount = MEMBER_PRICE_MONTH if cycle == "monthly" else MEMBER_PRICE_YEAR
    st.info(f"当前付款申请金额：¥{amount}。当前版本完成正式支付接入准备，真实收费时需要接入对应支付平台的签名、回调和对账。")

    with st.expander("正式支付接入准备清单", expanded=True):
        st.markdown(
            f"""
            - 微信支付回调预留：`{PAYMENT_WEBHOOKS['微信支付']}`
            - 支付宝回调预留：`{PAYMENT_WEBHOOKS['支付宝']}`
            - Stripe Webhook 预留：`{PAYMENT_WEBHOOKS['Stripe']}`
            - 支付成功后更新：`payment_requests.status = paid`，并将企业 `subscription_status` 更新为 `active`
            - 支付失败/取消：保留免费版能力，不强制中断用户试用体验
            - 客服邮箱：`{CONTACT_EMAIL}`
            """
        )

    conn = db()
    if st.button("生成付款申请", key="create_payment", use_container_width=True):
        conn.execute(
            "INSERT INTO payment_requests(company_id,plan,billing_cycle,payment_method,amount,status,created_at,note) VALUES(?,?,?,?,?,?,?,?)",
            (company["id"], selected_plan, cycle, method, amount, "pending", now_iso(), "Batch40 payment integration prep"),
        )
        conn.commit()
        st.success("付款申请已生成。正式环境中这里会跳转微信/支付宝/Stripe 支付页面。")
        st.rerun()
    reqs = conn.execute("SELECT * FROM payment_requests WHERE company_id=? ORDER BY id DESC", (company["id"],)).fetchall()
    if reqs:
        st.markdown("#### 付款申请记录")
        st.dataframe(pd.DataFrame([dict(r) for r in reqs]), use_container_width=True)
        latest = reqs[0]
        if latest["status"] == "pending":
            st.warning("MVP 测试：下面按钮用于模拟支付成功。正式商业环境必须由真实支付平台回调更新状态。")
            if st.button("模拟支付成功并升级会员版", key="mock_pay_success", use_container_width=True):
                months = 1 if latest["billing_cycle"] == "monthly" else 12
                sub_end = (dt.datetime.now() + dt.timedelta(days=30 * months)).isoformat()
                conn.execute("UPDATE payment_requests SET status='paid', paid_at=? WHERE id=?", (now_iso(), latest["id"]))
                conn.execute("UPDATE companies SET plan=?, subscription_status='active', subscription_end=? WHERE id=?", ("member", sub_end, company["id"]))
                conn.execute("INSERT INTO payment_events(payment_request_id,provider,event_type,payload_json,verify_status,created_at) VALUES(?,?,?,?,?,?)", (latest["id"], latest["payment_method"], "mock_paid", json.dumps(dict(latest), ensure_ascii=False), "verified", now_iso()))
                conn.commit()
                st.success("已模拟支付成功，已升级为会员版。")
                st.rerun()
    conn.close()



# -----------------------------------------------------------------------------
# API and private deployment
# -----------------------------------------------------------------------------
def render_api_private_page(user: sqlite3.Row, company: sqlite3.Row) -> None:
    st.markdown("<div class='orbi-section-title'>API 接入与企业私有化</div>", unsafe_allow_html=True)
    plan = current_plan(company)
    api_allowed = bool(plan["api"])
    private_allowed = bool(plan["private_deploy"])
    tab_api, tab_private, tab_db = st.tabs(["API 接入", "企业私有化", "正式数据库"])
    with tab_api:
        if not has_perm(user, "api"):
            st.warning("当前角色没有 API 管理权限。")
        elif not api_allowed:
            st.warning("当前套餐不支持 API 接入。请升级会员版。")
        else:
            st.markdown("API Key 用于未来 FastAPI 服务访问。当前 Streamlit 版本提供密钥管理和接口规范，正式 REST API 需部署 api_server.py。")
            name = st.text_input("API Key 名称", value="ERP/POS 接入", key="api_key_name")
            conn = db()
            if st.button("生成 API Key", key="create_api_key", use_container_width=True):
                raw = "orbi_" + secrets.token_urlsafe(32)
                token_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
                preview = raw[:10] + "..." + raw[-6:]
                conn.execute(
                    "INSERT INTO api_keys(company_id,name,token_hash,token_preview,status,created_at) VALUES(?,?,?,?,?,?)",
                    (company["id"], name, token_hash, preview, "active", now_iso()),
                )
                conn.commit()
                st.success("API Key 已生成。请立刻复制保存，系统不会再次明文显示。")
                st.code(raw)
            keys = conn.execute("SELECT id,name,token_preview,status,created_at,last_used_at FROM api_keys WHERE company_id=? ORDER BY id DESC", (company["id"],)).fetchall()
            if keys:
                st.dataframe(pd.DataFrame([dict(k) for k in keys]), use_container_width=True)
            conn.close()
            openapi = {
                "openapi": "3.0.0",
                "info": {"title": "OrbiRetail API", "version": "batch40-commercial-prep"},
                "paths": {
                    "/health": {"get": {"summary": "健康检查"}},
                    "/analyze": {"post": {"summary": "上传 Excel/CSV 并返回分析结果"}},
                    "/reports/{report_id}": {"get": {"summary": "获取报告摘要"}},
                },
            }
            st.download_button("下载 OpenAPI 草案", data=json.dumps(openapi, ensure_ascii=False, indent=2).encode("utf-8"), file_name="orbiretail_openapi_batch40.json", mime="application/json", key="dl_openapi", use_container_width=True)
            st.code("""curl -X POST https://api.your-domain.com/analyze \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -F "file=@sales.xlsx" \\
  -F "template_id=retail_daily""", language="bash")
    with tab_private:
        if not has_perm(user, "private"):
            st.warning("当前角色没有私有化管理权限。")
        elif not private_allowed:
            st.warning("企业私有化部署资料属于会员版能力。")
        else:
            st.markdown("企业私有化适合处理工资、财务、供应商、客户等敏感数据的客户。")
        private_doc = """
# OrbiRetail 企业私有化部署说明

推荐架构：Nginx + Streamlit/FastAPI + PostgreSQL + 对象存储。

适用场景：企业内部部署、内网访问、数据不出企业网络。

步骤：
1. 准备服务器。
2. 安装 Docker / Docker Compose。
3. 配置数据库密码和管理员账号。
4. 启动服务。
5. 配置 HTTPS。
6. 导入业务模板。
"""
        compose = """
version: "3.9"
services:
  orbiretail-web:
    image: python:3.11-slim
    working_dir: /app
    volumes:
      - ./:/app
      - orbiretail_data:/app/saas_data
    command: sh -c "pip install -r requirements.txt && streamlit run app.py --server.address=0.0.0.0 --server.port=8501"
    ports:
      - "8501:8501"
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: orbiretail
      POSTGRES_USER: orbiretail
      POSTGRES_PASSWORD: change_me
volumes:
  orbiretail_data:
"""
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("下载私有化部署说明", data=private_doc.encode("utf-8"), file_name="OrbiRetail_企业私有化部署说明.md", mime="text/markdown", key="dl_private_doc", use_container_width=True)
        with c2:
            st.download_button("下载 docker-compose 示例", data=compose.encode("utf-8"), file_name="docker-compose.yml", mime="text/yaml", key="dl_compose", use_container_width=True)
    with tab_db:
        st.markdown("#### 正式数据库状态")
        st.markdown(f"当前数据库文件：`{DB_PATH}`")
        conn = db()
        stats = []
        for table in ["companies", "users", "sessions", "payment_requests", "payment_events", "api_keys", "reports", "feedback", "db_migrations", "admin_audit_logs"]:
            count = conn.execute(f"SELECT COUNT(*) AS c FROM {table}").fetchone()["c"]
            stats.append({"数据表": table, "记录数": count})
        conn.close()
        st.dataframe(pd.DataFrame(stats), use_container_width=True)
        st.info("当前为 SQLite 正式数据库雏形，适合 MVP 和早期试用。正式商业版建议升级 PostgreSQL/Supabase，并增加备份、审计和迁移脚本。")


# -----------------------------------------------------------------------------
# Report center and mobile report
# -----------------------------------------------------------------------------
def fetch_reports(company_id: int) -> List[sqlite3.Row]:
    conn = db()
    rows = conn.execute("SELECT * FROM reports WHERE company_id=? ORDER BY id DESC LIMIT 100", (company_id,)).fetchall()
    conn.close()
    return rows


def render_reports_page(user: sqlite3.Row, company: sqlite3.Row) -> None:
    st.markdown("<div class='orbi-section-title'>报告中心</div>", unsafe_allow_html=True)
    rows = fetch_reports(company["id"])
    if not rows:
        st.info("暂无历史报告。请先在工作台运行一次样例或上传数据。")
        return
    df = pd.DataFrame([dict(r) for r in rows])
    st.dataframe(df[["id", "template_name", "report_title", "trust_score", "total_rows", "total_amount", "net_amount", "issue_count", "created_at"]], use_container_width=True)


def render_mobile_page(user: sqlite3.Row, company: sqlite3.Row) -> None:
    st.markdown("<div class='orbi-section-title'>手机端报告查看</div>", unsafe_allow_html=True)
    st.markdown("<div class='orbi-section-subtitle'>适合老板或区域负责人用手机快速查看经营摘要。当前页面已做响应式卡片适配。</div>", unsafe_allow_html=True)
    rows = fetch_reports(company["id"])
    if not rows:
        st.info("暂无可查看报告。请先运行样例体验或上传数据。")
        return
    for r in rows[:10]:
        summary = json.loads(r["summary_json"])
        metrics = summary.get("metrics", {})
        diagnosis = summary.get("diagnosis", [])
        st.markdown(
            f"""
            <div class='mobile-report-card'>
              <h3>{r['template_name']}</h3>
              <div class='orbi-small'>{r['created_at']} · 报告ID #{r['id']}</div>
              <div style='display:flex; gap:10px; flex-wrap:wrap; margin-top:12px;'>
                <span class='plan-badge'>可信度 {r['trust_score']}/100</span>
                <span class='role-badge'>净额 {money(r['net_amount'])}</span>
                <span class='role-badge'>问题 {r['issue_count']} 条</span>
              </div>
              <p class='orbi-muted'>{diagnosis[0] if diagnosis else ''}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# -----------------------------------------------------------------------------
# Feedback
# -----------------------------------------------------------------------------
def render_feedback_page(user: sqlite3.Row, company: sqlite3.Row) -> None:
    st.markdown("<div class='orbi-section-title'>用户反馈入口</div>", unsafe_allow_html=True)
    category = st.selectbox("反馈类型", ["使用卡点", "模板建议", "数据结果问题", "界面体验", "付费意愿", "API/私有化需求", "其他"], key="feedback_category")
    content = st.text_area("反馈内容", placeholder="请描述你卡在哪里、希望新增什么模板、报告哪里不准确，或是否愿意付费。", key="feedback_content", height=150)
    if st.button("提交反馈", key="submit_feedback", use_container_width=True):
        if not content.strip():
            st.error("请填写反馈内容。")
        else:
            conn = db()
            conn.execute("INSERT INTO feedback(company_id,user_id,category,content,created_at) VALUES(?,?,?,?,?)", (company["id"], user["id"], category, content.strip(), now_iso()))
            conn.commit()
            conn.close()
            st.success("反馈已提交。")


# -----------------------------------------------------------------------------
# Admin console and migration plan
# -----------------------------------------------------------------------------
def postgres_schema_sql() -> str:
    return """
-- OrbiRetail Batch 40 PostgreSQL migration draft
CREATE TABLE companies (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    plan TEXT NOT NULL DEFAULT 'free',
    trial_start TIMESTAMPTZ NOT NULL,
    trial_end TIMESTAMPTZ NOT NULL,
    subscription_status TEXT NOT NULL DEFAULT 'trialing',
    subscription_end TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    company_id BIGINT NOT NULL REFERENCES companies(id),
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'admin',
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE payment_requests (
    id BIGSERIAL PRIMARY KEY,
    company_id BIGINT NOT NULL REFERENCES companies(id),
    plan TEXT NOT NULL,
    billing_cycle TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    amount INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    paid_at TIMESTAMPTZ,
    note TEXT
);
CREATE TABLE payment_events (
    id BIGSERIAL PRIMARY KEY,
    payment_request_id BIGINT REFERENCES payment_requests(id),
    provider TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload_json JSONB NOT NULL,
    verify_status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE reports (
    id BIGSERIAL PRIMARY KEY,
    company_id BIGINT NOT NULL REFERENCES companies(id),
    user_id BIGINT NOT NULL REFERENCES users(id),
    template_id TEXT NOT NULL,
    template_name TEXT NOT NULL,
    report_title TEXT NOT NULL,
    trust_score INTEGER NOT NULL,
    total_rows INTEGER NOT NULL,
    total_amount NUMERIC(18,2) NOT NULL,
    net_amount NUMERIC(18,2) NOT NULL,
    issue_count INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    summary_json JSONB NOT NULL
);
""".strip()


def migration_plan_md() -> str:
    return f"""
# OrbiRetail Batch 40 数据库迁移方案

当前 Streamlit MVP 使用 SQLite：`{DB_PATH}`。正式商业版建议迁移到 PostgreSQL / Supabase / 阿里云 RDS。

## 推荐迁移步骤

1. 冻结当前版本，备份 `saas_data/orbiretail.db`。
2. 使用 `postgresql_schema.sql` 创建生产数据库表。
3. 导出 SQLite 数据：companies、users、reports、feedback、payment_requests、api_keys。
4. 导入 PostgreSQL，校验记录数和关键字段。
5. 配置 `DATABASE_URL`，让正式 API/后台读取 PostgreSQL。
6. 先灰度 1-3 个企业账号，再迁移全部用户。
7. 保留 SQLite 备份至少 30 天。

## 风险控制

- 支付状态、用户账号、报告记录必须先备份再迁移。
- 迁移前不要删除旧数据库。
- 生产库需开启每日备份。
- 反馈包和报告包建议进入对象存储，不再长期放 Streamlit 临时目录。

## 联系方式

遇到迁移、支付、账号问题，请联系：{CONTACT_EMAIL}
""".strip()


def render_admin_console(user: sqlite3.Row, company: sqlite3.Row) -> None:
    st.markdown("<div class='orbi-section-title'>管理员后台</div>", unsafe_allow_html=True)
    if user["role"] != "admin":
        st.warning("仅管理员可访问后台。")
        return
    st.markdown(f"<div class='contact-strip'><b>运营联系邮箱：</b>{CONTACT_EMAIL} · 用于用户无法解决问题、支付核查、数据库迁移和企业部署支持。</div>", unsafe_allow_html=True)
    conn = db()
    tab_overview, tab_users, tab_payments, tab_feedback, tab_migration = st.tabs(["总览", "用户/企业", "支付/订阅", "反馈", "数据库迁移"])
    with tab_overview:
        tables = ["companies", "users", "payment_requests", "payment_events", "api_keys", "reports", "feedback"]
        cards = []
        for table in tables:
            try:
                count = conn.execute(f"SELECT COUNT(*) AS c FROM {table}").fetchone()["c"]
            except Exception:
                count = 0
            cards.append((table, count))
        cols = st.columns(4)
        for i, (name, count) in enumerate(cards):
            with cols[i % 4]:
                st.markdown(f"<div class='metric-card'><div class='metric-label'>{name}</div><div class='metric-value'>{count}</div></div>", unsafe_allow_html=True)
        st.info("这个后台用于早期运营管理。正式商业版建议单独做管理端，并增加操作审计、角色审批和导出脱敏。")
    with tab_users:
        rows = conn.execute("""
            SELECT users.id AS user_id, users.email, users.role, users.status, users.created_at,
                   companies.id AS company_id, companies.name AS company_name, companies.plan, companies.subscription_status, companies.trial_end, companies.subscription_end
            FROM users JOIN companies ON users.company_id = companies.id
            ORDER BY users.id DESC
        """).fetchall()
        if rows:
            st.dataframe(pd.DataFrame([dict(r) for r in rows]), use_container_width=True)
        else:
            st.info("暂无用户。")
        with st.expander("快速调整企业套餐/状态（测试用）", expanded=False):
            company_ids = [r["company_id"] for r in rows] if rows else []
            if company_ids:
                cid = st.selectbox("企业ID", sorted(set(company_ids)), key="admin_company_id")
                new_plan = st.selectbox("套餐", ["free", "member"], format_func=lambda x: PLANS[x]["name"], key="admin_plan")
                new_status = st.selectbox("订阅状态", ["trialing", "free", "active", "past_due", "canceled"], key="admin_status")
                if st.button("更新企业套餐/状态", key="admin_update_company", use_container_width=True):
                    conn.execute("UPDATE companies SET plan=?, subscription_status=? WHERE id=?", (new_plan, new_status, cid))
                    conn.execute("INSERT INTO admin_audit_logs(user_id,action,target_type,target_id,detail,created_at) VALUES(?,?,?,?,?,?)", (user["id"], "update_company_subscription", "company", str(cid), f"plan={new_plan}, status={new_status}", now_iso()))
                    conn.commit()
                    st.success("已更新。")
                    st.rerun()
    with tab_payments:
        reqs = conn.execute("SELECT * FROM payment_requests ORDER BY id DESC LIMIT 200").fetchall()
        if reqs:
            st.dataframe(pd.DataFrame([dict(r) for r in reqs]), use_container_width=True)
        else:
            st.info("暂无付款申请。")
        st.markdown("#### 支付回调预留地址")
        st.json(PAYMENT_WEBHOOKS)
        st.markdown("#### 支付事件")
        events = conn.execute("SELECT * FROM payment_events ORDER BY id DESC LIMIT 100").fetchall()
        if events:
            st.dataframe(pd.DataFrame([dict(e) for e in events]), use_container_width=True)
        else:
            st.caption("暂无支付事件。")
    with tab_feedback:
        rows = conn.execute("SELECT * FROM feedback ORDER BY id DESC LIMIT 200").fetchall()
        if rows:
            st.dataframe(pd.DataFrame([dict(r) for r in rows]), use_container_width=True)
        else:
            st.info("暂无反馈。")
    with tab_migration:
        st.markdown("#### 正式数据库迁移方案")
        st.markdown(migration_plan_md())
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("下载 PostgreSQL 建表 SQL", data=postgres_schema_sql().encode("utf-8"), file_name="postgresql_schema_batch40.sql", mime="text/sql", key="dl_pg_schema_admin", use_container_width=True)
        with c2:
            st.download_button("下载数据库迁移方案", data=migration_plan_md().encode("utf-8"), file_name="OrbiRetail_数据库迁移方案_Batch40.md", mime="text/markdown", key="dl_migration_admin", use_container_width=True)
        st.markdown("#### 当前 SQLite 表记录数")
        stats = []
        for table in ["companies", "users", "sessions", "payment_requests", "payment_events", "api_keys", "reports", "feedback", "db_migrations", "admin_audit_logs"]:
            try:
                count = conn.execute(f"SELECT COUNT(*) AS c FROM {table}").fetchone()["c"]
                stats.append({"数据表": table, "记录数": count})
            except Exception as exc:
                stats.append({"数据表": table, "记录数": 0, "备注": str(exc)})
        st.dataframe(pd.DataFrame(stats), use_container_width=True)
    conn.close()

# -----------------------------------------------------------------------------
# Main app
# -----------------------------------------------------------------------------
def render_home(user: sqlite3.Row, company: sqlite3.Row) -> None:
    inject_css()
    render_topbar(user, company)
    st.write("")
    st.markdown(
        """
        <div class='orbi-hero'>
            <h1>AI 驱动的经营分析与教育智能工作台。</h1>
            <p>Batch 44 新增真实大模型接入预留，支持 OpenAI、通义千问、智谱、DeepSeek。AI 可以基于上传数据生成字段映射建议、异常解释、经营摘要、未来趋势预测、客服回复、报告配置，并增强高校作业批改、学生成长画像和班级风险预警。</p>
            <div class='orbi-pill-row'>
                <span class='orbi-pill'>真实大模型接入</span>
                <span class='orbi-pill'>AI 作业批改增强</span>
                <span class='orbi-pill'>经营预测与建议</span>
                <span class='orbi-pill'>免费版 + 低价会员版</span>
                <span class='orbi-pill'>角色权限</span>
                <span class='orbi-pill'>数据库迁移方案</span>
                <span class='orbi-pill'>API 接入</span>
                <span class='orbi-pill'>管理员后台</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    tabs = st.tabs(["工作台", "AI智能中心", "AI作业批改", "模板中心", "报告中心", "团队与权限", "订阅与支付", "API / 私有化", "手机报告", "管理员后台", "反馈"])
    with tabs[0]:
        render_workbench(user, company)
    with tabs[1]:
        render_ai_intelligence_center(user, company)
    with tabs[2]:
        render_assignment_grading_page(user, company)
    with tabs[3]:
        render_template_picker()
    with tabs[4]:
        render_reports_page(user, company)
    with tabs[5]:
        render_team_page(user, company)
    with tabs[6]:
        render_billing_page(user, company)
    with tabs[7]:
        render_api_private_page(user, company)
    with tabs[8]:
        render_mobile_page(user, company)
    with tabs[9]:
        render_admin_console(user, company)
    with tabs[10]:
        render_feedback_page(user, company)


def main() -> None:
    inject_css()
    user, company = get_current_context()
    if not user or not company:
        render_login_page()
    else:
        render_home(user, company)


if __name__ == "__main__":
    main()
