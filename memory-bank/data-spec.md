# 数据规范说明（Step25~30 口径）

## 1. 数据来源

### 主数据源

1. CityFlow Benchmark
   - 链接：https://www.cityflow-benchmark.org/
   - 用途：交通流与时空占用模式参考。

### 辅助数据源

1. 社区物业脱敏模拟数据
   - 用途：预约行为、业主画像、计费规则模拟。
2. Open Data Parkeren（荷兰 RDW）
   - 用途：开放停车运营数据补充。
3. CityPulse Smart Parking 参考资料
   - 用途：多传感器智慧停车场景对照。
4. Kaggle Parking Lot Occupancy
   - 用途：占用标注与可视化参考。

## 2. Raw 接入层（Step26 增强）

1. `sensor_event_raw`
   - 字段：`event_id`, `slot_id`, `region_id`, `event_ts`, `occupied`, `sensor_source`, `quality_flag`, `business_date`, `hour_bucket`, `created_at`
   - 用途：IoT 车位传感器近真实接入层。

2. `lpr_event_raw`
   - 字段：`event_id`, `plate_hash`, `region_id`, `event_type(in|out)`, `event_ts`, `business_date`, `hour_bucket`, `created_at`
   - 用途：车牌识别事件近真实接入层。
   - 约束：禁止明文车牌落库。

3. `resident_trip_raw`
   - 字段：`raw_id`, `resident_id`, `home_region`, `weekday`, `hour_bucket`, `trip_probability`, `created_at`
   - 用途：业主出行规律近真实接入层。

## 3. 逻辑事实表定义

1. `slot_status_fact`
   - 字段：`slot_id`, `region_id`, `ts`, `occupied`, `sensor_source`, `quality_flag`

2. `vehicle_event_fact`
   - 字段：`event_id`, `plate_hash`, `region_id`, `event_type(in|out)`, `event_ts`

3. `resident_pattern_fact`
   - 字段：`resident_id`, `home_region`, `weekday`, `hour_bucket`, `trip_probability`

4. `reservation_fact`
   - 字段：`reservation_id`, `user_id`, `slot_id`, `window_start`, `window_end`, `status`, `price`

5. `billing_records`
   - 字段：`order_id`, `reservation_id`, `user_id`, `slot_id`, `region_id`, `started_at`, `ended_at`, `billable_minutes`, `estimated_amount`, `final_amount`, `billing_status`, `recognized_on`
   - 说明：共享计费主链数据源；物业收益汇总必须从该表回溯。

6. `geo_catalog`
   - 字段：`region_id`, `slot_id`, `lat`, `lng`, `display_name`, `map_label`
   - 说明：固定地理目录，用于导航页和地图预览。

## 4. 特征与分析输出

1. `forecast_feature_table`
   - 供 LSTM 与基线模型使用的时窗特征表。

2. `dispatch_input_table`
   - 调度输入表（候选车位、供需缺口、惩罚因子）。

3. `step26_occupancy_heatmap_summary.json`
   - 输出：区域占用热度摘要。

4. `step26_vehicle_flow_summary.json`
   - 输出：车辆流入 / 流出摘要。

5. `step26_resident_peak_summary.json`
   - 输出：业主出行高峰摘要。

## 5. 时间范围与频率

1. 预测窗口：未来 15~30 分钟。
2. 演示刷新频率：15 分钟批处理，实时状态走 WebSocket / Polling。
3. 存储时区：基础事件统一 UTC；计费与收益聚合按 `Asia/Shanghai` 业务时区结算。
4. 收益统计粒度：`day + region`。

## 6. 数据清洗与验收规则

1. 按 `(source_id, ts, slot_id/event_id)` 去重。
2. 统一布尔与枚举值格式。
3. 各特征空值策略显式声明。
4. ETL 输出强制带 schema 版本号。
5. 验收态必须 `engine=spark`，不接受 Python fallback 替代通过。
6. 开发态允许 `files/mysql/auto` 多输入模式并存。

## 7. 计费规则冻结口径

1. 时区：`Asia/Shanghai`。
2. 计费单位：`15` 分钟。
3. 舍入规则：不足一个计费块向上取整。
4. 收益确认时点：车辆离场 / 订单完成后确认。
5. 规则引擎版本：`rules engine v1`，按 `region + 时间桶 + 时长` 计算，不含营销活动。

## 8. 合规与隐私

1. 不存储明文车牌，仅存哈希标识。
2. 仅使用脱敏业主属性字段。
3. 论文与答辩材料保留数据来源与引用说明。
