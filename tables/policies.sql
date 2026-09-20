CREATE DATABASE IF NOT EXISTS smart_ecommerce_agent
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE smart_ecommerce_agent;

DROP TABLE IF EXISTS policies;

CREATE TABLE policies (
    policy_id INT NOT NULL AUTO_INCREMENT COMMENT '政策ID',
    scenario VARCHAR(100) NOT NULL COMMENT '售后场景',
    rule TEXT NOT NULL COMMENT '具体规则',
    basis VARCHAR(255) DEFAULT NULL COMMENT '规则依据',
    PRIMARY KEY (policy_id)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='售后政策表';

INSERT INTO policies
    (scenario, rule, basis)
VALUES
(
    '普通商品退货',
    '商品签收后7天内可以申请退货。商品应保持完好，不影响二次销售。',
    '本项目售后模拟规则'
),
(
    '商品质量问题退货',
    '商品存在质量问题时，可以申请退货，不受普通7天退货条件限制，具体以售后审核结果为准。',
    '本项目售后模拟规则'
),
(
    '商品换货',
    '商品签收后7天内可以申请换货。换货商品应保持完好，并提供完整商品及配件。',
    '本项目售后模拟规则'
),
(
    '非质量问题退货运费',
    '因个人原因申请退货的，退回商品产生的运费由用户承担。',
    '本项目售后模拟规则'
),
(
    '质量问题退货运费',
    '因商品质量问题申请退货的，符合售后审核条件时，退货运费由商家承担。',
    '本项目售后模拟规则'
),
(
    '影响二次销售',
    '商品存在明显使用痕迹、损坏、缺失配件或其他影响二次销售的情况，普通退货申请可能无法通过。',
    '本项目售后模拟规则'
),
(
    '超过退货期限',
    '普通商品超过签收后7天，原则上不能申请普通退货；如果存在质量问题，可以进一步申请售后审核。',
    '本项目售后模拟规则'
),
(
    '待发货订单',
    '订单尚未发货时，用户可以先联系商家申请取消订单，不属于已签收商品的普通退货流程。',
    '本项目售后模拟规则'
);