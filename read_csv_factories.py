#!/usr/bin/env python3
"""
读取 CSV 文件，检查工厂列表
"""
import pandas as pd

print("="*70)
print("读取 CSV 文件 - 波次号工厂货品编码")
print("="*70)

# 读取 CSV 文件
file_path = r'C:\Users\Administrator\.openclaw\qqbot\downloads\波次号工厂货品编码_1774500684885.csv'

try:
    # 尝试不同编码
    for encoding in ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']:
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            print(f"\n[OK] 使用 {encoding} 编码读取成功")
            print(f"  记录数：{len(df)} 条")
            print(f"  列名：{list(df.columns)}")
            break
        except:
            continue
    else:
        # 如果都失败，尝试无表头
        df = pd.read_csv(file_path, encoding='gbk', header=None)
        print(f"\n[OK] 无表头读取成功")
        df.columns = ['波次号', '工厂', '货品编码']
    
    # 获取工厂列表
    factories = df['工厂'].dropna().unique()
    factories = [str(f).strip() for f in factories if str(f).strip()]
    
    print(f"\n工厂数量：{len(factories)} 个")
    print("\n完整工厂列表:")
    print("-"*60)
    for i, factory in enumerate(sorted(factories), 1):
        count = (df['工厂'] == factory).sum()
        print(f"  {i:2d}. {factory:<15} ({count} 条)")
    
    # 特别检查
    print("\n" + "="*60)
    print("特定工厂检查:")
    print("="*60)
    
    target_factories = ['浩茂', '浩迅', '东遇', '元合', '春秋']
    for factory in target_factories:
        if factory in factories:
            count = (df['工厂'] == factory).sum()
            print(f"  ✅ {factory}: {count} 条")
        else:
            print(f"  ❌ {factory}: 不存在")
    
    # 保存工厂列表
    with open('factories_from_csv.txt', 'w', encoding='utf-8') as f:
        f.write("CSV 文件中的工厂列表\n")
        f.write("="*60 + "\n\n")
        f.write(f"总计：{len(factories)} 个工厂\n\n")
        for factory in sorted(factories):
            count = (df['工厂'] == factory).sum()
            f.write(f"{factory}: {count} 条\n")
    
    print(f"\n[SAVE] 工厂列表已保存：factories_from_csv.txt")
    
except Exception as e:
    print(f"[ERROR] {e}")

print("\n" + "="*70)
