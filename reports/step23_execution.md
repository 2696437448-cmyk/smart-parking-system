# Step23 执行报告

## 目标

1. 将 `defense_demo.sh start` 升级为业务前端默认入口。
2. 让 README / runbook / 脚本输出统一指向 owner/admin 页面。
3. 保留 RabbitMQ / Grafana 作为诊断地址，而不是默认首屏。

## 实际改动

1. 重写 `scripts/defense_demo.sh`：
   - `start` 自动 `npm run build` + `npm run preview`
   - 输出 `http://localhost:4173/owner/dashboard`
   - 输出 `http://localhost:4173/admin/monitor`
   - `acceptance` 默认切换到 `Step24`
   - 新增 `acceptance-legacy`
2. 更新 `README.md` 与 `docs/defense_demo_runbook.md`。
3. 新增 `scripts/test_step23_demo_entry.py`。

## 验证命令

```bash
./scripts/defense_demo.sh start
python3 scripts/test_step23_demo_entry.py
```

## 验证结果

1. 启动成功后输出业务页面 URL：
   - `http://localhost:4173/owner/dashboard`
   - `http://localhost:4173/admin/monitor`
2. 闸门输出：`STEP23_GATE_PASS`
3. RabbitMQ / Grafana 仅以 `ops` 诊断地址形式保留。

## 结论

Step23 通过，演示入口与文档口径已统一到业务页面。
