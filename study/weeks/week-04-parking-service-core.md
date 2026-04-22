# 第 4 周：Java 业务主链

## 本周目标

- 看懂项目里最重要的业务服务
- 理解预约、订单、计费、导航这几条主链
- 学会区分 `Controller / Service / Repository`

## 你会先看哪些文件

- `services/parking-service/src/main/java/com/smartparking/parking/ParkingServiceApplication.java`
- `services/parking-service/src/main/java/com/smartparking/parking/ParkingBusinessExtensions.java`
- `services/parking-service/src/main/java/com/smartparking/parking/ParkingDashboardViewController.java`
- `services/parking-service/src/main/java/com/smartparking/parking/ParkingDashboardViewModules.java`
- `services/parking-service/src/main/java/com/smartparking/parking/ParkingEnhancementController.java`

## 这部分代码到底在做什么

`parking-service` 是整个系统的业务核心。  
如果把前端、网关、模型、实时都看作配套角色，那么它就是负责“真正把停车业务跑起来”的那一层。

这层主要做 4 件事：

1. 接预约请求，生成订单和预估账单
2. 管订单状态和结算
3. 返回导航和业务视图数据
4. 为 dashboard 和经营分析准备聚合结果

### 如何阅读这个服务

新手最容易犯的错误是：看到一个大文件就从头到尾硬啃。  
这里更好的办法是按职责分层看：

1. 先看 `Controller`
   回答“有哪些接口”
2. 再看 `Service`
   回答“核心业务怎么做”
3. 再看 `Repository`
   回答“数据怎么读写”

### 当前主线

- 预约主链在 `ParkingServiceApplication.java`
- 订单、计费、导航在 `ParkingBusinessExtensions.java`
- dashboard 聚合是下一周重点

### 历史保留

- `services/parking_service.py` 是旧的 Python 业务版本，现在不是默认主链

## 一条必须跟读的调用链

这周建议你重点跟 `预约一辆车位` 的调用链：

1. 前端调用 `/api/v1/owner/reservations`
2. `ParkingController.createReservation()` 接到请求
3. 它把请求交给 `ReservationService.reserve()`
4. `ReservationService` 先检查字段和幂等键
5. 然后用 Redisson 拿锁，避免同一车位窗口被并发重复预订
6. 再查 MySQL 是否已有有效预约
7. 成功后写入预约记录
8. 再调用 `BillingService.createEstimatedOrder()` 生成预估账单
9. 最后把订单号、金额、状态回给前端

## 给新手的概念解释

### 什么是 Controller / Service / Repository

- `Controller`：对外接收 HTTP 请求
- `Service`：处理业务规则
- `Repository`：负责数据库读写

可以把它理解成：

- Controller 像前台
- Service 像业务经理
- Repository 像仓库管理员

### 什么是幂等

幂等的意思是：  
同样的请求，重复发多次，不应该把结果搞乱。  
这里最典型的例子就是用户重复点击“预约”，系统不应该生成两张不同订单。

### 为什么是三重防护

这里用了：

- 幂等键
- 分布式锁
- 数据库唯一约束

它们不是重复设计，而是从不同层面防止超卖和重复操作。

## 本周可直接运行的命令

```bash
# 启动整套环境
./scripts/defense_demo.sh start

# 发起一次预约请求
curl -X POST "http://localhost:8080/api/v1/owner/reservations" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: reserve-demo-r1-s001" \
  -d '{
    "user_id": "owner-app-001",
    "preferred_window": "2026-03-31T09:00:00/2026-03-31T10:00:00",
    "location": "R1",
    "slot_id": "R1-S001"
  }'
```

## 本周小练习

1. 找出预约接口里哪个类负责真正的业务逻辑，哪个类只负责 HTTP 入口。
2. 写下 `ReservationService.reserve()` 中最关键的 5 个步骤。
3. 用自己的话解释：为什么计费逻辑没有直接写在 Controller 里。
4. 找到订单完成接口和导航接口分别在哪里。

## 本周完成标准

- 你能说清预约主链从接口到落库的大致流程
- 你知道计费逻辑在什么类里
- 你能分辨哪些代码是业务规则，哪些只是接口包装

## 可选加深阅读

- `reports/step20_execution.md`
- `reports/step39_execution.md`
- `memory-bank/architecture.md`

## 继续深入

如果你准备真正跟 owner 主业务闭环，请继续：

- `../chains/chain-02-owner-order-billing-navigation.md`
- `../labs/lab-02-owner-business.md`

