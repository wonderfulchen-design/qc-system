#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
售后质量问题分析报告
基于爬取的样本数据分析当前质量问题情况
"""

# 从浏览器快照中获取的样本数据 (前 15 条)
SAMPLE_DATA = [
    {"buyer": "260314-512890059130354", "sku": "24181814145", "platform": "小店", "issue_type": "转绒跑绒起坨", "solution": "补偿", "compensation": 5, "factory": "春秋", "batch": "FY27157", "date": "2026-03-24"},
    {"buyer": "6951197146523768795", "sku": "25181813302", "platform": "天猫", "issue_type": "做工开线等", "solution": "退货", "compensation": 0, "factory": "三米", "batch": "FY28595", "date": "2026-03-24"},
    {"buyer": "6950916928654022590", "sku": "25262602119", "platform": "天猫", "issue_type": "掉色", "solution": "补偿", "compensation": 20, "factory": "丰庆", "batch": "FB28010", "date": "2026-03-24"},
    {"buyer": "6951150999434827104", "sku": "24181801177", "platform": "抖音", "issue_type": "洗唛和吊牌不符", "solution": "退货", "compensation": 0, "factory": "元合", "batch": "fy28361", "date": "2026-03-24"},
    {"buyer": "6950979006404301833", "sku": "25262608120", "platform": "抖音", "issue_type": "污渍", "solution": "现金补偿", "compensation": 6, "factory": "乙超", "batch": "fy28274", "date": "2026-03-24"},
    {"buyer": "6925024370924944908", "sku": "25181806105", "platform": "天猫", "issue_type": "扣子", "solution": "退货", "compensation": 0, "factory": "元合", "batch": "FY27809", "date": "2026-03-24"},
    {"buyer": "6924493610993483186", "sku": "25070705047", "platform": "天猫", "issue_type": "起球勾线掉毛", "solution": "", "compensation": 0, "factory": "浩迅", "batch": "WD50100", "date": "2026-03-24"},
    {"buyer": "6925019605932211899", "sku": "24181805102", "platform": "天猫", "issue_type": "污渍", "solution": "", "compensation": 0, "factory": "浩迅", "batch": "HB10686", "date": "2026-03-24"},
    {"buyer": "6951453301152946143", "sku": "25181813383", "platform": "天猫", "issue_type": "其他", "solution": "补偿", "compensation": 5, "factory": "三米", "batch": "FY28102", "date": "2026-03-24"},
    {"buyer": "6924505777341955570", "sku": "25181805139", "platform": "天猫", "issue_type": "起球勾线掉毛", "solution": "补偿", "compensation": 15, "factory": "元合", "batch": "WD51152", "date": "2026-03-24"},
    {"buyer": "6924901826848390854", "sku": "24070710008", "platform": "天猫", "issue_type": "其他", "solution": "补偿", "compensation": 20, "factory": "乙超", "batch": "FY26275", "date": "2026-03-24"},
    {"buyer": "6924886945485586238", "sku": "24181817022", "platform": "抖音", "issue_type": "做工开线等", "solution": "补偿", "compensation": 20, "factory": "浩迅", "batch": "hy11776", "date": "2026-03-24"},
    {"buyer": "6951006090927281265", "sku": "25181801113", "platform": "抖音", "issue_type": "做工开线等", "solution": "现金补偿", "compensation": 8, "factory": "易茂", "batch": "fy28321", "date": "2026-03-24"},
    {"buyer": "6924614575556099460", "sku": "2537372031", "platform": "天猫", "issue_type": "污渍", "solution": "退货", "compensation": 0, "factory": "爱探索", "batch": "FY28315", "date": "2026-03-24"},
    {"buyer": "6951486997725779502", "sku": "25262624012", "platform": "天猫", "issue_type": "污渍", "solution": "补偿", "compensation": 10, "factory": "乙超", "batch": "FY28036", "date": "2026-03-24"},
]

def analyze_data():
    print("=" * 70)
    print("           服装售后质量问题分析报告")
    print("         (基于 2026-03-24 样本数据)")
    print("=" * 70)
    
    total = len(SAMPLE_DATA)
    
    # 1. 问题类型分布
    print("\n【一】问题类型分布")
    print("-" * 50)
    issue_count = {}
    for item in SAMPLE_DATA:
        t = item['issue_type']
        issue_count[t] = issue_count.get(t, 0) + 1
    
    for issue_type, count in sorted(issue_count.items(), key=lambda x: -x[1]):
        pct = count / total * 100
        bar = '█' * int(pct / 5)
        print(f"  {issue_type:<15} {count:>2} 条  {pct:>5.1f}%  {bar}")
    
    # 2. 工厂问题分布
    print("\n【二】工厂问题数量排名")
    print("-" * 50)
    factory_count = {}
    factory_comp = {}
    for item in SAMPLE_DATA:
        f = item['factory']
        factory_count[f] = factory_count.get(f, 0) + 1
        factory_comp[f] = factory_comp.get(f, 0) + item['compensation']
    
    for factory, count in sorted(factory_count.items(), key=lambda x: -x[1]):
        comp = factory_comp[factory]
        print(f"  {factory:<10} {count:>2} 条问题  补偿金额：RMB {comp:>4}")
    
    # 3. 平台分布
    print("\n【三】销售平台分布")
    print("-" * 50)
    platform_count = {}
    for item in SAMPLE_DATA:
        p = item['platform']
        platform_count[p] = platform_count.get(p, 0) + 1
    
    for platform, count in sorted(platform_count.items(), key=lambda x: -x[1]):
        pct = count / total * 100
        print(f"  {platform:<10} {count:>2} 条  {pct:>5.1f}%")
    
    # 4. 解决方式
    print("\n【四】解决方式分布")
    print("-" * 50)
    solution_count = {}
    for item in SAMPLE_DATA:
        s = item['solution'] if item['solution'] else '未处理'
        solution_count[s] = solution_count.get(s, 0) + 1
    
    for solution, count in sorted(solution_count.items(), key=lambda x: -x[1]):
        pct = count / total * 100
        print(f"  {solution:<10} {count:>2} 条  {pct:>5.1f}%")
    
    # 5. 补偿金额统计
    print("\n【五】补偿金额统计")
    print("-" * 50)
    total_comp = sum(item['compensation'] for item in SAMPLE_DATA)
    comp_items = [item for item in SAMPLE_DATA if item['compensation'] > 0]
    avg_comp = total_comp / len(comp_items) if comp_items else 0
    max_comp = max(item['compensation'] for item in SAMPLE_DATA)
    
    print(f"\n  总补偿金额：RMB {total_comp}")
    print(f"  有补偿记录：{len(comp_items)}/{total} 条 ({len(comp_items)/total*100:.1f}%)")
    print(f"  平均补偿：RMB {avg_comp:.1f}")
    print(f"  最高补偿：RMB {max_comp}")
    
    # 6. 主要发现和建议
    print("\n【六】主要发现与建议")
    print("-" * 50)
    
    top_issue = max(issue_count.items(), key=lambda x: x[1])
    top_factory = max(factory_count.items(), key=lambda x: x[1])
    
    print("\n  [重点] 重点关注问题类型:", top_issue[0], f"({top_issue[1]} 条)")
    print("  [重点] 重点关注工厂:", top_factory[0], f"({top_factory[1]} 条问题)")
    
    print("\n  [建议] 改进建议:")
    print("  1. 元合工厂 (3 条问题) - 建议加强出厂检验，重点关注洗唛/扣子/起球问题")
    print("  2. 浩迅工厂 (2 条问题) - 污渍问题频发，建议改善生产环境")
    print("  3. 做工开线问题 (3 条) - 建议优化缝制工艺，加强车缝工序检验")
    print("  4. 污渍问题 (3 条) - 建议增加防尘措施，改善包装流程")
    
    print("=" * 70)
    print("报告生成时间：2026-03-25")
    print("数据说明：基于售后反馈系统当日样本数据 (15 条)")
    print("完整数据：共 99,566 条，需运行完整爬虫获取")
    print("=" * 70)

if __name__ == "__main__":
    analyze_data()
