"""
Luna 数据处理模块
负责数据的解析、清洗、合并和关联
"""

import re
import json
import csv
from pathlib import Path
from typing import List, Dict, Any, Set, Optional
from collections import defaultdict

from .utils import (
    read_file_lines, write_file_lines, 
    filter_email_domains, merge_and_deduplicate,
    setup_logger
)


class DataProcessor:
    """数据处理器"""
    
    def __init__(self, domain: str, output_dir: Path):
        """
        初始化数据处理器
        
        Args:
            domain: 主域名
            output_dir: 输出目录
        """
        self.domain = domain
        self.output_dir = output_dir
        self.logger = setup_logger(f"Luna.DataProcessor.{domain}")
        
        # 数据存储
        self.subdomains: List[Dict[str, Any]] = []
        self.urls: List[Dict[str, Any]] = []
        self.ports: List[Dict[str, Any]] = []
        self.http_probes: List[Dict[str, Any]] = []
    
    def process_subdomain_results(self, oneforall_data: Dict = None, 
                                  puzzle_data: Dict = None) -> List[str]:
        """
        处理子域名收集结果
        
        Args:
            oneforall_data: OneForAll的输出数据
            puzzle_data: puzzle的输出数据
        
        Returns:
            List[str]: 过滤后的子域名列表
        """
        self.logger.info("处理子域名收集结果")
        
        all_subdomains = []
        
        # 处理OneForAll结果
        if oneforall_data:
            subdomains = self._parse_oneforall_subdomains(oneforall_data)
            all_subdomains.extend(subdomains)
            self.logger.info(f"OneForAll收集到 {len(subdomains)} 个子域名")
        
        # 处理puzzle结果
        if puzzle_data:
            subdomains = self._parse_puzzle_subdomains(puzzle_data)
            all_subdomains.extend(subdomains)
            self.logger.info(f"puzzle收集到 {len(subdomains)} 个子域名")
        
        # 合并去重
        unique_subdomains = list(set(all_subdomains))
        self.logger.info(f"合并去重后: {len(unique_subdomains)} 个子域名")
        
        # 过滤邮件域名
        filtered_subdomains = filter_email_domains(unique_subdomains)
        removed_count = len(unique_subdomains) - len(filtered_subdomains)
        self.logger.info(f"过滤邮件域名: 移除 {removed_count} 个")
        
        # 保存结果
        self._save_subdomains(filtered_subdomains)
        
        return filtered_subdomains
    
    def process_directory_results(self, dirsearch_data: Dict = None,
                                  ffuf_data: Dict = None) -> List[str]:
        """
        处理目录挖掘结果
        
        Args:
            dirsearch_data: dirsearch的输出数据
            ffuf_data: ffuf的输出数据
        
        Returns:
            List[str]: URL列表
        """
        self.logger.info("处理目录挖掘结果")
        
        all_urls = []
        
        # 处理dirsearch结果
        if dirsearch_data:
            urls = self._parse_dirsearch_urls(dirsearch_data)
            all_urls.extend(urls)
            self.logger.info(f"dirsearch发现 {len(urls)} 个URL")
        
        # 处理ffuf结果
        if ffuf_data:
            urls = self._parse_ffuf_urls(ffuf_data)
            all_urls.extend(urls)
            self.logger.info(f"ffuf发现 {len(urls)} 个URL")
        
        # 去重
        unique_urls = list(set(all_urls))
        self.logger.info(f"合并去重后: {len(unique_urls)} 个URL")
        
        # 保存结果
        self._save_urls(unique_urls)
        
        return unique_urls
    
    def process_http_probe_results(self, httpx_data: Dict, 
                                   alias: str = "httpx") -> List[Dict[str, Any]]:
        """
        处理HTTP探测结果
        
        Args:
            httpx_data: httpx的输出数据
            alias: 工具别名（用于区分多次调用）
        
        Returns:
            List[Dict]: HTTP探测结果列表
        """
        self.logger.info(f"处理HTTP探测结果 ({alias})")
        
        probes = self._parse_httpx_results(httpx_data)
        self.logger.info(f"探测到 {len(probes)} 个HTTP服务")
        
        # 添加到总列表
        self.http_probes.extend(probes)
        
        # 保存结果
        self._save_http_probes(probes, alias)
        
        return probes
    
    def process_port_scan_results(self, txportmap_data: Dict = None,
                                  fscan_data: Dict = None) -> List[Dict[str, Any]]:
        """
        处理端口扫描结果
        
        Args:
            txportmap_data: TXPortMap的输出数据
            fscan_data: fscan的输出数据
        
        Returns:
            List[Dict]: 端口扫描结果列表
        """
        self.logger.info("处理端口扫描结果")
        
        all_ports = []
        
        # 处理TXPortMap结果
        if txportmap_data:
            ports = self._parse_txportmap_ports(txportmap_data)
            all_ports.extend(ports)
            self.logger.info(f"TXPortMap发现 {len(ports)} 个开放端口")
        
        # 处理fscan结果
        if fscan_data:
            ports = self._parse_fscan_ports(fscan_data)
            all_ports.extend(ports)
            self.logger.info(f"fscan发现 {len(ports)} 个开放端口")
        
        # 去重（基于IP+端口）
        unique_ports = self._deduplicate_ports(all_ports)
        self.logger.info(f"合并去重后: {len(unique_ports)} 个开放端口")
        
        # 保存结果
        self.ports = unique_ports
        self._save_ports(unique_ports)
        
        return unique_ports
    
    def _parse_oneforall_subdomains(self, data: Dict) -> List[str]:
        """解析OneForAll的子域名结果"""
        # OneForAll通常输出CSV文件
        # 这里假设data包含解析后的数据
        subdomains = []
        
        if 'subdomains' in data:
            subdomains = data['subdomains']
        elif 'results' in data:
            for item in data['results']:
                if 'subdomain' in item:
                    subdomains.append(item['subdomain'])
        
        return subdomains
    
    def _parse_puzzle_subdomains(self, data: Dict) -> List[str]:
        """解析puzzle的子域名结果"""
        subdomains = []
        
        if 'subdomains' in data:
            subdomains = data['subdomains']
        elif 'domains' in data:
            subdomains = data['domains']
        
        return subdomains
    
    def _parse_dirsearch_urls(self, data: Dict) -> List[str]:
        """解析dirsearch的URL结果"""
        urls = []
        
        if 'urls' in data:
            urls = data['urls']
        elif 'results' in data:
            for item in data['results']:
                if 'url' in item:
                    urls.append(item['url'])
        
        return urls
    
    def _parse_ffuf_urls(self, data: Dict) -> List[str]:
        """解析ffuf的URL结果"""
        urls = []
        
        if 'results' in data:
            for item in data['results']:
                if 'url' in item:
                    urls.append(item['url'])
        
        return urls
    
    def _parse_httpx_results(self, data: Dict) -> List[Dict[str, Any]]:
        """解析httpx的探测结果"""
        probes = []
        
        if 'results' in data:
            for item in data['results']:
                probe = {
                    'url': item.get('url', ''),
                    'status_code': item.get('status_code', 0),
                    'title': item.get('title', ''),
                    'content_length': item.get('content_length', 0),
                    'tech': item.get('tech', [])
                }
                probes.append(probe)
        
        return probes
    
    def _parse_txportmap_ports(self, data: Dict) -> List[Dict[str, Any]]:
        """解析TXPortMap的端口扫描结果"""
        ports = []
        
        if 'results' in data:
            for item in data['results']:
                port = {
                    'ip': item.get('ip', ''),
                    'port': item.get('port', 0),
                    'service': item.get('service', ''),
                    'banner': item.get('banner', '')
                }
                ports.append(port)
        
        return ports
    
    def _parse_fscan_ports(self, data: Dict) -> List[Dict[str, Any]]:
        """解析fscan的端口扫描结果"""
        ports = []
        
        if 'ports' in data:
            for item in data['ports']:
                port = {
                    'ip': item.get('ip', ''),
                    'port': item.get('port', 0),
                    'service': item.get('service', ''),
                    'banner': item.get('banner', '')
                }
                ports.append(port)
        
        return ports
    
    def _deduplicate_ports(self, ports: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重端口列表（基于IP+端口）"""
        seen = set()
        unique = []
        
        for port in ports:
            key = (port['ip'], port['port'])
            if key not in seen:
                seen.add(key)
                unique.append(port)
        
        return unique
    
    def _save_subdomains(self, subdomains: List[str]):
        """保存子域名列表"""
        output_file = self.output_dir / "filtered_subdomains.txt"
        write_file_lines(output_file, subdomains)
        self.logger.info(f"子域名已保存到: {output_file}")
    
    def _save_urls(self, urls: List[str]):
        """保存URL列表"""
        output_file = self.output_dir / "discovered_urls.txt"
        write_file_lines(output_file, urls)
        self.logger.info(f"URL已保存到: {output_file}")
    
    def _save_http_probes(self, probes: List[Dict[str, Any]], alias: str):
        """保存HTTP探测结果"""
        output_file = self.output_dir / f"{alias}_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(probes, f, indent=2, ensure_ascii=False)
        self.logger.info(f"HTTP探测结果已保存到: {output_file}")
    
    def _save_ports(self, ports: List[Dict[str, Any]]):
        """保存端口扫描结果"""
        output_file = self.output_dir / "port_scan_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(ports, f, indent=2, ensure_ascii=False)
        self.logger.info(f"端口扫描结果已保存到: {output_file}")
    
    def generate_summary(self) -> Dict[str, Any]:
        """
        生成数据汇总
        
        Returns:
            Dict: 汇总数据
        """
        summary = {
            'domain': self.domain,
            'subdomain_count': len(self.subdomains),
            'url_count': len(self.urls),
            'port_count': len(self.ports),
            'http_probe_count': len(self.http_probes)
        }
        
        return summary
