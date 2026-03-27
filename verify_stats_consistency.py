#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统计图表数据一致性验证 - 对比前端图表数据与数据库实际数据
"""

import requests
import json
from datetime import datetime, timedelta
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
import sys
import os

# ==================== Configuration ====================

API_BASE = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "admin123"
DATABASE_URL = "mysql+pymysql://qc_user:QcUser2025@localhost:3306/qc_system"

# ==================== Database Models ====================

from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, Text, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class QualityIssue(Base):
    __tablename__ = "quality_issues"
    
    id = Column(Integer, primary_key=True, index=True)
    issue_no = Column(String(32), unique=True, nullable=False)
    goods_no = Column(String(32), index=True)
    platform = Column(String(16), index=True)
    issue_type = Column(String(32), index=True, nullable=False)
    issue_desc = Column(Text)
    solution_type = Column(String(32))
    compensation_amount = Column(DECIMAL(10, 2), default=0)
    factory_name = Column(String(64), index=True)
    batch_no = Column(String(32), index=True)
    status = Column(String(16), default="pending")
    qc_user_id = Column(Integer, nullable=True)
    qc_username = Column(String(32), nullable=True)
    product_image = Column(String(255))
    issue_images = Column(JSON)
    created_at = Column(DateTime, index=True)
    imported_at = Column(DateTime)


# ==================== Helper Functions ====================

def login():
    """登录获取 token"""
    try:
        r = requests.post(f"{API_BASE}/token", 
                         data={'username': USERNAME, 'password': PASSWORD},
                         timeout=10)
        if r.status_code == 200:
            return r.json()['access_token']
        return None
    except:
        return None

def get_db_session():
    """获取数据库会话"""
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    return Session()

def get_stats_from_db():
    """从数据库直接获取统计数据"""
    db = get_db_session()
    
    stats = {}
    
    # 1. 总数
    stats['total_count'] = db.query(QualityIssue).count()
    
    # 2. 总补偿金额
    total_comp = db.query(func.sum(QualityIssue.compensation_amount)).scalar() or 0
    stats['total_compensation'] = float(total_comp)
    
    # 3. 工厂数量
    factory_count = db.query(func.count(func.distinct(QualityIssue.factory_name))).scalar() or 0
    stats['factory_count'] = factory_count
    
    # 4. 按工厂统计
    factory_stats = db.query(
        QualityIssue.factory_name,
        func.count(QualityIssue.id).label('count')
    ).group_by(QualityIssue.factory_name).order_by(func.count(QualityIssue.id).desc()).all()
    
    stats['by_factory'] = [
        {'factory': f[0], 'count': f[1]} 
        for f in factory_stats[:10]  # TOP 10
    ]
    
    # 5. 按问题类型统计
    type_stats = db.query(
        QualityIssue.issue_type,
        func.count(QualityIssue.id).label('count')
    ).group_by(QualityIssue.issue_type).order_by(func.count(QualityIssue.id).desc()).all()
    
    stats['by_type'] = [
        {'type': t[0], 'count': t[1]} 
        for t in type_stats
    ]
    
    # 6. 按平台统计
    platform_stats = db.query(
        QualityIssue.platform,
        func.count(QualityIssue.id).label('count')
    ).group_by(QualityIssue.platform).order_by(func.count(QualityIssue.id).desc()).all()
    
    stats['by_platform'] = [
        {'platform': p[0], 'count': p[1]} 
        for p in platform_stats
    ]
    
    # 7. 按状态统计
    status_stats = db.query(
        QualityIssue.status,
        func.count(QualityIssue.id).label('count')
    ).group_by(QualityIssue.status).all()
    
    stats['by_status'] = [
        {'status': s[0], 'count': s[1]} 
        for s in status_stats
    ]
    
    # 8. 解决率
    solved_count = db.query(QualityIssue).filter(
        QualityIssue.status.in_(['solved', 'completed', '已解决'])
    ).count()
    
    stats['solve_rate'] = (solved_count / stats['total_count'] * 100) if stats['total_count'] > 0 else 0
    
    # 9. 按月份统计 (近 12 个月)
    from sqlalchemy import extract
    
    monthly_stats = db.query(
        extract('year', QualityIssue.created_at).label('year'),
        extract('month', QualityIssue.created_at).label('month'),
        func.count(QualityIssue.id).label('count')
    ).filter(
        QualityIssue.created_at >= datetime.now() - timedelta(days=365)
    ).group_by(
        extract('year', QualityIssue.created_at),
        extract('month', QualityIssue.created_at)
    ).order_by(
        extract('year', QualityIssue.created_at),
        extract('month', QualityIssue.created_at)
    ).all()
    
    stats['monthly'] = [
        {'year': int(m[0]), 'month': int(m[1]), 'count': m[2]} 
        for m in monthly_stats
    ]
    
    db.close()
    return stats

def get_stats_from_api(token):
    """从 API 获取统计数据"""
    headers = {'Authorization': f'Bearer {token}'}
    
    stats = {}
    
    # 获取问题列表 (用于计算总数等)
    r = requests.get(f"{API_BASE}/api/issues", headers=headers, 
                     params={'page': 1, 'page_size': 1})
    if r.status_code == 200:
        data = r.json()
        stats['api_total'] = data.get('total', 0)
    else:
        stats['api_total'] = 0
    
    # 获取较大样本用于统计
    r = requests.get(f"{API_BASE}/api/issues", headers=headers,
                     params={'page': 1, 'page_size': 100})
    
    if r.status_code == 200:
        data = r.json()
        issues = data.get('data', [])
        
        # 工厂统计
        factory_count = {}
        for issue in issues:
            factory = issue.get('factory_name', 'Unknown')
            factory_count[factory] = factory_count.get(factory, 0) + 1
        
        stats['api_factory_stats'] = dict(sorted(factory_count.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # 类型统计
        type_count = {}
        for issue in issues:
            issue_type = issue.get('issue_type', 'Unknown')
            type_count[issue_type] = type_count.get(issue_type, 0) + 1
        
        stats['api_type_stats'] = dict(sorted(type_count.items(), key=lambda x: x[1], reverse=True))
    else:
        stats['api_factory_stats'] = {}
        stats['api_type_stats'] = {}
    
    return stats

def compare_stats(db_stats, api_stats):
    """对比数据库和 API 数据"""
    print("\n" + "=" * 80)
    print("数据一致性对比")
    print("=" * 80)
    
    issues = []
    
    # 对比总数
    print(f"\n[1] 总数据量:")
    print(f"    数据库：{db_stats['total_count']} 条")
    print(f"    API:     {api_stats.get('api_total', 'N/A')} 条")
    
    if db_stats['total_count'] != api_stats.get('api_total', 0):
        issues.append(f"总数不匹配：DB={db_stats['total_count']}, API={api_stats.get('api_total')}")
        print(f"    [WARN] 不匹配！")
    else:
        print(f"    [OK] 一致")
    
    # 对比工厂统计 (基于 API 返回的样本)
    print(f"\n[2] 工厂统计 (基于 100 条样本):")
    api_factory = api_stats.get('api_factory_stats', {})
    db_factory_sample = {f['factory']: f['count'] for f in db_stats['by_factory'][:10]}
    
    # 只对比 API 样本中存在的工厂
    for factory, api_count in api_factory.items():
        db_count = db_factory_sample.get(factory, 0)
        match = "[OK]" if api_count == db_count else "[DIFF]"
        print(f"    {factory}: API={api_count}, DB={db_count} {match}")
        if api_count != db_count:
            issues.append(f"工厂'{factory}'数量不匹配：API={api_count}, DB={db_count}")
    
    # 对比类型统计
    print(f"\n[3] 问题类型统计 (基于 100 条样本):")
    api_type = api_stats.get('api_type_stats', {})
    db_type_sample = {t['type']: t['count'] for t in db_stats['by_type']}
    
    for issue_type, api_count in api_type.items():
        db_count = db_type_sample.get(issue_type, 0)
        match = "[OK]" if api_count == db_count else "[DIFF]"
        print(f"    {issue_type}: API={api_count}, DB={db_count} {match}")
        if api_count != db_count:
            issues.append(f"类型'{issue_type}'数量不匹配：API={api_count}, DB={db_count}")
    
    # 数据库统计摘要
    print(f"\n[4] 数据库完整统计:")
    print(f"    总问题数：{db_stats['total_count']}")
    print(f"    总补偿金额：RMB {db_stats['total_compensation']:,.2f}")
    print(f"    涉及工厂数：{db_stats['factory_count']}")
    print(f"    解决率：{db_stats['solve_rate']:.1f}%")
    
    print(f"\n[5] TOP5 工厂 (数据库):")
    medals = ["[1st]", "[2nd]", "[3rd]", "[4th]", "[5th]"]
    for i, f in enumerate(db_stats['by_factory'][:5], 1):
        medal = medals[i-1]
        print(f"    {medal} {f['factory']}: {f['count']} 条")
    
    print(f"\n[6] 问题类型分布 (数据库):")
    for t in db_stats['by_type'][:5]:
        pct = t['count'] / db_stats['total_count'] * 100 if db_stats['total_count'] > 0 else 0
        print(f"    {t['type']}: {t['count']} 条 ({pct:.1f}%)")
    
    # 总结
    print("\n" + "=" * 80)
    if issues:
        print(f"[WARN] 发现 {len(issues)} 个不一致:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("[OK] 所有数据一致！")
    print("=" * 80)
    
    return issues

def main():
    """主函数"""
    print("=" * 80)
    print("QC SYSTEM - 统计图表数据一致性验证")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # 登录
    print("\n[1/3] 登录 API...")
    token = login()
    if not token:
        print("[ERROR] 登录失败，请确保后端服务运行中")
        return
    
    print("[OK] 登录成功")
    
    # 获取数据库统计
    print("\n[2/3] 从数据库获取统计数据...")
    try:
        db_stats = get_stats_from_db()
        print(f"[OK] 获取完成 (共 {db_stats['total_count']} 条数据)")
    except Exception as e:
        print(f"[ERROR] 数据库查询失败：{e}")
        return
    
    # 获取 API 统计
    print("\n[3/3] 从 API 获取统计数据...")
    api_stats = get_stats_from_api(token)
    print("[OK] 获取完成")
    
    # 对比
    issues = compare_stats(db_stats, api_stats)
    
    # 保存报告
    report = {
        'timestamp': datetime.now().isoformat(),
        'db_stats': {
            'total_count': db_stats['total_count'],
            'total_compensation': db_stats['total_compensation'],
            'factory_count': db_stats['factory_count'],
            'solve_rate': db_stats['solve_rate'],
            'by_factory': db_stats['by_factory'],
            'by_type': db_stats['by_type'],
            'by_platform': db_stats['by_platform']
        },
        'api_stats': api_stats,
        'issues': issues
    }
    
    report_file = f'stats_verification_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n[SAVE] 详细报告已保存：{report_file}")
    
    return len(issues)

if __name__ == "__main__":
    try:
        issue_count = main()
        sys.exit(0 if issue_count == 0 else 1)
    except KeyboardInterrupt:
        print("\n\n[INFO] 验证被中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] 验证异常：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
