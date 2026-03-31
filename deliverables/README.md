# Deliverables 目录说明（Step40）

本目录用于承载“可交付、可答辩、可归档”的最终资产，而不是日常开发源码。

## 目录约定

1. `bundles/`
   - 通过 `make release-bundle` 或 `./scripts/create_release_bundle.sh` 生成的版本化交付包。
   - 默认命名：`smart-parking-step40-release-YYYYMMDD-HHMMSS.tar.gz`。
   - 当前默认 bundle 对应 `Step40`，同时保留 `Step36` 作为回滚锚点说明。

2. `screenshots/`
   - 答辩截图、页面截图、关键证据截图。
   - 推荐命名：`YYYYMMDD-owner-dashboard-step40.png`、`YYYYMMDD-admin-monitor-step40.png`。

3. `recordings/`
   - 演示录屏、故障注入录屏、答辩视频素材。
   - 推荐命名：`YYYYMMDD-step40-demo.mp4`。

## 建议流程

1. 先运行 `make ci-smoke`、`make step38-check`、`make step39-check`。
2. 再运行当前默认验收：`python3 scripts/test_step40_release_acceptance.py`。
3. 使用 `make release-bundle` 生成 Step40 交付包。
4. 将截图和录屏补入 `screenshots/`、`recordings/`。
5. 最后按答辩或交付场景归档到远端仓库 / 网盘 / 发布页。
