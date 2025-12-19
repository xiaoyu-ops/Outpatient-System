# 社区医院门诊管理系统 MVP 规划

## 目标与范围
- 满足课程要求：患者预约→到诊登记→就诊→结算→统计分析，全流程跑通并可演示。
- 技术栈：Python 3.10+, Django 4.2+, MySQL 8.0，单体架构（Templates + Bootstrap 5）。
- 交付物：模型层（含完整性约束）、核心业务视图（事务保证）、Admin 配置、统计查询示例。

## 数据模型草案（3NF 思路）
- Department(科室)：name(unique)、code(unique)、location、is_active。
- Doctor(医生)：user/name、department(FK, PROTECT)、title、phone(unique)、available_slots_per_day。
- Patient(患者)：name、id_card(unique)、phone(unique)、dob、gender、insurance_type、address。
- Schedule(排班)：doctor(FK)、date、time_slot、room_no、capacity、status；unique_together(doctor, date, time_slot)。
- Appointment(预约)：patient(FK)、schedule(FK, CASCADE)
  - fields: status(BOOKED/COMPLETED/CANCELLED/NO_SHOW)、check_in_time、assigned_room、created_at。
  - unique_together(patient, schedule) 以防重复预约。
- MedicalRecord(就诊记录)：appointment(FK, PROTECT)、doctor(FK, PROTECT)、diagnosis、treatment、prescription、visit_time。
- Billing(账单)：medical_record(FK, CASCADE)、total_amount、insurance_amount、self_pay_amount、status(PENDING/PAID/REFUNDED)、paid_at、payment_method。
- 约束示例：
  - Check: total_amount = insurance_amount + self_pay_amount。
  - Appointment.status 与 Billing.status 状态流转使用 choices 与信号/视图逻辑保证；删除策略避免级联误删（多用 PROTECT）。

## 核心业务流
- 患者预约：
  1) 选择科室/医生/日期/时段→创建 Appointment(status=BOOKED)，Schedule.capacity 自减或用计数检查。
- 前台到诊登记：
  1) 通过身份证/手机号查找 Appointment→核验 schedule→标记 status=COMPLETED 并记录 check_in_time/assigned_room。
  2) 同步生成 MedicalRecord（占位，待医生填写）。
- 缴费结算：
  1) 医生完成诊疗，写 MedicalRecord。
  2) 前台基于 MedicalRecord 生成 Billing，录入总额/医保/自费并校验合计，设为 PAID，患者状态“已离院”。
- 统计分析：
  - 按日期、科室汇总门诊收入/人次：使用 annotate、Sum、Count、TruncDate。

## 事务与并发策略
- 所有“登记/结算”视图使用 transaction.atomic，必要时 select_for_update 锁定 Schedule 容量与 Appointment。
- 状态机防重复提交：仅允许 BOOKED→COMPLETED→BILLED→PAID 的有序流转，非法状态抛 ValidationError。

## Django Admin 计划
- 注册 Department、Doctor、Schedule、Patient、Appointment、MedicalRecord、Billing。
- 自定义 list_display / search / list_filter；在 Schedule admin 中内联 Appointment 只读计数；在 Doctor admin 中展示当天/未来排班数。

## 工程结构（拟）
- project_root/
  - hospital/ (Django project)
  - core/ (app) models.py, views.py, urls.py, admin.py, forms.py, templates/
  - static/ (Bootstrap 5 引入)
  - requirements.txt, env.example, manage.py

## 后续实现顺序
1) 初始化 Django + MySQL 连接，创建 core app。
2) 完善 models.py（含 constraints / choices / __str__）。
3) makemigrations & migrate，准备基础种子数据脚本（fixtures）。
4) 编写核心 views：预约、到诊登记、结算（使用事务、表单校验）。
5) 配置 Admin + 简单模板（Bootstrap 表单）。
6) 编写统计查询示例（视图或管理后台 action）。
7) 本地跑通演示流：预约→登记→就诊→结算→统计。
