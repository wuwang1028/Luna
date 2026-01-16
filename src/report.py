"""
Luna 报告生成模块
负责生成最终的信息收集报告
"""

import csv
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

from .utils import setup_logger, read_file_lines


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, domain: str, output_dir: Path):
        """
        初始化报告生成器
        
        Args:
            domain: 主域名
            output_dir: 输出目录
        """
        self.domain = domain
        self.output_dir = output_dir
        self.logger = setup_logger(f"Luna.Report.{domain}")
        
        # 数据容器
        self.web_assets = []  # 表1: Web资产
        self.ip_ports = []    # 表2: IP端口
    
    def load_data(self):
        """加载所有数据"""
        self.logger.info("开始加载数据")
        
        # 加载子域名
        subdomains = self._load_subdomains()
        
        # 加载URL
        urls = self._load_urls()
        
        # 加载HTTP探测结果
        http_probes = self._load_http_probes()
        
        # 加载端口扫描结果
        ports = self._load_ports()
        
        # 加载puzzle的IP映射
        subdomain_ip_map = self._load_subdomain_ip_map()
        
        # 构建表1: Web资产表
        self._build_web_assets_table(subdomains, urls, http_probes)
        
        # 构建表2: IP端口表
        self._build_ip_ports_table(subdomains, subdomain_ip_map, ports, http_probes)
        
        self.logger.info(f"数据加载完成: Web资产 {len(self.web_assets)} 条, IP端口 {len(self.ip_ports)} 条")
    
    def _load_subdomains(self) -> List[str]:
        """加载子域名列表"""
        subdomain_file = self.output_dir / "filtered_subdomains.txt"
        if subdomain_file.exists():
            return read_file_lines(subdomain_file)
        return []
    
    def _load_urls(self) -> List[str]:
        """加载URL列表"""
        url_file = self.output_dir / "discovered_urls.txt"
        if url_file.exists():
            return read_file_lines(url_file)
        return []
    
    def _load_http_probes(self) -> Dict[str, Dict[str, Any]]:
        """
        加载HTTP探测结果
        
        Returns:
            Dict: URL -> 探测信息的映射
        """
        probes = {}
        
        # 查找所有httpx结果文件
        for probe_file in self.output_dir.glob("*_results.json"):
            if probe_file.stem.startswith("httpx") or "probe" in probe_file.stem:
                try:
                    with open(probe_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        if isinstance(data, list):
                            for item in data:
                                url = item.get('url', '')
                                if url:
                                    probes[url] = item
                        elif isinstance(data, dict) and 'results' in data:
                            for item in data['results']:
                                url = item.get('url', '')
                                if url:
                                    probes[url] = item
                except Exception as e:
                    self.logger.warning(f"加载HTTP探测结果失败 {probe_file}: {e}")
        
        return probes
    
    def _load_ports(self) -> List[Dict[str, Any]]:
        """加载端口扫描结果"""
        ports = []
        
        port_file = self.output_dir / "port_scan_results.json"
        if port_file.exists():
            try:
                with open(port_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        ports = data
                    elif isinstance(data, dict) and 'ports' in data:
                        ports = data['ports']
            except Exception as e:
                self.logger.warning(f"加载端口扫描结果失败: {e}")
        
        return ports
    
    def _load_subdomain_ip_map(self) -> Dict[str, str]:
        """
        加载子域名到IP的映射（从puzzle结果）
        
        Returns:
            Dict: 子域名 -> IP的映射
        """
        mapping = {}
        
        puzzle_file = self.output_dir / "puzzle" / "puzzle_result.txt"
        if puzzle_file.exists():
            lines = read_file_lines(puzzle_file)
            for line in lines:
                # puzzle输出格式: subdomain [IP]
                parts = line.split()
                if len(parts) >= 2:
                    subdomain = parts[0]
                    ip = parts[1].strip('[]')
                    if ip:
                        mapping[subdomain] = ip
        
        return mapping
    
    def _build_web_assets_table(self, subdomains: List[str], urls: List[str], 
                                http_probes: Dict[str, Dict[str, Any]]):
        """
        构建表1: Web资产表
        
        格式: 主域名 | 子域名 | 目录URL | 状态码 | 网页标题
        """
        self.logger.info("构建Web资产表")
        
        # 首先添加所有子域名（即使没有探测结果）
        for subdomain in subdomains:
            # 尝试匹配HTTP探测结果
            http_url = f"http://{subdomain}"
            https_url = f"https://{subdomain}"
            
            probe = http_probes.get(https_url) or http_probes.get(http_url)
            
            if probe:
                self.web_assets.append({
                    'domain': self.domain,
                    'subdomain': subdomain,
                    'url': probe.get('url', ''),
                    'status_code': probe.get('status_code', ''),
                    'title': probe.get('title', '')
                })
            else:
                # 没有探测结果，只记录子域名
                self.web_assets.append({
                    'domain': self.domain,
                    'subdomain': subdomain,
                    'url': '',
                    'status_code': '',
                    'title': ''
                })
        
        # 添加目录挖掘发现的URL
        for url in urls:
            probe = http_probes.get(url)
            
            # 从URL提取子域名
            subdomain = self._extract_subdomain_from_url(url)
            
            if probe:
                self.web_assets.append({
                    'domain': self.domain,
                    'subdomain': subdomain,
                    'url': url,
                    'status_code': probe.get('status_code', ''),
                    'title': probe.get('title', '')
                })
            else:
                self.web_assets.append({
                    'domain': self.domain,
                    'subdomain': subdomain,
                    'url': url,
                    'status_code': '',
                    'title': ''
                })
    
    def _build_ip_ports_table(self, subdomains: List[str], 
                             subdomain_ip_map: Dict[str, str],
                             ports: List[Dict[str, Any]], 
                             http_probes: Dict[str, Dict[str, Any]]):
        """
        构建表2: IP端口表
        
        格式: 主域名 | 子域名 | IP | 端口 | 状态码 | 网页标题
        """
        self.logger.info("构建IP端口表")
        
        # 为每个端口扫描结果匹配子域名
        for port_info in ports:
            ip = port_info.get('ip', '')
            port = port_info.get('port', '')
            
            # 查找对应的子域名
            matching_subdomains = [sub for sub, sub_ip in subdomain_ip_map.items() if sub_ip == ip]
            
            if not matching_subdomains:
                matching_subdomains = ['']
            
            for subdomain in matching_subdomains:
                # 尝试匹配HTTP探测结果
                # 构造可能的URL
                possible_urls = [
                    f"http://{ip}:{port}",
                    f"https://{ip}:{port}",
                    f"http://{subdomain}:{port}" if subdomain else None,
                    f"https://{subdomain}:{port}" if subdomain else None
                ]
                
                probe = None
                for url in possible_urls:
                    if url and url in http_probes:
                        probe = http_probes[url]
                        break
                
                if probe:
                    self.ip_ports.append({
                        'domain': self.domain,
                        'subdomain': subdomain,
                        'ip': ip,
                        'port': port,
                        'status_code': probe.get('status_code', ''),
                        'title': probe.get('title', '')
                    })
                else:
                    self.ip_ports.append({
                        'domain': self.domain,
                        'subdomain': subdomain,
                        'ip': ip,
                        'port': port,
                        'status_code': '',
                        'title': ''
                    })
    
    def _extract_subdomain_from_url(self, url: str) -> str:
        """从URL提取子域名"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.split(':')[0]  # 移除端口号
        except:
            return ''
    
    def generate_csv(self):
        """生成CSV格式报告"""
        self.logger.info("生成CSV报告")
        
        # 表1: Web资产表
        table1_file = self.output_dir / f"{self.domain}_web_assets.csv"
        with open(table1_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=['domain', 'subdomain', 'url', 'status_code', 'title'])
            writer.writeheader()
            writer.writerows(self.web_assets)
        
        self.logger.info(f"Web资产表已保存: {table1_file}")
        
        # 表2: IP端口表
        table2_file = self.output_dir / f"{self.domain}_ip_ports.csv"
        with open(table2_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=['domain', 'subdomain', 'ip', 'port', 'status_code', 'title'])
            writer.writeheader()
            writer.writerows(self.ip_ports)
        
        self.logger.info(f"IP端口表已保存: {table2_file}")
        
        return table1_file, table2_file
    
    def generate_excel(self):
        """生成Excel格式报告"""
        if not PANDAS_AVAILABLE:
            self.logger.warning("pandas未安装，无法生成Excel报告")
            return None
        
        self.logger.info("生成Excel报告")
        
        try:
            excel_file = self.output_dir / f"{self.domain}_report.xlsx"
            
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                # 表1: Web资产
                df1 = pd.DataFrame(self.web_assets)
                df1.columns = ['主域名', '子域名', '目录URL', '状态码', '网页标题']
                df1.to_excel(writer, sheet_name='Web资产', index=False)
                
                # 表2: IP端口
                df2 = pd.DataFrame(self.ip_ports)
                df2.columns = ['主域名', '子域名', 'IP', '端口', '状态码', '网页标题']
                df2.to_excel(writer, sheet_name='IP端口', index=False)
            
            self.logger.info(f"Excel报告已保存: {excel_file}")
            return excel_file
            
        except Exception as e:
            self.logger.error(f"生成Excel报告失败: {e}")
            return None
    
    def generate_summary(self):
        """生成汇总信息"""
        summary = {
            'domain': self.domain,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'web_assets_count': len(self.web_assets),
            'ip_ports_count': len(self.ip_ports),
            'unique_subdomains': len(set(item['subdomain'] for item in self.web_assets if item['subdomain'])),
            'unique_ips': len(set(item['ip'] for item in self.ip_ports if item['ip'])),
            'unique_ports': len(set(item['port'] for item in self.ip_ports if item['port']))
        }
        
        summary_file = self.output_dir / "summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"汇总信息已保存: {summary_file}")
        
        return summary
    
    def generate_all(self, format: str = 'csv'):
        """
        生成所有报告
        
        Args:
            format: 报告格式 ('csv' 或 'xlsx')
        
        Returns:
            List[Path]: 生成的报告文件列表
        """
        self.logger.info(f"开始生成报告 (格式: {format})")
        
        # 加载数据
        self.load_data()
        
        # 生成汇总
        summary = self.generate_summary()
        
        # 生成报告
        report_files = []
        
        if format.lower() == 'csv':
            table1, table2 = self.generate_csv()
            report_files.extend([table1, table2])
        elif format.lower() in ['xlsx', 'excel']:
            excel_file = self.generate_excel()
            if excel_file:
                report_files.append(excel_file)
            else:
                # 降级到CSV
                self.logger.warning("Excel生成失败，降级到CSV")
                table1, table2 = self.generate_csv()
                report_files.extend([table1, table2])
        else:
            # 默认生成CSV
            table1, table2 = self.generate_csv()
            report_files.extend([table1, table2])
        
        self.logger.info(f"报告生成完成，共 {len(report_files)} 个文件")
        
        return report_files, summary


def generate_report(domain: str, output_dir: Path, format: str = 'csv') -> tuple:
    """
    生成报告的便捷函数
    
    Args:
        domain: 主域名
        output_dir: 输出目录
        format: 报告格式
    
    Returns:
        tuple: (报告文件列表, 汇总信息)
    """
    generator = ReportGenerator(domain, output_dir)
    return generator.generate_all(format)
