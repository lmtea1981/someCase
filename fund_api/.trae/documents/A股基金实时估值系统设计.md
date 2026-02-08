# A股基金实时估值系统设计

## 项目结构

```
fund_api/
├── config/
│   ├── config.yaml       # 主配置文件（更新时间等）
│   └── funds.yaml        # 基金信息（基金代码、名称）
├── data/                 # CSV数据存储目录
├── src/
│   ├── main.py           # 主脚本
│   ├── fund.py           # 基金类
│   └── utils.py          # 工具函数
└── requirements.txt      # 依赖包
```

## 核心功能

1. **配置管理**

   * 使用YAML文件维护基金信息

   * 支持配置更新时间间隔

2. **数据获取**

   * 从 `http://fundgz.1234567.com.cn/js/{fundcode}.js` 获取实时估值

   * 解析JSONP格式响应

3. **数据存储**

   * 每个基金单独保存为CSV文件

   * 字段：基金代码、基金名称、前一天净值、当前估值、当前涨跌幅度、估计时间

4. **定时执行**

   * 支持自定义更新间隔（默认15分钟）

   * 每次更新打印基金变化情况

## 技术栈

* Python 3.8+

* pyyaml（YAML解析）

* requests（HTTP请求）

* schedule（定时任务）

* pandas（CSV处理）

## 实现步骤

1. 创建项目目录结构
2. 编写依赖文件 requirements.txt
3. 创建配置文件模板
4. 实现基金类（数据获取、解析、存储）
5. 实现主脚本（定时任务、配置加载）
6. 测试系统功能

## 配置文件示例

**config.yaml**:

```yaml
update_interval: 15  # 分钟
```

**funds.yaml**:

```yaml
funds:
  - code: "008888"
    name: "华夏国证半导体芯片ETF联接C"
  - code: "001593"
    name: "天弘创业板ETF联接C"
```

## 运行方式

```bash
python src/main.py
```

系统将自动加载配置，定时更新基金估值数据，并打印变化情况。
