# Luna 安装部署手册

## 系统要求

### 操作系统
- Linux (推荐 Ubuntu 20.04+, Kali Linux, CentOS 7+)
- macOS 10.15+
- Windows 10+ (WSL2)

### 软件依赖
- Python 3.8+
- Go 1.18+ (用于编译Go工具)
- Git

### 硬件要求
- CPU: 2核心以上
- 内存: 4GB以上
- 磁盘: 10GB可用空间

## 快速安装

### 1. 克隆仓库

```bash
git clone https://github.com/wuwang1028/Luna.git
cd Luna
```

### 2. 安装Python依赖

```bash
# 使用pip安装
pip3 install -r requirements.txt

# 或使用虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 准备工具

Luna需要7个外部工具，需要手动准备：

#### 方式1: 使用提供的工具包（推荐）

如果你已经有这些工具的压缩包：

```bash
# 解压工具到tools目录
cd tools
unzip OneForAll-master.zip
unzip httpx-dev.zip
unzip ffuf-master.zip
unzip dirsearch-master.zip
unzip fscan-main.zip
unzip TXPortMap-main.zip
unzip puzzle-master.zip
```

#### 方式2: 从GitHub下载

```bash
cd tools

# OneForAll (Python)
git clone https://github.com/shmilylty/OneForAll.git OneForAll-master
cd OneForAll-master
pip3 install -r requirements.txt
cd ..

# dirsearch (Python)
git clone https://github.com/maurosoria/dirsearch.git dirsearch-master

# httpx (Go)
git clone https://github.com/projectdiscovery/httpx.git httpx-dev

# ffuf (Go)
git clone https://github.com/ffuf/ffuf.git ffuf-master

# fscan (Go)
git clone https://github.com/shadow1ng/fscan.git fscan-main

# TXPortMap (Go)
git clone https://github.com/4dogs-cn/TXPortMap.git TXPortMap-main

# puzzle (Go)
git clone https://github.com/Becivells/puzzle.git puzzle-master
```

### 4. 编译Go工具

```bash
cd tools

# 编译httpx
cd httpx-dev
go build -o httpx cmd/httpx/httpx.go
cd ..

# 编译ffuf
cd ffuf-master
go build
cd ..

# 编译fscan
cd fscan-main
go build
cd ..

# 编译TXPortMap
cd TXPortMap-main
go build -o TxPortMap
cd ..

# 编译puzzle
cd puzzle-master
go build
cd ..

cd ..
```

### 5. 验证安装

```bash
# 检查Luna是否正常
python3 luna.py --help

# 列出可用流程
python3 luna.py list

# 查看默认流程
python3 luna.py show default
```

如果一切正常，你应该看到Luna的帮助信息和内置流程列表。

## 详细安装步骤

### Python依赖说明

Luna的Python依赖包括：

| 包名 | 版本 | 用途 |
|------|------|------|
| click | >=8.0.0 | 命令行界面 |
| pandas | >=1.3.0 | 数据处理和Excel生成 |
| openpyxl | >=3.0.0 | Excel文件支持 |
| pyyaml | >=5.4.0 | 配置文件处理 |
| colorlog | >=6.0.0 | 彩色日志输出 |
| tqdm | >=4.62.0 | 进度条显示 |
| tabulate | >=0.8.9 | 表格美化 |

### 工具目录结构

安装完成后，`tools/` 目录应该是这样的：

```
tools/
├── OneForAll-master/
│   ├── oneforall.py          # 主程序
│   ├── requirements.txt
│   └── ...
├── dirsearch-master/
│   ├── dirsearch.py          # 主程序
│   └── ...
├── httpx-dev/
│   ├── httpx                 # 编译后的二进制
│   └── ...
├── ffuf-master/
│   ├── ffuf                  # 编译后的二进制
│   └── ...
├── fscan-main/
│   ├── fscan                 # 编译后的二进制
│   └── ...
├── TXPortMap-main/
│   ├── TxPortMap             # 编译后的二进制
│   └── ...
└── puzzle-master/
    ├── puzzle                # 编译后的二进制
    └── ...
```

### 配置工具路径

Luna会自动检测工具路径，但如果工具不在默认位置，你需要修改 `src/config.py`：

```python
TOOL_PATHS = {
    "oneforall": "/path/to/OneForAll-master/oneforall.py",
    "puzzle": "/path/to/puzzle-master/puzzle",
    "httpx": "/path/to/httpx-dev/httpx",
    # ... 其他工具
}
```

## 可选配置

### 1. 字典文件

某些工具需要字典文件：

```bash
# 创建字典目录
mkdir -p wordlists

# 下载常用字典（示例）
wget https://github.com/danielmiessler/SecLists/raw/master/Discovery/DNS/subdomains-top1million-5000.txt -O wordlists/subdomains.txt
wget https://github.com/danielmiessler/SecLists/raw/master/Discovery/Web-Content/common.txt -O wordlists/common.txt
```

### 2. 环境变量

可以设置环境变量来自定义Luna的行为：

```bash
# 设置输出目录
export LUNA_OUTPUT_DIR=/path/to/outputs

# 设置日志级别
export LUNA_LOG_LEVEL=DEBUG

# 添加到 ~/.bashrc 或 ~/.zshrc 使其永久生效
```

### 3. 全局安装（可选）

如果想在任何地方使用Luna：

```bash
# 创建符号链接
sudo ln -s $(pwd)/luna.py /usr/local/bin/luna

# 或添加到PATH
echo 'export PATH=$PATH:'$(pwd) >> ~/.bashrc
source ~/.bashrc

# 现在可以直接使用
luna --help
```

## 权限问题

某些工具可能需要root权限（如端口扫描）：

```bash
# 方式1: 使用sudo运行Luna
sudo python3 luna.py run --profile default --target example.com

# 方式2: 给工具添加capabilities（推荐）
sudo setcap cap_net_raw,cap_net_admin+eip tools/TXPortMap-main/TxPortMap
sudo setcap cap_net_raw,cap_net_admin+eip tools/fscan-main/fscan
```

## 故障排除

### 问题1: Python依赖安装失败

```bash
# 升级pip
pip3 install --upgrade pip

# 使用国内镜像
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题2: Go工具编译失败

```bash
# 设置Go代理
export GOPROXY=https://goproxy.cn,direct

# 更新Go模块
cd tools/httpx-dev
go mod tidy
go build
```

### 问题3: OneForAll依赖问题

```bash
cd tools/OneForAll-master
pip3 install -r requirements.txt --upgrade
```

### 问题4: 工具路径错误

检查 `src/config.py` 中的 `TOOL_PATHS` 配置是否正确。

### 问题5: 权限被拒绝

```bash
# 给Luna执行权限
chmod +x luna.py

# 给工具执行权限
chmod +x tools/*/puzzle
chmod +x tools/*/httpx
# ... 其他工具
```

## 验证安装

运行以下命令验证所有组件：

```bash
# 1. 检查Python依赖
python3 -c "import click, pandas, yaml; print('Python dependencies OK')"

# 2. 检查Luna主程序
python3 luna.py --version

# 3. 检查工具是否存在
ls -lh tools/httpx-dev/httpx
ls -lh tools/puzzle-master/puzzle
# ... 检查其他工具

# 4. 运行测试（如果有）
python3 -m pytest tests/  # 如果有测试文件
```

## 更新Luna

```bash
cd Luna
git pull origin master
pip3 install -r requirements.txt --upgrade
```

## 卸载

```bash
# 删除Luna目录
rm -rf Luna

# 删除虚拟环境（如果使用了）
rm -rf venv

# 删除符号链接（如果创建了）
sudo rm /usr/local/bin/luna
```

## Docker安装（可选）

如果你喜欢使用Docker：

```dockerfile
# Dockerfile (示例，需要根据实际情况调整)
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 python3-pip git golang-go

WORKDIR /app
COPY . /app

RUN pip3 install -r requirements.txt
RUN cd tools && ./build_all.sh  # 需要创建编译脚本

ENTRYPOINT ["python3", "luna.py"]
```

```bash
# 构建镜像
docker build -t luna:latest .

# 运行
docker run -v $(pwd)/outputs:/app/outputs luna:latest run --profile default --target example.com
```

## 下一步

安装完成后，请阅读 [使用手册](USER_GUIDE.md) 了解如何使用Luna。

---

**版本**: v1.0
**最后更新**: 2026-01-16
