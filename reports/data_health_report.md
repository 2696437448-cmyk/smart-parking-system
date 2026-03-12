# Data Health Report

- generated_at: 2026-03-11T10:08:46.295673+00:00
- overall_passed: True

## Thresholds

- required_completeness_min: 0.98
- duplicate_rate_max: 0.01
- critical_null_rate_max: 0.05
- timestamp_parse_success_min: 0.99

## Source Results

### slot_status

- exists: True
- path: /Users/yanchen/VscodeProject/smart-parking-thesis/data/raw/slot_status.csv
- row_count: 17280
- column_count: 6
- required_completeness: 1.0000
- duplicate_rate: 0.0000
- critical_null_rate: 0.0000
- timestamp_parse_success: {"ts": 1.0}
- passed: True
- failed_reasons: none

### vehicle_event

- exists: True
- path: /Users/yanchen/VscodeProject/smart-parking-thesis/data/raw/vehicle_event.csv
- row_count: 1728
- column_count: 5
- required_completeness: 1.0000
- duplicate_rate: 0.0000
- critical_null_rate: 0.0000
- timestamp_parse_success: {"event_ts": 1.0}
- passed: True
- failed_reasons: none

### resident_pattern

- exists: True
- path: /Users/yanchen/VscodeProject/smart-parking-thesis/data/raw/resident_pattern.csv
- row_count: 5040
- column_count: 5
- required_completeness: 1.0000
- duplicate_rate: 0.0000
- critical_null_rate: 0.0000
- timestamp_parse_success: {}
- passed: True
- failed_reasons: none
