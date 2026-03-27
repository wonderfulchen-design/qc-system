#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于 1000 页完整数据的快速分析报告
"""

import json
import os
import pandas as pd
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
REPORT_DIR = os.path.join(os.path.dirname(__file__), "reports")

print("[INFO] 加载数据...")
json_files = sorted([f for f in os.listdir(DATA_DIR) if f.endswith('.json') and f.startswith('quality_issues_page')])

all_data = []
for file in json_files:
    filepath = os.path.join(DATA_DIR, file)
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        all_data.extend(data)

print(f"[OK] 总数据量：{len(all_data):,} 条")

df = pd.DataFrame(all_data)
df['compensation_num'] = pd.to_numeric(df['compensation'], errors='coerce').fillna(0)
df['created_at_dt'] = pd.to_datetime(df['created_at'], errors='coerce')

total = len(all_data)
date_start = df['created_at_dt'].min()
date_end = df['created_at_dt'].max()
days = (date_end - date_start).days if pd.notna(date_end) else 1

print(f"\n[INFO] 生成报告...")

# 问题类型
issue_types = df['issue_type'].value_counts()
# 工厂
factories = df['factory'].value_counts()
# 平台
platforms = df['platform'].value_counts()
# 解决方式
solutions = df['solution'].value_counts()

# 补偿
total_comp = df['compensation_num'].sum()
avg_comp = df['compensation_num'].mean()
comp_records = len(df[df['compensation_num'] > 0])

report = f"""# 服装售后质量问题深度分析报告

**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**数据来源**: 售后反馈系统完整爬取 (1000 页)  
**样本数量**: {total:,} 条  
**时间范围**: {date_start.strftime('%Y-%m-%d')} 至 {date_end.strftime('%Y-%m-%d')} ({days}天)

---

## 核心数据

| 指标 | 数值 |
|------|------|
| 总记录数 | {total:,} 条 |
| 时间跨度 | {days} 天 |
| 日均问题量 | {total//max(1,days)} 条 |
| 年度推算 | {total//max(1,days)*365:,} 条/年 |
| 总补偿金额 | RMB {total_comp:,.0f} |
| 平均补偿 | RMB {avg_comp:.1f}/条 |
| 年度补偿推算 | RMB {int(total_comp/max(1,days)*365):,} |

---

## 问题类型 TOP10

| 排名 | 问题类型 | 数量 | 占比 |
|------|----------|------|------|
"""

for i, (issue_type, count) in enumerate(issue_types.head(10).items(), 1):
    pct = count / total * 100
    report += f"| {i} | {issue_type} | {count:,} | {pct:.1f}% |\n"

top3_count = issue_types.head(3).sum()
report += f"""
**TOP3 问题集中度**: {top3_count:,} 条 ({top3_count/total*100:.1f}%)

---

## 工厂排名 TOP20

| 排名 | 工厂名称 | 问题数 | 占比 |
|------|----------|--------|------|
"""

for i, (factory, count) in enumerate(factories.head(20).items(), 1):
    pct = count / total * 100
    report += f"| {i} | {factory} | {count:,} | {pct:.1f}% |\n"

report += f"""
---

## 平台分布

| 平台 | 问题数 | 占比 |
|------|--------|------|
"""

for platform, count in platforms.items():
    pct = count / total * 100
    report += f"| {platform} | {count:,} | {pct:.1f}% |\n"

report += f"""
---

## 解决方式

| 解决方式 | 数量 | 占比 |
|----------|------|------|
"""

for solution, count in solutions.items():
    pct = count / total * 100
    report += f"| {solution} | {count:,} | {pct:.1f}% |\n"

report += f"""
---

## 成本分析

- **总补偿**: RMB {total_comp:,.0f}
- **有补偿**: {comp_records:,}/{total:,} 条 ({comp_records/total*100:.1f}%)
- **平均补偿**: RMB {avg_comp:.1f}
- **日均补偿**: RMB {total_comp/max(1,days):,.0f}
- **年度推算**: RMB {int(total_comp/max(1,days)*365):,}

---

## 重点发现

### 问题类型
1. **{issue_types.index[0]}**: {issue_types.iloc[0]:,} 条 - 需专项工艺改进
2. **{issue_types.index[1]}**: {issue_types.iloc[1]:,} 条 - 需环境整治
3. **{issue_types.index[2]}**: {issue_types.iloc[2]:,} 条 - 需面料管控

### 工厂
- **D 级工厂**: {factories.head(5).index.tolist()} - 需立即整改
- **年度节约空间**: RMB {int(total_comp/max(1,days)*365*0.7):,} (改善 70%)

---

## 建议

1. **本周**: 约谈 TOP5 工厂，启动质量审核
2. **本月**: 组建 QC 团队，建立检验标准
3. **本季**: 问题率降低 30%，补偿成本降低 30%

---

*数据量：{total:,} 条真实数据 | 覆盖时间：{days} 天*
"""

report_path = os.path.join(REPORT_DIR, f"深度分析_1000 页_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(report)

print(f"[OK] 报告已保存：{report_path}")
print(f"\n[OK] 分析完成！")
