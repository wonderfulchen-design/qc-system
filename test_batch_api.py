#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
波次工厂商品编码关系 API 测试脚本
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

# 测试数据
TEST_BATCHES = [
    {"batch_no": f"TEST{datetime.now().strftime('%Y%m%d%H%M%S')}001", "factory_name": "广州制衣厂", "goods_no": "SKU123456"},
    {"batch_no": f"TEST{datetime.now().strftime('%Y%m%d%H%M%S')}002", "factory_name": "深圳制衣厂", "goods_no": "SKU123457"},
    {"batch_no": f"TEST{datetime.now().strftime('%Y%m%d%H%M%S')}003", "factory_name": "杭州服装厂", "goods_no": "SKU123458"},
]

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def success_msg(msg):
    print(f"[OK] {msg}")

def error_msg(msg):
    print(f"[ERROR] {msg}")

def test_login():
    """测试登录获取 token"""
    print_section("1. 测试登录")
    
    try:
        # 尝试默认账号
        response = requests.post(f"{BASE_URL}/token", data={
            "username": "admin",
            "password": "admin123"
        })
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            success_msg("登录成功！")
            print(f"Token: {token[:50]}...")
            return token
        else:
            error_msg(f"登录失败：{response.status_code}")
            print(f"响应：{response.text}")
            return None
    except Exception as e:
        error_msg(f"请求失败：{e}")
        print(f"提示：请确保后端服务已启动 (uvicorn main:app --reload)")
        return None

def test_create_batch(token, batch_data):
    """测试创建波次关系"""
    print_section("2. 测试创建波次关系")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(f"{BASE_URL}/api/batches", json=batch_data, headers=headers)
        print(f"状态码：{response.status_code}")
        print(f"请求数据：{json.dumps(batch_data, ensure_ascii=False)}")
        print(f"响应数据：{json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        
        if response.status_code == 200:
            success_msg("创建成功！")
            return response.json()
        else:
            error_msg("创建失败")
            return None
    except Exception as e:
        error_msg(f"请求失败：{e}")
        return None

def test_list_batches(token, filters=None):
    """测试分页查询"""
    print_section("3. 测试分页查询")
    
    headers = {"Authorization": f"Bearer {token}"}
    params = {"page": 1, "page_size": 10}
    if filters:
        params.update(filters)
    
    try:
        response = requests.get(f"{BASE_URL}/api/batches/list", params=params, headers=headers)
        print(f"状态码：{response.status_code}")
        print(f"查询参数：{params}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"总数：{data['total']}")
            print(f"当前页：{data['page']}/{data['page_size']}")
            print(f"返回数据：")
            for item in data['data'][:5]:  # 只显示前 5 条
                print(f"  - {item['batch_no']} | {item['factory_name']} | {item['goods_no']}")
            success_msg("查询成功！")
            return data
        else:
            error_msg("查询失败")
            return None
    except Exception as e:
        error_msg(f"请求失败：{e}")
        return None

def test_update_batch(token, batch_no, update_data):
    """测试更新波次关系"""
    print_section("4. 测试更新波次关系")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.put(f"{BASE_URL}/api/batches/{batch_no}", json=update_data, headers=headers)
        print(f"状态码：{response.status_code}")
        print(f"波次号：{batch_no}")
        print(f"更新数据：{json.dumps(update_data, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print(f"响应数据：{json.dumps(response.json(), ensure_ascii=False, indent=2)}")
            success_msg("更新成功！")
            return response.json()
        else:
            error_msg(f"更新失败：{response.text}")
            return None
    except Exception as e:
        error_msg(f"请求失败：{e}")
        return None

def test_batch_import(token, batches):
    """测试批量导入"""
    print_section("5. 测试批量导入")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(f"{BASE_URL}/api/batches/batch", json=batches, headers=headers)
        print(f"状态码：{response.status_code}")
        print(f"导入数量：{len(batches)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"成功：{result['success_count']}")
            print(f"失败：{result['error_count']}")
            if result['errors']:
                print(f"错误详情：{result['errors']}")
            success_msg("批量导入成功！")
            return result
        else:
            error_msg(f"批量导入失败：{response.text}")
            return None
    except Exception as e:
        error_msg(f"请求失败：{e}")
        return None

def test_delete_batch(token, batch_no):
    """测试删除"""
    print_section("6. 测试删除")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.delete(f"{BASE_URL}/api/batches/{batch_no}", headers=headers)
        print(f"状态码：{response.status_code}")
        print(f"波次号：{batch_no}")
        
        if response.status_code == 200:
            print(f"响应数据：{json.dumps(response.json(), ensure_ascii=False, indent=2)}")
            success_msg("删除成功！")
            return True
        else:
            error_msg(f"删除失败：{response.text}")
            return False
    except Exception as e:
        error_msg(f"请求失败：{e}")
        return False

def test_search(token, batch_no=None, goods_no=None):
    """测试快速查询"""
    print_section("7. 测试快速查询")
    
    headers = {"Authorization": f"Bearer {token}"}
    params = {}
    if batch_no:
        params['batch_no'] = batch_no
    if goods_no:
        params['goods_no'] = goods_no
    
    try:
        response = requests.get(f"{BASE_URL}/api/batches/search", params=params, headers=headers)
        print(f"状态码：{response.status_code}")
        print(f"查询参数：{params}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"返回数量：{len(data)}")
            for item in data[:5]:
                print(f"  - {item['batch_no']} | {item['factory_name']} | {item['goods_no']}")
            success_msg("查询成功！")
            return data
        else:
            error_msg(f"查询失败：{response.text}")
            return None
    except Exception as e:
        error_msg(f"请求失败：{e}")
        return None

def main():
    print(f"\n{'#'*60}")
    print(f"#  波次工厂商品编码关系 API 测试")
    print(f"#  目标地址：{BASE_URL}")
    print(f"{'#'*60}")
    
    # 1. 登录
    token = test_login()
    if not token:
        print("\n测试终止：无法获取 token")
        return
    
    # 2. 创建单个波次
    test_batch = TEST_BATCHES[0].copy()
    created = test_create_batch(token, test_batch)
    if created:
        test_batch_no = created['batch_no']
    else:
        # 如果创建失败，使用一个测试波次号
        test_batch_no = f"TEST{datetime.now().strftime('%Y%m%d%H%M%S')}999"
        print(f"\n使用测试波次号：{test_batch_no}")
    
    # 3. 分页查询
    test_list_batches(token)
    
    # 4. 更新
    test_update_batch(token, test_batch_no, {"factory_name": "更新的工厂名称"})
    
    # 5. 批量导入
    test_batch_import(token, TEST_BATCHES[1:])
    
    # 6. 快速查询
    test_search(token, batch_no="TEST")
    
    # 7. 再次查询列表
    test_list_batches(token, {"batch_no": "TEST"})
    
    # 8. 删除测试数据
    print_section("8. 清理测试数据")
    for batch in TEST_BATCHES:
        test_delete_batch(token, batch['batch_no'])
    
    print_section("测试完成")
    success_msg("所有接口测试结束！")

if __name__ == "__main__":
    main()
