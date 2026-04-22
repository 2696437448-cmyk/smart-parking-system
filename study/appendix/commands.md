# 新手常用命令

这份命令表只保留当前主线最常用、最适合学习时使用的命令。  
所有命令默认在项目根目录执行。

## 安装依赖

```bash
python3 -m pip install -r requirements-dev.txt
cd apps/frontend
npm install
cd ../..
```

## 启动前的预检查

```bash
./scripts/defense_demo.sh preflight
make preflight-static
```

作用：

- 检查环境是否满足要求
- 提前发现 Docker、Node、Python、配置等问题

## 启动整套演示环境

```bash
./scripts/defense_demo.sh start
```

启动后默认可以访问：

- 业主端：`http://localhost:4173/owner/dashboard`
- 物业端：`http://localhost:4173/admin/monitor`
- 网关：`http://localhost:8080`
- parking-service：`http://localhost:8081`
- model-service：`http://localhost:8000`
- realtime-service：`http://localhost:8090`
- Grafana：`http://localhost:13000`

## 前端常用命令

```bash
cd apps/frontend
npm run dev
npm run typecheck
npm run build
```

适用场景：

- `dev`：本地开发时实时预览
- `typecheck`：检查 TypeScript 类型问题
- `build`：确认前端可以正常打包

## 默认验收

```bash
./scripts/defense_demo.sh acceptance

# 或
python3 scripts/test_step40_release_acceptance.py
```

作用：

- 验证当前 `Step40` 主线是否通过默认验收

## 历史验收入口

```bash
./scripts/defense_demo.sh acceptance-step36
./scripts/defense_demo.sh acceptance-step30
./scripts/defense_demo.sh acceptance-step24
```

说明：

- 这些是历史基线验收入口
- 当前学习默认不以它们为主线

## 运行 ETL 与模型脚本

```bash
python3 scripts/step11_etl.py
python3 scripts/step12_train_models.py
python3 scripts/step13_sync_model_registry.py
```

适用场景：

- 学习数据如何整理
- 学习模型如何训练和注册

## 常见接口测试命令

### 查看网关健康状态

```bash
curl http://localhost:8080/actuator/health
```

### 查看 owner dashboard

```bash
curl "http://localhost:8080/api/v1/owner/dashboard?location=R1&preferred_window=2026-03-31T09:00:00/2026-03-31T10:00:00&user_id=owner-app-001"
```

### 查看 admin dashboard

```bash
curl "http://localhost:8080/api/v1/admin/dashboard?date=2026-03-31&trend_days=7&trend_limit=12"
```

### 查看 realtime polling 降级接口

```bash
curl "http://localhost:8080/api/v1/admin/realtime/status"
```

## 打包交付物

```bash
make release-bundle
```

作用：

- 生成默认 release bundle
- 输出位置通常在 `deliverables/bundles/`

## 常见排错顺序

遇到问题时，建议按这个顺序排查：

1. 先跑 `./scripts/defense_demo.sh preflight`
2. 再看 `README.md` 和 `docs/defense_demo_runbook.md`
3. 再看对应服务是否启动成功
4. 再看接口健康检查
5. 最后才去深挖源码细节

## 新手提示

- 不要一开始就自己手动拼整套 Docker 命令，优先用 `defense_demo.sh`
- 不要把 `services/parking_service.py` 当成当前默认业务服务
- 每次只验证一条链路，例如先只看 owner dashboard，再看 admin dashboard
