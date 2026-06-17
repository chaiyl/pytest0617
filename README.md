# Pytest API 自动化测试框架

这是一个基于 pytest 的接口自动化测试框架，当前已包含真实接口测试、登录 API 多场景 demo、测试数据 YAML 管理、统一 HTTP 客户端、日志输出、数据恢复机制、SQLite 访问工具和 MySQL 访问工具。

## 目录结构

```text
.
├── config/
│   ├── develop.yaml       # 开发环境接口地址配置
│   ├── env.yaml           # 示例环境配置
│   ├── database.yaml      # SQLite 数据库配置
│   └── mysql.yaml         # MySQL 数据库配置模板
├── data/
│   ├── users.yaml         # 用户接口测试数据
│   ├── login_cases.yaml   # 登录 API demo 测试数据
│   └── ticket.yaml        # ticket 接口测试数据
├── reports/
│   ├── login_report.html  # HTML 报告示例
│   └── logs/test.log      # 测试日志
├── services/
│   ├── __init__.py
│   └── ticket_service.py  # ticket 业务接口封装
├── tests/
│   ├── conftest.py        # pytest 公共 fixture
│   ├── test_demo.py       # 框架 smoke 示例
│   └── api/
│       ├── test_user_api.py
│       ├── test_login_api.py
│       ├── test_ticket_api.py
│       └── test_data_recovery_example.py
├── utils/
│   ├── config_loader.py   # YAML 配置读取
│   ├── http_client.py     # HTTP 请求封装
│   ├── logger.py          # 日志工具
│   ├── mock_login_api.py  # 登录 demo mock 接口
│   ├── data_recovery.py   # 数据恢复/清理工具
│   ├── db_client.py       # SQLite 数据库访问工具
│   └── mysql_client.py    # MySQL 数据库访问工具
├── pytest.ini
├── requirements.txt
└── README.md
```

## 环境准备

建议使用 Python 3.11 或更高版本。

安装依赖：

```bash
python -m pip install -r requirements.txt
```

主要依赖：

```text
pytest                测试框架
pytest-html           HTML 测试报告
pytest-rerunfailures  失败重跑插件
pyyaml                YAML 文件读取
requests              HTTP 接口请求
pymysql               MySQL 数据库访问
```

## 接口环境配置

真实接口地址配置在：

```text
config/develop.yaml
```

示例：

```yaml
develop_url: "http://ai.nextop.com/xapi/api/tool/haoya"
timeout: 10
```

`tests/conftest.py` 中的 `api_client` 会读取该配置，并通过 `utils/http_client.py` 拼接完整 URL。

例如用例中请求：

```python
api_client.post("/get-ticket-info", json=payload)
```

实际请求地址是：

```text
http://ai.nextop.com/xapi/api/tool/haoya/get-ticket-info
```

## 执行用例

进入项目目录：

```bash
cd C:\Users\hzcyl\Documents\Codex\2026-05-28\hi
```

执行全部用例：

```bash
python -m pytest
```

只执行登录 API demo：

```bash
python -m pytest -m login
```

只执行 ticket 真实接口用例：

```bash
python -m pytest -m ticket
```

只执行 API 类用例：

```bash
python -m pytest -m api
```

查看更详细的用例名称：

```bash
python -m pytest -vv
```

生成 HTML 报告：

```bash
python -m pytest --html=reports/report.html --self-contained-html
```

## Marker 说明

marker 在 `pytest.ini` 中注册：

```text
smoke       冒烟测试
regression  回归测试
api         API 接口测试
login       登录 API demo 场景测试
ticket      ticket 真实接口测试
```

用例中使用方式：

```python
@pytest.mark.api
@pytest.mark.ticket
def test_ticket_scenarios(api_client, case):
    ...
```

## 测试数据管理

测试数据统一放在 `data/` 目录下，使用 YAML 文件维护。

例如 `data/ticket.yaml`：

```yaml
scenarios:
  - name: get_success
    payload:
      ticketId: "3a202efb-e00b-41af-3e74-3e58a02ace20"
    expected_code: 200
    expected_success: true
```

测试代码通过 `load_yaml()` 读取：

```python
LOGIN_CASES = load_yaml("data/ticket.yaml")["scenarios"]
```

再通过 pytest 参数化执行：

```python
@pytest.mark.parametrize("case", LOGIN_CASES, ids=[case["name"] for case in LOGIN_CASES])
```

## 公共 Fixture

公共 fixture 在 `tests/conftest.py` 中维护。

当前主要 fixture：

```text
env_config      读取接口环境配置
test_data       读取用户测试数据
login_data      读取登录 demo 数据
api_client      真实 HTTP 接口客户端
login_client    登录 demo mock 客户端
db_client       SQLite 数据库客户端
mysql_client    MySQL 数据库客户端
data_recovery   数据恢复工具
logger          日志对象
```

用例中不需要手工 import fixture，只要在函数参数里声明即可：

```python
def test_ticket_scenarios(api_client):
    response = api_client.post("/get-ticket-info", json={...})
```

## HTTP 客户端

`utils/http_client.py` 封装了常用 HTTP 请求：

```python
api_client.get("/users/1")
api_client.get("/users", params={"page": 1})
api_client.post("/get-ticket-info", json={"ticketId": "xxx"})
api_client.put("/orders/1", json={"status": "paid"})
api_client.patch("/orders/1", json={"remark": "updated"})
api_client.delete("/orders/1")
```

路径会通过 `_url()` 方法和 `base_url` 拼接：

```python
return f"{self.base_url}/{path.lstrip('/')}"
```

所以 `"/users/1"` 和 `"users/1"` 都可以被拼成规范 URL。

当前支持的常用能力：

```text
request()          统一请求入口，支持任意 HTTP method
get()              GET 请求，支持 params 查询参数
post()             POST 请求，支持 json 和 data 请求体
put()              PUT 请求
patch()            PATCH 请求
delete()           DELETE 请求
upload()           文件上传
set_headers()      设置公共请求头
set_bearer_token() 设置 Authorization: Bearer token
remove_header()    删除指定请求头
close()            关闭 requests session
```

请求头示例：

```python
api_client.set_headers({
    "Content-Type": "application/json",
    "X-Request-Source": "pytest",
})
```

登录后设置 token 示例：

```python
login_response = api_client.post("/login", json={
    "username": "admin",
    "password": "123456",
})
token = login_response.json()["data"]["token"]
api_client.set_bearer_token(token)
```

文件上传示例：

```python
with open("data/example.txt", "rb") as file:
    response = api_client.upload(
        "/upload",
        files={"file": file},
        data={"bizType": "ticket"},
    )
```

## Services 业务封装层

`services/` 用来封装业务模块级接口调用，适合多接口场景复用。

当前示例：

```text
services/ticket_service.py
```

示例用法：

```python
from services.ticket_service import TicketService


def test_ticket_scenarios(api_client, case):
    ticket_service = TicketService(api_client)
    response = ticket_service.get_ticket_info(case["payload"])
    body = response.json()

    assert response.status_code == case["expected_code"]
```

推荐职责划分：

```text
utils/http_client.py       只负责底层 HTTP 请求
services/*.py              封装某个业务模块的接口方法
tests/api/*.py             编排测试场景和断言
data/*.yaml                维护测试数据
tests/conftest.py          统一管理 fixture
```

多接口流程用例建议在测试函数中编排业务步骤，在 `services/` 中复用单个接口动作。这样用例能看清业务链路，接口路径和请求细节也不会散落在各个测试文件里。

## 登录 API Demo

登录 demo 使用本地 mock，不访问真实网络，适合演示多场景测试设计。

相关文件：

```text
utils/mock_login_api.py
data/login_cases.yaml
tests/api/test_login_api.py
```

覆盖场景包括：

```text
登录成功
请求体缺失
用户名缺失
密码缺失
账号不存在
密码错误
账号锁定
字段类型错误
响应结构契约校验
```

执行：

```bash
python -m pytest -m login
```

## Ticket 真实接口测试

ticket 用例访问真实接口，不走 mock。

相关文件：

```text
config/develop.yaml
data/ticket.yaml
tests/api/test_ticket_api.py
```

执行：

```bash
python -m pytest -m ticket
```

当前用例会请求：

```text
POST /get-ticket-info
```

并校验：

```text
HTTP 状态码
业务 code
success 字段
ticketId
storeName 前缀
```

## 数据恢复机制

数据恢复工具位于：

```text
utils/data_recovery.py
```

fixture 位于：

```text
tests/conftest.py
```

用例中通过 `data_recovery` 登记清理动作。用例结束后，fixture 会自动执行恢复逻辑。

新增数据后删除：

```python
def test_create_resource(api_client, data_recovery):
    response = api_client.post("/create-resource", json={"name": "pytest_test"})
    assert response.status_code == 200

    resource_id = response.json()["data"]["id"]

    data_recovery.delete_created(
        path="/delete-resource",
        payload={"id": resource_id},
        name=f"delete resource {resource_id}",
    )
```

修改数据后恢复旧值：

```python
def test_update_resource(api_client, data_recovery):
    before = api_client.post("/query-resource", json={"id": "xxx"})
    old_name = before.json()["data"]["name"]

    response = api_client.post("/update-resource", json={
        "id": "xxx",
        "name": "pytest_updated_name",
    })
    assert response.status_code == 200

    data_recovery.restore_updated(
        path="/update-resource",
        payload={"id": "xxx", "name": old_name},
        name="restore resource name",
    )
```

示例文件：

```text
tests/api/test_data_recovery_example.py
```

该文件默认 `skip`，需要替换成真实新增、删除、查询、更新接口后再启用。

## SQLite 数据库访问

SQLite 配置文件：

```text
config/database.yaml
```

示例：

```yaml
type: sqlite
database: "data/test.db"
```

用例中使用：

```python
def test_query_db(db_client):
    row = db_client.fetch_one(
        "select * from users where id = ?",
        [1],
    )

    assert row is not None
```

SQLite 占位符使用 `?`。

常用方法：

```python
db_client.execute(sql, params)
db_client.execute_many(sql, params_list)
db_client.fetch_one(sql, params)
db_client.fetch_all(sql, params)
db_client.close()
```

## MySQL 数据库访问

MySQL 配置文件：

```text
config/mysql.yaml
```

示例：

```yaml
host: "127.0.0.1"
port: 3306
user: "root"
password: "replace-with-password"
database: "replace-with-database"
charset: "utf8mb4"
connect_timeout: 10
read_timeout: 10
write_timeout: 10
```

安装依赖：

```bash
python -m pip install -r requirements.txt
```

用例中使用：

```python
def test_query_mysql(mysql_client):
    row = mysql_client.fetch_one(
        "select * from users where id = %s",
        [1],
    )

    assert row is not None
```

MySQL 占位符使用 `%s`。

常用方法：

```python
mysql_client.execute(sql, params)
mysql_client.execute_many(sql, params_list)
mysql_client.fetch_one(sql, params)
mysql_client.fetch_all(sql, params)
mysql_client.commit()
mysql_client.rollback()
mysql_client.close()
```

## 日志与报告

日志工具：

```text
utils/logger.py
```

日志输出位置：

```text
reports/logs/test.log
```

HTML 报告生成命令：

```bash
python -m pytest --html=reports/report.html --self-contained-html
```

## 新增接口用例建议

推荐流程：

```text
1. 在 data/ 下新增接口测试数据 YAML
2. 在 services/ 下新增 xxx_service.py，封装接口方法
3. 在 tests/api/ 下新增 test_xxx_api.py
4. 使用 service 方法调用真实接口
5. 使用 pytest.mark.parametrize 做多场景参数化
6. 如涉及新增/修改数据，使用 data_recovery 登记恢复动作
7. 如需数据库断言，使用 db_client 或 mysql_client
8. 在 pytest.ini 中按需新增 marker
9. 更新 README.md
```

示例结构：

```python
import pytest

from services.ticket_service import TicketService
from utils.config_loader import load_yaml


CASES = load_yaml("data/example.yaml")["scenarios"]


@pytest.mark.api
@pytest.mark.parametrize("case", CASES, ids=[case["name"] for case in CASES])
def test_example_api(api_client, case):
    ticket_service = TicketService(api_client)
    response = ticket_service.get_ticket_info(case["payload"])
    body = response.json()

    assert response.status_code == case["expected_code"]
    assert body["success"] is case["expected_success"]
```

## 注意事项

- `ticket` 用例是真实接口调用，执行时需要网络可访问目标服务。
- `login` 用例是本地 mock demo，不依赖真实网络。
- MySQL 工具需要安装 `pymysql`，并正确配置 `config/mysql.yaml`。
- 数据恢复动作要尽早登记，避免用例中途失败后无法清理。
- 不建议在测试代码里硬编码环境地址，应统一放到 `config/`。
