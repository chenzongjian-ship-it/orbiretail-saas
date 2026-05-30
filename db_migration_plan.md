# OrbiRetail Batch 40 数据库迁移方案

当前 Streamlit MVP 使用 SQLite，适合试用和演示。正式商业版建议迁移到 PostgreSQL、Supabase 或阿里云 RDS。

## 迁移步骤

1. 备份 `saas_data/orbiretail.db`。
2. 用 `migrations/postgresql_schema_batch40.sql` 创建 PostgreSQL 表。
3. 导出 SQLite 数据。
4. 导入 PostgreSQL。
5. 校验企业数、用户数、付款记录、报告记录、反馈记录。
6. 配置正式服务的 `DATABASE_URL`。
7. 先灰度少量用户，再迁移全部用户。

## 必须迁移的数据

- companies
- users
- payment_requests
- payment_events
- api_keys
- reports
- feedback

## 不建议长期依赖 Streamlit Cloud 文件系统

Streamlit MVP 可以快速试用，但正式商业版的账号、支付、报告记录不应长期依赖本地文件系统。建议使用 PostgreSQL + 对象存储。

支持邮箱：2790569814@qq.com
