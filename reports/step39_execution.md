# Step39 执行报告（dashboard 聚合层与性能硬化）

## 执行范围

1. 目标：在保持 dashboard URL 和业务语义不变的前提下，完成聚合层模块化、请求/实时通道硬化与前端图表包体优化。
2. 范围：
   - `parking-service` dashboard 组装逻辑拆分
   - `requestJson` 与实时通道硬化
   - admin 图表按需加载与 `vendor-echarts` chunk 收敛
   - Step39 gate 与 Makefile / CI 接入
3. 不包含：
   - 改动 reservation、billing、navigation、dispatch、predict、optimize 公共合同
   - 替换 Vue / Capacitor / Leaflet / ECharts 技术栈

## 实际改动

1. 后端模块化
   - 新增 `services/parking-service/src/main/java/com/smartparking/parking/ParkingDashboardViewModules.java`
   - 更新 `services/parking-service/src/main/java/com/smartparking/parking/ParkingDashboardViewController.java`
   - 形成 query / assembler / view service 分层

2. 前端硬化
   - 更新 `apps/frontend/src/services/http.ts`
   - 更新 `apps/frontend/src/composables/useRealtimeChannel.ts`
   - 更新 `apps/frontend/src/components/EChartPanel.vue`
   - 更新 `apps/frontend/vite.config.ts`

3. CI / Makefile
   - 新增 `make step39-check`
   - GitHub Actions 前端质量 job 直接执行 Step39 gate

## 核心结果

1. controller 不再继续膨胀，dashboard 组装逻辑集中到 `ParkingDashboardViewModules.java`。
2. `requestJson` 统一了 trace header、HTTP 错误与非 JSON 响应处理。
3. `useRealtimeChannel` 避免重复 polling 与 reconnect 生命周期冲突。
4. ECharts 按 admin 路由按需加载，构建产物拆为 `vendor-zrender` 与 `vendor-echarts`，默认 build 不再出现 warning。

## 执行命令与结果

```bash
cd apps/frontend && npm run typecheck
cd apps/frontend && npm run build
python3 scripts/test_step39_dashboard_hardening.py
```

结果：通过。构建输出中的 `vendor-echarts` 已降到 warning 阈值以下。
