# 前端工程（Step16）

本目录为 Vue3 + TypeScript + Pinia 的工程化前端实现，替代纯单文件演示页。

## 运行命令

```bash
cd apps/frontend
npm install
npm run dev
```

默认访问地址：`http://localhost:5173`

## 环境变量

复制 `.env.example` 为 `.env.local`，可覆盖：

1. `VITE_GATEWAY_BASE_URL`
1. `VITE_REALTIME_WS_URL`
2. `VITE_GATEWAY_POLL_URL`

如需整体项目的 secure 配置，请在仓库根目录使用 `.env.secure.example` 生成 `.env`，前端仍只保留本机的 `.env.local` 覆盖。

## 关键能力

1. WebSocket 主通道实时更新。
2. WebSocket 故障后自动降级到 Polling。
3. Pinia 管理连接模式与可视化状态。
4. 保留 `apps/frontend/realtime_dashboard_demo.html` 作为答辩保底页。
