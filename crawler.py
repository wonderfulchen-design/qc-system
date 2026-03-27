#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
服装售后质量问题数据爬虫
爬取 2025 年至今的售后反馈数据
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import os
import time
from datetime import datetime, timedelta
from urllib.parse import urljoin
import re

# 配置
BASE_URL = "http://114.55.34.212:8080"
FEEDBACK_URL = f"{BASE_URL}/afterSalesFeedback.html"
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
IMAGE_DIR = os.path.join(DATA_DIR, "images")

# 确保目录存在
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)

# 问题类型映射
ISSUE_TYPES = [
    "污渍", "扣子", "拉链", "尺码不符", "掉色", "印花问题", 
    "做工开线等", "破洞", "起球勾线掉毛", "过敏", 
    "洗唛和吊牌不符", "有味道", "面料硬不舒服", "色差", 
    "松紧坏", "长短不一", "发错", "少发", "其他"
]

# 平台映射
PLATFORMS = ["天猫", "淘宝", "小店", "抖音"]


class AfterSalesCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        })
        self.data = []
        self.total_pages = 0
        self.total_records = 0
        
    def login(self, username=None, password=None):
        """
        如果系统需要登录，实现登录逻辑
        目前页面似乎是公开访问的
        """
        # TODO: 如果需要登录，在这里实现
        # response = self.session.post(login_url, data={...})
        print("[OK] 无需登录或已登录")
        return True
    
    def get_total_count(self, html):
        """从页面获取总记录数和总页数"""
        soup = BeautifulSoup(html, 'html.parser')
        # 查找分页信息，如 "共 99566 条数据/共 6638 页"
        pagination_text = soup.find(string=re.compile(r"共\d+条数据"))
        if pagination_text:
            match = re.search(r"共 (\d+) 条数据/共 (\d+) 页", pagination_text)
            if match:
                self.total_records = int(match.group(1))
                self.total_pages = int(match.group(2))
                print(f"[INFO] 总记录数：{self.total_records:,}, 总页数：{self.total_pages:,}")
                return True
        return False
    
    def parse_table_row(self, row):
        """解析表格行数据"""
        cells = row.find_all(['td', 'th'])
        if len(cells) < 17:
            return None
            
        try:
            # 提取各列数据
            data = {
                'buyer_wangwang': cells[0].get_text(strip=True),  # 买家旺旺
                'merchant_no': cells[1].get_text(strip=True),      # 商家编号
                'platform': cells[2].get_text(strip=True),         # 问题来源
                'order_no': cells[3].get_text(strip=True),         # 交易单号
                'product_image': '',                               # 商品图
                'issue_image_1': '',                               # 问题图 1
                'issue_image_2': '',                               # 问题图 2
                'issue_type': cells[7].get_text(strip=True),       # 问题描述
                'solution': cells[8].get_text(strip=True),         # 解决方式
                'compensation': cells[9].get_text(strip=True),     # 补偿金额
                'factory': cells[10].get_text(strip=True),         # 车缝工厂
                'batch_no': cells[11].get_text(strip=True),        # 波次号
                'pattern_batch': cells[12].get_text(strip=True),   # 版型波次
                'designer': cells[13].get_text(strip=True),        # 设计师
                'handler': cells[14].get_text(strip=True),         # 处理人
                'batch_source': cells[15].get_text(strip=True),    # 波次来源
                'created_at': cells[16].get_text(strip=True),      # 添加时间
            }
            
            # 提取图片链接
            for i, cell in enumerate(cells[4:7], 4):
                img = cell.find('img')
                link = cell.find('a')
                if link and link.get('href'):
                    if i == 4:
                        data['product_image'] = link.get('href')
                    elif i == 5:
                        data['issue_image_1'] = link.get('href')
                    elif i == 6:
                        data['issue_image_2'] = link.get('href')
            
            # 验证时间范围 (2025 年至今)
            if data['created_at']:
                try:
                    create_date = datetime.strptime(data['created_at'], '%Y-%m-%d %H:%M:%S')
                    if create_date.year < 2025:
                        return None  # 跳过 2025 年之前的数据
                except:
                    pass
            
            return data
        except Exception as e:
            print(f"解析行数据出错：{e}")
            return None
    
    def fetch_page(self, page_num):
        """获取指定页的数据"""
        try:
            # 构建请求参数 (根据实际页面调整)
            params = {
                'page': page_num,
                # 可以添加时间范围筛选
                'startDate': '2025-01-01',
                'endDate': datetime.now().strftime('%Y-%m-%d'),
            }
            
            # 如果是 POST 请求或需要特殊参数，需要调整
            response = self.session.get(FEEDBACK_URL, params=params, timeout=30)
            response.raise_for_status()
            
            return response.text
        except Exception as e:
            print(f"获取第{page_num}页失败：{e}")
            return None
    
    def parse_page(self, html):
        """解析页面数据"""
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table')
        if not table:
            print("未找到数据表格")
            return []
        
        rows = []
        # 获取 tbody 中的所有行 (跳过表头)
        tbody = table.find('tbody')
        if tbody:
            for row in tbody.find_all('tr', recursive=False):
                data = self.parse_table_row(row)
                if data:
                    rows.append(data)
        
        return rows
    
    def download_image(self, url, save_path):
        """下载图片"""
        if not url:
            return False
        
        try:
            # 处理相对 URL
            if url.startswith('/'):
                url = urljoin(BASE_URL, url)
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # 提取文件名
            filename = os.path.basename(url.split('?')[0])
            filepath = os.path.join(save_path, filename)
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            return filepath
        except Exception as e:
            print(f"下载图片失败 {url}: {e}")
            return None
    
    def save_to_csv(self, filename='quality_issues.csv'):
        """保存数据到 CSV"""
        if not self.data:
            print("[WARN] 没有数据可保存")
            return
        
        filepath = os.path.join(DATA_DIR, filename)
        fieldnames = list(self.data[0].keys())
        
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.data)
        
        print(f"[OK] 数据已保存到：{filepath}")
    
    def save_to_json(self, filename='quality_issues.json'):
        """保存数据到 JSON"""
        if not self.data:
            print("[WARN] 没有数据可保存")
            return
        
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        
        print(f"[OK] 数据已保存到：{filepath}")
    
    def crawl(self, max_pages=None, download_images=False):
        """执行爬取"""
        print("[INFO] 开始爬取售后反馈数据...")
        print(f"[INFO] 时间范围：2025-01-01 至今")
        
        # 登录 (如果需要)
        self.login()
        
        # 获取第一页，解析总记录数
        print("[INFO] 获取第一页数据...")
        first_page_html = self.fetch_page(1)
        if not first_page_html:
            print("[ERROR] 无法获取第一页数据")
            return False
        
        self.get_total_count(first_page_html)
        
        # 解析第一页数据
        first_page_data = self.parse_page(first_page_html)
        self.data.extend(first_page_data)
        print(f"[OK] 第 1 页：获取 {len(first_page_data)} 条记录")
        
        # 确定爬取页数
        if max_pages:
            total_pages = min(max_pages, self.total_pages)
        else:
            total_pages = self.total_pages
        
        print(f"[INFO] 计划爬取 {total_pages} 页...")
        
        # 爬取剩余页面
        for page in range(2, total_pages + 1):
            print(f"[INFO] 爬取第 {page}/{total_pages} 页...", end=" ")
            
            html = self.fetch_page(page)
            if html:
                page_data = self.parse_page(html)
                self.data.extend(page_data)
                print(f"[OK] {len(page_data)} 条")
            else:
                print("[FAILED]")
            
            # 避免请求过快
            time.sleep(1)
        
        print(f"\n[SUMMARY] 爬取完成！共获取 {len(self.data)} 条记录")
        
        # 保存数据
        self.save_to_csv()
        self.save_to_json()
        
        # 下载图片 (可选)
        if download_images:
            print("\n[INFO] 开始下载图片...")
            self.download_all_images()
        
        return True
    
    def download_all_images(self):
        """下载所有图片"""
        for i, record in enumerate(self.data):
            if (i + 1) % 100 == 0:
                print(f"下载进度：{i + 1}/{len(self.data)}")
            
            for img_field in ['product_image', 'issue_image_1', 'issue_image_2']:
                url = record.get(img_field)
                if url:
                    self.download_image(url, IMAGE_DIR)


def main():
    crawler = AfterSalesCrawler()
    
    # 测试爬取前 10 页
    crawler.crawl(max_pages=10, download_images=False)
    
    # 完整爬取 (取消注释以启用)
    # crawler.crawl(max_pages=None, download_images=True)
    
    # 输出统计信息
    print("\n" + "="*50)
    print("数据统计")
    print("="*50)
    
    if crawler.data:
        # 按问题类型统计
        issue_type_count = {}
        for record in crawler.data:
            issue_type = record.get('issue_type', '未知')
            issue_type_count[issue_type] = issue_type_count.get(issue_type, 0) + 1
        
        print("\n问题类型分布:")
        for issue_type, count in sorted(issue_type_count.items(), key=lambda x: -x[1]):
            print(f"  {issue_type}: {count}")
        
        # 按工厂统计
        factory_count = {}
        for record in crawler.data:
            factory = record.get('factory', '未知')
            factory_count[factory] = factory_count.get(factory, 0) + 1
        
        print("\n工厂问题数量 TOP10:")
        for factory, count in sorted(factory_count.items(), key=lambda x: -x[1])[:10]:
            print(f"  {factory}: {count}")
        
        # 按平台统计
        platform_count = {}
        for record in crawler.data:
            platform = record.get('platform', '未知')
            platform_count[platform] = platform_count.get(platform, 0) + 1
        
        print("\n平台分布:")
        for platform, count in sorted(platform_count.items(), key=lambda x: -x[1]):
            print(f"  {platform}: {count}")


if __name__ == "__main__":
    main()
