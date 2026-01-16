# 7个信息收集工具详细分析报告

## 1. httpx - HTTP探测工具

### 技术栈
- 语言: Go
- 类型: 编译型二进制工具

### 核心参数

| 参数分类 | 参数 | 说明 | 示例 |
|---------|------|------|------|
| **输入** | `-l, -list` | 输入文件（主机列表） | `-l hosts.txt` |
| | `-u, -target` | 单个目标 | `-u http://example.com` |
| | `-rr, -request` | 原始HTTP请求文件 | `-rr request.txt` |
| **探测** | `-sc, -status-code` | 显示HTTP状态码 | 默认启用 |
| | `-title` | 获取网页标题 | 默认启用 |
| | `-ip` | 显示IP地址 | 默认启用 |
| | `-cname` | 显示CNAME | 默认启用 |
| | `-cdn` | 检测CDN | 默认启用 |
| | `-tls-grab` | TLS数据抓取 | 可选 |
| **性能** | `-t, -threads` | 线程数 | `-t 50` (默认50) |
| | `-rl, -rate-limit` | 每秒请求数 | `-rl 150` (默认150) |
| **输出** | `-o, -output` | 输出文件 | `-o result.txt` |
| | `-json` | JSON格式输出 | 可选 |
| **过滤** | `-mc, -match-code` | 匹配状态码 | `-mc 200,302` |
| | `-fc, -filter-code` | 过滤状态码 | `-fc 403,401` |
| | `-ms, -match-string` | 匹配字符串 | `-ms admin` |

### 输出格式
```
http://example.com [200] [Title: Example Domain] [IP: 93.184.216.34] [CNAME: example.com]
```

### 支持的输入格式
- URL列表
- 主机列表（自动添加http/https）
- CIDR段

---

## 2. ffuf - Web模糊测试工具

### 技术栈
- 语言: Go
- 类型: 编译型二进制工具

### 核心参数

| 参数分类 | 参数 | 说明 | 示例 |
|---------|------|------|------|
| **输入** | `-u` | 目标URL | `-u https://target/FUZZ` |
| | `-w` | 字典文件 | `-w wordlist.txt` |
| | `-mode` | 模糊模式 | `-mode clusterbomb` |
| | `-d` | POST数据 | `-d 'param=FUZZ'` |
| | `-X` | HTTP方法 | `-X POST` |
| **过滤** | `-mc` | 匹配状态码 | `-mc 200` |
| | `-fc` | 过滤状态码 | `-fc 404,403` |
| | `-fs` | 过滤响应大小 | `-fs 4242` |
| | `-mr` | 匹配正则 | `-mr pattern` |
| | `-fr` | 过滤正则 | `-fr error` |
| **性能** | `-t` | 线程数 | `-t 40` |
| | `-rate` | 请求速率 | `-rate 100` |
| | `-timeout` | 超时时间 | `-timeout 10` |
| **输出** | `-o` | 输出文件 | `-o result.txt` |
| | `-of` | 输出格式 | `-of json` |
| **高级** | `-recursion` | 递归扫描 | 可选 |
| | `-recursion-depth` | 递归深度 | `-recursion-depth 2` |

### 输出格式
```
admin                       [Status: 200, Size: 1234, Words: 45, Lines: 12]
api                         [Status: 200, Size: 5678, Words: 89, Lines: 23]
```

### JSON输出示例
```json
{
  "url": "https://target/admin",
  "status": 200,
  "length": 1234,
  "words": 45,
  "lines": 12,
  "duration": 123456789
}
```

---

## 3. dirsearch - 目录爆破工具

### 技术栈
- 语言: Python
- 类型: 脚本工具

### 核心参数

| 参数分类 | 参数 | 说明 | 示例 |
|---------|------|------|------|
| **输入** | `-u` | 单个URL | `-u http://target.com` |
| | `-l` | URL列表文件 | `-l urls.txt` |
| | `-w` | 字典文件 | `-w wordlist.txt` |
| **扫描** | `-r` | 递归扫描 | 可选 |
| | `-R` | 最大递归深度 | `-R 2` |
| | `--prefixes` | 前缀 | `--prefixes /api,/v1` |
| | `--suffixes` | 后缀 | `--suffixes .php,.html` |
| **过滤** | `-i` | 包含状态码 | `-i 200,301` |
| | `-x` | 排除状态码 | `-x 403,404` |
| | `--exclude-sizes` | 排除大小 | `--exclude-sizes 0B,4KB` |
| **性能** | `-t` | 线程数 | `-t 50` |
| | `-a` | 异步模式 | 可选 |
| | `--delay` | 请求延迟 | `--delay 0.5` |
| **输出** | `-o` | 输出文件 | `-o result.txt` |
| | `--format` | 输出格式 | `--format json` |

### 输出格式
```
Target: http://target.com

[10:30:45] Starting: 
[10:30:50] 200 -  1234B  - /admin
[10:30:51] 200 -  5678B  - /api
[10:30:52] 301 -    0B   - /old -> /new
```

---

## 4. OneForAll - 子域名收集工具

### 技术栈
- 语言: Python
- 类型: 脚本工具
- 依赖: fire, requests, dnspython等

### 核心参数

| 参数分类 | 参数 | 说明 | 示例 |
|---------|------|------|------|
| **输入** | `--target` | 单个域名 | `--target example.com` |
| | `--targets` | 域名文件 | `--targets domains.txt` |
| **功能** | `--brute` | 是否爆破 | `--brute True` |
| | `--dns` | DNS解析 | `--dns True` (默认) |
| | `--req` | HTTP请求验证 | `--req True` (默认) |
| | `--port` | 验证端口 | `--port small/default/large` |
| | `--valid` | 只导出存活 | `--valid True/False/None` |
| **输出** | `--fmt` | 输出格式 | `--fmt csv/json` |
| | `--path` | 输出路径 | `--path /path/to/output` |
| **其他** | `--takeover` | 接管检测 | `--takeover False` |
| | `--show` | 显示结果 | `--show True` |

### 输出格式
- CSV格式: `subdomain,ip,status_code,title,server`
- JSON格式: 结构化JSON数据
- SQLite3数据库: result.sqlite3

### 输出文件
- `example.com.csv` - 单个域名结果
- `all_subdomain_result_*.csv` - 汇总结果
- `result.sqlite3` - 数据库

---

## 5. fscan - 内网综合扫描工具

### 技术栈
- 语言: Go
- 类型: 编译型二进制工具

### 核心参数

| 参数分类 | 参数 | 说明 | 示例 |
|---------|------|------|------|
| **输入** | `-h` | 目标主机/IP段 | `-h 192.168.1.0/24` |
| | `-hf` | 主机文件 | `-hf hosts.txt` |
| **扫描** | `-p` | 端口范围 | `-p 80,443,3306` |
| | `-m` | 扫描模式 | `-m icmp/netbios/all` |
| **爆破** | `-u` | 用户名 | `-u admin` |
| | `-pwd` | 密码 | `-pwd password123` |
| | `-pwdf` | 密码文件 | `-pwdf pass.txt` |
| **Web** | `-proxy` | 代理 | `-proxy http://127.0.0.1:8080` |
| | `-pocpath` | POC路径 | `-pocpath ./pocs` |
| **输出** | `-o` | 输出文件 | `-o result.txt` |
| | `-json` | JSON输出 | 可选 |

### 输出格式
```
[+] 192.168.1.1:22 ssh open
[+] 192.168.1.1:80 http open
[+] 192.168.1.1:3306 mysql open
[+] Title: Apache Server
[+] WebServer: Apache/2.4.41
```

---

## 6. TXPortMap - 端口扫描工具

### 技术栈
- 语言: Go
- 类型: 编译型二进制工具

### 核心参数

| 参数分类 | 参数 | 说明 | 示例 |
|---------|------|------|------|
| **输入** | `-h` | 目标主机 | `-h 192.168.1.1` |
| | `-hf` | 主机文件 | `-hf hosts.txt` |
| **扫描** | `-p` | 端口 | `-p 22,80,443` |
| | `-t1000` | Top1000端口 | 可选 |
| **输出** | `-o` | 输出文件 | `-o result.txt` |
| | `-l` | 日志文件 | `-l scan.log` |

### 输出格式
```
192.168.1.1:22 [open] [ssh] [OpenSSH 7.4]
192.168.1.1:80 [open] [http] [Apache/2.4.41] [Title: Example]
192.168.1.1:443 [open] [https] [nginx/1.14.0]
```

---

## 7. puzzle - 一体化信息收集工具

### 技术栈
- 语言: Go
- 类型: 编译型二进制工具

### 核心参数

| 参数分类 | 参数 | 说明 | 示例 |
|---------|------|------|------|
| **输入** | `-d` | 单个域名/IP | `-d example.com` |
| | `-dl` | 域名/IP文件 | `-dl targets.txt` |
| | `-i` | IP地址 | `-i 192.168.1.1/24` |
| | `-ipl` | IP文件 | `-ipl ips.txt` |
| **模式** | `-m` | 扫描模式 | `-m all/domain/ip` |
| **扫描** | `-p` | 端口 | `-p 1-65535,22,3306` |
| | `-pt` | 端口线程 | `-pt 500` (默认) |
| | `-wt` | Web线程 | `-wt 25` (默认) |
| | `-l3` | 爆破三级域名 | 可选 |
| | `-ping` | 开启ping探测 | 可选 |
| **输出** | `-o` | 输出文件 | `-o result` |
| **其他** | `-timeout` | Web超时 | `-timeout 10` |
| | `-proxy` | Web代理 | `-proxy socks5://127.0.0.1:1080` |

### 输出格式
```
[+] example.com
[+] sub.example.com (IP: 1.2.3.4)
[+] 192.168.1.1:22 [ssh]
[+] 192.168.1.1:80 [http] [Apache]
```

---

## 工具输出对比总结

| 工具 | 输出格式 | 支持JSON | 支持数据库 | 支持自定义格式 |
|------|---------|---------|----------|-------------|
| httpx | 文本/JSON | ✓ | ✗ | ✗ |
| ffuf | 文本/JSON | ✓ | ✗ | ✓ |
| dirsearch | 文本/JSON | ✓ | ✗ | ✓ |
| OneForAll | CSV/JSON | ✓ | ✓ (SQLite3) | ✗ |
| fscan | 文本/JSON | ✓ | ✗ | ✗ |
| TXPortMap | 文本 | ✗ | ✗ | ✗ |
| puzzle | 文本 | ✗ | ✗ | ✗ |

---

## 依赖和环境要求

| 工具 | 依赖 | 环境要求 | 权限要求 |
|------|------|---------|---------|
| httpx | Go运行环境 | 跨平台 | 普通用户 |
| ffuf | Go运行环境 | 跨平台 | 普通用户 |
| dirsearch | Python 3.6+ | 跨平台 | 普通用户 |
| OneForAll | Python 3.6+, fire, requests等 | 跨平台 | 普通用户 |
| fscan | Go运行环境 | 跨平台 | 普通用户/root* |
| TXPortMap | Go运行环境 | 跨平台 | 普通用户 |
| puzzle | Go运行环境, libpcap/npcap | 跨平台 | root/Administrator* |

*: 某些功能需要提升权限

---

## 集成建议

### 工具调用顺序
1. **OneForAll** → 子域名收集
2. **httpx** → HTTP服务探测
3. **ffuf/dirsearch** → Web路径发现
4. **TXPortMap/fscan** → 端口扫描
5. **puzzle** → 综合扫描（可选）

### 参数标准化
- 统一线程参数
- 统一输出格式（JSON）
- 统一超时设置
- 统一代理配置

### 结果聚合
- 统一结果存储格式
- 去重处理
- 结果合并
- 报告生成
