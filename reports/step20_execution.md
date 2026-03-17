# Step20 执行报告

## 目标

1. 补齐预约 -> 预估金额 -> 完成结算 -> 最终账单的主业务链路。
2. 引入 `billing_records` 持久化模型。
3. 让预约接口直接返回预估金额和 `order_id`。

## 实际改动

1. 新增 `services/parking-service/src/main/java/com/smartparking/parking/ParkingBusinessExtensions.java`：
   - `BillingRepository`
   - `BillingService`
   - `ParkingBusinessController`
2. 在预约成功路径中新增预估账单写入逻辑。
3. 新增接口：
   - `GET /api/v1/owner/recommendations`
   - `GET /api/v1/owner/orders/{order_id}`
   - `POST /api/v1/owner/orders/{order_id}/complete`
   - `GET /api/v1/owner/navigation/{order_id}`
4. 扩展合同：`openapi/smart-parking.yaml`
5. 新增验收脚本：`scripts/test_step20_billing_revenue.py`

## 验证命令

```bash
python3 scripts/test_step20_billing_revenue.py
```

## 验证结果

1. 闸门输出：`STEP20_22_GATE_PASS`
2. 预约响应中可见 `order_id` 与 `estimated_amount`。
3. 订单详情初始状态为 `ESTIMATED`。
4. 完成订单后账单状态变为 `CONFIRMED`，存在 `final_amount`。

## 结论

Step20 通过，共享计费主链已打通。
