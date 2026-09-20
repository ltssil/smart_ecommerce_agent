-- 创建售后工单表

CREATE TABLE IF NOT EXISTS tickets (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
    ticket_no VARCHAR(32) NOT NULL COMMENT '售后工单号',
    order_no VARCHAR(64) NOT NULL COMMENT '订单号',
    issue VARCHAR(500) NOT NULL COMMENT '问题描述',
    status VARCHAR(20) NOT NULL DEFAULT '待处理' COMMENT '工单状态',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    PRIMARY KEY (id),
    UNIQUE KEY uk_ticket_no (ticket_no),
    KEY idx_order_no (order_no)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='售后工单表';