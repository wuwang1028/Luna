# Luna - 信息收集工具集成平台

[![Version](https://img.shields.io/badge/version-0.3.0-blue.svg)](https://github.com/wuwang1028/Luna)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](docs/TEST_RESULTS.md)

Luna是一个模块化的信息收集工具集成平台，整合了7个常用的信息收集工具，提供统一的CLI接口、流程管理和自动化报告生成功能。

## ✨ 特性

- 🔧 **模块化设计** - 灵活组合7个信息收集工具
- 📋 **流程管理** - 预设和自定义扫描流程
- 🔄 **参数绑定** - 每个流程保存独立的参数配置
- 📊 **自动报告** - 生成CSV/Excel格式的结构化报告
- 🎯 **批量处理** - 支持多域名串行扫描
- 💾 **数据整合** - 自动合并、去重和过滤数据
- 🎨 **友好界面** - 彩色输出和交互式配置

## 🛠️ 集成工具

| 工具 | 类型 | 功能 | 官方仓库 |
|------|------|------|---------|
| **OneForAll** | Python | 专业子域名收集 | [shmilylty/OneForAll](https://github.com/shmilylty/OneForAll) |
| **puzzle** | Go | 综合信息收集 | [Becivells/puzzle](https://github.com/Becivells/puzzle) |
| **httpx** | Go | HTTP服务探测 | [projectdiscovery/httpx](https://github.com/projectdiscovery/httpx) |
| **dirsearch** | Python | 目录爆破 | [maurosoria/dirsearch](https://github.com/maurosoria/dirsearch) |
| **ffuf** | Go | Web模糊测试 | [ffuf/ffuf](https://github.com/ffuf/ffuf) |
| **fscan** | Go | 内网综合扫描 | [shadow1ng/fscan](https://github.com/shadow1ng/fscan) |
| **TXPortMap** | Go | 快速端口扫描 | [4dogs-cn/TXPortMap](https://github.com/4dogs-cn/TXPortMap) |

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/wuwang1028/Luna.git
cd Luna

# 安装Python依赖
pip3 install -r requirements.txt

# 准备工具（详见安装手册）
# 1. 将工具放入 tools/ 目录
# 2. 编译Go工具
# 3. 安装Python工具依赖
```

详细安装步骤请参考 [安装部署手册](docs/INSTALLATION.md)

### 使用

```bash
# 查看帮助
python3 luna.py --help

# 列出可用流程
python3 luna.py list

# 使用默认流程扫描
python3 luna.py run --profile default --target example.com

# 批量扫描
python3 luna.py run --profile quick --target-file domains.txt

# 创建自定义流程
python3 luna.py create my-scan
```

详细使用说明请参考 [用户使用手册](docs/USER_GUIDE.md)

## 📖 文档

### 用户文档
- [安装部署手册](docs/INSTALLATION.md) - 完整的安装和配置指南
- [用户使用手册](docs/USER_GUIDE.md) - 详细的使用说明和示例
- [常见问题](docs/USER_GUIDE.md#常见问题) - FAQ和故障排除

### 开发文档
- [架构设计](docs/architecture.md) - 系统架构和设计理念
- [工具实现说明](docs/tools_implementation.md) - 工具集成细节
- [开发进度](docs/development_progress.md) - 项目开发进度
- [测试指南](docs/TESTING_GUIDE.md) - 测试方法和脚本
- [测试结果](docs/TEST_RESULTS.md) - 最新测试报告

## 🎯 使用场景

### 场景1: 外网信息收集
```bash
python3 luna.py run -p default -t target.com
```
完整流程：子域名收集 → 目录挖掘 → HTTP探测 → 端口扫描 → 生成报告

### 场景2: 快速探测
```bash
python3 luna.py run -p quick -t target.com
```
快速流程：子域名收集 → HTTP探测 → 生成报告

### 场景3: 深度扫描
```bash
python3 luna.py run -p deep -t target.com
```
深度流程：全面信息收集 + 递归目录 + 漏洞扫描

### 场景4: 批量扫描
```bash
python3 luna.py run -p default -f domains.txt
```
批量处理多个域名，每个域名独立输出

## 📊 输出报告

Luna自动生成两个报告表：

### 表1: Web资产表
| 主域名 | 子域名 | 目录URL | 状态码 | 网页标题 |
|--------|--------|---------|--------|---------|
| example.com | www.example.com | http://www.example.com/admin | 200 | Admin Panel |

### 表2: IP端口表
| 主域名 | 子域名 | IP | 端口 | 状态码 | 网页标题 |
|--------|--------|----|----|--------|---------|
| example.com | www.example.com | 192.168.1.1 | 80 | 200 | Welcome |

报告格式：CSV（默认）或 Excel（需要pandas）

## 🏗️ 项目结构

```
Luna/
├── luna.py                 # 主程序入口
├── src/                    # 源代码
│   ├── config.py          # 配置管理
│   ├── core.py            # 核心逻辑
│   ├── profile.py         # 流程管理
│   ├── modules.py         # 工具封装
│   ├── data_processor.py  # 数据处理
│   ├── report.py          # 报告生成
│   ├── tools_wrapper.py   # 工具调用基类
│   └── utils.py           # 工具函数
├── tools/                  # 外部工具目录
├── profiles/               # 流程配置文件
│   ├── default.json       # 默认流程
│   ├── quick.json         # 快速流程
│   └── deep.json          # 深度流程
├── outputs/                # 输出目录
├── docs/                   # 文档
└── requirements.txt        # Python依赖
```

## 🔧 核心功能

### 1. 流程管理
- 3个内置流程（default, quick, deep）
- 支持自定义流程创建
- 流程配置持久化
- 参数绑定和复用

### 2. 工具调用
- 统一的工具调用接口
- 自动捕获stdout/stderr
- 超时控制和错误处理
- 特殊工具适配（puzzle文件冲突、OneForAll结果移动）

### 3. 数据处理
- 多源数据合并去重
- 自动过滤邮件域名
- 子域名-IP映射
- URL收集和整理

### 4. 报告生成
- 双表格式报告
- CSV/Excel支持
- 数据汇总统计
- 自动降级处理

## 📈 开发状态

**当前版本**: v0.3.0

**开发进度**: 90%

- ✅ 阶段1: 工具分析和调研
- ✅ 阶段2: 需求讨论和架构设计
- ✅ 阶段3: 更新设计文档到GitHub
- ✅ 阶段4: 实现Luna核心框架
- ✅ 阶段5: 实现工具调用和数据处理模块
- ✅ 阶段6: 实现报告生成功能
- 🔄 阶段7: 测试和优化（进行中）
- ⏳ 阶段8: 交付最终程序

**测试状态**: 
- 基础单元测试: ✅ 100% 通过
- 集成测试: ⏳ 待进行（需要安装实际工具）

详见 [开发进度](docs/development_progress.md) 和 [测试结果](docs/TEST_RESULTS.md)

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

### 贡献方式
1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 问题反馈
- 使用 [Issues](https://github.com/wuwang1028/Luna/issues) 报告bug
- 使用 [Discussions](https://github.com/wuwang1028/Luna/discussions) 讨论功能

## ⚠️ 免责声明

本工具仅供安全研究和授权测试使用。使用本工具进行未授权的扫描和渗透测试是违法的。

使用者应当：
- 仅在授权范围内使用
- 遵守相关法律法规
- 承担使用本工具的一切后果

作者不对使用本工具造成的任何损失或法律责任负责。

## 📝 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 👨‍💻 作者

**wuwang1028**
- GitHub: [@wuwang1028](https://github.com/wuwang1028)

## 🙏 致谢

感谢以下开源项目：
- [OneForAll](https://github.com/shmilylty/OneForAll) - 子域名收集
- [puzzle](https://github.com/Becivells/puzzle) - 综合信息收集
- [httpx](https://github.com/projectdiscovery/httpx) - HTTP探测
- [dirsearch](https://github.com/maurosoria/dirsearch) - 目录爆破
- [ffuf](https://github.com/ffuf/ffuf) - Web模糊测试
- [fscan](https://github.com/shadow1ng/fscan) - 内网扫描
- [TXPortMap](https://github.com/4dogs-cn/TXPortMap) - 端口扫描

## 📮 联系方式

如有问题或建议，请通过以下方式联系：
- GitHub Issues: https://github.com/wuwang1028/Luna/issues

---

**⭐ 如果这个项目对你有帮助，请给个Star！**

**🔔 Watch本仓库以获取最新更新**

---

*最后更新: 2026-01-16*
