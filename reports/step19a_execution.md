# Step19A 执行报告

## 目标

1. 将 ETL 验收口径升级为 `Spark strict`。
2. 补齐 `PyYAML + pyspark + Java Runtime` 运行依赖。
3. 保证 OpenAPI 校验在同一依赖环境下可直接通过。

## 实际改动

1. 更新 `requirements-dev.txt`，固定 `PyYAML==6.0.3` 与 `pyspark==3.5.1`。
2. 新增 `scripts/test_step19a_spark_strict.py`，强制执行 `scripts/step11_etl.py --engine spark`。
3. 为 Step19A 测试脚本补充 Homebrew JDK 自动探测逻辑，避免手工配置 `JAVA_HOME`。
4. 生成证据：`reports/step19a_spark_quality.json`。

## 验证命令

```bash
python3 scripts/test_step19a_spark_strict.py
```

## 验证结果

1. 闸门输出：`STEP19A_GATE_PASS`
2. 质量报告：`reports/step19a_spark_quality.json`
3. 核心结论：质量报告中 `engine=spark`，`overall_passed=true`

## 结论

Step19A 通过，ETL 验收已从“Spark 优先 + fallback”升级为“Spark strict 必过”。
