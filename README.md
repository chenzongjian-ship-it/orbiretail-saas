# Batch 47：真实支付回调验签 + 订单对账后台 + 会员生命周期自动化

本版本在 Batch 46 基础上增强支付与财务风控能力。

## Streamlit 主应用

上传覆盖到 GitHub / Streamlit Cloud：

```text
app.py
requirements.txt
README.md
.streamlit/config.toml
```

运行：

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 本批新增

- 微信支付回调验签方案与 FastAPI webhook 示例
- 支付宝异步通知验签方案与 webhook 示例
- Stripe webhook 验签方案
- 订单金额校验
- 支付失败 / 重复回调幂等处理
- 会员自动续期记录
- 会员到期自动降级检查
- 管理员对账报表
- 退款 / 取消订阅记录
- 平台结算账户绑定记录页

## 重要说明：结算账户绑定

我无法替你直接绑定微信支付、支付宝或 Stripe 的结算账户。真实绑定必须在对应平台商户后台完成实名认证、商户审核、合同签约和银行账户配置。本系统只记录你的商户号、结算主体、账户尾号掩码和财务联系人，用于内部核查。

## FastAPI 支付回调服务

Streamlit Cloud 默认只运行 `app.py`，不会运行 `api_server.py`。真实支付回调建议单独部署 FastAPI 服务：

```bash
uvicorn api_server:app --host 0.0.0.0 --port 8000
```

回调地址示例：

```text
https://你的API域名/payment/webhook/wechat
https://你的API域名/payment/webhook/alipay
https://你的API域名/payment/webhook/stripe
```

## Secrets / 环境变量示例

### Stripe

```text
STRIPE_WEBHOOK_SECRET=whsec_xxx
```

### 支付宝

```text
ALIPAY_PUBLIC_KEY="-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----"
```

### 微信支付 API v3

```text
WECHATPAY_PLATFORM_PUBLIC_KEY="-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----"
WECHATPAY_API_V3_KEY=你的APIv3密钥
```

## 财务核查原则

1. 支付平台真实回调必须先验签，再处理业务。
2. 每笔订单必须校验金额，防止低金额伪造回调开通会员。
3. 重复回调必须幂等处理，不得重复开通或重复记账。
4. 系统后台订单对账表只能作为业务核查依据；最终到账以支付平台账单为准。
5. 退款 / 取消订阅必须关联原订单，保留记录。

联系：2790569814@qq.com
