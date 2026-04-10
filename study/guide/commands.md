# 学习常用命令

所有命令默认在项目根目录执行。

## 启动前检查

```bash
./scripts/defense_demo.sh preflight
make preflight-static
```

## 启动整套演示环境

```bash
./scripts/defense_demo.sh start
```

默认入口：

- 业主端：`http://localhost:4173/owner/dashboard`
- 物业端：`http://localhost:4173/admin/monitor`
- 网关：`http://localhost:8080`
- model-service：`http://localhost:8000`
- realtime-service：`http://localhost:8090`

## Owner / Admin 接口验证

```bash
curl "http://localhost:8080/api/v1/owner/dashboard?location=R1&preferred_window=2026-03-31T09:00:00/2026-03-31T10:00:00&user_id=owner-app-001"
curl "http://localhost:8080/api/v1/admin/dashboard?date=2026-03-31&trend_days=7&trend_limit=12"
curl "http://localhost:8080/api/v1/admin/realtime/status"
```

## 模型与 ETL

```bash
python3 scripts/step11_etl.py
python3 scripts/step12_train_models.py
python3 scripts/step13_sync_model_registry.py
curl http://localhost:8000/internal/v1/model/registry
```

## 默认验收

```bash
python3 scripts/test_step40_release_acceptance.py
```

## 前端最小验证

```bash
cd apps/frontend
npm run typecheck
npm run build
```
