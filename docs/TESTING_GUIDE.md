# Luna 测试指南

## 测试准备

### 1. 确认安装

```bash
# 检查Python依赖
python3 -c "import click, pandas, yaml; print('✓ Python dependencies OK')"

# 检查Luna主程序
python3 luna.py --help

# 检查工具目录
ls -la tools/
```

### 2. 准备测试环境

```bash
# 创建测试目录
mkdir -p test_data
cd test_data

# 准备测试域名列表
cat > test_domains.txt << EOF
example.com
EOF

# 准备测试字典（小字典用于快速测试）
cat > test_wordlist.txt << EOF
admin
test
api
www
mail
EOF
```

## 单元测试

### 测试1: 配置模块

```bash
python3 << 'EOF'
from src.config import *

# 测试工具路径
print("Testing tool paths...")
for tool, path in TOOL_PATHS.items():
    print(f"  {tool}: {path}")

# 测试输出目录
output_dir = get_output_dir("test.com")
print(f"\nOutput directory: {output_dir}")

# 测试日志文件
log_file = get_log_file()
print(f"Log file: {log_file}")

print("\n✓ Config module OK")
EOF
```

### 测试2: 工具函数

```bash
python3 << 'EOF'
from src.utils import *

# 测试域名验证
print("Testing domain validation...")
assert validate_domain("example.com") == True
assert validate_domain("invalid domain") == False
print("✓ Domain validation OK")

# 测试邮件域名过滤
print("\nTesting email domain filtering...")
domains = ["www.example.com", "mail.example.com", "smtp.example.com", "api.example.com"]
filtered = filter_email_domains(domains)
print(f"  Original: {len(domains)}, Filtered: {len(filtered)}")
assert "mail.example.com" not in filtered
assert "smtp.example.com" not in filtered
print("✓ Email filtering OK")

# 测试文件操作
print("\nTesting file operations...")
test_file = "/tmp/test_luna.txt"
test_data = ["line1", "line2", "line3"]
write_file_lines(test_file, test_data)
read_data = read_file_lines(test_file)
assert read_data == test_data
print("✓ File operations OK")

print("\n✓ Utils module OK")
EOF
```

### 测试3: 流程管理

```bash
python3 << 'EOF'
from src.profile import ProfileManager

print("Testing profile management...")

pm = ProfileManager()

# 测试加载内置流程
print("\nLoading built-in profiles...")
default = pm.load_profile("default")
print(f"  Default profile: {default.name}")
print(f"  Tools: {[t['name'] for t in default.tools]}")

quick = pm.load_profile("quick")
print(f"  Quick profile: {quick.name}")
print(f"  Tools: {[t['name'] for t in quick.tools]}")

# 测试列出流程
print("\nListing all profiles...")
profiles = pm.list_profiles()
print(f"  Found {len(profiles)} profiles")

print("\n✓ Profile management OK")
EOF
```

## 集成测试

### 测试4: 命令行接口

```bash
echo "Testing CLI..."

# 测试help命令
echo "  Testing --help..."
python3 luna.py --help > /dev/null && echo "    ✓ --help OK"

# 测试list命令
echo "  Testing list..."
python3 luna.py list > /dev/null && echo "    ✓ list OK"

# 测试show命令
echo "  Testing show..."
python3 luna.py show default > /dev/null && echo "    ✓ show OK"

echo "✓ CLI OK"
```

### 测试5: 工具调用（需要实际工具）

```bash
python3 << 'EOF'
from pathlib import Path
from src.tools_wrapper import get_tool_wrapper
from src.config import TOOL_PATHS
import os

print("Testing tool wrappers...")

# 检查工具是否存在
for tool_name, tool_path in TOOL_PATHS.items():
    exists = os.path.exists(tool_path)
    status = "✓" if exists else "✗"
    print(f"  {status} {tool_name}: {tool_path}")

print("\nNote: Tools need to be installed and compiled for actual testing")
EOF
```

## 功能测试

### 测试6: 完整流程（模拟）

创建测试脚本 `test_full_workflow.py`:

```python
#!/usr/bin/env python3
"""
Luna完整流程测试脚本（模拟模式）
"""

from pathlib import Path
from src.core import LunaCore
from src.config import get_output_dir

def test_full_workflow():
    """测试完整工作流程"""
    print("=" * 60)
    print("Luna Full Workflow Test (Simulation Mode)")
    print("=" * 60)
    
    # 初始化
    core = LunaCore()
    
    # 测试目标解析
    print("\n[1/5] Testing target parsing...")
    
    # 单个目标
    targets = core._parse_targets(target="test.com", target_file=None)
    assert len(targets) == 1
    assert targets[0] == "test.com"
    print("  ✓ Single target parsing OK")
    
    # 文件目标
    test_file = Path("/tmp/test_targets.txt")
    test_file.write_text("example1.com\nexample2.com\n")
    targets = core._parse_targets(target=None, target_file=str(test_file))
    assert len(targets) == 2
    print("  ✓ File target parsing OK")
    
    # 测试流程加载
    print("\n[2/5] Testing profile loading...")
    profile = core.profile_manager.load_profile("quick")
    assert profile is not None
    assert len(profile.tools) > 0
    print(f"  ✓ Loaded profile '{profile.name}' with {len(profile.tools)} tools")
    
    # 测试输出目录创建
    print("\n[3/5] Testing output directory...")
    output_dir = get_output_dir("test.com")
    assert output_dir.exists()
    print(f"  ✓ Output directory created: {output_dir}")
    
    # 测试数据处理器
    print("\n[4/5] Testing data processor...")
    from src.data_processor import DataProcessor
    dp = DataProcessor("test.com", output_dir)
    
    # 模拟数据
    mock_subdomains = ["www.test.com", "api.test.com", "mail.test.com"]
    filtered = dp._load_subdomains() or mock_subdomains
    print(f"  ✓ Data processor initialized")
    
    # 测试报告生成器
    print("\n[5/5] Testing report generator...")
    from src.report import ReportGenerator
    rg = ReportGenerator("test.com", output_dir)
    print(f"  ✓ Report generator initialized")
    
    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)
    
    print("\nNote: This is a simulation test.")
    print("For actual tool execution, run:")
    print("  python3 luna.py run -p quick -t test.com")

if __name__ == "__main__":
    test_full_workflow()
```

运行测试：

```bash
chmod +x test_full_workflow.py
python3 test_full_workflow.py
```

## 实际工具测试

### 前提条件

1. 所有工具已安装并编译
2. 工具路径配置正确
3. 有测试目标域名（建议使用自己的域名）

### 测试7: 快速流程测试

```bash
echo "Testing quick profile with real tools..."

# 使用quick流程测试（最快）
python3 luna.py run -p quick -t example.com

# 检查输出
if [ -d "outputs/example.com" ]; then
    echo "✓ Output directory created"
    ls -lh outputs/example.com/
    
    # 检查关键文件
    [ -f "outputs/example.com/filtered_subdomains.txt" ] && echo "  ✓ Subdomains file exists"
    [ -f "outputs/example.com/summary.json" ] && echo "  ✓ Summary file exists"
    [ -f "outputs/example.com/example.com_web_assets.csv" ] && echo "  ✓ Web assets report exists"
    [ -f "outputs/example.com/example.com_ip_ports.csv" ] && echo "  ✓ IP ports report exists"
else
    echo "✗ Output directory not created"
fi
```

### 测试8: 批量处理测试

```bash
echo "Testing batch processing..."

# 创建小批量测试文件
cat > test_batch.txt << EOF
example.com
test.com
EOF

# 运行批量测试
python3 luna.py run -p quick -f test_batch.txt

# 检查每个域名的输出
for domain in example.com test.com; do
    if [ -d "outputs/$domain" ]; then
        echo "✓ $domain processed"
    else
        echo "✗ $domain not processed"
    fi
done
```

### 测试9: 流程创建测试

```bash
echo "Testing profile creation..."

# 创建测试流程（交互式，需要手动输入）
# python3 luna.py create test-profile

# 或者手动创建配置文件
cat > profiles/test-profile.json << 'EOF'
{
  "name": "test-profile",
  "description": "Test profile for validation",
  "tools": [
    {
      "name": "puzzle",
      "order": 1,
      "params": {
        "mode": "domain",
        "timeout": 10,
        "l3": false,
        "ping": false,
        "pt": 500,
        "wt": 25
      }
    }
  ]
}
EOF

# 验证流程
python3 luna.py show test-profile

# 使用测试流程
python3 luna.py run -p test-profile -t example.com

# 清理
rm profiles/test-profile.json
```

## 性能测试

### 测试10: 性能基准

```bash
echo "Performance benchmarking..."

# 记录开始时间
start_time=$(date +%s)

# 运行quick流程
python3 luna.py run -p quick -t example.com

# 记录结束时间
end_time=$(date +%s)
duration=$((end_time - start_time))

echo "Execution time: ${duration}s"

# 检查内存使用
ps aux | grep luna.py | grep -v grep
```

## 错误测试

### 测试11: 错误处理

```bash
echo "Testing error handling..."

# 测试无效域名
echo "  Testing invalid domain..."
python3 luna.py run -p quick -t "invalid domain with spaces" 2>&1 | grep -q "Invalid" && echo "    ✓ Invalid domain rejected"

# 测试不存在的流程
echo "  Testing non-existent profile..."
python3 luna.py run -p nonexistent -t example.com 2>&1 | grep -q "not found" && echo "    ✓ Non-existent profile rejected"

# 测试不存在的目标文件
echo "  Testing non-existent target file..."
python3 luna.py run -p quick -f /nonexistent/file.txt 2>&1 | grep -q "not found" && echo "    ✓ Non-existent file rejected"

echo "✓ Error handling OK"
```

## 回归测试

### 测试12: 版本兼容性

```bash
echo "Testing version compatibility..."

# 检查配置文件格式
for profile in profiles/*.json; do
    echo "  Validating $profile..."
    python3 -m json.tool "$profile" > /dev/null && echo "    ✓ Valid JSON"
done

echo "✓ Version compatibility OK"
```

## 测试报告

### 生成测试报告

```bash
cat > test_report.md << 'EOF'
# Luna Test Report

## Test Date
$(date)

## Test Environment
- OS: $(uname -s)
- Python: $(python3 --version)
- Luna Version: v0.3.0

## Test Results

### Unit Tests
- [ ] Config module
- [ ] Utils module
- [ ] Profile management

### Integration Tests
- [ ] CLI interface
- [ ] Tool wrappers

### Functional Tests
- [ ] Full workflow (simulation)
- [ ] Quick profile (real)
- [ ] Batch processing
- [ ] Profile creation

### Performance Tests
- [ ] Execution time
- [ ] Memory usage

### Error Tests
- [ ] Invalid input handling
- [ ] Missing file handling

## Issues Found
(List any issues discovered during testing)

## Recommendations
(List any recommendations for improvements)

EOF

echo "Test report template created: test_report.md"
```

## 持续测试

### 自动化测试脚本

创建 `run_all_tests.sh`:

```bash
#!/bin/bash

echo "================================"
echo "Luna Automated Test Suite"
echo "================================"

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

passed=0
failed=0

# 测试函数
run_test() {
    test_name=$1
    test_command=$2
    
    echo -n "Running $test_name... "
    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((passed++))
    else
        echo -e "${RED}✗ FAILED${NC}"
        ((failed++))
    fi
}

# 执行测试
run_test "CLI Help" "python3 luna.py --help"
run_test "List Profiles" "python3 luna.py list"
run_test "Show Default Profile" "python3 luna.py show default"
run_test "Config Module" "python3 -c 'from src.config import *'"
run_test "Utils Module" "python3 -c 'from src.utils import *'"
run_test "Profile Module" "python3 -c 'from src.profile import *'"
run_test "Core Module" "python3 -c 'from src.core import *'"
run_test "Report Module" "python3 -c 'from src.report import *'"

# 总结
echo "================================"
echo "Test Summary"
echo "================================"
echo -e "Passed: ${GREEN}$passed${NC}"
echo -e "Failed: ${RED}$failed${NC}"
echo "Total: $((passed + failed))"

if [ $failed -eq 0 ]; then
    echo -e "\n${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}Some tests failed!${NC}"
    exit 1
fi
```

运行自动化测试：

```bash
chmod +x run_all_tests.sh
./run_all_tests.sh
```

## 测试清理

```bash
# 清理测试数据
rm -rf test_data/
rm -rf outputs/test.com
rm -rf outputs/example.com
rm -f test_full_workflow.py
rm -f test_report.md
rm -f run_all_tests.sh

echo "✓ Test cleanup complete"
```

---

**版本**: v1.0
**最后更新**: 2026-01-16
