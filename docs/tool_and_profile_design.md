# Luna 工具和流程设计详解

## 重要设计变更

**核心变更**：从"模块"概念改为"工具"概念

**原因**：
- 避免模块和工具的混淆
- 用户需要精确控制使用哪个工具
- 例如：用户可能只想用ffuf而不是dirsearch

---

## 一、工具定义

### 1.1 可用工具列表

用户在创建流程时，以**工具**为最小单位进行选择和配置。

| 工具ID | 工具名称 | 语言 | 主要功能 | 说明 |
|--------|---------|------|---------|------|
| 1 | OneForAll | Python | 子域名收集 | 专业子域名枚举工具，多数据源 |
| 2 | puzzle | Go | 子域名收集 + 综合扫描 | 一体化信息收集，可同时获取IP |
| 3 | httpx | Go | HTTP探测 | 快速HTTP服务探测，获取状态码和标题 |
| 4 | dirsearch | Python | 目录爆破 | Web路径发现，支持递归 |
| 5 | ffuf | Go | 目录爆破/Web模糊测试 | 高速模糊测试，功能强大 |
| 6 | fscan | Go | 内网综合扫描 | 端口扫描+漏洞检测+爆破 |
| 7 | TXPortMap | Go | 端口扫描 | 快速端口扫描和指纹识别 |

### 1.2 工具功能分类

**子域名收集**：
- **OneForAll**：专业、全面、多数据源、慢但准确
- **puzzle**：快速、集成度高、可同时获取IP

**目录爆破**：
- **dirsearch**：Python实现、递归支持好、配置灵活
- **ffuf**：Go实现、速度快、功能强大、支持模糊测试

**HTTP探测**：
- **httpx**：专业HTTP探测工具，支持多种探针

**端口扫描**：
- **TXPortMap**：快速、准确、专注端口扫描
- **fscan**：功能更全面，包含漏洞检测和爆破

**综合扫描**：
- **fscan**：内网综合扫描，适合内网渗透
- **puzzle**：外网信息收集，流程化

---

## 二、流程（Profile）系统

### 2.1 流程定义

**流程** = 工具组合 + 执行顺序 + 参数配置

流程是用户自定义的工作流，由一个或多个工具按特定顺序执行组成。

### 2.2 流程配置文件结构

```json
{
  "name": "my-scan",
  "description": "我的自定义扫描流程",
  "created_at": "2026-01-16 10:30:00",
  "updated_at": "2026-01-16 10:30:00",
  "tools": [
    {
      "name": "puzzle",
      "order": 1,
      "alias": null,
      "description": "子域名收集和IP获取",
      "params": {
        "mode": "domain",
        "timeout": 10,
        "l3": false,
        "ping": false,
        "pt": 500,
        "wt": 25
      }
    },
    {
      "name": "ffuf",
      "order": 2,
      "alias": null,
      "description": "目录爆破",
      "params": {
        "wordlist": "/path/to/dict.txt",
        "threads": 40,
        "timeout": 10,
        "mc": "200,301,302,403",
        "recursion": false
      }
    },
    {
      "name": "httpx",
      "order": 3,
      "alias": "httpx_probe",
      "description": "HTTP探测",
      "params": {
        "threads": 50,
        "timeout": 10,
        "status_code": true,
        "title": true,
        "tech_detect": true
      }
    }
  ]
}
```

### 2.3 内置流程

**default - 默认完整流程**
```json
{
  "name": "default",
  "description": "默认完整流程：子域名收集→目录挖掘→HTTP探测→端口扫描→HTTP探测",
  "tools": [
    {"name": "oneforall", "order": 1},
    {"name": "puzzle", "order": 2},
    {"name": "dirsearch", "order": 3},
    {"name": "httpx", "order": 4, "alias": "httpx_probe_1"},
    {"name": "txportmap", "order": 5},
    {"name": "httpx", "order": 6, "alias": "httpx_probe_2"}
  ]
}
```

**quick - 快速扫描**
```json
{
  "name": "quick",
  "description": "快速扫描：仅子域名收集和HTTP探测",
  "tools": [
    {"name": "puzzle", "order": 1},
    {"name": "httpx", "order": 2}
  ]
}
```

**deep - 深度扫描**
```json
{
  "name": "deep",
  "description": "深度扫描：全面信息收集+递归目录+漏洞扫描",
  "tools": [
    {"name": "oneforall", "order": 1},
    {"name": "puzzle", "order": 2},
    {"name": "ffuf", "order": 3},  // 使用ffuf进行递归扫描
    {"name": "httpx", "order": 4},
    {"name": "fscan", "order": 5}   // 使用fscan进行漏洞扫描
  ]
}
```

---

## 三、创建自定义流程

### 3.1 方式1：交互式创建

```bash
luna create-profile my-scan
```

**完整交互过程**：

```
[Luna] 创建新流程

[Luna] 流程名称: my-scan
[Luna] 流程描述 (可选): 我的自定义扫描流程

[Luna] 可用工具:
  1. OneForAll    - 子域名收集 (专业、全面)
  2. puzzle       - 子域名收集 + 综合扫描 (快速、集成)
  3. httpx        - HTTP探测
  4. dirsearch    - 目录爆破 (Python、递归支持好)
  5. ffuf         - 目录爆破/Web模糊测试 (Go、速度快)
  6. fscan        - 内网综合扫描
  7. TXPortMap    - 端口扫描

[Luna] 请选择要使用的工具 (用逗号分隔, 如: 2,5,3): 2,5,3

[Luna] 已选择:
  - puzzle (子域名收集 + 综合扫描)
  - ffuf (目录爆破/Web模糊测试)
  - httpx (HTTP探测)

[Luna] 执行顺序:
  1. puzzle
  2. ffuf
  3. httpx

[Luna] 是否调整顺序？(Y/n): n

[Luna] 开始配置各工具参数...

=== 配置 puzzle (1/3) ===
[Luna] 用途描述 (可选): 子域名收集和IP获取
[Luna] 扫描模式 (all/domain/ip, 默认: domain): domain
[Luna] 超时时间(秒, 默认: 10): 10
[Luna] 是否爆破三级域名？(y/N): n
[Luna] 是否开启ping探测？(y/N): n
[Luna] 端口爆破线程 (默认: 500): 500
[Luna] Web指纹爆破线程 (默认: 25): 25

=== 配置 ffuf (2/3) ===
[Luna] 用途描述 (可选): 目录爆破
[Luna] 字典文件路径: /path/to/wordlist.txt
[Luna] 线程数 (默认: 40): 40
[Luna] 超时时间(秒, 默认: 10): 10
[Luna] 匹配状态码 (默认: 200,301,302,403): 200,301,302,403
[Luna] 是否启用递归？(y/N): n
[Luna] 递归深度 (默认: 2): 2

=== 配置 httpx (3/3) ===
[Luna] 用途描述 (可选): HTTP探测
[Luna] 线程数 (默认: 50): 50
[Luna] 超时时间(秒, 默认: 10): 10
[Luna] 显示状态码？(Y/n): y
[Luna] 显示标题？(Y/n): y
[Luna] 技术栈检测？(Y/n): y

[Luna] ✓ 流程配置完成！
[Luna] 已保存到: profiles/my-scan.json

[Luna] 使用方式:
  luna run --profile my-scan --target example.com
```

### 3.2 方式2：命令行指定

```bash
luna create-profile my-scan --tools puzzle,ffuf,httpx --description "快速扫描流程"
```

然后进入参数配置交互。

### 3.3 方式3：基于现有流程创建

```bash
luna create-profile my-scan --from default
```

**交互过程**：
```
[Luna] 基于流程 'default' 创建新流程
[Luna] 新流程名称: my-scan

[Luna] 原流程包含的工具:
  1. oneforall
  2. puzzle
  3. dirsearch
  4. httpx (第1次)
  5. txportmap
  6. httpx (第2次)

[Luna] 是否修改工具组合？(Y/n): y

[Luna] 请选择要保留的工具 (输入编号, 用逗号分隔): 2,3,4
[Luna] 是否添加新工具？(Y/n): n

[Luna] 新流程工具:
  1. puzzle
  2. dirsearch
  3. httpx

[Luna] 是否修改参数？(Y/n): y
[Luna] 修改哪个工具的参数？(输入工具名或'done'完成): puzzle
  [Luna] 修改 mode (当前: domain): domain
  [Luna] 修改 timeout (当前: 10): 15
  ...
[Luna] 修改哪个工具的参数？(输入工具名或'done'完成): done

[Luna] ✓ 流程创建完成！
```

### 3.4 特殊处理：同一工具多次调用

如果用户选择同一工具多次（如httpx），Luna会自动处理：

```
[Luna] 检测到 httpx 被添加了2次
[Luna] 为第2次调用设置别名

[Luna] 配置 httpx (第1次调用):
  [Luna] 用途描述: 探测目录挖掘结果
  [Luna] 别名 (默认: httpx_1): httpx_probe_1
  [Luna] 线程数: 50
  ...

[Luna] 配置 httpx (第2次调用):
  [Luna] 用途描述: 探测端口扫描结果
  [Luna] 别名 (默认: httpx_2): httpx_probe_2
  [Luna] 线程数: 100
  ...
```

生成的配置：
```json
{
  "tools": [
    {
      "name": "httpx",
      "order": 1,
      "alias": "httpx_probe_1",
      "description": "探测目录挖掘结果",
      "params": {"threads": 50}
    },
    {
      "name": "httpx",
      "order": 2,
      "alias": "httpx_probe_2",
      "description": "探测端口扫描结果",
      "params": {"threads": 100}
    }
  ]
}
```

---

## 四、流程管理命令

### 4.1 列出所有流程

```bash
luna list-profiles
```

输出：
```
可用流程:
  [内置] default    - 默认完整流程
  [内置] quick      - 快速扫描
  [内置] deep       - 深度扫描
  [自定义] my-scan  - 我的自定义扫描流程
  [自定义] stealth  - 隐蔽扫描流程
```

### 4.2 查看流程详情

```bash
luna show-profile my-scan
```

输出：
```
流程: my-scan
描述: 我的自定义扫描流程
创建时间: 2026-01-16 10:30:00
最后修改: 2026-01-16 10:30:00

包含的工具:
  1. puzzle (子域名收集和IP获取)
     - mode: domain
     - timeout: 10
     - l3: false
     
  2. ffuf (目录爆破)
     - wordlist: /path/to/wordlist.txt
     - threads: 40
     - recursion: false
     
  3. httpx (HTTP探测)
     - threads: 50
     - timeout: 10
```

### 4.3 编辑流程

```bash
luna edit-profile my-scan
```

进入交互式编辑模式。

### 4.4 删除流程

```bash
luna delete-profile my-scan
```

**注意**：内置流程不能删除。

---

## 五、使用流程

### 5.1 基本使用

```bash
# 使用默认流程
luna run --profile default --target example.com

# 使用自定义流程
luna run --profile my-scan --target example.com

# 批量处理
luna run --profile my-scan --target-file domains.txt
```

### 5.2 参数管理

**首次运行流程**：
```bash
luna run --profile my-scan --target example.com
```

如果流程配置文件中没有参数，会进入交互式配置。

**后续运行**：
```
[Luna] 使用上次的参数？(Y/n): Y
[Luna] 开始执行...
```

如果选择 `n`：
```
[Luna] 使用上次的参数？(Y/n): n
[Luna] 重新配置参数...
（进入交互式配置）

[Luna] 保存覆盖原参数？(Y/n): Y
[Luna] 参数已更新
```

### 5.3 临时覆盖参数

```bash
luna run --profile my-scan --target example.com \
  --puzzle-timeout 20 \
  --ffuf-threads 80
```

临时覆盖的参数不会保存到配置文件。

---

## 六、设计优势

### 6.1 解决的问题

1. **工具选择灵活**：用户可以精确选择使用哪个工具
2. **避免混淆**：不再有"模块"概念，直接操作工具
3. **支持多次调用**：同一工具可以在流程中多次使用
4. **参数独立**：每次调用可以有不同的参数

### 6.2 用户体验

- **简单场景**：使用内置流程，一键执行
- **自定义场景**：创建自己的流程，保存复用
- **灵活调整**：可以基于现有流程修改
- **参数记忆**：不需要每次都输入参数

---

## 七、实现要点

### 7.1 流程加载

```python
def load_profile(profile_name):
    """加载流程配置"""
    profile_path = f"profiles/{profile_name}.json"
    with open(profile_path, 'r') as f:
        return json.load(f)
```

### 7.2 工具执行

```python
def execute_profile(profile, target):
    """执行流程"""
    for tool_config in profile['tools']:
        tool_name = tool_config['name']
        params = tool_config['params']
        
        print(f"[Luna] 执行 {tool_name}...")
        result = execute_tool(tool_name, target, params)
        
        if not result.success:
            print(f"[Luna] {tool_name} 执行失败，终止流程")
            return False
    
    return True
```

### 7.3 别名处理

```python
def get_tool_instance(tool_config):
    """获取工具实例，处理别名"""
    tool_name = tool_config['name']
    alias = tool_config.get('alias', tool_name)
    
    return ToolWrapper(
        name=tool_name,
        alias=alias,
        params=tool_config['params']
    )
```

---

**最后更新**: 2026-01-16
