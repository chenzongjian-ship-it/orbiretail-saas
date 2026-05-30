CREATE TABLE IF NOT EXISTS payment_webhook_events (
  id BIGSERIAL PRIMARY KEY,
  event_id TEXT UNIQUE,
  order_no TEXT,
  platform TEXT,
  raw_payload JSONB,
  signature_valid BOOLEAN DEFAULT FALSE,
  amount_valid BOOLEAN DEFAULT FALSE,
  status TEXT,
  processed BOOLEAN DEFAULT FALSE,
  error_message TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS settlement_accounts (
  id BIGSERIAL PRIMARY KEY,
  platform TEXT UNIQUE,
  merchant_id TEXT,
  account_name TEXT,
  settlement_account_masked TEXT,
  contact TEXT,
  enabled BOOLEAN DEFAULT FALSE,
  updated_at TIMESTAMP DEFAULT NOW(),
  note TEXT
);

CREATE TABLE IF NOT EXISTS membership_events (
  id BIGSERIAL PRIMARY KEY,
  company_id BIGINT,
  user_email TEXT,
  event_type TEXT,
  old_plan TEXT,
  new_plan TEXT,
  member_until TIMESTAMP,
  source_order_no TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  note TEXT
);

CREATE TABLE IF NOT EXISTS refund_cancel_records (
  id BIGSERIAL PRIMARY KEY,
  order_no TEXT,
  platform TEXT,
  refund_no TEXT,
  amount NUMERIC(12,2),
  status TEXT,
  reason TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  processed_at TIMESTAMP
);
