CREATE DATABASE IF NOT EXISTS smart_ecommerce_agent
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE smart_ecommerce_agent;

DROP TABLE IF EXISTS tracks;

CREATE TABLE tracks (
    id INT NOT NULL AUTO_INCREMENT COMMENT '物流轨迹ID',
    tracking_no VARCHAR(50) NOT NULL COMMENT '物流单号',
    track_time DATETIME NOT NULL COMMENT '物流时间',
    node VARCHAR(100) NOT NULL COMMENT '物流节点',
    description VARCHAR(255) NOT NULL COMMENT '物流描述',
    PRIMARY KEY (id),
    INDEX idx_tracking_no (tracking_no),
    INDEX idx_track_time (track_time)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='物流轨迹表';

INSERT INTO tracks
    (tracking_no, track_time, node, description)
VALUES

-- ORD202609180001：已签收
('SF1234567890', '2026-09-15 16:20:00', '深圳宝安集散中心', '已到达深圳宝安集散中心'),
('SF1234567890', '2026-09-16 08:35:00', '深圳转运中心', '已从深圳转运中心发出'),
('SF1234567890', '2026-09-17 10:10:00', '广州白云营业部', '已到达广州白云营业部'),
('SF1234567890', '2026-09-18 09:25:00', '广州白云派送点', '正在派送'),
('SF1234567890', '2026-09-18 14:36:00', '用户地址', '快件已签收'),

-- ORD202609180002：运输中
('YT2345678901', '2026-09-16 18:10:00', '上海浦东分拨中心', '已揽收'),
('YT2345678901', '2026-09-17 07:40:00', '上海转运中心', '已从上海转运中心发出'),
('YT2345678901', '2026-09-18 11:20:00', '南京转运中心', '已到达南京转运中心'),
('YT2345678901', '2026-09-19 07:15:00', '南京转运中心', '运输中，下一站杭州'),

-- ORD202609180003：已发货
('JD3456789012', '2026-09-17 13:00:00', '北京仓库', '商品已出库'),
('JD3456789012', '2026-09-17 19:25:00', '北京物流中心', '已到达北京物流中心'),
('JD3456789012', '2026-09-18 08:45:00', '北京物流中心', '已发往下一站'),

-- ORD202609180005：已签收
('SF4567890123', '2026-09-18 09:30:00', '杭州仓库', '已揽收'),
('SF4567890123', '2026-09-18 15:20:00', '杭州转运中心', '已到达杭州转运中心'),
('SF4567890123', '2026-09-19 08:10:00', '用户地址', '快件已签收');

