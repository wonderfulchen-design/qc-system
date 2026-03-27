#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 QC 项目数据分析可视化图表
"""

import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime
import os

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False

# 创建输出目录
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "reports", "images")
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("[INFO] 生成 QC 项目数据分析图表...")

# 创建多子图仪表板
fig = plt.figure(figsize=(20, 16))
fig.patch.set_facecolor('#f5f6f8')

# ============ 图 1: 问题类型分布 ============
ax1 = plt.subplot(2, 3, 1)
issue_types = ['做工开线', '污渍', '起球勾线', '其他', '扣子', '掉色']
issue_counts = [19000, 15000, 9000, 8000, 7000, 6000]
colors1 = ['#ff4757', '#ffa502', '#ff7f50', '#70a1ff', '#1e90ff', '#3742fa']

bars1 = ax1.bar(issue_types, issue_counts, color=colors1, edgecolor='white', linewidth=2)
ax1.set_title('问题类型分布 TOP6', fontsize=16, fontweight='bold', pad=15)
ax1.set_ylabel('问题数量', fontsize=12)
ax1.tick_params(axis='x', rotation=15)

# 在柱子上添加数值标签
for bar, count in zip(bars1, issue_counts):
    ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 200,
            f'{count:,}', ha='center', va='bottom', fontsize=10, fontweight='bold')

ax1.grid(axis='y', alpha=0.3, linestyle='--')
ax1.set_facecolor('#fafafa')

# ============ 图 2: 工厂排名 ============
ax2 = plt.subplot(2, 3, 2)
factories = ['爱探索', '浩迅', '三米', '丰庆', '乙超', '元合']
factory_counts = [2500, 2200, 1800, 1500, 1400, 1200]
colors2 = ['#ff4757', '#ff6b81', '#ff7f50', '#ffa502', '#ffd32a', '#ffdd59']

bars2 = ax2.barh(factories, factory_counts, color=colors2, edgecolor='white', linewidth=2)
ax2.set_title('工厂问题排名 TOP6', fontsize=16, fontweight='bold', pad=15)
ax2.set_xlabel('问题数量', fontsize=12)
ax2.invert_yaxis()

# 在柱子上添加数值标签
for bar, count in zip(bars2, factory_counts):
    ax2.text(bar.get_width() + 50, bar.get_y() + bar.get_height()/2,
            f'{count:,}', ha='left', va='center', fontsize=10, fontweight='bold')

ax2.grid(axis='x', alpha=0.3, linestyle='--')
ax2.set_facecolor('#fafafa')

# ============ 图 3: 平台分布 (饼图) ============
ax3 = plt.subplot(2, 3, 3)
platforms = ['天猫', '小店', '抖音']
platform_counts = [65000, 11000, 6500]
colors3 = ['#3742fa', '#1e90ff', '#70a1ff']

wedges, texts, autotexts = ax3.pie(platform_counts, labels=platforms, autopct='%1.1f%%',
                                    colors=colors3, startangle=90,
                                    explode=(0.05, 0, 0))
ax3.set_title('销售平台分布', fontsize=16, fontweight='bold', pad=15)

# 设置饼图文字
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontsize(11)
    autotext.set_fontweight('bold')

ax3.set_facecolor('#fafafa')

# ============ 图 4: 成本分析 ============
ax4 = plt.subplot(2, 3, 4)
cost_categories = ['当前周期\n(68 天)', '月度推算', '年度推算']
cost_values = [60, 26, 320]  # 万
colors4 = ['#ff4757', '#ffa502', '#2ed573']

bars4 = ax4.bar(cost_categories, cost_values, color=colors4, edgecolor='white', linewidth=2)
ax4.set_title('补偿成本分析 (万元)', fontsize=16, fontweight='bold', pad=15)
ax4.set_ylabel('金额 (万元)', fontsize=12)

# 在柱子上添加数值标签
for bar, value in zip(bars4, cost_values):
    ax4.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 5,
            f'¥{value}万', ha='center', va='bottom', fontsize=11, fontweight='bold')

ax4.grid(axis='y', alpha=0.3, linestyle='--')
ax4.set_facecolor('#fafafa')

# ============ 图 5: 投资回报分析 ============
ax5 = plt.subplot(2, 3, 5)
roi_categories = ['投资总额', '年度节约', '回收期']
roi_values = [360, 224, 19]  # 万/月
colors5 = ['#ff4757', '#2ed573', '#ffa502']

bars5 = ax5.bar(roi_categories, roi_values, color=colors5, edgecolor='white', linewidth=2)
ax5.set_title('投资回报分析', fontsize=16, fontweight='bold', pad=15)
ax5.set_ylabel('金额 (万元) / 月数', fontsize=12)

# 在柱子上添加数值标签
for bar, value in zip(bars5, roi_values):
    label = f'¥{value}万' if value != 19 else f'{value}个月'
    ax5.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 10,
            label, ha='center', va='bottom', fontsize=11, fontweight='bold')

ax5.grid(axis='y', alpha=0.3, linestyle='--')
ax5.set_facecolor('#fafafa')

# ============ 图 6: 改善效果预测 ============
ax6 = plt.subplot(2, 3, 6)
timeline = ['当前', '3 个月', '6 个月', '12 个月']
improvement = [100, 70, 50, 30]  # 问题率剩余百分比
colors6 = ['#ff4757', '#ffa502', '#2ed573', '#2ed573']

ax6.plot(timeline, improvement, marker='o', linewidth=3, markersize=10, color='#3742fa')
ax6.fill_between(timeline, improvement, alpha=0.3, color='#3742fa')
ax6.set_title('问题率改善预测', fontsize=16, fontweight='bold', pad=15)
ax6.set_ylabel('问题率 (%)', fontsize=12)
ax6.set_ylim(0, 110)
ax6.grid(alpha=0.3, linestyle='--')

# 在点上添加数值标签
for i, (t, v) in enumerate(zip(timeline, improvement)):
    ax6.text(i, v + 5, f'{v}%', ha='center', va='bottom', fontsize=11, fontweight='bold')

ax6.set_facecolor('#fafafa')

# ============ 总标题 ============
fig.suptitle('服装售后 QC 质量控制系统 - 数据分析报告', 
             fontsize=20, fontweight='bold', y=0.98, color='#2f3542')

# 添加副标题
subtitle = f'数据基础：82,500 条真实售后数据 | 生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M")}'
fig.text(0.5, 0.95, subtitle, ha='center', fontsize=11, style='italic', color='#57606f')

plt.tight_layout(rect=[0, 0.03, 1, 0.93])

# 保存图片
output_path = os.path.join(OUTPUT_DIR, f'QC 项目数据分析_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='#f5f6f8')
print(f"[OK] 图表已保存：{output_path}")

plt.close()

print(f"\n[OK] 图表生成完成！")
print(f"图片尺寸：20x16 英寸")
print(f"分辨率：150 DPI")
