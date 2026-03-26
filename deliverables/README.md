# Deliverables 目录说明

本目录用于承载“可交付、可答辩、可归档”的最终资产，而不是日常开发源码。

## 目录约定

1. `bundles/`
   - 通过 `make release-bundle` 或 `./scripts/create_release_bundle.sh` 生成的版本化交付包。
   - 默认命名：`smart-parking-<label>-release-YYYYMMDD-HHMMSS.tar.gz`

2. `screenshots/`
   - 答辩截图、页面截图、关键证据截图。
   - 推荐命名：`YYYYMMDD-owner-dashboard.png`、`YYYYMMDD-admin-monitor.png`

3. `recordings/`
   - 演示录屏、故障注入录屏、答辩视频素材。
   - 推荐命名：`YYYYMMDD-step30-demo.mp4`

## 建议流程

1. 先运行 `make ci-smoke` 或当前默认验收。
2. 再运行 `make release-bundle` 生成交付包。
3. 将截图和录屏补入 `screenshots/`、`recordings/`。
4. 最后按答辩或交付场景归档到远端仓库 / 网盘 / 发布页。
