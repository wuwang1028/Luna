# Luna 报告生成模块说明

## 概述

报告生成模块负责将Luna收集的所有数据整合成结构化的报告，支持CSV和Excel格式。

## 模块文件

**src/report.py** - 报告生成核心模块

## 核心类

### ReportGenerator

报告生成器类，负责数据加载、处理和报告生成。

#### 初始化

```python
generator = ReportGenerator(domain, output_dir)
```

**参数**:
- `domain`: 主域名
- `output_dir`: 输出目录（包含所有工具的输出文件）

#### 主要方法

##### load_data()
加载所有数据源：
- 子域名列表 (`filtered_subdomains.txt`)
- URL列表 (`discovered_urls.txt`)
- HTTP探测结果 (`*_results.json`)
- 端口扫描结果 (`port_scan_results.json`)
- 子域名-IP映射 (`puzzle/puzzle_result.txt`)

##### generate_csv()
生成两个CSV文件：
1. `{domain}_web_assets.csv` - Web资产表
2. `{domain}_ip_ports.csv` - IP端口表

**返回**: (table1_file, table2_file)

##### generate_excel()
生成单个Excel文件，包含两个工作表：
- `{domain}_report.xlsx`
  - Sheet1: Web资产
  - Sheet2: IP端口

**依赖**: pandas, openpyxl

**返回**: excel_file 或 None（如果失败）

##### generate_summary()
生成数据汇总信息：
```json
{
  "domain": "example.com",
  "generated_at": "2026-01-16 10:30:00",
  "web_assets_count": 150,
  "ip_ports_count": 45,
  "unique_subdomains": 23,
  "unique_ips": 12,
  "unique_ports": 8
}
```

保存到 `summary.json`

##### generate_all(format='csv')
一键生成所有报告：
1. 加载数据
2. 生成汇总
3. 生成报告（CSV或Excel）

**参数**:
- `format`: 'csv' 或 'xlsx'

**返回**: (report_files, summary)

## 报告格式

### 表1: Web资产表

| 列名 | 说明 | 示例 |
|------|------|------|
| 主域名 | 目标主域名 | example.com |
| 子域名 | 发现的子域名 | www.example.com |
| 目录URL | 目录挖掘发现的URL | http://www.example.com/admin |
| 状态码 | HTTP状态码 | 200 |
| 网页标题 | 页面标题 | Admin Login |

**数据来源**:
- 子域名: OneForAll + puzzle
- 目录URL: dirsearch + ffuf
- 状态码/标题: httpx

### 表2: IP端口表

| 列名 | 说明 | 示例 |
|------|------|------|
| 主域名 | 目标主域名 | example.com |
| 子域名 | 对应的子域名 | www.example.com |
| IP | IP地址 | 192.168.1.100 |
| 端口 | 开放端口 | 80 |
| 状态码 | HTTP状态码（如果是Web服务） | 200 |
| 网页标题 | 页面标题（如果是Web服务） | Welcome |

**数据来源**:
- IP: puzzle
- 端口: TXPortMap + fscan
- 状态码/标题: httpx（第二轮探测）

## 数据处理逻辑

### 1. 数据加载

```python
# 加载各类数据
subdomains = _load_subdomains()          # 子域名列表
urls = _load_urls()                      # URL列表
http_probes = _load_http_probes()        # HTTP探测结果（字典）
ports = _load_ports()                    # 端口扫描结果
subdomain_ip_map = _load_subdomain_ip_map()  # 子域名-IP映射
```

### 2. 构建Web资产表

```python
def _build_web_assets_table():
    # 1. 遍历所有子域名
    for subdomain in subdomains:
        # 尝试匹配HTTP探测结果
        probe = find_probe(subdomain)
        
        # 添加记录
        web_assets.append({
            'domain': domain,
            'subdomain': subdomain,
            'url': probe.url if probe else '',
            'status_code': probe.status_code if probe else '',
            'title': probe.title if probe else ''
        })
    
    # 2. 添加目录挖掘发现的URL
    for url in urls:
        probe = find_probe(url)
        subdomain = extract_subdomain(url)
        
        web_assets.append({
            'domain': domain,
            'subdomain': subdomain,
            'url': url,
            'status_code': probe.status_code if probe else '',
            'title': probe.title if probe else ''
        })
```

### 3. 构建IP端口表

```python
def _build_ip_ports_table():
    # 遍历所有端口扫描结果
    for port_info in ports:
        ip = port_info['ip']
        port = port_info['port']
        
        # 查找对应的子域名
        subdomains = find_subdomains_by_ip(ip)
        
        for subdomain in subdomains:
            # 尝试匹配HTTP探测结果
            probe = find_probe_by_ip_port(ip, port)
            
            ip_ports.append({
                'domain': domain,
                'subdomain': subdomain,
                'ip': ip,
                'port': port,
                'status_code': probe.status_code if probe else '',
                'title': probe.title if probe else ''
            })
```

## 使用方式

### 方式1: 使用ReportGenerator类

```python
from src.report import ReportGenerator

generator = ReportGenerator('example.com', output_dir)

# 加载数据
generator.load_data()

# 生成CSV
table1, table2 = generator.generate_csv()

# 生成Excel
excel_file = generator.generate_excel()

# 生成汇总
summary = generator.generate_summary()
```

### 方式2: 使用便捷函数

```python
from src.report import generate_report

# 一键生成所有报告
report_files, summary = generate_report('example.com', output_dir, format='csv')

print(f"生成了 {len(report_files)} 个报告文件")
print(f"Web资产: {summary['web_assets_count']} 条")
print(f"IP端口: {summary['ip_ports_count']} 条")
```

### 方式3: 集成在Luna核心流程中

```python
# 在core.py中自动调用
def _execute_profile_for_target(profile, target):
    # ... 执行所有工具 ...
    
    # 生成报告
    report_files, summary = generate_report(target, output_dir, format='csv')
```

## 输出文件

执行完成后，输出目录包含：

```
outputs/example.com/
├── filtered_subdomains.txt           # 子域名列表
├── discovered_urls.txt               # URL列表
├── port_scan_results.json            # 端口扫描结果
├── httpx_probe_1_results.json        # HTTP探测结果1
├── httpx_probe_2_results.json        # HTTP探测结果2
├── summary.json                      # 数据汇总
├── example.com_web_assets.csv        # 表1: Web资产
├── example.com_ip_ports.csv          # 表2: IP端口
└── example.com_report.xlsx           # Excel报告（可选）
```

## 错误处理

### CSV生成失败
- 不太可能失败，因为只依赖Python标准库
- 如果失败，会记录错误日志

### Excel生成失败
- 如果pandas或openpyxl未安装，自动降级到CSV
- 如果生成过程出错，记录错误并降级到CSV

### 数据缺失
- 如果某些数据文件不存在，使用空列表
- 报告中对应字段留空
- 不会导致程序崩溃

## 依赖项

### 必需依赖
- Python标准库: csv, json, pathlib, datetime

### 可选依赖
- pandas >= 1.3.0 (Excel支持)
- openpyxl >= 3.0.0 (Excel支持)

如果不安装pandas和openpyxl，只能生成CSV格式报告。

## 性能考虑

### 内存使用
- 所有数据加载到内存中处理
- 对于大规模扫描（10000+子域名），可能占用较多内存
- 未来可以考虑流式处理

### 处理速度
- CSV生成速度快（秒级）
- Excel生成速度较慢（可能需要数秒到数十秒）
- 主要瓶颈在数据加载和匹配

## 未来改进

### 功能增强
- [ ] 支持HTML格式报告
- [ ] 支持PDF格式报告
- [ ] 添加图表和可视化
- [ ] 支持自定义报告模板
- [ ] 支持增量报告（对比历史数据）

### 性能优化
- [ ] 流式处理大数据集
- [ ] 并行处理多个域名的报告
- [ ] 缓存中间结果

### 数据增强
- [ ] 添加漏洞信息
- [ ] 添加技术栈信息
- [ ] 添加截图
- [ ] 添加时间戳

---

**版本**: v0.3.0 (报告生成模块)
**最后更新**: 2026-01-16
