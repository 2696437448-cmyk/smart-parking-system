# 数据规范说明

## 1. 数据来源

### 主数据源

1. CityFlow Benchmark
   - 链接：https://www.cityflow-benchmark.org/
   - 用途：交通流与时空占用模式参考。

### 辅助数据源

1. 社区物业脱敏模拟数据
   - 链接：https://wenku.csdn.net/doc/2e37929884868762caaed5b91a9d838b
   - 用途：预约行为、业主画像、计费规则模拟。

2. Open Data Parkeren（荷兰 RDW）
   - 链接：https://data.overheid.nl/dataset/11358-open-data-parkeren--parking-open
   - 许可：CC0 1.0
   - 用途：开放停车运营数据补充。

3. CityPulse Smart Parking 参考资料
   - 链接：https://cordis.europa.eu/project/id/690979/reporting
   - 用途：多传感器智慧城市场景对照。

4. Kaggle Parking Lot Occupancy
   - 链接：https://www.kaggle.com/datasets/tunguz/parking-lot-occupancy
   - 用途：占用标注与可视化对照数据。

## 2. 逻辑事实表定义

1. `slot_status_fact`
   - 字段：`slot_id`, `region_id`, `ts`, `occupied`, `sensor_source`, `quality_flag`

2. `vehicle_event_fact`
   - 字段：`event_id`, `plate_hash`, `region_id`, `event_type(in|out)`, `event_ts`

3. `resident_pattern_fact`
   - 字段：`resident_id`, `home_region`, `weekday`, `hour_bucket`, `trip_probability`

4. `reservation_fact`
   - 字段：`reservation_id`, `user_id`, `slot_id`, `window_start`, `window_end`, `status`, `price`

## 3. 特征输出表

1. `forecast_feature_table`
   - 供 LSTM 与基线模型的时窗对齐特征。

2. `dispatch_input_table`
   - 调度输入（候选车位、待分配请求、惩罚项特征）。

## 4. 时间范围与频率

1. 预测窗口：未来 15~30 分钟。
2. 演示刷新频率：15 分钟批处理。
3. 时间规范：存储统一 UTC，前端按本地时区展示。

## 5. 数据清洗规则

1. 按 `(source_id, ts, slot_id/event_id)` 去重。
2. 统一布尔与枚举值格式。
3. 各特征空值策略显式声明。
4. ETL 输出强制带 schema 版本号。

## 6. 合规与隐私

1. 不存储明文车牌，仅存哈希标识。
2. 仅使用脱敏业主属性字段。
3. 论文中保留数据来源与引用说明。
