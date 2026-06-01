# 贡献指南

感谢你关注这个项目。

## 提交前建议

- 先阅读根目录 [README.md](./README.md)
- 确认本地环境可以正常运行基础命令
- 尽量保证改动聚焦，避免把无关文件一起提交

## 推荐提交流程

1. Fork 或新建分支进行开发
2. 保持提交信息清晰、单一职责
3. 提交前至少执行以下检查

```bash
make preflight-static
make ci-smoke
cd apps/frontend && npm run typecheck && npm run build
```

如改动涉及 dashboard、网关鉴权或主流程验收，建议额外执行：

```bash
make step38-check
make step39-check
make step40-check
```

## Pull Request 要求

- 说明改动背景和目标
- 描述影响范围
- 说明验证方式
- 如涉及界面变更，建议附截图
- 如涉及接口变更，建议同步更新 `openapi/smart-parking.yaml`

## 代码与文档约定

- 保持目录职责清晰，不随意混放临时产物
- 修改接口时同步考虑前后端契约一致性
- 修改演示环境配置时，注意区分 demo 场景和正式场景
- 文档优先写清“做了什么、为什么改、怎么验证”

## 不建议直接提交的内容

- 本地环境缓存
- 无关的生成产物
- 未整理的临时实验文件
- 包含敏感信息的配置和凭据
