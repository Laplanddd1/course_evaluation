# 高校课程评价与管理系统（Django）

本项目为高校课程评价与管理系统，基于 Django 构建，包含学生端、教师端、管理员端三类角色，实现课程管理、选课、课表可视化、成绩录入与查询、课程评价与结果统计、教师人气排行榜等功能。

## 功能概览

- 统一登录入口：按角色自动跳转至对应仪表盘
- 学生端：选课（按学期筛选）、课表可视化、成绩查询与 CSV 导出、课程评价、历史评价记录、教师投票
- 教师端：授课课程列表、成绩权重设置与成绩录入、课程评价结果查看
- 管理员端：后台维护用户/课程/问卷模板/评价任务等基础数据
- 教师排行榜：Chart.js 可视化展示得票统计（支持导出 CSV）

## 技术栈

- 后端：Python + Django
- 前端：Django Templates + Bootstrap 5
- 数据库：SQLite（开发默认，可迁移到 MySQL）

## 目录结构

- users：用户、学生/教师/管理员扩展信息与仪表盘
- courses：课程与成绩模型
- evaluations：问卷模板、评价任务、评价结果、投票、选课/课表/成绩查询等业务
- templates：系统页面模板

## 本地运行

### 1. 创建虚拟环境并安装依赖

```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 配置环境变量（可选但推荐）

项目使用环境变量读取 `DJANGO_SECRET_KEY` 与 `DJANGO_DEBUG`。仓库中提供了 `.env.example` 作为参考，但默认不会自动加载 `.env` 文件，你可以在启动前手动设置环境变量。

PowerShell 示例：

```powershell
$env:DJANGO_SECRET_KEY="change-me"
$env:DJANGO_DEBUG="true"
```

### 3. 数据库迁移与启动

```bash
python manage.py migrate
python manage.py runserver
```

访问：
- 登录页：`http://127.0.0.1:8000/accounts/login/`
- 管理后台：`http://127.0.0.1:8000/admin/`

### 4. 创建管理员账号（可选）

```bash
python manage.py createsuperuser
```

### 5. 生成示例数据（可选）

项目内置数据填充命令：

```bash
python manage.py populate_data
```

## 常用功能入口

- 仪表盘：`/dashboard/`
- 学生任务：`/tasks/`
- 选课：`/select-courses/`
- 课表：`/schedule/`
- 成绩：`/my-grades/`
- 教师排行榜：`/teacher-leaderboard/`

## 注意事项

- 默认使用 SQLite，本地开发无需额外安装数据库。
