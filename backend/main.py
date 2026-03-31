#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QC Quality Management System - Backend API
All error messages in English to avoid encoding issues
"""

# MySQL 兼容层 - 使用 PyMySQL 替代 MySQLdb
import pymysql
import uuid
pymysql.install_as_MySQLdb()

from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Form, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum
import jwt
import hashlib
import os
import json
import httpx
import urllib.parse
from pathlib import Path

# Database
from sqlalchemy import create_engine, Column, Integer, String, DateTime, DECIMAL, Text, ForeignKey, JSON, Boolean, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.sql import func

# Config
from dotenv import load_dotenv
load_dotenv()

# WeChat OAuth2
from backend.wechat_auth import get_wechat_oauth2_url, get_user_info, get_user_detail

# ==================== Configuration ====================

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://qc_user:QcUser2025@localhost:3306/qc_system")
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "qc-system-super-secret-jwt-key-2025")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS", "1"))

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "/app/uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# 七牛云配置
QINIU_ACCESS_KEY = os.getenv("QINIU_ACCESS_KEY", "")
QINIU_SECRET_KEY = os.getenv("QINIU_SECRET_KEY", "")
QINIU_BUCKET = os.getenv("QINIU_BUCKET", "lswsampleimg")
QINIU_DOMAIN = os.getenv("QINIU_DOMAIN", "https://lswsampleimg.qiniudn.com").rstrip("/") + "/"
QINIU_PREFIX = os.getenv("QINIU_PREFIX", "qcImg/")

# 企业微信配置
WECHAT_CORP_ID = os.getenv("WECHAT_CORP_ID", "")
WECHAT_AGENT_ID = os.getenv("WECHAT_AGENT_ID", "")
WECHAT_SECRET = os.getenv("WECHAT_SECRET", "")
WECHAT_REDIRECT_URI = os.getenv("WECHAT_REDIRECT_URI", "")
WECHAT_WEBHOOK_URL = os.getenv("WECHAT_WEBHOOK_URL", "")

# 图片上传限制
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_IMAGE_WIDTH = 4096  # 最大宽度
MAX_IMAGE_HEIGHT = 4096  # 最大高度
ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']

# ==================== Database Models ====================

# 数据库连接池配置 - 防止 "MySQL server has gone away" 错误
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,        # 连接前检查是否有效
    pool_recycle=3600,         # 1 小时后回收连接
    pool_size=10,              # 连接池大小
    max_overflow=20,           # 最大溢出连接数
    pool_timeout=30            # 获取连接超时
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class QCUser(Base):
    __tablename__ = "qc_users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(32), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    real_name = Column(String(32))
    nickname = Column(String(32))  # 昵称，用于评论显示
    phone = Column(String(16))
    email = Column(String(64))
    department = Column(String(32), index=True)
    role = Column(String(16), default="qc")
    status = Column(Integer, default=1)
    avatar_url = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class ProductBatch(Base):
    __tablename__ = "product_batches"
    
    id = Column(Integer, primary_key=True, index=True)
    batch_no = Column(String(32), unique=True, index=True)
    factory_name = Column(String(64), index=True)
    goods_no = Column(String(32), index=True)
    merchandiser = Column(String(32))  # 订单跟单员
    designer = Column(String(32))  # 设计师


class QualityIssue(Base):
    __tablename__ = "quality_issues"
    
    id = Column(Integer, primary_key=True, index=True)
    issue_no = Column(String(32), unique=True, nullable=False)
    order_no = Column(String(64), index=True)
    goods_no = Column(String(32), index=True)
    platform = Column(String(16), index=True)
    buyer_wangwang = Column(String(64))
    issue_type = Column(String(32), index=True, nullable=False)
    issue_desc = Column(Text)
    solution_type = Column(String(32))
    compensation_amount = Column(DECIMAL(10, 2), default=0)
    factory_name = Column(String(64), index=True)
    batch_no = Column(String(32), index=True)
    pattern_batch = Column(String(32))
    merchandiser = Column(String(32))  # 订单跟单员
    designer = Column(String(32))
    handler = Column(String(32))
    batch_source = Column(String(32))
    status = Column(String(16), default="pending")
    qc_user_id = Column(Integer, nullable=True)
    qc_username = Column(String(32), nullable=True)
    product_image = Column(String(255))
    issue_images = Column(JSON)
    created_at = Column(DateTime, index=True, server_default=func.now())
    imported_at = Column(DateTime, server_default=func.now())


class QCInspection(Base):
    __tablename__ = "qc_inspections"
    
    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("quality_issues.id"), index=True)
    inspector_id = Column(Integer, ForeignKey("qc_users.id"), index=True)
    inspection_result = Column(String(16))
    inspection_notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class IssueComment(Base):
    __tablename__ = "issue_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("quality_issues.id"), index=True)
    user_id = Column(Integer, ForeignKey("qc_users.id"), index=True)
    username = Column(String(32))
    nickname = Column(String(32))
    content = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


# ==================== Pydantic Models ====================

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[str] = None
    username: Optional[str] = None
    role: Optional[str] = None


class UserCreate(BaseModel):
    username: str
    password: str
    real_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    department: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    real_name: Optional[str]
    nickname: Optional[str]
    department: Optional[str]
    role: str
    phone: Optional[str]
    email: Optional[str]
    avatar_url: Optional[str]
    
    model_config = ConfigDict(from_attributes=True)


class BatchCreate(BaseModel):
    batch_no: str
    factory_name: str
    goods_no: str
    merchandiser: Optional[str] = None
    designer: Optional[str] = None


class BatchResponse(BaseModel):
    batch_no: str
    factory_name: str
    goods_no: str
    merchandiser: Optional[str]
    designer: Optional[str]
    
    model_config = ConfigDict(from_attributes=True)


class BatchListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    data: List[BatchResponse]


class IssueCreate(BaseModel):
    goods_no: str
    factory_name: str
    batch_no: str
    issue_type: str
    issue_desc: Optional[str] = None
    solution_type: Optional[str] = None
    compensation_amount: Optional[float] = 0
    product_image: Optional[str] = None
    issue_images: Optional[List[str]] = None
    # QC 信息由后端自动填充，不需要前端传递


class IssueResponse(BaseModel):
    id: int
    issue_no: str
    goods_no: str
    factory_name: str
    batch_no: str
    issue_type: str
    issue_desc: Optional[str]
    solution_type: Optional[str]
    compensation_amount: float
    status: str
    qc_user_id: Optional[int]
    qc_username: Optional[str]
    product_image: Optional[str]
    issue_images: Optional[List[str]]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class CommentCreate(BaseModel):
    content: str


class CommentResponse(BaseModel):
    id: int
    issue_id: int
    user_id: int
    username: str
    nickname: Optional[str]
    content: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ==================== FastAPI App ====================

app = FastAPI(title="QC Management System")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Static Files ====================

# 挂载静态文件目录
app.mount("/qc-mobile", StaticFiles(directory="mobile", html=True), name="mobile")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR, html=True), name="uploads")


# ==================== Dependencies ====================

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token", auto_error=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> QCUser:
    """获取当前登录用户"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未授权",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="未授权",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未授权",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(QCUser).filter(QCUser.id == int(user_id)).first()
    if user is None or user.status != 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已禁用",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建 JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ==================== Root Redirect ====================

@app.get("/")
async def root_redirect():
    """根路径自动跳转到问题列表页"""
    return RedirectResponse(url="/qc-mobile/issue-list.html")


# ==================== WeChat OAuth2 Login ====================

@app.get("/auth/wechat/login")
async def wechat_login():
    """
    跳转到企业微信授权页面
    """
    import uuid
    redirect_uri = f"{WECHAT_REDIRECT_URI}/auth/wechat/callback"
    state = str(uuid.uuid4())  # 生成随机 state 防止 CSRF
    
    oauth_url = get_wechat_oauth2_url(redirect_uri, state)
    
    return RedirectResponse(url=oauth_url)


@app.get("/auth/wechat/callback")
async def wechat_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    """
    企业微信回调处理
    
    1. 用 code 换取用户信息
    2. 自动创建或更新用户
    3. 登录并跳转回首页
    """
    try:
        # 1. 获取用户信息
        user_info = await get_user_info(code)
        wechat_userid = user_info.get('userid')
        
        if not wechat_userid:
            return JSONResponse(
                status_code=400,
                content={"detail": "获取用户信息失败"}
            )
        
        # 2. 尝试获取详细信息（需要读取权限）
        try:
            detail_info = await get_user_detail(wechat_userid)
            user_name = detail_info.get('name', wechat_userid)
            user_department = detail_info.get('department', [])
            user_mobile = detail_info.get('mobile', '')
            user_email = detail_info.get('email', '')
        except Exception as e:
            # 如果没有权限，只用基本信息
            print(f"获取用户详情失败：{e}")
            user_name = wechat_userid
            user_department = []
            user_mobile = ''
            user_email = ''
        
        # 3. 查找或创建用户
        user = db.query(QCUser).filter(QCUser.username == wechat_userid).first()
        
        if not user:
            # 创建新用户
            random_password = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
            
            # 优先使用中文名作为昵称，如果获取失败则用 userid
            display_name = user_name if user_name != wechat_userid else wechat_userid
            
            user = QCUser(
                username=wechat_userid,
                password_hash=random_password,  # 随机密码，实际用企业微信登录
                real_name=user_name,
                nickname=display_name,  # 使用中文名作为昵称
                department=str(user_department[0]) if user_department else '',
                phone=user_mobile,
                email=user_email,
                role='qc',
                status=1,
                avatar_url=detail_info.get('avatar', '') if 'detail_info' in locals() else ''
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # 更新用户信息 - 只更新 real_name，不覆盖 nickname（除非 nickname 还是 userid）
            user.real_name = user_name
            # 如果当前昵称等于 userid（英文），则更新为中文名
            if user.nickname == wechat_userid:
                user.nickname = user_name
            if user_department:
                user.department = str(user_department[0])
            if user_mobile:
                user.phone = user_mobile
            if user_email:
                user.email = user_email
            db.commit()
        
        # 4. 生成登录 token
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username, "role": user.role},
            expires_delta=timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
        )
        
        # 5. 跳转到登录成功页面（带上 token）
        redirect_url = f"{WECHAT_REDIRECT_URI}/qc-mobile/index.html?token={access_token}&wechat_login=1"
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"登录失败：{e}")
        print(f"错误堆栈：{error_trace}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"登录失败：{str(e)}"}
        )
