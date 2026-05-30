# Batch 47：真实支付回调验签与财务对账说明

## 1. 核心原则

正式收费不能依赖前端按钮或人工输入“已支付”。必须由支付平台回调经过验签后，再更新订单和会员状态。

处理顺序：

1. 接收支付平台回调。
2. 验证签名 / 证书 / endpoint secret。
3. 校验内部订单号是否存在。
4. 校验订单金额是否一致。
5. 校验支付状态是否为成功。
6. 处理幂等：重复回调只记录，不重复开通。
7. 保存平台交易号。
8. 开通 / 续期会员。
9. 生成对账记录。

## 2. 微信支付

需要配置：

- 商户号 mchid
- 商户 API 证书
- API v3 Key
- 微信支付平台证书
- 回调地址

API v3 回调通常需要读取这些 Header：

- Wechatpay-Timestamp
- Wechatpay-Nonce
- Wechatpay-Signature
- Wechatpay-Serial

通过平台证书进行 RSA-SHA256 验签，验签通过后再解密 resource，并校验订单和金额。

## 3. 支付宝

需要配置：

- app_id
- 商户私钥
- 支付宝公钥 / 证书
- notify_url

收到异步通知后，必须先验签，再校验：

- out_trade_no
- trade_no
- total_amount
- trade_status
- seller_id / app_id

## 4. Stripe

需要配置：

- Stripe Secret Key
- Webhook Endpoint Secret
- Checkout Session 或 Subscription

处理 Stripe webhook 时，必须使用原始请求体、Stripe-Signature header 和 endpoint secret 验证事件来源。

## 5. 结算账户说明

Aurevia 智策云不能直接替你绑定微信、支付宝或 Stripe 的银行结算账户。真实资金会进入你在对应支付平台后台绑定的商户结算账户。

本系统负责记录：

- 商户号
- 结算账户掩码
- 内部订单号
- 平台交易号
- 支付金额
- 回调验签状态
- 会员开通状态
- 对账导出报表

## 6. 财务纠纷预防

必须保留：

- 内部订单号
- 平台交易号
- 原始回调摘要
- 验签结果
- 金额校验结果
- 管理员操作记录
- 退款 / 取消订阅记录

