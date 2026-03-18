# 技术定稿差距矩阵（Step24 口径）

> 目的：统一记录“原始题目要求 / 技术定稿要求 vs 当前实现 vs 证据路径 vs 下一闸门”。

## 1. 架构与服务形态

1. 定稿要求：`Java 主业务微服务 + Python 算法服务 + Vue3 前端 + 单机 Docker Compose 可复现`。
2. 当前实现：`gateway-service`（Java）+ `parking-service`（Java）+ `model-service`（Python）+ `realtime-service`（伴生）+ `frontend-app`（Vue3+TS+Pinia）。
3. 证据路径：
   - `infra/docker-compose.yml`
   - `services/gateway-service/src/main/java/com/smartparking/gateway/*`
   - `services/parking-service/src/main/java/com/smartparking/parking/ParkingServiceApplication.java`
   - `apps/frontend/src/*`
4. 差距判定：基础对齐，需补 Step21 页面化交付与 Step23 默认演示入口。

## 2. 一致性主链路

1. 定稿要求：Redis 幂等 + Redisson 锁 + MySQL 唯一约束。
2. 当前实现：写路径已切换为 Redis 幂等 + Redisson 锁 + MySQL 唯一约束。
3. 证据路径：
   - `scripts/test_step14_java_consistency.py`
   - `reports/step14_execution.md`
4. 差距判定：已对齐，后续仅允许增强，不允许退化。

## 3. 数据工程

1. 定稿要求：PySpark 多源 ETL，产出统一特征表，验收严格走 Spark 主链。
2. 当前实现：Step11 已产出两张特征表，但当前报告仍允许 `Spark 优先 + Python fallback`。
3. 证据路径：
   - `scripts/step11_etl.py`
   - `scripts/test_step11_etl.py`
   - `reports/step11_execution.md`
4. 差距判定：未完全对齐，需 Step19A 将验收提升为 `engine=spark` strict。

## 4. 模型训练与论文对比

1. 定稿要求：轻量 LSTM 训练 + 传统基线模型对比。
2. 当前实现：训练脚本、模型产物、统一指标对比（MAE/RMSE/MAPE）完整。
3. 证据路径：
   - `scripts/step12_train_models.py`
   - `scripts/step12_baseline_model.py`
   - `reports/step12_model_comparison.md`
4. 差距判定：已对齐。

## 5. 调度算法语义

1. 定稿要求：匈牙利算法最小化代价函数，结果可复现。
2. 当前实现：接口名为 Hungarian，但历史实现存在 `小规模暴力 + 大规模贪心`，并使用 Python `hash()` 造成随机漂移。
3. 证据路径：
   - `services/model_service.py`
   - `scripts/test_step5_model_core.py`
4. 差距判定：未完全对齐，需 Step19B 落地确定性真实 Hungarian。

## 6. 模型管理（注册与热切换）

1. 定稿要求：模型注册表 + 激活接口 + 在线热切换回滚。
2. 当前实现：注册、激活、回滚、历史查询均已落地。
3. 证据路径：
   - `scripts/test_step13_model_registry.py`
   - `reports/step13_execution.md`
4. 差距判定：已对齐。

## 7. 网关治理

1. 定稿要求：Spring Cloud Gateway + Resilience4j，固化超时/熔断/降级语义。
2. 当前实现：Gateway 路由 + CircuitBreaker + fallback 语义完整。
3. 证据路径：
   - `scripts/test_step15_gateway_governance.py`
   - `reports/step15_execution.md`
4. 差距判定：已对齐；Step21 需补前端跨域访问与页面入口一致性。

## 8. 共享计费与收益统计

1. 原始需求：支持共享计费，物业端查看收益统计。
2. 当前实现：预约主链已完成，但缺少冻结后的 `billing_records`、结算闭环和日/区域收益汇总。
3. 证据路径：
   - `memory-bank/data-spec.md`
   - `services/parking-service/src/main/java/com/smartparking/parking/ParkingServiceApplication.java`
4. 差距判定：未对齐，需 Step20 + Step22 补齐。

## 9. 前端页面交付

1. 原始需求：业主端支持预约、共享计费、导航引导；物业端支持资源监控与收益统计。
2. 当前实现：Step16 为工程化单页实时看板，尚未形成 owner/admin 多页面业务界面。
3. 证据路径：
   - `apps/frontend/src/App.vue`
   - `apps/frontend/package.json`
   - `reports/step16_execution.md`
4. 差距判定：未对齐，需 Step21 增加 `vue-router`、业务页面和静态地理目录。

## 10. 演示入口与默认完成态

1. 定稿要求：一键启动后打开业务页面，文档与脚本指向同一入口。
2. 当前实现：`defense_demo.sh start` 主要拉起后端栈，默认仍容易误导到 RabbitMQ/Grafana 等诊断地址；默认验收入口仍是 Step18。
3. 证据路径：
   - `scripts/defense_demo.sh`
   - `README.md`
   - `docs/defense_demo_runbook.md`
4. 差距判定：未对齐，需 Step23 + Step24 收口。

## 11. 阶段结论

1. Step0~Step18：定义为“工程化基线已通过”。
2. Step19A~24：定义为“对齐原始题目需求的补完阶段”。
3. 默认冻结状态：Step18 已验收能力不允许退化，后续仅可增强。
