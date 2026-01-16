# Luna 核心框架实现说明

## 已完成的工作

### 1. 项目结构

```
Luna/
├── luna.py                     # ✅ 主程序入口
├── requirements.txt            # ✅ Python依赖
├── src/                        # ✅ 源代码目录
│   ├── __init__.py
│   ├── config.py              # ✅ 配置管理
│   ├── utils.py               # ✅ 工具函数
│   ├── profile.py             # ✅ 流程管理
│   └── core.py                # ✅ 核心逻辑
├── profiles/                   # ✅ 流程配置目录
│   ├── default.json           # ✅ 默认流程
│   ├── quick.json             # ✅ 快速扫描
│   └── deep.json              # ✅ 深度扫描
├── outputs/                    # 输出目录
├── logs/                       # 日志目录
└── tools/                      # 工具目录（待放入）
```

### 2. 核心模块

#### 2.1 config.py - 配置管理
**功能**：
- 定义所有路径常量
- 工具路径映射
- 工具信息管理
- 默认参数配置
- 邮件域名过滤规则

**关键函数**：
- `get_tool_path()` - 获取工具路径
- `get_tool_type()` - 获取工具类型
- `get_tool_info()` - 获取工具信息
- `get_default_params()` - 获取默认参数
- `get_output_dir()` - 获取输出目录

#### 2.2 utils.py - 工具函数
**功能**：
- 日志管理
- 文件操作
- 数据处理
- 用户交互
- 输出美化

**关键函数**：
- `setup_logger()` - 设置日志
- `is_email_related()` - 判断邮件域名
- `filter_email_domains()` - 过滤邮件域名
- `read_file_lines()` / `write_file_lines()` - 文件读写
- `merge_and_deduplicate()` - 合并去重
- `ask_yes_no()` / `ask_input()` / `ask_choice()` - 用户交互
- `print_*()` - 输出美化

#### 2.3 profile.py - 流程管理
**功能**：
- 流程的创建、加载、保存
- 交互式参数配置
- 工具选择和排序
- 多次调用同一工具的处理

**关键类**：
- `Profile` - 流程类
  - `add_tool()` - 添加工具
  - `save()` - 保存流程
  - `load()` - 加载流程
  - `display()` - 显示详情

- `ProfileManager` - 流程管理器
  - `list_profiles()` - 列出所有流程
  - `profile_exists()` - 检查流程是否存在
  - `delete_profile()` - 删除流程
  - `create_profile_interactive()` - 交互式创建流程
  - `_configure_tool_params()` - 配置工具参数

#### 2.4 core.py - 核心逻辑
**功能**：
- 流程执行调度
- 目标解析
- 参数管理
- 流程管理接口

**关键类**：
- `LunaCore` - 核心类
  - `run_profile()` - 运行流程
  - `create_profile()` - 创建流程
  - `list_profiles()` - 列出流程
  - `show_profile()` - 显示流程详情
  - `delete_profile()` - 删除流程
  - `parse_targets()` - 解析目标

### 3. 命令行接口

#### 3.1 luna.py - 主程序
**使用Click框架实现的命令行工具**

**可用命令**：
```bash
# 运行流程
luna run --profile <name> --target <domain>
luna run --profile <name> --target-file <file>

# 创建流程
luna create <name>
luna create <name> --from <existing-profile>

# 列出流程
luna list

# 显示流程详情
luna show <name>

# 删除流程
luna delete <name>

# 编辑流程（暂未实现）
luna edit <name>
```

### 4. 内置流程

#### 4.1 default - 默认完整流程
```
1. oneforall - 子域名收集
2. puzzle - 子域名收集和IP获取
3. dirsearch - 目录挖掘
4. httpx (httpx_probe_1) - HTTP探测-目录结果
5. txportmap - 端口扫描
6. httpx (httpx_probe_2) - HTTP探测-端口结果
```

#### 4.2 quick - 快速扫描
```
1. puzzle - 子域名收集
2. httpx - HTTP探测
```

#### 4.3 deep - 深度扫描
```
1. oneforall - 子域名收集
2. puzzle - 子域名收集和IP获取
3. ffuf - 递归目录爆破
4. httpx - HTTP探测
5. fscan - 综合漏洞扫描
```

## 测试结果

### 基本功能测试

✅ **命令行帮助**
```bash
$ python3 luna.py --help
# 正常显示帮助信息
```

✅ **列出流程**
```bash
$ python3 luna.py list
# 正常显示3个内置流程
```

✅ **显示流程详情**
```bash
$ python3 luna.py show default
# 正常显示default流程的详细信息
```

## 待实现功能

### 阶段5：工具调用和数据处理模块
- [ ] `tools_wrapper.py` - 工具调用封装
- [ ] `modules.py` - 模块执行逻辑
- [ ] `data_processor.py` - 数据处理
- [ ] 实现7个工具的调用逻辑
- [ ] 实现输出捕获和解析
- [ ] 实现邮件域名过滤
- [ ] 实现数据去重和合并

### 阶段6：报告生成功能
- [ ] `report.py` - 报告生成
- [ ] 实现表1生成（Web资产表）
- [ ] 实现表2生成（IP端口表）
- [ ] 支持CSV格式
- [ ] 支持XLSX格式（可选）

### 阶段7：测试和优化
- [ ] 单元测试
- [ ] 集成测试
- [ ] 实际环境测试
- [ ] 性能优化
- [ ] 错误处理完善

## 使用说明

### 安装依赖
```bash
cd Luna
pip3 install -r requirements.txt
```

### 基本使用
```bash
# 列出所有流程
python3 luna.py list

# 查看流程详情
python3 luna.py show default

# 创建自定义流程
python3 luna.py create my-scan

# 运行流程（工具调用功能尚未实现）
python3 luna.py run --profile quick --target example.com
```

## 注意事项

1. **工具目录**：需要将7个工具放入 `tools/` 目录
2. **Go工具编译**：Go工具需要预编译成二进制文件
3. **Python工具**：OneForAll和dirsearch需要安装依赖
4. **权限问题**：puzzle可能需要root权限

## 下一步开发

1. 实现工具调用封装（`tools_wrapper.py`）
2. 实现各工具的具体调用逻辑
3. 实现输出解析和数据处理
4. 实现报告生成功能
5. 完整测试和优化

---

**当前版本**: v0.1.0 (核心框架)
**最后更新**: 2026-01-16
