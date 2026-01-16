# Luna 用户使用手册

## 目录

1. [快速开始](#快速开始)
2. [基本概念](#基本概念)
3. [命令参考](#命令参考)
4. [使用场景](#使用场景)
5. [流程管理](#流程管理)
6. [高级用法](#高级用法)
7. [常见问题](#常见问题)

## 快速开始

### 第一次使用

```bash
# 1. 查看帮助
python3 luna.py --help

# 2. 列出可用流程
python3 luna.py list

# 3. 查看默认流程
python3 luna.py show default

# 4. 运行默认流程（第一次会要求配置参数）
python3 luna.py run --profile default --target example.com
```

### 最简单的使用方式

```bash
# 使用默认流程扫描单个域名
python3 luna.py run --profile default --target example.com
```

Luna会：
1. 询问你是否使用上次的参数（首次运行会逐个工具询问参数）
2. 执行完整的信息收集流程
3. 生成两个CSV报告文件

## 基本概念

### 流程 (Profile)

流程是一组工具的组合和配置。Luna内置了3个流程：

| 流程名 | 说明 | 包含的工具 |
|--------|------|-----------|
| default | 默认完整流程 | OneForAll + puzzle + dirsearch + httpx + TXPortMap + httpx |
| quick | 快速扫描 | puzzle + httpx |
| deep | 深度扫描 | OneForAll + puzzle + dirsearch + ffuf + httpx + fscan + httpx |

### 工具 (Tool)

Luna集成了7个信息收集工具：

| 工具 | 类型 | 功能 |
|------|------|------|
| OneForAll | Python | 专业子域名收集 |
| puzzle | Go | 综合信息收集（子域名+IP+端口+指纹） |
| httpx | Go | HTTP服务探测 |
| dirsearch | Python | 目录爆破 |
| ffuf | Go | Web模糊测试 |
| fscan | Go | 内网综合扫描 |
| TXPortMap | Go | 快速端口扫描 |

### 参数绑定

每个流程都有自己的参数配置。首次运行时配置的参数会保存，后续运行可以直接使用。

### 输出目录

所有结果保存在 `outputs/{domain}/` 目录下。

## 命令参考

### luna run - 运行流程

```bash
python3 luna.py run --profile <流程名> --target <目标>
```

**参数**:
- `--profile, -p`: 流程名称（必需）
- `--target, -t`: 单个目标域名
- `--target-file, -f`: 包含多个域名的文件（每行一个）

**示例**:

```bash
# 扫描单个域名
python3 luna.py run -p default -t example.com

# 批量扫描
python3 luna.py run -p quick -f domains.txt

# 使用完整参数名
python3 luna.py run --profile default --target example.com
```

### luna list - 列出流程

```bash
python3 luna.py list
```

显示所有可用的流程（内置和自定义）。

### luna show - 查看流程详情

```bash
python3 luna.py show <流程名>
```

**示例**:

```bash
# 查看默认流程
python3 luna.py show default

# 查看自定义流程
python3 luna.py show my-scan
```

### luna create - 创建流程

```bash
python3 luna.py create <流程名> [--from <基础流程>]
```

**参数**:
- `<流程名>`: 新流程的名称
- `--from, -f`: 基于现有流程创建（可选）

**示例**:

```bash
# 从头创建新流程
python3 luna.py create my-scan

# 基于默认流程创建
python3 luna.py create my-scan --from default
```

创建流程时会进入交互式向导，引导你：
1. 选择要使用的工具
2. 配置每个工具的参数
3. 保存流程配置

### luna delete - 删除流程

```bash
python3 luna.py delete <流程名>
```

**注意**: 不能删除内置流程（default, quick, deep）。

## 使用场景

### 场景1: 外网信息收集

**目标**: 收集目标域名的所有子域名、目录、开放端口

```bash
# 使用默认流程
python3 luna.py run -p default -t target.com
```

**流程**:
1. 子域名收集（OneForAll + puzzle）
2. 自动过滤邮件域名
3. 目录挖掘（dirsearch）
4. HTTP探测（httpx）
5. 端口扫描（TXPortMap，针对puzzle收集的IP）
6. HTTP探测（httpx，针对端口扫描结果）
7. 生成报告

**输出**:
- `target.com_web_assets.csv` - Web资产表
- `target.com_ip_ports.csv` - IP端口表

### 场景2: 快速探测

**目标**: 快速了解目标的基本情况

```bash
# 使用快速流程
python3 luna.py run -p quick -t target.com
```

**流程**:
1. 子域名收集（puzzle）
2. HTTP探测（httpx）
3. 生成报告

**特点**: 速度快，适合初步侦察。

### 场景3: 深度扫描

**目标**: 全面深入的信息收集

```bash
# 使用深度流程
python3 luna.py run -p deep -t target.com
```

**流程**:
1. 子域名收集（OneForAll + puzzle）
2. 目录挖掘（dirsearch + ffuf，递归）
3. HTTP探测（httpx）
4. 内网扫描（fscan）
5. HTTP探测（httpx）
6. 生成报告

**特点**: 最全面，但耗时较长。

### 场景4: 批量扫描

**目标**: 扫描多个域名

```bash
# 准备域名列表文件
cat > domains.txt << EOF
example1.com
example2.com
example3.com
EOF

# 批量扫描
python3 luna.py run -p default -f domains.txt
```

**特点**: 
- 串行处理，一个域名完成后再处理下一个
- 每个域名独立输出目录
- 每个域名独立报告

### 场景5: 自定义流程

**目标**: 只想做子域名收集和端口扫描

```bash
# 创建自定义流程
python3 luna.py create subdomain-port

# 在交互式向导中选择:
# 工具: puzzle, TXPortMap, httpx
# 配置各工具参数

# 使用自定义流程
python3 luna.py run -p subdomain-port -t target.com
```

## 流程管理

### 查看流程配置文件

流程配置保存在 `profiles/` 目录：

```bash
# 查看流程配置
cat profiles/default.json
```

配置文件格式：

```json
{
  "name": "default",
  "description": "默认完整流程",
  "tools": [
    {
      "name": "oneforall",
      "order": 1,
      "params": {
        "brute": true,
        "dns": true,
        "wordlist": "/path/to/dict.txt"
      }
    },
    {
      "name": "puzzle",
      "order": 2,
      "params": {
        "mode": "domain",
        "timeout": 10
      }
    }
  ]
}
```

### 手动编辑流程

你可以直接编辑JSON文件来修改流程：

```bash
# 编辑流程配置
vim profiles/default.json

# 修改后直接使用
python3 luna.py run -p default -t example.com
```

### 复制流程

```bash
# 复制流程配置文件
cp profiles/default.json profiles/my-custom.json

# 编辑新流程
vim profiles/my-custom.json

# 使用新流程
python3 luna.py run -p my-custom -t example.com
```

### 参数重新配置

如果想重新配置某个流程的参数：

```bash
# 运行时选择 "n" 不使用上次参数
python3 luna.py run -p default -t example.com
# 提示: 使用上次的参数？(Y/n) n

# 然后重新输入所有参数
# 最后选择 "Y" 保存覆盖原参数
```

## 高级用法

### 工具参数说明

#### OneForAll参数

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| brute | bool | 是否启用爆破 | true |
| dns | bool | 是否DNS解析 | true |
| req | bool | 是否HTTP请求 | true |
| wordlist | string | 字典文件路径 | 默认字典 |

#### puzzle参数

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| mode | string | 模式(domain/ip/all) | domain |
| timeout | int | 超时时间(秒) | 10 |
| l3 | bool | 三级域名爆破 | false |
| ping | bool | Ping探测 | false |
| pt | int | 端口爆破线程 | 500 |
| wt | int | Web指纹线程 | 25 |

#### httpx参数

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| threads | int | 线程数 | 50 |
| timeout | int | 超时时间(秒) | 10 |
| status_code | bool | 显示状态码 | true |
| title | bool | 显示标题 | true |
| tech_detect | bool | 技术栈检测 | false |

#### dirsearch参数

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| wordlist | string | 字典文件路径 | 默认字典 |
| threads | int | 线程数 | 50 |
| timeout | int | 超时时间(秒) | 10 |
| recursive | bool | 递归扫描 | false |
| recursion_depth | int | 递归深度 | 2 |
| exclude_status | string | 排除状态码 | "404,403" |

#### ffuf参数

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| wordlist | string | 字典文件路径 | 默认字典 |
| threads | int | 线程数 | 40 |
| timeout | int | 超时时间(秒) | 10 |
| mc | string | 匹配状态码 | "200,301,302,403" |
| recursion | bool | 递归扫描 | false |
| recursion_depth | int | 递归深度 | 2 |

#### TXPortMap参数

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| port_range | string | 端口范围 | "top1000" |
| threads | int | 线程数 | 1000 |
| timeout | int | 超时时间(秒) | 3 |

#### fscan参数

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| port | string | 端口范围 | "top1000" |
| threads | int | 线程数 | 100 |
| timeout | int | 超时时间(秒) | 3 |
| no_ping | bool | 不Ping | false |
| web_scan | bool | Web扫描 | true |

### 输出文件说明

每个域名的输出目录结构：

```
outputs/example.com/
├── filtered_subdomains.txt           # 过滤后的子域名列表
├── discovered_urls.txt               # 发现的URL列表
├── port_scan_results.json            # 端口扫描结果
├── httpx_probe_1_results.json        # 第1轮HTTP探测
├── httpx_probe_2_results.json        # 第2轮HTTP探测（如果有）
├── summary.json                      # 数据汇总
├── example.com_web_assets.csv        # 表1: Web资产
├── example.com_ip_ports.csv          # 表2: IP端口
├── oneforall/                        # OneForAll原始输出
├── puzzle/                           # puzzle原始输出
├── dirsearch/                        # dirsearch原始输出
├── httpx/                            # httpx原始输出
└── txportmap/                        # TXPortMap原始输出
```

### 日志文件

Luna的日志保存在 `logs/luna.log`：

```bash
# 查看日志
tail -f logs/luna.log

# 查看错误
grep ERROR logs/luna.log

# 查看特定域名的日志
grep "example.com" logs/luna.log
```

### 性能调优

#### 调整线程数

在首次配置参数时，可以根据网络和目标情况调整线程数：

- **快速网络**: 线程数可以设置较大（100-200）
- **慢速网络**: 线程数应该较小（20-50）
- **目标有WAF**: 线程数应该很小（10-20）

#### 调整超时时间

- **快速响应的目标**: 超时5-10秒
- **慢速响应的目标**: 超时20-30秒

#### 递归深度

- **快速扫描**: 不启用递归
- **深度扫描**: 递归深度2-3

## 常见问题

### Q1: 首次运行需要配置很多参数，太麻烦了

**A**: 只需要配置一次！后续运行会询问"使用上次的参数？"，选择Y即可。

### Q2: 如何修改已保存的参数？

**A**: 运行时选择"n"不使用上次参数，重新配置后选择"Y"保存覆盖。

### Q3: 某个工具执行失败了怎么办？

**A**: 
- 查看日志文件 `logs/luna.log` 了解详情
- 检查工具是否正确安装和编译
- 检查工具路径配置是否正确
- 如果是关键工具（子域名收集），流程会终止
- 如果是非关键工具，流程会继续执行

### Q4: 如何只运行某个工具？

**A**: 创建一个只包含该工具的自定义流程。

### Q5: 批量扫描时如何查看进度？

**A**: Luna会实时显示当前处理的域名和进度，例如：
```
[1/10] 正在处理: example1.com
[2/10] 正在处理: example2.com
```

### Q6: 报告中某些字段为空？

**A**: 这是正常的，可能原因：
- 工具没有探测到数据
- 目标没有响应
- 工具执行失败

### Q7: 如何生成Excel报告？

**A**: 确保安装了pandas和openpyxl：
```bash
pip3 install pandas openpyxl
```

然后Luna会自动生成Excel格式报告。

### Q8: 扫描速度太慢？

**A**: 
- 使用quick流程进行快速扫描
- 增加线程数（重新配置参数）
- 减少字典大小
- 不启用递归扫描

### Q9: 扫描被目标WAF拦截？

**A**:
- 减少线程数
- 增加超时时间
- 使用deep流程的隐蔽模式（如果有）

### Q10: 如何备份和迁移流程配置？

**A**:
```bash
# 备份
cp -r profiles profiles_backup

# 迁移到其他机器
scp -r profiles user@remote:/path/to/Luna/
```

## 最佳实践

### 1. 首次使用建议

- 先用quick流程测试
- 确认工具正常后再用default流程
- 保存好首次配置的参数

### 2. 批量扫描建议

- 将域名分批处理
- 定期检查输出目录
- 注意磁盘空间

### 3. 参数配置建议

- 线程数不要设置过大
- 超时时间根据目标调整
- 字典文件选择合适大小

### 4. 安全建议

- 仅在授权范围内使用
- 注意扫描频率
- 遵守目标的robots.txt

### 5. 结果分析建议

- 优先查看summary.json了解概况
- 重点关注Web资产表
- 结合原始输出进行深入分析

## 下一步

- 查看 [架构设计](architecture.md) 了解Luna的内部实现
- 查看 [开发进度](development_progress.md) 了解最新功能
- 查看 [工具实现说明](tools_implementation.md) 了解工具集成细节

---

**版本**: v1.0
**最后更新**: 2026-01-16
