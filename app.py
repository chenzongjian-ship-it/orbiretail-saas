# app.py
# OrbiRetail（奥比零售云）Streamlit SaaS MVP
# 运行：python -m streamlit run app.py
#
# 说明：
# 1. 这是最快上线版本：注册 / 登录 / 7天试用 / 上传 Excel / 自动分析 / 下载结果。
# 2. 这是试用型 SaaS 原型，不是最终商业级认证系统。
# 3. 真正收费前，需要把 SQLite 换成 PostgreSQL / Supabase，并接入正式支付系统。

from __future__ import annotations

import hashlib
import hmac
import io
import sqlite3
import unicodedata
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st

APP_NAME = "OrbiRetail 奥比零售云"
TRIAL_DAYS = 7
DATA_DIR = Path("saas_data")
DB_PATH = DATA_DIR / "orbiretail.db"


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value)


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return unicodedata.normalize("NFKC", str(value)).strip()


def normalize_column_name(name: Any) -> str:
    text = normalize_text(name)
    text = text.replace("\n", "").replace("\r", "").replace(" ", "")
    return text.lower()


def make_salt() -> str:
    return secrets.token_hex(16)


def hash_password(password: str, salt: str) -> str:
    raw = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        120_000,
    )
    return raw.hex()


def verify_password(password: str, salt: str, password_hash: str) -> bool:
    return hmac.compare_digest(hash_password(password, salt), password_hash)


def get_conn() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                company TEXT NOT NULL,
                tenant_id TEXT NOT NULL,
                salt TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                plan TEXT NOT NULL DEFAULT 'trial',
                created_at TEXT NOT NULL,
                trial_start TEXT NOT NULL,
                trial_end TEXT NOT NULL,
                last_login_at TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS analysis_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                tenant_id TEXT NOT NULL,
                template_name TEXT NOT NULL,
                filename TEXT NOT NULL,
                row_count INTEGER NOT NULL,
                amount_total REAL,
                trust_score REAL,
                created_at TEXT NOT NULL
            )
            """
        )


def register_user(email: str, company: str, password: str) -> Tuple[bool, str]:
    email = email.strip().lower()
    company = company.strip()

    if not email or "@" not in email:
        return False, "请输入有效邮箱。"
    if not company:
        return False, "请输入公司或门店名称。"
    if len(password) < 8:
        return False, "密码至少 8 位。"

    salt = make_salt()
    password_hash = hash_password(password, salt)
    trial_start = now_utc()
    trial_end = trial_start + timedelta(days=TRIAL_DAYS)
    tenant_id = f"tenant_{secrets.token_hex(8)}"

    try:
        with get_conn() as conn:
            conn.execute(
                """
                INSERT INTO users (
                    email, company, tenant_id, salt, password_hash, plan,
                    created_at, trial_start, trial_end
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    email,
                    company,
                    tenant_id,
                    salt,
                    password_hash,
                    "trial",
                    iso(trial_start),
                    iso(trial_start),
                    iso(trial_end),
                ),
            )
        return True, "注册成功，请登录。"
    except sqlite3.IntegrityError:
        return False, "该邮箱已经注册，请直接登录。"


def login_user(email: str, password: str) -> Tuple[bool, str, Optional[sqlite3.Row]]:
    email = email.strip().lower()
    with get_conn() as conn:
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if not user:
            return False, "账号不存在。", None
        if not verify_password(password, user["salt"], user["password_hash"]):
            return False, "密码错误。", None
        conn.execute(
            "UPDATE users SET last_login_at = ? WHERE id = ?",
            (iso(now_utc()), user["id"]),
        )
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user["id"],)).fetchone()
    return True, "登录成功。", user


def save_run(user_id: int, tenant_id: str, template_name: str, filename: str, row_count: int, amount_total: Optional[float], trust_score: Optional[float]) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO analysis_runs (
                user_id, tenant_id, template_name, filename, row_count,
                amount_total, trust_score, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                tenant_id,
                template_name,
                filename,
                int(row_count),
                None if amount_total is None else float(amount_total),
                None if trust_score is None else float(trust_score),
                iso(now_utc()),
            ),
        )


def trial_info(user: Dict[str, Any]) -> Dict[str, Any]:
    trial_end = parse_iso(user["trial_end"])
    remaining = trial_end - now_utc()
    return {
        "trial_end": trial_end,
        "days_left": max(0, remaining.days),
        "hours_left": max(0, int(remaining.total_seconds() // 3600)),
        "expired": remaining.total_seconds() <= 0 and user["plan"] == "trial",
    }


FIELD_ALIASES = {
    "日期": ["日期", "业务日期", "销售日期", "支付时间", "结算时间", "date"],
    "月份": ["月份", "月", "month"],
    "门店": ["门店", "门店名称", "店铺", "店名", "store"],
    "区域": ["区域", "大区", "城市", "region"],
    "渠道": ["渠道", "平台", "销售渠道", "来源", "channel", "platform"],
    "订单号": ["订单号", "订单编号", "交易号", "业务单号", "orderid", "order_id"],
    "单据类型": ["单据类型", "类型", "业务类型", "订单类型", "doctype"],
    "品类": ["品类", "类别", "商品类别", "category"],
    "商品": ["商品", "商品名称", "产品", "product", "sku"],
    "订单数": ["订单数", "单数", "笔数", "orders"],
    "数量": ["数量", "件数", "销量", "qty", "quantity"],
    "金额": ["金额", "销售额", "应收金额", "订单金额", "amount", "sales"],
    "实收金额": ["实收金额", "实付金额", "支付金额", "结算金额", "netamount", "net_amount"],
    "退款金额": ["退款金额", "退款", "refund", "refundamount"],
    "佣金": ["佣金", "平台佣金", "服务费", "commission"],
    "优惠金额": ["优惠金额", "折扣金额", "平台优惠", "门店优惠", "discount"],
}


def build_alias_map() -> Dict[str, str]:
    alias_map: Dict[str, str] = {}
    for standard, aliases in FIELD_ALIASES.items():
        alias_map[normalize_column_name(standard)] = standard
        for alias in aliases:
            alias_map[normalize_column_name(alias)] = standard
    return alias_map


def map_columns(df: pd.DataFrame) -> pd.DataFrame:
    alias_map = build_alias_map()
    rename: Dict[str, str] = {}
    used: set[str] = set()
    for col in df.columns:
        key = normalize_column_name(col)
        standard = alias_map.get(key)
        if standard and standard not in used:
            rename[col] = standard
            used.add(standard)
    return df.rename(columns=rename).copy()


def read_uploaded_file(uploaded_file) -> pd.DataFrame:
    filename = uploaded_file.name.lower()
    if filename.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    if filename.endswith((".xlsx", ".xlsm", ".xls")):
        excel = pd.ExcelFile(uploaded_file)
        return pd.read_excel(excel, sheet_name=excel.sheet_names[0])
    raise ValueError("仅支持 .xlsx / .xlsm / .xls / .csv 文件。")


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [normalize_text(c) for c in df.columns]
    df = map_columns(df)

    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].map(lambda x: normalize_text(x) if pd.notna(x) else "")

    for col in ["金额", "实收金额", "退款金额", "佣金", "优惠金额", "订单数", "数量"]:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.replace("￥", "", regex=False)
                .str.replace("元", "", regex=False)
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "日期" in df.columns:
        df["日期"] = pd.to_datetime(df["日期"], errors="coerce")
        df["月份"] = df["日期"].dt.strftime("%Y-%m")
        df["日期"] = df["日期"].dt.strftime("%Y-%m-%d")

    if "实收金额" not in df.columns and "金额" in df.columns:
        df["实收金额"] = df["金额"]

    if "实收金额" in df.columns:
        df["净销售额"] = df["实收金额"].fillna(0)
        if "退款金额" in df.columns:
            df["净销售额"] = df["净销售额"] - df["退款金额"].fillna(0)
        if "佣金" in df.columns:
            df["净销售额"] = df["净销售额"] - df["佣金"].fillna(0)
        if "优惠金额" in df.columns:
            df["净销售额"] = df["净销售额"] - df["优惠金额"].fillna(0)

    if "单据类型" in df.columns and "实收金额" in df.columns:
        refund_mask = df["单据类型"].astype(str).str.contains("退款|退货|冲销", regex=True, na=False)
        df.loc[refund_mask & (df["实收金额"] > 0), "净销售额"] = -df.loc[refund_mask & (df["实收金额"] > 0), "实收金额"]

    return df


def make_summary(df: pd.DataFrame, template_name: str) -> pd.DataFrame:
    group_candidates = {
        "门店/渠道销售日报汇总": ["日期", "门店", "渠道"],
        "月度费用汇总": ["月份", "门店", "渠道"],
        "销售业绩汇总": ["月份", "区域", "渠道"],
        "通用汇总": ["月份", "门店", "渠道"],
    }
    group_cols = [c for c in group_candidates.get(template_name, ["月份", "门店", "渠道"]) if c in df.columns]
    if not group_cols:
        group_cols = [c for c in ["月份", "日期"] if c in df.columns]
    if not group_cols:
        df = df.copy()
        df["_全部数据"] = "全部"
        group_cols = ["_全部数据"]

    value_col = "净销售额" if "净销售额" in df.columns else "实收金额" if "实收金额" in df.columns else "金额"
    if value_col not in df.columns:
        return pd.DataFrame({"提示": ["未找到金额字段，无法生成金额汇总。"]})

    agg = df.groupby(group_cols, dropna=False)[value_col].agg(["sum", "count", "mean", "max", "min"]).reset_index()
    agg = agg.rename(columns={"sum": "金额合计", "count": "记录数", "mean": "平均金额", "max": "最大金额", "min": "最小金额"})
    return agg.sort_values("金额合计", ascending=False)


def make_diagnosis(df: pd.DataFrame) -> pd.DataFrame:
    issues: List[Dict[str, Any]] = []
    for col in ["日期", "门店", "渠道"]:
        if col not in df.columns:
            issues.append({"级别": "WARNING", "问题": f"缺少字段：{col}", "建议": "检查表头或增加字段别名。"})
        else:
            empty_count = int(df[col].isna().sum() + (df[col].astype(str).str.strip() == "").sum())
            if empty_count:
                issues.append({"级别": "WARNING", "问题": f"{col} 存在空值：{empty_count} 行", "建议": "补齐后再用于正式对账。"})

    if "净销售额" in df.columns:
        neg_count = int((df["净销售额"] < 0).sum())
        if neg_count:
            issues.append({"级别": "INFO", "问题": f"发现负向金额/退款/冲销：{neg_count} 行", "建议": "核对退款或冲销是否属于本期。"})
        zero_count = int((df["净销售额"] == 0).sum())
        if zero_count:
            issues.append({"级别": "WARNING", "问题": f"净销售额为 0：{zero_count} 行", "建议": "检查是否为赠品、冲销或异常订单。"})

    if not issues:
        issues.append({"级别": "OK", "问题": "未发现明显问题", "建议": "可进入下一步复核或报告生成。"})
    return pd.DataFrame(issues)


def trust_score(df: pd.DataFrame) -> Tuple[float, str, pd.DataFrame]:
    score = 100.0
    total = max(len(df), 1)
    rows: List[Dict[str, Any]] = []
    for col, penalty in [("日期", 15), ("门店", 20), ("渠道", 15), ("实收金额", 25)]:
        if col not in df.columns:
            score -= penalty
            rows.append({"检查项": col, "结果": "缺失", "扣分": penalty})
        else:
            empty = int(df[col].isna().sum() + (df[col].astype(str).str.strip() == "").sum())
            ratio = empty / total
            deduct = round(min(penalty, penalty * ratio), 2)
            score -= deduct
            rows.append({"检查项": col, "结果": f"空值 {empty} 行", "扣分": deduct})

    score = max(0.0, min(100.0, round(score, 2)))
    if score >= 85:
        level = "可信"
    elif score >= 65:
        level = "需复核"
    else:
        level = "不可用"
    return score, level, pd.DataFrame(rows)


def to_excel_bytes(sheets: Dict[str, pd.DataFrame]) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        for name, df in sheets.items():
            df.to_excel(writer, sheet_name=name[:31], index=False)
    return buffer.getvalue()


def inject_css() -> None:
    st.markdown(
        """
        <style>
        .main .block-container {max-width: 1180px; padding-top: 2rem;}
        .hero {
            padding: 28px 32px;
            border-radius: 22px;
            background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 55%, #0f766e 100%);
            color: white;
            margin-bottom: 22px;
        }
        .hero h1 {font-size: 38px; margin-bottom: 8px;}
        .hero p {font-size: 17px; opacity: .92;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_landing() -> None:
    st.markdown(
        """
        <div class="hero">
            <h1>OrbiRetail 奥比零售云</h1>
            <p>上传门店 / 渠道销售 Excel，自动完成汇总、对账、利润诊断和经营报告。</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("试用", "7 天", "注册即开通")
    c2.metric("核心场景", "门店日报", "渠道对账")
    c3.metric("输出", "Excel 报告", "经营诊断")
    st.write("适合：连锁门店、零售渠道、区域运营、财务结算、老板经营看板。")


def auth_page() -> None:
    show_landing()
    tab_login, tab_register = st.tabs(["登录", "注册 7 天试用"])
    with tab_login:
        email = st.text_input("邮箱", key="login_email")
        password = st.text_input("密码", type="password", key="login_password")
        if st.button("登录", type="primary"):
            ok, msg, user = login_user(email, password)
            if ok and user:
                st.session_state["user"] = dict(user)
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
    with tab_register:
        company = st.text_input("公司 / 门店名称", key="register_company")
        email = st.text_input("邮箱", key="register_email")
        password = st.text_input("设置密码（至少8位）", type="password", key="register_password")
        if st.button("注册并开始 7 天试用", type="primary"):
            ok, msg = register_user(email, company, password)
            if ok:
                st.success(msg)
            else:
                st.error(msg)


def sidebar_user(user: Dict[str, Any]) -> None:
    info = trial_info(user)
    st.sidebar.title("账户")
    st.sidebar.write(user["company"])
    st.sidebar.caption(user["email"])
    st.sidebar.write(f"套餐：{user['plan']}")
    if user["plan"] == "trial":
        st.sidebar.write(f"试用剩余：{info['hours_left']} 小时")
    if st.sidebar.button("退出登录"):
        st.session_state.pop("user", None)
        st.rerun()


def pricing_page(user: Dict[str, Any]) -> None:
    st.warning("你的 7 天试用已结束。当前版本保留升级入口，后续接入微信支付 / Stripe 后即可自动升级。")
    st.subheader("建议定价")
    col1, col2, col3 = st.columns(3)
    col1.metric("标准版", "¥39/月/门店", "日报汇总 + 基础对账")
    col2.metric("专业版", "¥99/月/门店", "利润诊断 + 老板一页纸")
    col3.metric("企业版", "¥299+/月", "多区域 + 权限 + API")


def analysis_page(user: Dict[str, Any]) -> None:
    st.title("经营数据分析")
    with st.expander("使用说明", expanded=False):
        st.write("上传结构化 Excel。建议字段包含：日期、门店、渠道、订单号、实收金额、退款金额、佣金、优惠金额。")
        st.write("如果字段名不同，系统会尝试用别名自动识别。")

    template_name = st.selectbox("选择场景模板", ["门店/渠道销售日报汇总", "月度费用汇总", "销售业绩汇总", "通用汇总"])
    uploaded = st.file_uploader("上传 Excel / CSV", type=["xlsx", "xlsm", "xls", "csv"])
    if not uploaded:
        st.info("请上传一个 Excel 或 CSV 文件。")
        return

    try:
        raw = read_uploaded_file(uploaded)
        cleaned = clean_dataframe(raw)
        summary = make_summary(cleaned, template_name)
        diagnosis = make_diagnosis(cleaned)
        score, level, trust_df = trust_score(cleaned)

        value_col = "净销售额" if "净销售额" in cleaned.columns else "实收金额" if "实收金额" in cleaned.columns else None
        amount_total = float(cleaned[value_col].fillna(0).sum()) if value_col else None

        save_run(int(user["id"]), user["tenant_id"], template_name, uploaded.name, len(cleaned), amount_total, score)

        st.success("分析完成。")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("数据行数", f"{len(cleaned):,}")
        m2.metric("金额合计", f"{amount_total:,.2f}" if amount_total is not None else "未识别")
        m3.metric("可信度", f"{score:.0f}/100")
        m4.metric("状态", level)

        st.subheader("汇总结果")
        st.dataframe(summary, use_container_width=True)

        if "金额合计" in summary.columns:
            chart_cols = [c for c in summary.columns if c not in ["金额合计", "记录数", "平均金额", "最大金额", "最小金额"]]
            if chart_cols:
                st.bar_chart(summary.head(15).set_index(chart_cols[0])[["金额合计"]])

        st.subheader("经营诊断")
        st.dataframe(diagnosis, use_container_width=True)

        st.subheader("数据可信度")
        st.write(f"评级：**{level}**")
        st.dataframe(trust_df, use_container_width=True)

        with st.expander("查看清洗后的明细"):
            st.dataframe(cleaned, use_container_width=True)

        result_bytes = to_excel_bytes({"明细": cleaned, "汇总": summary, "经营诊断": diagnosis, "数据可信度": trust_df})
        st.download_button(
            "下载分析结果 Excel",
            data=result_bytes,
            file_name=f"OrbiRetail_分析结果_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
        )
    except Exception as exc:
        st.error("分析失败。")
        st.write("建议检查：文件是否为结构化表格、是否有表头、金额列是否可识别。")
        st.exception(exc)


def history_page(user: Dict[str, Any]) -> None:
    st.title("历史分析")
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT template_name, filename, row_count, amount_total, trust_score, created_at
            FROM analysis_runs
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT 100
            """,
            (user["id"],),
        ).fetchall()
    if not rows:
        st.info("暂无历史记录。")
        return
    st.dataframe(pd.DataFrame([dict(r) for r in rows]), use_container_width=True)


def main() -> None:
    st.set_page_config(page_title=APP_NAME, page_icon="📊", layout="wide")
    inject_css()
    init_db()

    if "user" not in st.session_state:
        auth_page()
        return

    user = st.session_state["user"]
    sidebar_user(user)
    info = trial_info(user)
    if info["expired"]:
        pricing_page(user)
        return

    page = st.sidebar.radio("导航", ["经营分析", "历史记录", "升级套餐"])
    if page == "经营分析":
        analysis_page(user)
    elif page == "历史记录":
        history_page(user)
    else:
        pricing_page(user)


if __name__ == "__main__":
    main()
