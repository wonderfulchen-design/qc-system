#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网页自动化测试 - 登录并提交问题录入
使用 Selenium 操作浏览器
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import random

# 配置
API_BASE = 'http://localhost:8000'
LOGIN_URL = 'http://localhost/qc-mobile/login.html'
ENTRY_URL = 'http://localhost/qc-mobile/issue-entry.html'
USERNAME = 'admin'
PASSWORD = 'admin123'

# 测试数据
BATCH_NUMBERS = ['F21139', 'F21140', 'F21141', 'F21142', 'F21143']
FACTORIES = ['三米', '春秋', '丰庆', '乙超', '元合', '爱探索', '浩迅']
GOODS_NO_LIST = [
    '23181802105', '23181802104', '24181802186', '23181802121',
    '23181813008', '23181813015', '23181813011', '23181813010',
    '23181802122', '23181802118'
]
ISSUE_TYPES = ['污渍', '扣子', '拉链', '掉色', '做工开线等', '破洞', '起球勾线掉毛', '色差']
SOLUTION_TYPES = ['返工', '拒收', '全检', '代卖', '报废']

def setup_driver():
    """配置 Chrome 浏览器"""
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    # chrome_options.add_argument('--headless')  # 无头模式（可选）
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    return driver

def login(driver):
    """登录系统"""
    print("📝 正在登录...")
    driver.get(LOGIN_URL)
    
    try:
        # 等待页面加载
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'username'))
        )
        
        # 输入用户名
        username_input = driver.find_element(By.NAME, 'username')
        username_input.clear()
        username_input.send_keys(USERNAME)
        
        # 输入密码
        password_input = driver.find_element(By.NAME, 'password')
        password_input.clear()
        password_input.send_keys(PASSWORD)
        
        # 点击登录按钮
        login_btn = driver.find_element(By.XPATH, '//button[@type="submit"]')
        login_btn.click()
        
        # 等待跳转
        time.sleep(2)
        
        # 检查是否登录成功
        if 'index.html' in driver.current_url or '首页' in driver.title:
            print("✅ 登录成功！")
            return True
        else:
            print("❌ 登录失败")
            return False
            
    except Exception as e:
        print(f"❌ 登录错误：{e}")
        return False

def submit_issue(driver, index):
    """提交单个问题"""
    print(f"\n📝 正在提交第 {index + 1} 条问题...")
    
    try:
        # 生成随机数据
        batch_no = random.choice(BATCH_NUMBERS)
        factory = random.choice(FACTORIES)
        goods_no = random.choice(GOODS_NO_LIST)
        issue_type = random.choice(ISSUE_TYPES)
        solution_type = random.choice(SOLUTION_TYPES)
        issue_desc = f"自动化测试问题 #{index + 1} - 这是通过 Selenium 自动生成的测试数据"
        
        # 填写表单
        print(f"   波次号：{batch_no}")
        print(f"   工厂：{factory}")
        print(f"   货品编码：{goods_no}")
        
        # 输入波次号
        batch_input = driver.find_element(By.ID, 'batchNo')
        batch_input.clear()
        batch_input.send_keys(batch_no)
        time.sleep(1)  # 等待联想提示
        
        # 等待自动填充
        time.sleep(1)
        
        # 选择问题类型
        print(f"   问题类型：{issue_type}")
        type_items = driver.find_elements(By.CLASS_NAME, 'type-item')
        for item in type_items:
            if issue_type in item.text:
                item.click()
                break
        
        # 输入问题描述
        desc_textarea = driver.find_element(By.ID, 'issueDesc')
        desc_textarea.clear()
        desc_textarea.send_keys(issue_desc)
        time.sleep(0.5)
        
        # 选择解决方式
        print(f"   解决方式：{solution_type}")
        solution_items = driver.find_elements(By.CLASS_NAME, 'solution-option')
        for item in solution_items:
            if solution_type in item.text:
                item.click()
                break
        
        # 点击提交按钮
        submit_btn = driver.find_element(By.CLASS_NAME, 'btn-submit')
        submit_btn.click()
        
        # 等待提交结果
        time.sleep(2)
        
        # 处理 alert
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            print(f"   提交结果：{alert_text}")
            alert.accept()
            time.sleep(1)
            
            if '成功' in alert_text:
                print(f"   ✅ 第 {index + 1} 条提交成功！")
                return True
            else:
                print(f"   ❌ 第 {index + 1} 条提交失败")
                return False
        except:
            print("   ⚠️ 未检测到提交结果提示")
            return False
            
    except Exception as e:
        print(f"   ❌ 提交错误：{e}")
        return False

def run_test(count=10):
    """运行测试"""
    print("="*70)
    print("🤖 网页自动化测试 - 问题录入")
    print("="*70)
    
    driver = setup_driver()
    
    try:
        # 登录
        if not login(driver):
            return
        
        # 跳转到问题录入页
        print("\n📝 跳转到问题录入页面...")
        driver.get(ENTRY_URL)
        time.sleep(2)
        
        # 批量提交
        success_count = 0
        fail_count = 0
        
        print(f"\n🚀 开始批量提交 {count} 条问题...")
        print("-"*70)
        
        for i in range(count):
            if submit_issue(driver, i):
                success_count += 1
            else:
                fail_count += 1
            
            # 等待一下
            time.sleep(1)
            
            # 更新进度
            progress = (i + 1) / count * 100
            print(f"\n进度：{progress:.0f}% ({i + 1}/{count})")
        
        # 统计结果
        print("\n" + "="*70)
        print("📊 测试结果")
        print("="*70)
        print(f"提交总数：{count}")
        print(f"成功：{success_count} 条 ({success_count/count*100:.1f}%)")
        print(f"失败：{fail_count} 条 ({fail_count/count*100:.1f}%)")
        print("="*70)
        
        if success_count == count:
            print("✅ 所有问题提交成功！")
        elif success_count > 0:
            print("⚠️ 部分问题提交成功")
        else:
            print("❌ 所有问题提交失败")
        
        # 保持浏览器打开
        input("\n按 Enter 键关闭浏览器...")
        
    except Exception as e:
        print(f"\n❌ 测试错误：{e}")
        input("\n按 Enter 键关闭浏览器...")
    finally:
        driver.quit()
        print("\n✅ 测试完成，浏览器已关闭")

if __name__ == '__main__':
    import sys
    
    count = 10
    if len(sys.argv) > 1:
        count = int(sys.argv[1])
    
    run_test(count)
