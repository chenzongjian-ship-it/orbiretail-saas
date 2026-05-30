# 支付平台接入配置说明

## 微信支付

需要在微信支付商户平台完成：

- 商户认证
- API v3 密钥配置
- 平台证书 / 平台公钥获取
- 支付回调 URL 配置
- 结算账户配置

本系统 webhook 示例：`/payment/webhook/wechat`。

## 支付宝

需要在支付宝开放平台 / 商户平台完成：

- 商户认证
- 应用创建
- RSA2 密钥配置
- 支付异步通知 URL 配置
- 结算账户配置

本系统 webhook 示例：`/payment/webhook/alipay`。

## Stripe

需要在 Stripe Dashboard 完成：

- 账户注册与身份验证
- 银行账户绑定
- Webhook endpoint 创建
- Webhook signing secret 配置

本系统 webhook 示例：`/payment/webhook/stripe`。
