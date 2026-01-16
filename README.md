# Luna - 信息收集工具集成平台

![Status](https://img.shields.io/badge/status-in%20development-yellow)
![Python](https://img.shields.io/badge/python-3.6%2B-blue)
![License](https://img.shields.io/badge/license-TBD-green)

Luna是一个基于Python开发的CLI工具，旨在整合和统一调用多个常用的信息收集工具，提供一站式的安全测试解决方案。

## 🎯 项目目标

将以下7个信息收集工具进行整合，提供统一的调用接口、自动化流程和结果管理：

| 工具 | 语言 | 功能 |
|------|------|------|
| **OneForAll** | Python | 子域名收集 |
| **puzzle** | Go | 综合信息收集 |
| **httpx** | Go | HTTP探测 |
| **dirsearch** | Python | 目录爆破 |
| **ffuf** | Go | Web模糊测试 |
| **fscan** | Go | 内网综合扫描 |
| **TXPortMap** | Go | 端口扫描 |

## ✨ 核心特性

### 🔧 模块化设计
- 7个独立模块，灵活组合
- 每个模块可包含多个工具
- 支持自定义工作流程

### 📋 流程管理
- **默认流程**：完整的7步信息收集流程
- **自定义流程**：用户可创建和保存自己的流程
- **流程-参数绑定**：每个流程有独立的参数配置

### ⚙️ 智能参数管理
- **首次运行**：交互式参数配置，自动保存
- **后续运行**：询问是否使用上次参数
- **参数覆盖**：支持临时修改参数

### 📦 批量处理
- 支持单域名和批量域名处理
- 串行执行，确保数据完整性
- 每个域名独立输出目录

### 📊 自动报告生成
- **表1**：主域名 → 子域名 → 目录URL → 状态码 → 网页标题
- **表2**：主域名 → 子域名 → IP → 端口 → 状态码 → 网页标题
- 支持CSV和XLSX格式

## 🏗️ 默认流程

```
1. 子域名收集（OneForAll + puzzle）
   ↓ 自动过滤邮件域名
   
2. 目录挖掘（dirsearch）
   ↓ 快速模式
   
3. HTTP探测-第一轮（httpx）
   ↓ 探测目录挖掘结果
   
4. 端口扫描（TXPortMap）
   ↓ 扫描puzzle收集的IP
   
5. HTTP探测-第二轮（httpx）
   ↓ 探测端口扫描结果
   
6. 数据整合（Luna）
   ↓ 解析、清洗、关联
   
7. 报告生成
   ↓ 生成两张表格
```

## 📁 项目结构

```
Luna/
├── luna.py                     # 主程序入口
├── src/                        # Luna源代码
│   ├── __init__.py
│   ├── core.py                # 核心逻辑
│   ├── modules.py             # 模块定义
│   ├── profile.py             # 流程管理
│   ├── tools_wrapper.py       # 工具调用封装
│   ├── data_processor.py      # 数据处理
│   ├── report.py              # 报告生成
│   ├── config.py              # 配置管理
│   └── utils.py               # 工具函数
├── tools/                      # 工具目录
│   ├── OneForAll-master/
│   ├── httpx-dev/
│   ├── ffuf-master/
│   ├── dirsearch-master/
│   ├── fscan-main/
│   ├── TXPortMap-main/
│   └── puzzle-master/
├── profiles/                   # 流程配置文件
│   ├── default.json           # 默认流程
│   ├── quick.json             # 快速扫描
│   └── custom.json            # 用户自定义
├── outputs/                    # 输出结果目录
│   ├── example.com/
│   │   ├── 1_subdomain_collection/
│   │   ├── 2_directory_scan/
│   │   ├── 3_http_probe_1/
│   │   ├── 4_port_scan/
│   │   ├── 5_http_probe_2/
│   │   └── final_report.csv
│   └── test.com/
├── config/                     # 全局配置
│   └── settings.yaml
├── docs/                       # 文档
│   ├── tools_analysis.md      # 工具概览分析
│   ├── tools_detailed_analysis.md  # 工具详细参数
│   └── architecture.md        # 架构设计文档
└── README.md                   # 项目说明
```

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/wuwang1028/Luna.git
cd Luna

# 安装Python依赖
pip install -r requirements.txt

# 准备工具（将7个工具放入tools/目录）
# Go工具需要预编译
```

### 基本使用

```bash
# 首次使用默认流程
python luna.py run --profile default --target example.com
# → 交互式输入各工具参数
# → 执行完整流程
# → 生成报告

# 再次使用（使用保存的参数）
python luna.py run --profile default --target example.com
# → "使用上次的参数？(Y/n)" 

# 批量处理
python luna.py run --profile default --target-file domains.txt
```

### 流程管理

```bash
# 列出所有流程
python luna.py list-profiles

# 查看流程详情
python luna.py show-profile default

# 创建自定义流程
python luna.py create-profile quick --modules 1,3

# 删除流程
python luna.py delete-profile quick
```

## 📖 文档

详细文档请查看：
- [工具概览分析](docs/tools_analysis.md) - 7个工具的功能分类和协作流程
- [工具详细参数分析](docs/tools_detailed_analysis.md) - 每个工具的参数、输出格式、使用方式
- [架构设计文档](docs/architecture.md) - Luna的完整架构设计

## 🛠️ 技术栈

- **开发语言**: Python 3.6+
- **CLI框架**: argparse / click
- **进程管理**: subprocess
- **数据处理**: pandas（可选）
- **配置管理**: JSON
- **日志**: logging

## 📋 开发计划

- [x] 工具分析和调研
- [x] 需求讨论和架构设计
- [ ] 核心框架实现
- [ ] 工具调用模块实现
- [ ] 数据处理模块实现
- [ ] 报告生成功能实现
- [ ] 批量处理支持
- [ ] 自定义流程支持
- [ ] 测试和优化

## ⚠️ 注意事项

### 环境要求

**Python依赖**：
- Python 3.6+
- 需要安装OneForAll和dirsearch的依赖

**Go工具**：
- 需要预编译成二进制文件
- 确保二进制文件有执行权限

**系统权限**：
- puzzle需要root权限（Linux）或管理员权限（Windows）
- 需要安装libpcap（Linux）或npcap（Windows）

### 特殊处理

**puzzle输出问题**：
- ⚠️ 如果输出文件已存在，puzzle会拒绝输出
- Luna会在执行前自动检查并删除旧文件

**OneForAll输出**：
- OneForAll默认输出到自己的results/目录
- Luna会自动移动到统一的输出目录

## 🔒 免责声明

⚠️ **重要提醒**：

本工具仅用于**授权的安全测试**，使用者需自行承担使用本工具的法律责任。

- 仅面向合法授权的企业安全建设行为与个人学习行为
- 在使用本工具进行检测时，您应确保该行为符合当地的法律法规
- 已经取得了足够的授权，请勿对非授权目标进行扫描
- 如您在使用本工具的过程中存在任何非法行为，您需自行承担相应后果
- 我们将不承担任何法律及连带责任

## 📄 许可证

待定

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📧 联系方式

- GitHub: [wuwang1028/Luna](https://github.com/wuwang1028/Luna)
- Issues: [提交问题](https://github.com/wuwang1028/Luna/issues)

---

**Luna** - 让信息收集更简单、更高效 🌙
