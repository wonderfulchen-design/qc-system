#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于已爬取数据的快速分析报告
"""

import pandas as pd
import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
REPORT_DIR = os.path.join(os.path.dirname(__file__), "reports")

def analyze_existing_data():
    print("[INFO] 开始分析已爬取数据...")
    
    # 查找所有已保存的数据文件
    json_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.json') and f.startswith('quality_issues')]
    
    if not json_files:
        print("[ERROR] 未找到数据文件")
        return
    
    print(f"[INFO] 找到 {len(json_files)} 个数据文件")
    
    # 合并所有数据
    all_data = []
    for file in sorted(json_files):
        filepath = os.path.join(DATA_DIR, file)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            all_data.extend(data)
            print(f"[OK] {file}: {len(data)} 条")
    
    print(f"\n[INFO] 总数据量：{len(all_data)} 条")
    
    if len(all_data) == 0:
        print("[ERROR] 数据为空")
        return
    
    # 转换为 DataFrame
    df = pd.DataFrame(all_data)
    
    # 基础统计
    print("\n" + "="*60)
    print("基础统计")
    print("="*60)
    print(f"总记录数：{len(all_data):,} 条")
    print(f"数据文件：{len(json_files)} 个")
    
    # 问题类型分布
    print("\n" + "="*60)
    print("问题类型分布")
    print("="*60)
    issue_type_dist = df['issue_type'].value_counts()
    for issue_type, count in issue_type_dist.items():
        pct = count / len(all_data) * 100
        print(f"  {issue_type}: {count} 条 ({pct:.1f}%)")
    
    # 工厂分布
    print("\n" + "="*60)
    print("工厂问题分布")
    print("="*60)
    factory_dist = df['factory'].value_counts().head(20)
    for factory, count in factory_dist.items():
        print(f"  {factory}: {count} 条")
    
    # 平台分布
    print("\n" + "="*60)
    print("销售平台分布")
    print("="*60)
    platform_dist = df['platform'].value_counts()
    for platform, count in platform_dist.items():
        pct = count / len(all_data) * 100
        print(f"  {platform}: {count} 条 ({pct:.1f}%)")
    
    # 补偿统计
    print("\n" + "="*60)
    print("补偿金额统计")
    print("="*60)
    df['compensation_num'] = pd.to_numeric(df['compensation'], errors='coerce').fillna(0)
    total_comp = df['compensation_num'].sum()
    avg_comp = df['compensation_num'].mean()
    comp_records = len(df[df['compensation_num'] > 0])
    print(f"  总补偿金额：RMB {total_comp:,.0f}")
    print(f"  有补偿记录：{comp_records}/{len(all_data)} 条 ({comp_records/len(all_data)*100:.1f}%)")
    print(f"  平均补偿：RMB {avg_comp:.1f}")
    
    # 解决方式
    print("\n" + "="*60)
    print("解决方式分布")
    print("="*60)
    solution_dist = df['solution'].value_counts()
    for solution, count in solution_dist.items():
        pct = count / len(all_data) * 100
        print(f"  {solution}: {count} 条 ({pct:.1f}%)")
    
    # 生成报告
    generate_report(df, all_data)
    
    print("\n" + "="*60)
    print("分析完成！")
    print("="*60)

def generate_report(df, all_data):
    """生成 Markdown 报告"""
    
    report = f"""# 服装售后质量问题快速分析报告

**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**数据来源**: 售后反馈系统  
**样本数量**: {len(all_data):,} 条  
**数据覆盖**: 约 {len(all_data)/15*100:.0f} 页

---

## 一、数据概览

| 指标 | 数值 |
|------|------|
| 总记录数 | {len(all_data):,} 条 |
| 数据文件 | {len([f for f in os.listdir(DATA_DIR) if f.endswith('.json')])} 个 |
| 推算总量 | 约 {int(len(all_data)/100*6638):,} 条 (按 6638 页推算) |

---

## 二、问题类型分布

| 排名 | 问题类型 | 数量 | 占比 |
|------|----------|------|------|
"""
    
    issue_type_dist = df['issue_type'].value_counts()
    for i, (issue_type, count) in enumerate(issue_type_dist.items(), 1):
        pct = count / len(all_data) * 100
        report += f"| {i} | {issue_type} | {count} | {pct:.1f}% |\n"
    
    report += f"""
---

## 三、工厂问题排名 (TOP10)

| 排名 | 工厂名称 | 问题数 | 占比 |
|------|----------|--------|------|
"""
    
    factory_dist = df['factory'].value_counts().head(10)
    for i, (factory, count) in enumerate(factory_dist.items(), 1):
        pct = count / len(all_data) * 100
        report += f"| {i} | {factory} | {count} | {pct:.1f}% |\n"
    
    report += f"""
---

## 四、销售平台分布

| 平台 | 问题数 | 占比 |
|------|--------|------|
"""
    
    platform_dist = df['platform'].value_counts()
    for platform, count in platform_dist.items():
        pct = count / len(all_data) * 100
        report += f"| {platform} | {count} | {pct:.1f}% |\n"
    
    report += f"""
---

## 五、补偿成本统计

| 指标 | 数值 |
|------|------|
| 总补偿金额 | RMB {df['compensation_num'].sum():,.0f} |
| 有补偿占比 | {len(df[df['compensation_num'] > 0])}/{len(all_data)} ({len(df[df['compensation_num'] > 0])/len(all_data)*100:.1f}%) |
| 平均补偿 | RMB {df['compensation_num'].mean():.1f} |
| 最高补偿 | RMB {df['compensation_num'].max():.0f} |

**推算年度成本**: RMB {df['compensation_num'].sum()/len(all_data)*99566:,.0f} (按 99,566 条推算)

---

## 六、解决方式分布

| 解决方式 | 数量 | 占比 |
|----------|------|------|
"""
    
    solution_dist = df['solution'].value_counts()
    for solution, count in solution_dist.items():
        pct = count / len(all_data) * 100
        report += f"| {solution} | {count} | {pct:.1f}% |\n"
    
    report += f"""
---

## 七、重点发现

### 问题类型集中度
- TOP3 问题类型占比：{issue_type_dist.head(3).sum()/len(all_data)*100:.1f}%
- 主要问题：{issue_type_dist.index[0] if len(issue_type_dist) > 0 else 'N/A'}

### 工厂集中度
- TOP3 工厂问题数：{factory_dist.head(3).sum()} 条
- 占比：{factory_dist.head(3).sum()/len(all_data)*100:.1f}%

### 成本分析
- 日均补偿成本：RMB {df['compensation_num'].sum()/max(1, len([f for f in os.listdir(DATA_DIR) if f.endswith('.json')])):,.0f}
- 单条问题平均成本：RMB {df['compensation_num'].mean():.1f}

---

## 八、建议

1. **重点关注 TOP3 工厂**: {', '.join(factory_dist.head(3).index.tolist())}
2. **专项改善 TOP3 问题**: {', '.join(issue_type_dist.head(3).index.tolist())}
3. **加强天猫平台品控**: 占比{platform_dist.get('天猫', 0)/len(all_data)*100:.1f}%
4. **优化补偿策略**: 当前平均 RMB {df['compensation_num'].mean():.1f}/条

---

*本报告基于已爬取数据生成，数据量越大分析越准确*
"""
    
    # 保存报告
    report_path = os.path.join(REPORT_DIR, f"快速分析_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n[OK] 报告已保存：{report_path}")

if __name__ == "__main__":
    analyze_existing_data()
