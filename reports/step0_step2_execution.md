# Step 0-2 执行证据

## 执行范围

- Step 0：使用 fallback 样例数据完成数据健康基线。
- Step 1：完成仓库骨架与 compose 基线。
- Step 2：冻结并校验 OpenAPI 接口合同。

## 执行命令与结果

1. 生成 fallback 数据：

```bash
python3 scripts/generate_fallback_data.py --output-dir data/raw
```

结果：`generated=/Users/yanchen/VscodeProject/smart-parking-thesis/data/raw`

2. 数据健康闸门：

```bash
/Users/yanchen/PycharmProjects/quant-value-regression/.venv/bin/python scripts/data_health_check.py \
  --project-root . \
  --schema-config config/data_health_schema.yaml \
  --json-output reports/data_health_report.json \
  --md-output reports/data_health_report.md
```

结果：`overall_passed=True`

3. OpenAPI 合同闸门：

```bash
/Users/yanchen/PycharmProjects/quant-value-regression/.venv/bin/python scripts/validate_openapi.py --spec openapi/smart-parking.yaml
```

结果：`openapi_validation_passed`

4. Compose 语法闸门：

```bash
docker compose -f infra/docker-compose.yml config
```

结果：`COMPOSE_CONFIG_OK`

## 交付物

- `data/raw/slot_status.csv`
- `data/raw/vehicle_event.csv`
- `data/raw/resident_pattern.csv`
- `infra/docker-compose.yml`
- `openapi/smart-parking.yaml`
- `scripts/generate_fallback_data.py`
- `scripts/validate_openapi.py`
- `reports/data_health_report.json`
- `reports/data_health_report.md`

## 备注

- 首个阻塞点为 `/Users/yanchen/VscodeProject` 写权限受限。
- 已通过批准的提权写入命令解决。
