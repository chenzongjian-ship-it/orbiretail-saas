# OrbiRetail Batch 40 正式支付接入准备

本批次将套餐收敛为两种：

- 免费版：0 元，长期可用，适合轻量体验。
- 会员版：19 元/月，199 元/年，开放批量上传、全部模板、报告包、团队协作、API 接入和私有化资料。

## 支付接入顺序

1. 先保留“付款申请”流程，验证试用转会员转化。
2. 接入微信支付或支付宝，生成支付单和支付链接。
3. 支付平台回调后更新 `payment_requests.status=paid`。
4. 更新企业状态：`companies.plan=member`，`subscription_status=active`。
5. 后台记录 `payment_events`，用于对账与排障。

## 回调预留

- 微信支付：`/payment/webhook/wechat`
- 支付宝：`/payment/webhook/alipay`
- Stripe：`/payment/webhook/stripe`

## 风险控制

- 支付回调必须验签。
- 金额、订单号、企业 ID 必须匹配。
- 支付成功后要写入审计记录。
- 退款/取消支付需要保留免费版能力，不要直接让用户无法打开产品。

客服联系邮箱：2790569814@qq.com
