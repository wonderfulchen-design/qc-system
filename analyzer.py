#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
售后质量数据分析脚本
分析 2025 年至今的质量问题数据，生成统计报告
"""

import json
import csv
import os
from datetime import datetime
from collections import defaultdict
import re

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
REPORT_DIR = os.path.join(os.path.dirname(__file__), "reports")

os.makedirs(REPORT_DIR, exist_ok=True)


class QualityAnalyzer:
    def __init__(self, data_file=None):
        self.data = []
        self.load_data(data_file)
    
    def load_data(self, data_file=None):
        """加载数据"""
        if data_file is None:
            # 默认加载 JSON 文件
            json_path = os.path.join(DATA_DIR, "quality_issues.json")
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                print(f"✓ 已加载 {len(self.data)} 条数据")
                return
        
        # 尝试加载 CSV
        csv_path = data_file or os.path.join(DATA_DIR, "quality_issues.csv")
        if os.path.exists(csv_path):
            with open(csv_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                self.data = list(reader)
            print(f"✓ 已加载 {len(self.data)} 条数据")
    
    def analyze_overall(self):
        """整体情况分析"""
        print("\n" + "="*60)
        print("📊 整体情况分析")
        print("="*60)
        
        total = len(self.data)
        print(f"\n总记录数：{total:,}")
        
        # 时间范围
        dates = []
        for record in self.data:
            created_at = record.get('created_at', '')
            if created_at:
                try:
                    dt = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                    dates.append(dt)
                except:
                    pass
        
        if dates:
            print(f"时间范围：{min(dates).strftime('%Y-%m-%d')} 至 {max(dates).strftime('%Y-%m-%d')}")
        
        # 补偿金额统计
        total_compensation = 0
        compensation_count = 0
        for record in self.data:
            comp = record.get('compensation', '0')
            try:
                comp_val = float(comp) if comp else 0
                if comp_val > 0:
                    total_compensation += comp_val
                    compensation_count += 1
            except:
                pass
        
        print(f"\n💰 补偿金额统计:")
        print(f"  有补偿记录数：{compensation_count:,} ({compensation_count/total*100:.1f}%)")
        print(f"  总补偿金额：¥{total_compensation:,.2f}")
        if compensation_count > 0:
            print(f"  平均补偿金额：¥{total_compensation/compensation_count:.2f}")
    
    def analyze_by_issue_type(self):
        """按问题类型分析"""
        print("\n" + "="*60)
        print("🏷️ 问题类型分析")
        print("="*60)
        
        issue_count = defaultdict(int)
        issue_compensation = defaultdict(float)
        
        for record in self.data:
            issue_type = record.get('issue_type', '未知') or '未知'
            issue_count[issue_type] += 1
            
            comp = record.get('compensation', '0')
            try:
                comp_val = float(comp) if comp else 0
                issue_compensation[issue_type] += comp_val
            except:
                pass
        
        total = len(self.data)
        print(f"\n问题类型分布 (按数量排序):")
        print(f"{'问题类型':<15} {'数量':>8} {'占比':>8} {'补偿总额':>12} {'均补':>8}")
        print("-" * 60)
        
        for issue_type, count in sorted(issue_count.items(), key=lambda x: -x[1]):
            pct = count / total * 100
            comp_total = issue_compensation[issue_type]
            avg_comp = comp_total / count if count > 0 else 0
            print(f"{issue_type:<15} {count:>8,} {pct:>7.1f}% ¥{comp_total:>10,.0f} ¥{avg_comp:>7.0f}")
        
        # TOP5 问题类型
        print(f"\n⚠️ TOP5 质量问题:")
        for i, (issue_type, count) in enumerate(sorted(issue_count.items(), key=lambda x: -x[1])[:5], 1):
            pct = count / total * 100
            print(f"  {i}. {issue_type}: {count:,} 条 ({pct:.1f}%)")
    
    def analyze_by_factory(self):
        """按工厂分析"""
        print("\n" + "="*60)
        print("🏭 工厂质量分析")
        print("="*60)
        
        factory_count = defaultdict(int)
        factory_compensation = defaultdict(float)
        factory_issues = defaultdict(lambda: defaultdict(int))
        
        for record in self.data:
            factory = record.get('factory', '未知') or '未知'
            issue_type = record.get('issue_type', '未知') or '未知'
            
            factory_count[factory] += 1
            
            comp = record.get('compensation', '0')
            try:
                comp_val = float(comp) if comp else 0
                factory_compensation[factory] += comp_val
            except:
                pass
            
            factory_issues[factory][issue_type] += 1
        
        total = len(self.data)
        
        print(f"\n工厂问题数量排名:")
        print(f"{'工厂名称':<15} {'问题数':>8} {'占比':>8} {'补偿总额':>12} {'主要问题':>20}")
        print("-" * 70)
        
        for factory, count in sorted(factory_count.items(), key=lambda x: -x[1])[:15]:
            pct = count / total * 100
            comp_total = factory_compensation[factory]
            
            # 找出该工厂的主要问题类型
            main_issues = sorted(factory_issues[factory].items(), key=lambda x: -x[1])[:2]
            main_issue_str = ", ".join([f"{i[0]}({i[1]})" for i in main_issues])
            
            print(f"{factory:<15} {count:>8,} {pct:>7.1f}% ¥{comp_total:>10,.0f} {main_issue_str:>20}")
        
        # 质量评级 (模拟)
        print(f"\n📈 工厂质量评级 (基于问题率):")
        # 这里需要总订单数据来计算问题率，暂时用问题数量模拟
        avg_count = sum(factory_count.values()) / len(factory_count) if factory_count else 0
        
        for factory, count in sorted(factory_count.items(), key=lambda x: -x[1])[:10]:
            ratio = count / avg_count
            if ratio < 0.5:
                level = "A (优秀)"
            elif ratio < 0.8:
                level = "B (良好)"
            elif ratio < 1.2:
                level = "C (一般)"
            else:
                level = "D (需改进)"
            print(f"  {factory}: {level}")
    
    def analyze_by_platform(self):
        """按平台分析"""
        print("\n" + "="*60)
        print("📱 销售平台分析")
        print("="*60)
        
        platform_count = defaultdict(int)
        platform_compensation = defaultdict(float)
        
        for record in self.data:
            platform = record.get('platform', '未知') or '未知'
            platform_count[platform] += 1
            
            comp = record.get('compensation', '0')
            try:
                comp_val = float(comp) if comp else 0
                platform_compensation[platform] += comp_val
            except:
                pass
        
        total = len(self.data)
        
        print(f"\n平台问题分布:")
        print(f"{'平台':<10} {'问题数':>8} {'占比':>8} {'补偿总额':>12} {'均补':>8}")
        print("-" * 55)
        
        for platform, count in sorted(platform_count.items(), key=lambda x: -x[1]):
            pct = count / total * 100
            comp_total = platform_compensation[platform]
            avg_comp = comp_total / count if count > 0 else 0
            print(f"{platform:<10} {count:>8,} {pct:>7.1f}% ¥{comp_total:>10,.0f} ¥{avg_comp:>7.0f}")
    
    def analyze_by_time(self):
        """按时间趋势分析"""
        print("\n" + "="*60)
        print("📅 时间趋势分析")
        print("="*60)
        
        # 按月统计
        month_count = defaultdict(int)
        month_compensation = defaultdict(float)
        
        for record in self.data:
            created_at = record.get('created_at', '')
            if created_at:
                try:
                    dt = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                    month_key = dt.strftime('%Y-%m')
                    month_count[month_key] += 1
                    
                    comp = record.get('compensation', '0')
                    try:
                        comp_val = float(comp) if comp else 0
                        month_compensation[month_key] += comp_val
                    except:
                        pass
                except:
                    pass
        
        print(f"\n月度问题趋势:")
        print(f"{'月份':<10} {'问题数':>10} {'环比':>10} {'补偿金额':>12}")
        print("-" * 50)
        
        prev_count = 0
        for month in sorted(month_count.keys()):
            count = month_count[month]
            comp = month_compensation[month]
            
            if prev_count > 0:
                change = (count - prev_count) / prev_count * 100
                change_str = f"{change:+.1f}%"
            else:
                change_str = "-"
            
            print(f"{month:<10} {count:>10,} {change_str:>10} ¥{comp:>10,.0f}")
            prev_count = count
    
    def analyze_solution(self):
        """解决方式分析"""
        print("\n" + "="*60)
        print("🔧 解决方式分析")
        print("="*60)
        
        solution_count = defaultdict(int)
        solution_compensation = defaultdict(float)
        
        for record in self.data:
            solution = record.get('solution', '未知') or '未知'
            solution_count[solution] += 1
            
            comp = record.get('compensation', '0')
            try:
                comp_val = float(comp) if comp else 0
                solution_compensation[solution] += comp_val
            except:
                pass
        
        total = len(self.data)
        
        print(f"\n解决方式分布:")
        print(f"{'解决方式':<15} {'数量':>8} {'占比':>8} {'补偿总额':>12}")
        print("-" * 50)
        
        for solution, count in sorted(solution_count.items(), key=lambda x: -x[1]):
            pct = count / total * 100
            comp_total = solution_compensation[solution]
            print(f"{solution:<15} {count:>8,} {pct:>7.1f}% ¥{comp_total:>10,.0f}")
    
    def generate_report(self, output_file=None):
        """生成完整分析报告"""
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = os.path.join(REPORT_DIR, f"quality_analysis_report_{timestamp}.txt")
        
        # 重定向输出到文件
        import sys
        original_stdout = sys.stdout
        
        with open(output_file, 'w', encoding='utf-8') as f:
            sys.stdout = f
            
            print("=" * 60)
            print("服装售后质量问题分析报告")
            print("=" * 60)
            print(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"数据总量：{len(self.data):,} 条")
            print()
            
            sys.stdout = original_stdout
            print("正在生成报告...")
        
        # 重新执行所有分析，输出到文件
        with open(output_file, 'a', encoding='utf-8') as f:
            sys.stdout = f
            
            self.analyze_overall()
            self.analyze_by_issue_type()
            self.analyze_by_factory()
            self.analyze_by_platform()
            self.analyze_by_time()
            self.analyze_solution()
            
            sys.stdout = original_stdout
        
        print(f"\n✓ 报告已保存至：{output_file}")
        return output_file
    
    def get_summary_stats(self):
        """获取汇总统计数据"""
        stats = {
            'total_records': len(self.data),
            'issue_types': defaultdict(int),
            'factories': defaultdict(int),
            'platforms': defaultdict(int),
            'total_compensation': 0,
            'date_range': {'start': None, 'end': None}
        }
        
        dates = []
        for record in self.data:
            # 问题类型
            issue_type = record.get('issue_type', '未知') or '未知'
            stats['issue_types'][issue_type] += 1
            
            # 工厂
            factory = record.get('factory', '未知') or '未知'
            stats['factories'][factory] += 1
            
            # 平台
            platform = record.get('platform', '未知') or '未知'
            stats['platforms'][platform] += 1
            
            # 补偿金额
            comp = record.get('compensation', '0')
            try:
                stats['total_compensation'] += float(comp) if comp else 0
            except:
                pass
            
            # 日期
            created_at = record.get('created_at', '')
            if created_at:
                try:
                    dt = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                    dates.append(dt)
                except:
                    pass
        
        if dates:
            stats['date_range']['start'] = min(dates).strftime('%Y-%m-%d')
            stats['date_range']['end'] = max(dates).strftime('%Y-%m-%d')
        
        # 转换 defaultdict 为普通 dict
        stats['issue_types'] = dict(stats['issue_types'])
        stats['factories'] = dict(stats['factories'])
        stats['platforms'] = dict(stats['platforms'])
        
        return stats


def main():
    print("🔍 开始分析售后质量数据...")
    
    analyzer = QualityAnalyzer()
    
    if not analyzer.data:
        print("❌ 未找到数据文件，请先运行爬虫脚本")
        return
    
    # 执行各项分析
    analyzer.analyze_overall()
    analyzer.analyze_by_issue_type()
    analyzer.analyze_by_factory()
    analyzer.analyze_by_platform()
    analyzer.analyze_by_time()
    analyzer.analyze_solution()
    
    # 生成报告文件
    report_file = analyzer.generate_report()
    
    # 输出汇总统计 (JSON 格式)
    stats = analyzer.get_summary_stats()
    stats_file = os.path.join(REPORT_DIR, "summary_stats.json")
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"\n✓ 汇总统计已保存至：{stats_file}")
    
    print("\n" + "="*60)
    print("✅ 分析完成!")
    print("="*60)


if __name__ == "__main__":
    main()
