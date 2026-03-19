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
- 请勿将 `.env`、`db.sqlite3` 等敏感/本地文件提交到公开仓库（已在 `.gitignore` 中忽略）。

## 连接到你自己的 MySQL

项目已内置 MySQL 支持，通过环境变量切换：

- `DB_ENGINE`：`sqlite` 或 `mysql`（默认 sqlite）
- `DB_NAME`：数据库名（如 `course_evaluation`）
- `DB_USER`：数据库用户名（如 `ce_user`）
- `DB_PASSWORD`：数据库密码
- `DB_HOST`：主机（默认 `127.0.0.1`）
- `DB_PORT`：端口（默认 `3306`，自定义端口如 `3308` 请显式设置）

> 项目不会自动加载 `.env`，请在终端设置环境变量或在部署环境中配置。

### Windows PowerShell 示例

```powershell
$env:DB_ENGINE="mysql"
$env:DB_NAME="course_evaluation"
$env:DB_USER="ce_user"
$env:DB_PASSWORD="123456"
$env:DB_HOST="127.0.0.1"
$env:DB_PORT="3308"  # 若为默认3306可省略

python manage.py migrate
python manage.py runserver
```

### Linux/macOS 示例

```bash
export DB_ENGINE=mysql
export DB_NAME=course_evaluation
export DB_USER=ce_user
export DB_PASSWORD=123456
export DB_HOST=127.0.0.1
export DB_PORT=3308

python manage.py migrate
python manage.py runserver
```

### 初始化 MySQL（只需一次）

```sql
CREATE DATABASE IF NOT EXISTS course_evaluation
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'ce_user'@'%' IDENTIFIED BY '123456';
GRANT ALL PRIVILEGES ON course_evaluation.* TO 'ce_user'@'%';
FLUSH PRIVILEGES;
```

## 从 SQLite 迁移数据到 MySQL（可选）

1. 使用 SQLite 导出数据（使用 `--output` 确保 UTF‑8）：
   ```powershell
   $env:DB_ENGINE="sqlite"
   python manage.py dumpdata --exclude contenttypes --exclude auth.permission --indent 2 --output data.json
   ```
2. 切换 MySQL 并迁移表结构：
   ```powershell
   $env:DB_ENGINE="mysql"
   $env:DB_NAME="course_evaluation"
   $env:DB_USER="ce_user"
   $env:DB_PASSWORD="123456"
   $env:DB_HOST="127.0.0.1"
   $env:DB_PORT="3308"
   python manage.py migrate
   ```
3. 导入数据：
   ```powershell
   python manage.py loaddata data.json
   ```

如遇 `loaddata` UTF‑8 解码错误，可先转换为 UTF‑8 再导入：

```powershell
python - <<'PY'
import pathlib, json, sys
p = pathlib.Path('data.json'); b = p.read_bytes()
for enc in ('utf-8','utf-8-sig','utf-16','utf-16le','utf-16be','gbk','cp936','latin1'):
    try:
        s = b.decode(enc); obj = json.loads(s)
        pathlib.Path('data_utf8.json').write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')
        print('detected', enc); sys.exit(0)
    except Exception: pass
print('failed: unknown encoding', file=sys.stderr); sys.exit(1)
PY
python manage.py loaddata data_utf8.json
```


