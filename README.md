# 社区医院门诊管理系统 (Django + MySQL)

MVP 覆盖预约挂号、到诊登记、就诊记录与结算、收入人次统计，便于课堂演示。前后端不分离：Django Templates + Bootstrap 5。

## 环境要求
- Python 3.10+
- MySQL 8.0（Navicat 可直接连接同一账号）
- 依赖：`pip install -r requirements.txt`
   - Windows 装 `mysqlclient` 需 VC++ 编译环境；若安装困难，可改用 `PyMySQL` 并在 `settings.py` 顶部 `import pymysql; pymysql.install_as_MySQLdb()`。
   - 已包含 `python-dotenv` 用于加载 `.env` 配置。

## 快速启动
1. 复制环境变量模板：
   ```bash
   cp env.example .env  # 或手动导入到系统环境
   ```
   按需修改 `DB_NAME/DB_USER/DB_PASSWORD/DB_HOST/DB_PORT`，与 Navicat 使用同一凭据。
2. 创建数据库（Navicat 或 CLI 均可）：
   ```sql
   CREATE DATABASE clinic DEFAULT CHARACTER SET utf8mb4;
   ```
3. 安装依赖：
   ```bash
   # 建议在 conda 环境下
   pip install -r requirements.txt
   ```
4. 迁移：
   ```bash
   python manage.py migrate
   ```
5. 创建后台管理员：
   ```bash
   python manage.py createsuperuser
   ```
6. 运行：
   ```bash
   python manage.py runserver
   ```
7. 浏览：
   - 预约页面：`http://127.0.0.1:8000/`
   - 到诊登记：`/check-in/`
   - 结算：`/billing/`
   - 统计：`/stats/`
   - 后台：`/admin/`（管理科室、医生、排班等）

## 迁移到另一台机器
1. 将整个项目目录打包（含 `hospital/`、`core/`、`manage.py`、`requirements.txt`、`env.example`、`README.md`）。
2. 在目标机解压后，复制或创建 `.env`，填好数据库连接（与 Navicat 一致）。
3. 安装依赖：`pip install -r requirements.txt`（若 mysqlclient 安装失败，按上文提示切换 PyMySQL）。
4. 目标机 MySQL 中创建数据库 `clinic`（或 `.env` 中指定的库名），字符集使用 utf8mb4。
5. 执行迁移：`python manage.py migrate`，必要时用 `createsuperuser` 生成后台账号。
6. 运行 `python manage.py runserver`，在浏览器验证预约/登记/结算/统计流程；Navicat 可直接连库查看表数据。

## 前端与界面说明
- 采用 Bootstrap 5 + Bootstrap Icons，配色为医疗蓝，适配 PC。
- 全部文案为中文，导航包含：预约挂号 / 到诊报到 / 缴费结算 / 数据统计 / 后台管理。
- 预约页：分“患者信息”“挂号信息”两块，带红字校验提示。
- 报到页：支持预约号或身份证/手机号查找，适合前台输入或扫码。
- 结算页：发票风格，金额分栏显示，提示“应收=医保+自费”。
- 统计页：收入与人次表格，支持打印报表。

## 常见问题
- **MySQL 密码未读到 / Access denied (using password: NO)**：确认已 `pip install python-dotenv` 且 `.env` 配好；如果仍报错，临时在终端设置环境变量 `DB_USER/DB_PASSWORD` 后再跑 `migrate`。
- **mysqlclient 安装失败**：`pip install pymysql`，并在 `hospital/settings.py` 顶部添加：
   ```python
   import pymysql
   pymysql.install_as_MySQLdb()
   ```
- **STATICFILES_DIRS 警告**：在项目根目录创建 `static/` 目录即可（可为空）。

## 模型与约束（3NF）
- Department：科室唯一 `name/code`。
- Doctor：隶属科室，`name+department` 唯一，`phone` 唯一。
- Patient：`id_card`、`phone` 唯一，保险类型枚举。
- Schedule：医生排班，`(doctor, date, time_slot)` 唯一，`capacity>=1` 检查约束，状态 OPEN/FULL/CLOSED。
- Appointment：患者预约，`(patient, schedule)` 唯一，状态 BOOKED/COMPLETED/CANCELLED/NO_SHOW/PAID，状态流转 BOOKED→COMPLETED→PAID。
- MedicalRecord：就诊记录（Appointment 一对一，防止重复），关联医生。
- Billing：账单（MedicalRecord 一对一），检查约束确保 `total = insurance + self_pay` 且金额非负，状态 PENDING/PAID/REFUNDED。

## 核心业务流
- 预约：锁定 `Schedule` 后按容量创建 `Appointment`，仅允许 OPEN 状态，满额时标记 FULL。
- 到诊登记：锁定 `Appointment`（仅 BOOKED），支持按预约编号或身份证/手机号检索，写入 `check_in_time/assigned_room`，自动生成 `MedicalRecord`。
- 缴费结算：锁定 `MedicalRecord`，校验“应收=医保+自费”，仅在预约已 COMPLETED 时允许；生成/更新 `Billing` 并置为 PAID，同时将 Appointment 状态置为 PAID，视为“已离院”。

## 表单与页面提示
- 预约：校验医生必须隶属所选科室，满额或关闭的排班会提示。
- 到诊登记：支持预约号或身份证/手机号查找待登记预约，非 BOOKED 状态会提示。
- 结算：表单层校验金额平衡，重复支付会提示；成功后标记预约为 PAID。
- 统计：`Billing` 上按 `paid_at` 日期与科室聚合 `Sum(total_amount)`、`Count(medical_record)`。

## Django Admin
已注册全部模型，常用筛选/搜索：
- `ScheduleAdmin` 展示预约计数；
- `DoctorAdmin` 展示科室/职称；
- `BillingAdmin` 按状态筛选。

## 目录
- `hospital/` 项目配置
- `core/` 业务应用：`models.py`、`views.py`、`forms.py`、`admin.py`、`templates/`
- `static/` 静态资源占位
- `plan.md` 规划文档

## 提示
- 生产部署请设置强随机 `DJANGO_SECRET_KEY`，并将 `DEBUG=false`。
- 使用 Navicat：创建连接 → 选择数据库 → 可直接查看/编辑表结构与数据。迁移脚本与 ORM 均假定 utf8mb4。
