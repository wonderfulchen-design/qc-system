#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整数据爬虫 - 使用 Playwright 处理动态加载
爬取 2025 年至今所有售后质量数据
"""

from playwright.sync_api import sync_playwright
import pandas as pd
import json
import os
import time
from datetime import datetime

# 设置控制台编码
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

def crawl_all_data():
    print("[INFO] 开始爬取完整数据...")
    print(f"[INFO] 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_data = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # 访问页面
        print("[INFO] 访问售后反馈系统...")
        page.goto("http://114.55.34.212:8080/afterSalesFeedback.html", timeout=60000)
        page.wait_for_load_state("networkidle")
        time.sleep(3)
        
        # 获取总页数
        total_pages = 6638  # 默认值
        total_records = 99566
        try:
            page_count_text = page.locator("text=共").last.inner_text()
            import re
            match = re.search(r"共 (\d+) 条数据/共 (\d+) 页", page_count_text)
            if match:
                total_records = int(match.group(1))
                total_pages = int(match.group(2))
                print(f"[INFO] 总记录数：{total_records:,}, 总页数：{total_pages:,}")
        except Exception as e:
            print(f"[WARN] 无法获取总页数，使用默认值：{e}")
        
        # 设置时间范围 (2025 年至今)
        try:
            page.fill('input[placeholder*="开始"]', "2025-01-01")
            page.fill('input[placeholder*="结束"]', datetime.now().strftime("%Y-%m-%d"))
            page.click('button:has-text("查询")')
            page.wait_for_load_state("networkidle")
            time.sleep(2)
        except Exception as e:
            print(f"[WARN] 无法设置时间范围：{e}")
        
        # 爬取每页数据（先爬取 1000 页生成快速报告）
        max_pages = min(1000, total_pages)
        print(f"[INFO] 本次爬取目标：{max_pages} 页")
        
        for page_num in range(1, max_pages + 1):
            try:
                # 跳转到指定页
                if page_num > 1:
                    page.fill('input[type="number"]', str(page_num))
                    page.click('button:has-text("跳到")')
                    page.wait_for_load_state("networkidle")
                    time.sleep(2)
                
                # 提取表格数据
                rows = page.locator("table tbody tr").all()
                page_data = []
                
                for row in rows:
                    cells = row.locator("td").all()
                    if len(cells) >= 17:
                        try:
                            data = {
                                "buyer_wangwang": cells[0].inner_text().strip(),
                                "merchant_no": cells[1].inner_text().strip(),
                                "platform": cells[2].inner_text().strip(),
                                "order_no": cells[3].inner_text().strip(),
                                "issue_type": cells[7].inner_text().strip(),
                                "solution": cells[8].inner_text().strip(),
                                "compensation": cells[9].inner_text().strip(),
                                "factory": cells[10].inner_text().strip(),
                                "batch_no": cells[11].inner_text().strip(),
                                "pattern_batch": cells[12].inner_text().strip(),
                                "designer": cells[13].inner_text().strip(),
                                "handler": cells[14].inner_text().strip(),
                                "batch_source": cells[15].inner_text().strip(),
                                "created_at": cells[16].inner_text().strip(),
                                "page": page_num
                            }
                            page_data.append(data)
                        except Exception as e:
                            continue
                
                all_data.extend(page_data)
                print(f"[OK] 第 {page_num}/{total_pages} 页：{len(page_data)} 条")
                
                # 每 100 页保存一次
                if page_num % 100 == 0:
                    save_data(all_data, f"quality_issues_page{page_num}.json")
                    print(f"[INFO] 已保存 {len(all_data)} 条数据")
                
            except Exception as e:
                print(f"[ERROR] 第 {page_num} 页失败：{e}")
                continue
        
        browser.close()
    
    # 保存最终数据
    save_data(all_data, "quality_issues_full.json")
    print(f"\n[SUMMARY] 爬取完成！共 {len(all_data)} 条数据")
    return all_data

def save_data(data, filename):
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 同时保存 CSV
    if data:
        df = pd.DataFrame(data)
        csv_path = filepath.replace(".json", ".csv")
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        print(f"[OK] 已保存：{filepath}")

if __name__ == "__main__":
    data = crawl_all_data()
