# Luna 工具调用模块实现说明

## 概述

本文档说明Luna工具调用和数据处理模块的实现细节。

## 模块结构

### 1. tools_wrapper.py - 工具调用封装基类

**核心类**：

#### ToolResult
工具执行结果的数据结构：
```python
class ToolResult:
    success: bool          # 是否成功
    output: str           # 标准输出
    error: str            # 错误输出
    output_file: Path     # 输出文件路径
    data: Dict            # 解析后的数据
```

#### ToolWrapper (抽象基类)
所有工具封装的基类：
- `build_command()` - 构建命令行参数（抽象方法）
- `parse_output()` - 解析工具输出（抽象方法）
- `execute()` - 执行工具（通用实现）

**关键功能**：
- 统一的工具调用接口
- 自动捕获stdout/stderr
- 超时控制
- 错误处理
- 输出文件管理（特别处理puzzle的文件冲突问题）

### 2. modules.py - 各工具的具体实现

实现了7个工具的封装类：

#### OneForAllWrapper
- **功能**：子域名收集
- **输入**：域名
- **输出**：CSV文件（自动移动到Luna输出目录）
- **解析**：从CSV提取子域名列表

#### PuzzleWrapper
- **功能**：子域名收集 + IP获取
- **输入**：域名
- **输出**：文本文件
- **特殊处理**：自动删除已存在的输出文件
- **解析**：提取子域名和对应IP

#### HttpxWrapper
- **功能**：HTTP服务探测
- **输入**：URL列表文件或单个URL
- **输出**：JSONL格式（每行一个JSON对象）
- **解析**：提取URL、状态码、标题等信息

#### DirsearchWrapper
- **功能**：目录爆破
- **输入**：URL或URL列表文件
- **输出**：JSON文件
- **解析**：提取发现的URL列表

#### FfufWrapper
- **功能**：Web模糊测试
- **输入**：URL模板（包含FUZZ关键字）
- **输出**：JSON文件
- **解析**：提取发现的URL列表

#### FscanWrapper
- **功能**：内网综合扫描
- **输入**：IP或CIDR
- **输出**：文本文件
- **解析**：提取端口和漏洞信息

#### TXPortMapWrapper
- **功能**：端口扫描
- **输入**：IP或IP列表文件
- **输出**：文本文件
- **解析**：提取IP、端口、服务信息

### 3. data_processor.py - 数据处理模块

**核心类**：DataProcessor

**主要方法**：

#### process_subdomain_results()
- 处理OneForAll和puzzle的子域名收集结果
- 合并去重
- **自动过滤邮件域名**（绑定功能）
- 保存到 `filtered_subdomains.txt`

#### process_directory_results()
- 处理dirsearch和ffuf的目录挖掘结果
- 合并去重
- 保存到 `discovered_urls.txt`

#### process_http_probe_results()
- 处理httpx的HTTP探测结果
- 支持多次调用（通过alias区分）
- 保存到 `{alias}_results.json`

#### process_port_scan_results()
- 处理TXPortMap和fscan的端口扫描结果
- 基于IP+端口去重
- 保存到 `port_scan_results.json`

#### generate_summary()
- 生成数据汇总统计

## 工具执行流程

### 1. 目标准备

根据工具类型准备不同的输入：

```python
def _prepare_tool_target(tool_name, target, context):
    # 子域名收集：直接使用域名
    if tool_name in ['oneforall', 'puzzle']:
        return target
    
    # 目录挖掘：使用子域名列表文件
    if tool_name in ['dirsearch', 'ffuf']:
        return subdomain_file_path
    
    # HTTP探测：使用URL列表文件或子域名列表
    if tool_name == 'httpx':
        return url_file_path or subdomain_file_path
    
    # 端口扫描：使用IP列表文件
    if tool_name in ['txportmap', 'fscan']:
        return ip_file_path
```

### 2. 工具执行

```python
def _execute_tool(tool_name, alias, target, params, ...):
    # 1. 获取工具封装
    wrapper = get_tool_wrapper(tool_name, output_dir)
    
    # 2. 准备目标输入
    tool_target = _prepare_tool_target(tool_name, target, context)
    
    # 3. 执行工具
    result = wrapper.execute(tool_target, params)
    
    # 4. 处理结果
    _process_tool_result(tool_name, alias, result, context, data_processor)
```

### 3. 结果处理

```python
def _process_tool_result(tool_name, alias, result, context, data_processor):
    # 根据工具类型调用相应的数据处理方法
    if tool_name in ['oneforall', 'puzzle']:
        subdomains = data_processor.process_subdomain_results(...)
        context['subdomains'].extend(subdomains)
    
    elif tool_name in ['dirsearch', 'ffuf']:
        urls = data_processor.process_directory_results(...)
        context['urls'].extend(urls)
    
    elif tool_name == 'httpx':
        probes = data_processor.process_http_probe_results(...)
        context['http_probes'].extend(probes)
    
    elif tool_name in ['txportmap', 'fscan']:
        ports = data_processor.process_port_scan_results(...)
        context['ports'].extend(ports)
```

## 数据流转

```
目标域名
    ↓
OneForAll/puzzle → 子域名列表 → 过滤邮件域名
    ↓
dirsearch/ffuf → URL列表
    ↓
httpx (第1轮) → HTTP探测结果
    ↓
TXPortMap/fscan → 端口列表
    ↓
httpx (第2轮) → HTTP探测结果
    ↓
数据汇总 → 报告生成
```

## 输出目录结构

```
outputs/
└── example.com/
    ├── filtered_subdomains.txt          # 过滤后的子域名
    ├── discovered_urls.txt              # 发现的URL
    ├── port_scan_results.json           # 端口扫描结果
    ├── httpx_probe_1_results.json       # 第1轮HTTP探测
    ├── httpx_probe_2_results.json       # 第2轮HTTP探测
    ├── oneforall/                       # OneForAll输出
    │   └── example.com_2026-01-16.csv
    ├── puzzle/                          # puzzle输出
    │   └── puzzle_result.txt
    ├── dirsearch/                       # dirsearch输出
    │   └── dirsearch_result.json
    ├── httpx/                           # httpx输出
    │   └── httpx_result.json
    └── txportmap/                       # TXPortMap输出
        └── txportmap_result.txt
```

## 错误处理

### 关键工具失败策略
- **关键工具**：oneforall, puzzle（子域名收集）
- **失败处理**：终止流程，返回错误

### 非关键工具失败策略
- **非关键工具**：其他所有工具
- **失败处理**：记录警告，继续执行后续工具

## 特殊处理

### 1. puzzle输出文件冲突
```python
def _prepare_output_file(filename):
    output_file = self.output_dir / filename
    
    # puzzle如果文件存在会拒绝输出
    if self.tool_name == "puzzle" and output_file.exists():
        output_file.unlink()  # 删除旧文件
    
    return output_file
```

### 2. OneForAll结果移动
```python
# OneForAll输出到自己的results目录
# 需要找到最新的CSV文件并移动到Luna输出目录
results_dir = self.tool_path.parent / "results"
csv_files = list(results_dir.glob("*.csv"))
latest_csv = max(csv_files, key=lambda p: p.stat().st_mtime)
latest_csv.rename(target_file)
```

### 3. 邮件域名过滤
```python
# 在子域名收集后自动执行
def process_subdomain_results(...):
    # 合并去重
    unique_subdomains = list(set(all_subdomains))
    
    # 自动过滤邮件域名
    filtered_subdomains = filter_email_domains(unique_subdomains)
    
    return filtered_subdomains
```

## 测试状态

### 已测试
- ✅ 模块导入无错误
- ✅ 语法检查通过
- ✅ 基本命令行功能正常

### 待测试
- ⏳ 实际工具执行（需要工具二进制文件）
- ⏳ 数据解析准确性
- ⏳ 错误处理完整性
- ⏳ 边界情况处理

## 下一步

1. 将实际工具放入 `tools/` 目录
2. 编译Go工具
3. 安装Python工具依赖
4. 进行实际环境测试
5. 实现报告生成功能

---

**版本**: v0.2.0 (工具调用模块)
**最后更新**: 2026-01-16
