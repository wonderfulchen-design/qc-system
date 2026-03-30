#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企业微信 OAuth2 登录模块
"""

import httpx
import os
from dotenv import load_dotenv

load_dotenv()

# 企业微信配置
WECHAT_CORP_ID = os.getenv("WECHAT_CORP_ID", "")
WECHAT_AGENT_ID = os.getenv("WECHAT_AGENT_ID", "")
WECHAT_SECRET = os.getenv("WECHAT_SECRET", "")
WECHAT_REDIRECT_URI = os.getenv("WECHAT_REDIRECT_URI", "")

# 企业微信 OAuth2 地址
WECHAT_OAUTH2_URL = "https://open.weixin.qq.com/connect/oauth2/authorize"
WECHAT_TOKEN_URL = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
WECHAT_USERINFO_URL = "https://qyapi.weixin.qq.com/cgi-bin/user/getuserinfo"


def get_wechat_oauth2_url(redirect_uri: str, state: str = "") -> str:
    """
    获取企业微信 OAuth2 授权 URL
    
    Args:
        redirect_uri: 回调地址（需要 URL 编码）
        state: 状态参数，用于防止 CSRF 攻击
    
    Returns:
        授权 URL
    """
    import urllib.parse
    
    params = {
        'appid': WECHAT_CORP_ID,
        'redirect_uri': urllib.parse.quote(redirect_uri, safe=''),
        'response_type': 'code',
        'scope': 'snsapi_privateinfo',
        'state': state,
        'agentid': WECHAT_AGENT_ID
    }
    
    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    return f"{WECHAT_OAUTH2_URL}?{query_string}#wechat_redirect"


async def get_access_token() -> str:
    """
    获取企业微信 access_token
    
    Returns:
        access_token 字符串
    
    Raises:
        Exception: 获取失败时抛出异常
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            WECHAT_TOKEN_URL,
            params={
                'corpid': WECHAT_CORP_ID,
                'corpsecret': WECHAT_SECRET
            },
            timeout=10.0
        )
        
        result = response.json()
        
        if result.get('errcode') == 0:
            return result['access_token']
        else:
            raise Exception(f"获取 access_token 失败：{result.get('errmsg')}")


async def get_user_info(code: str) -> dict:
    """
    用 code 换取用户信息
    
    Args:
        code: 授权码
    
    Returns:
        用户信息字典，包含 UserId, DeviceId, user_ticket 等
    
    Raises:
        Exception: 获取失败时抛出异常
    """
    access_token = await get_access_token()
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            WECHAT_USERINFO_URL,
            params={
                'access_token': access_token,
                'code': code
            },
            timeout=10.0
        )
        
        result = response.json()
        
        if result.get('errcode') == 0:
            # 如果是 snsapi_base 模式，只返回 UserId 和 DeviceId
            return {
                'userid': result.get('UserId'),
                'deviceid': result.get('DeviceId'),
                'user_ticket': result.get('user_ticket'),
                'expires_in': result.get('expires_in')
            }
        else:
            raise Exception(f"获取用户信息失败：{result.get('errmsg')}")


async def get_user_detail(userid: str) -> dict:
    """
    获取用户详细信息（需要读取权限）
    
    Args:
        userid: 用户 ID
    
    Returns:
        用户详细信息字典
    """
    access_token = await get_access_token()
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://qyapi.weixin.qq.com/cgi-bin/user/get?access_token={access_token}",
            json={'userid': userid},
            timeout=10.0
        )
        
        result = response.json()
        
        if result.get('errcode') == 0:
            return {
                'userid': result.get('userid'),
                'name': result.get('name'),
                'department': result.get('department'),
                'position': result.get('position'),
                'mobile': result.get('mobile'),
                'email': result.get('email'),
                'avatar': result.get('avatar')
            }
        else:
            # 如果没有权限，至少返回 userid 和 name
            return {
                'userid': userid,
                'name': userid  # 默认用 userid 作为名字
            }


# 测试代码
if __name__ == "__main__":
    import asyncio
    
    async def test():
        # 测试获取 access_token
        try:
            token = await get_access_token()
            print(f"✅ Access Token: {token[:20]}...")
        except Exception as e:
            print(f"❌ 获取 token 失败：{e}")
        
        # 测试 OAuth2 URL 生成
        redirect_uri = f"{WECHAT_REDIRECT_URI}/auth/wechat/callback"
        oauth_url = get_wechat_oauth2_url(redirect_uri, "test123")
        print(f"\n✅ OAuth2 URL:\n{oauth_url}")
    
    asyncio.run(test())
