# Luna 架构设计文档

## 项目概述

Luna是一个基于Python开发的CLI工具，旨在整合7个常用的信息收集工具，提供自动化、可配置的安全测试流程。

**设计理念**：模块化 + 流程化 + 参数绑定

---

## 一、核心工具

### 1.1 工具列表

| 工具 | 语言 | 功能 | 在Luna中的角色 |
|------|------|------|---------------|
| OneForAll | Python | 子域名收集 | 模块1 - 子域名收集 |
| puzzle | Go | 综合信息收集 | 模块1 - 子域名收集 |
| httpx | Go | HTTP探测 | 模块3 - HTTP探测 |
| dirsearch | Python | 目录爆破 | 模块2 - 目录挖掘 |
| ffuf | Go | Web模糊测试 | 可选模块 |
| fscan | Go | 内网综合扫描 | 可选模块 |
| TXPortMap | Go | 端口扫描 | 模块4 - 端口扫描 |

### 1.2 工具部署

**Go工具（需要预编译）**：
- httpx, ffuf, puzzle, fscan, TXPortMap
- 编译后的二进制文件放在 `tools/` 目录

**Python工具（直接调用）**：
- OneForAll, dirsearch
- 通过 `python3 script.py` 调用

---

## 二、模块定义

### 2.1 模块列表

| 模块ID | 模块名称 | 包含工具 | 绑定操作 | 说明 |
|--------|---------|---------|---------|------|
| 1 | 子域名收集 | OneForAll + puzzle | 自动过滤邮件域名 | 并行运行，结果合并去重 |
| 2 | 目录挖掘 | dirsearch | - | 快速模式 |
| 3 | HTTP探测 | httpx | - | 可多次调用 |
| 4 | 端口扫描 | TXPortMap | - | 针对IP地址 |
| 5 | 综合扫描 | fscan | - | 可选 |
| 6 | Web模糊测试 | ffuf | - | 可选 |

### 2.2 模块依赖关系

```
模块1（子域名收集）
    ↓ 输出：子域名列表
模块2（目录挖掘）
    ↓ 输出：URL列表
模块3（HTTP探测-第一轮）
    ↓ 输出：HTTP状态和标题
模块4（端口扫描）← 使用模块1中puzzle收集的IP
    ↓ 输出：开放端口列表
模块3（HTTP探测-第二轮）
    ↓ 输出：HTTP状态和标题
报告生成
```

---

## 三、默认流程

### 3.1 流程步骤

```
步骤1: 子域名收集
  - 并行运行 OneForAll 和 puzzle
  - 合并结果并去重
  - 自动过滤邮件相关域名（mail.*, smtp.*, pop.* 等）
  - 输出：merged_subdomains.txt

步骤2: 目录挖掘
  - 使用 dirsearch 对所有子域名进行目录扫描
  - 快速模式（减少字典大小和递归深度）
  - 输出：dirsearch_result.json

步骤3: HTTP探测（第一轮）
  - 使用 httpx 探测目录挖掘的结果
  - 获取状态码和网页标题
  - 输出：httpx_probe_1.json

步骤4: 端口扫描
  - 使用 TXPortMap 扫描 puzzle 收集到的IP地址
  - 扫描常用端口（Top100或Top1000）
  - 输出：txportmap_result.txt

步骤5: HTTP探测（第二轮）
  - 使用 httpx 探测端口扫描发现的HTTP服务
  - 获取状态码和网页标题
  - 输出：httpx_probe_2.json

步骤6: 数据整合
  - Luna解析所有工具输出
  - 数据清洗和格式统一
  - 去重和关联

步骤7: 报告生成
  - 生成两张表格
  - 表1: 主域名 → 子域名 → 目录URL → 状态码 → 网页标题
  - 表2: 主域名 → 子域名 → IP → 端口 → 状态码 → 网页标题
```

### 3.2 错误处理

**原则**：前置工具失败则终止流程

```python
if 子域名收集失败:
    记录错误日志
    终止流程
    提示用户检查配置

if 目录挖掘失败:
    记录警告
    继续执行（使用子域名进行HTTP探测）
```

---

## 四、流程管理系统

### 4.1 流程（Profile）概念

**流程** = 模块组合 + 参数配置

```json
{
  "name": "default",
  "description": "默认完整流程",
  "modules": [1, 2, 3, 4, 3],
  "params": {
    "oneforall": {
      "brute": true,
      "dns": true,
      "wordlist": "/path/to/dict.txt"
    },
    "puzzle": {
      "mode": "domain",
      "timeout": 10
    },
    "dirsearch": {
      "threads": 50,
      "wordlist": "/path/to/web.txt",
      "recursive": false
    }
  }
}
```

### 4.2 流程类型

**内置流程**：
- `default` - 完整7步流程
- `quick` - 快速扫描（子域名 + HTTP探测）
- `deep` - 深度扫描（包含递归目录扫描）

**自定义流程**：
- 用户创建的流程
- 保存在 `profiles/{name}.json`

### 4.3 参数绑定机制

**首次运行流程**：
```
1. 检测流程配置文件是否存在
2. 不存在 → 进入交互式参数配置
3. 逐个工具询问参数
4. 保存参数到流程配置文件
5. 执行流程
```

**后续运行流程**：
```
1. 加载流程配置文件
2. 询问："使用上次的参数？(Y/n)"
3. Y → 直接使用保存的参数
4. n → 重新输入参数
   - 询问："保存覆盖原参数？(Y/n)"
   - Y → 更新配置文件
   - n → 仅本次使用新参数
```

---

## 五、批量处理

### 5.1 输入方式

```bash
# 单个目标
luna run --profile default --target example.com

# 批量目标（文件）
luna run --profile default --target-file domains.txt

# 多个目标（逗号分隔）
luna run --profile default --target example.com,test.com,demo.com
```

### 5.2 处理策略

**串行处理**（不支持并发）：
```python
for domain in domains:
    print(f"[{idx}/{total}] 正在处理: {domain}")
    
    # 执行完整流程
    success = run_profile(profile, domain)
    
    if success:
        # 生成该域名的报告
        generate_report(domain)
        print(f"[✓] {domain} 处理完成")
    else:
        print(f"[✗] {domain} 处理失败")
```

**原因**：
- Luna需要实时监控和处理工具输出
- 部分工具不支持并发
- 避免资源竞争和输出冲突

---

## 六、输出管理

### 6.1 目录结构

```
outputs/
├── example.com/                    # 按域名分类
│   ├── 1_subdomain_collection/
│   │   ├── oneforall_raw/         # OneForAll原始输出
│   │   ├── oneforall_result.csv
│   │   ├── puzzle_result.txt
│   │   ├── merged_subdomains.txt  # 合并去重后的子域名
│   │   └── filtered_subdomains.txt # 过滤邮件后的子域名
│   ├── 2_directory_scan/
│   │   ├── dirsearch_result.json
│   │   └── urls.txt
│   ├── 3_http_probe_1/
│   │   └── httpx_result.json
│   ├── 4_port_scan/
│   │   └── txportmap_result.txt
│   ├── 5_http_probe_2/
│   │   └── httpx_result.json
│   ├── final_report_table1.csv    # 最终报告-表1
│   ├── final_report_table2.csv    # 最终报告-表2
│   └── luna.log                   # Luna执行日志
└── test.com/
    └── ...
```

### 6.2 输出文件管理

**原则**：
1. 所有工具输出必须保存到Luna管理的目录
2. 原始输出和处理后的数据分别保存
3. 每个模块有独立的输出目录

**特殊处理**：

**OneForAll**：
- 默认输出到自己的 `results/` 目录
- Luna执行后移动到 `outputs/{domain}/1_subdomain_collection/oneforall_raw/`

**puzzle**：
- ⚠️ **关键**：如果输出文件已存在，puzzle会拒绝输出
- Luna在执行前检查并删除旧文件
- 或使用时间戳生成唯一文件名

**不支持文件输出的工具**：
- Luna捕获stdout
- 保存到对应的输出文件

---

## 七、数据处理

### 7.1 Luna的数据处理职责

**实时监控**：
- 监控工具执行状态
- 捕获标准输出和错误输出
- 超时控制

**数据解析**：
- 统一解析各工具的输出格式
- 文本 → 结构化数据（JSON/Dict）

**数据处理**：
- 去重和合并
- 邮件域名过滤
- 数据验证和清洗
- 关联不同模块的数据

### 7.2 邮件域名过滤

**触发时机**：子域名收集完成后自动执行

**过滤规则**：
```python
EMAIL_PATTERNS = [
    r'^mail\.',
    r'^smtp\.',
    r'^pop\.',
    r'^pop3\.',
    r'^imap\.',
    r'^webmail\.',
    r'^email\.',
    r'^mx\.',
    r'^mx[0-9]+\.',
]

def is_email_related(subdomain):
    for pattern in EMAIL_PATTERNS:
        if re.match(pattern, subdomain):
            return True
    return False
```

### 7.3 数据格式统一

**内部数据结构**：
```python
{
  "domain": "example.com",
  "subdomains": [
    {
      "subdomain": "www.example.com",
      "ip": "1.2.3.4",
      "source": "oneforall"
    }
  ],
  "urls": [
    {
      "url": "http://www.example.com/admin",
      "status_code": 200,
      "title": "Admin Panel",
      "content_length": 1234
    }
  ],
  "ports": [
    {
      "ip": "1.2.3.4",
      "port": 8080,
      "service": "http",
      "banner": "nginx/1.14.0"
    }
  ]
}
```

---

## 八、报告生成

### 8.1 报告格式

**表1：Web资产表**
| 主域名 | 子域名 | 目录URL | 状态码 | 网页标题 |
|--------|--------|---------|--------|---------|
| example.com | www.example.com | http://www.example.com/admin | 200 | Admin Panel |
| example.com | api.example.com | http://api.example.com/v1 | 200 | API v1 |

**表2：IP端口表**
| 主域名 | 子域名 | IP地址 | 端口 | 状态码 | 网页标题 |
|--------|--------|--------|------|--------|---------|
| example.com | www.example.com | 1.2.3.4 | 80 | 200 | Example Domain |
| example.com | www.example.com | 1.2.3.4 | 8080 | 200 | Admin Panel |

### 8.2 输出格式

- CSV（默认）：轻量、易于处理
- XLSX（可选）：使用pandas生成，更美观

---

## 九、技术实现

### 9.1 技术栈

- **语言**：Python 3.6+
- **CLI框架**：argparse 或 click
- **进程管理**：subprocess
- **数据处理**：pandas（可选，用于报告生成）
- **配置管理**：JSON
- **日志**：logging

### 9.2 核心模块

```
src/
├── __init__.py
├── core.py              # 核心逻辑和流程控制
├── modules.py           # 模块定义和执行
├── profile.py           # 流程管理
├── tools_wrapper.py     # 工具调用封装
├── data_processor.py    # 数据处理
├── report.py            # 报告生成
├── config.py            # 配置管理
└── utils.py             # 工具函数
```

### 9.3 工具调用封装

```python
class ToolWrapper:
    def __init__(self, tool_name, tool_path):
        self.tool_name = tool_name
        self.tool_path = tool_path
    
    def run(self, args, output_file=None, capture=True):
        """运行工具并捕获输出"""
        cmd = [self.tool_path] + args
        
        if capture:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            # 保存输出
            if output_file:
                with open(output_file, 'w') as f:
                    f.write(result.stdout)
            
            return result.stdout
        else:
            subprocess.run(cmd)
```

---

## 十、使用示例

### 10.1 基本使用

```bash
# 首次使用默认流程
luna run --profile default --target example.com
# → 交互式输入参数
# → 执行流程
# → 生成报告

# 再次使用
luna run --profile default --target example.com
# → "使用上次的参数？(Y/n)" Y
# → 直接执行

# 批量处理
luna run --profile default --target-file domains.txt
```

### 10.2 流程管理

```bash
# 列出所有流程
luna list-profiles

# 查看流程详情
luna show-profile default

# 创建自定义流程
luna create-profile quick --modules 1,3
# → 交互式配置参数
# → 保存流程

# 删除流程
luna delete-profile quick
```

### 10.3 参数覆盖

```bash
# 临时覆盖参数（不保存）
luna run --profile default --target example.com \
  --oneforall-threads 100 \
  --dirsearch-wordlist /custom/dict.txt
```

---

## 十一、待实现功能

### 11.1 第一阶段（MVP）
- [x] 架构设计
- [ ] 核心框架实现
- [ ] 默认流程实现
- [ ] 基础报告生成
- [ ] 单域名处理

### 11.2 第二阶段
- [ ] 批量处理
- [ ] 自定义流程
- [ ] 参数管理优化
- [ ] 进度显示

### 11.3 第三阶段
- [ ] 错误恢复机制
- [ ] 结果缓存
- [ ] 增量扫描
- [ ] Web界面（可选）

---

## 十二、注意事项

### 12.1 环境要求

**Python依赖**：
- Python 3.6+
- 需要安装OneForAll和dirsearch的依赖

**Go工具**：
- 需要预编译
- 确保二进制文件有执行权限

**系统权限**：
- puzzle需要root权限（Linux）或管理员权限（Windows）
- 需要安装libpcap（Linux）或npcap（Windows）

### 12.2 性能考虑

- 子域名收集可能耗时较长（取决于目标和配置）
- 目录挖掘建议使用快速模式（小字典）
- 批量处理时注意磁盘空间

### 12.3 安全和合规

⚠️ **重要提醒**：
- 仅用于授权的安全测试
- 遵守当地法律法规
- 不得用于非法用途
- 使用者需自行承担法律责任
