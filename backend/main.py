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
    inspection_no = Column(String(32), unique=True, nullable=False)
    qc_user_id = Column(Integer, ForeignKey("qc_users.id"), index=True)
    qc_user_name = Column(String(32))
    factory_name = Column(String(64), index=True)
    batch_no = Column(String(32), index=True)
    sku_no = Column(String(32))
    inspect_date = Column(DateTime, index=True)
    total_pieces = Column(Integer, default=0)
    passed_pieces = Column(Integer, default=0)
    failed_pieces = Column(Integer, default=0)
    pass_rate = Column(DECIMAL(5, 2), default=0)
    issues_found = Column(JSON)
    inspect_images = Column(JSON)
    status = Column(String(16), default="completed")
    created_at = Column(DateTime, server_default=func.now())


# ==================== Pydantic Models ====================

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    role: str


class UserResponse(BaseModel):
    id: int
    username: str
    real_name: Optional[str]
    nickname: Optional[str]
    department: Optional[str]
    role: str
    
    class Config:
        from_attributes = True


class IssueCreate(BaseModel):
    goods_no: str
    factory_name: str
    batch_no: str  # 波次号必填
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
    goods_no: Optional[str]
    factory_name: Optional[str]
    issue_type: str
    issue_desc: Optional[str]
    solution_type: Optional[str]
    compensation_amount: Optional[float]
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class BatchResponse(BaseModel):
    batch_no: str
    factory_name: str
    goods_no: str
    merchandiser: Optional[str] = None
    designer: Optional[str] = None


class BatchCreate(BaseModel):
    batch_no: str
    factory_name: str
    goods_no: str
    merchandiser: Optional[str] = None
    designer: Optional[str] = None


class BatchUpdate(BaseModel):
    factory_name: Optional[str] = None
    goods_no: Optional[str] = None


class BatchListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    data: List[BatchResponse]


# ==================== Utility Functions ====================

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> QCUser:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(QCUser).filter(QCUser.id == user_id, QCUser.status == 1).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# ==================== FastAPI App ====================

app = FastAPI(
    title="QC Quality Management System API",
    description="Quality Control Management Backend",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件挂载
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
app.mount("/qc-mobile", StaticFiles(directory="mobile", html=True), name="mobile")

# 企业微信验证文件需要放在根目录
# 单独挂载验证文件到根路径
from pathlib import Path
import os

@app.get("/WW_verify_bNelEDV6Mj48InFj.txt")
async def wechat_verification_file():
    """企业微信域名验证文件"""
    from fastapi.responses import PlainTextResponse
    verification_file = Path("mobile") / "WW_verify_bNelEDV6Mj48InFj.txt"
    if verification_file.exists():
        content = verification_file.read_text().strip()
        return PlainTextResponse(content, media_type="text/plain")
    else:
        return PlainTextResponse("bNelEDV6Mj48InFj", media_type="text/plain")

# 根路径重定向到问题列表页
@app.get("/")
async def root_redirect():
    """根路径自动跳转到问题列表页"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/qc-mobile/issue-list.html")


# ==================== Exception Handler ====================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理，确保返回 JSON 格式"""
    return JSONResponse(
        status_code=500,
        content={"detail": f"服务器错误：{str(exc)}"}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP 异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


# ==================== Auth Endpoints ====================

@app.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(QCUser).filter(QCUser.username == form_data.username).first()
    
    if not user or user.status != 1:
        raise HTTPException(status_code=401, detail="User not found or disabled")
    
    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect password")
    
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username, "role": user.role},
        expires_delta=timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    )
    
    return Token(
        access_token=access_token,
        user_id=user.id,
        username=user.username,
        role=user.role
    )


@app.get("/api/user/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: QCUser = Depends(get_current_user)
):
    return current_user


# ==================== WeChat OAuth2 Login ====================

@app.get("/auth/wechat/login")
async def wechat_login():
    """
    跳转到企业微信授权页面
    """
    import uuid
    redirect_uri = f"{WECHAT_REDIRECT_URI}/auth/wechat/callback"
    state = str(uuid.uuid4())  # 生成随机 state 防止 CSRF
    
    # 存储 state 到 session 或缓存（这里简化处理，实际应该存储）
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
    import traceback
    import logging
    
    try:
        logging.info(f"微信回调开始：code={code[:10]}..., state={state}")
        
        # 1. 获取用户信息
        logging.info("步骤 1: 获取用户信息...")
        user_info = await get_user_info(code)
        wechat_userid = user_info.get('userid')
        logging.info(f"获取到 userid: {wechat_userid}")
        
        if not wechat_userid:
            logging.error("获取 userid 失败")
            return JSONResponse(
                status_code=400,
                content={"detail": "获取用户信息失败"}
            )
        
        # 2. 尝试获取详细信息（需要读取权限）
        logging.info("步骤 2: 获取用户详情...")
        try:
            detail_info = await get_user_detail(wechat_userid)
            user_name = detail_info.get('name', wechat_userid)
            user_department = detail_info.get('department', [])
            user_mobile = detail_info.get('mobile', '')
            user_email = detail_info.get('email', '')
            logging.info(f"用户详情：name={user_name}, dept={user_department}")
        except Exception as e:
            logging.warning(f"获取用户详情失败：{e}")
            user_name = wechat_userid
            user_department = []
            user_mobile = ''
            user_email = ''
        
        # 3. 查找或创建用户
        logging.info("步骤 3: 查找或创建用户...")
        user = db.query(QCUser).filter(QCUser.username == wechat_userid).first()
        
        if not user:
            logging.info(f"创建新用户：{wechat_userid}")
            import hashlib
            random_password = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
            
            display_name = user_name if user_name != wechat_userid else wechat_userid
            
            user = QCUser(
                username=wechat_userid,
                password_hash=random_password,
                real_name=user_name,
                nickname=display_name,
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
            logging.info(f"用户创建成功：id={user.id}")
        else:
            logging.info(f"更新现有用户：{wechat_userid}")
            user.real_name = user_name
            if user.nickname == wechat_userid:
                user.nickname = user_name
            if user_department:
                user.department = str(user_department[0])
            if user_mobile:
                user.phone = user_mobile
            if user_email:
                user.email = user_email
            db.commit()
            logging.info("用户更新成功")
        
        # 4. 生成登录 token
        logging.info("步骤 4: 生成 token...")
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username, "role": user.role},
            expires_delta=timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
        )
        logging.info("token 生成成功")
        
        # 5. 跳转到登录成功页面
        logging.info("步骤 5: 跳转回首页...")
        redirect_url = f"{WECHAT_REDIRECT_URI}/qc-mobile/index.html?token={access_token}&wechat_login=1"
        logging.info(f"跳转 URL: {redirect_url[:50]}...")
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        error_trace = traceback.format_exc()
        logging.error(f"登录失败：{e}")
        logging.error(f"错误堆栈：{error_trace}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"登录失败：{str(e)}", "trace": error_trace}
        )


@app.post("/api/batches/import-csv")
async def import_batches_from_csv(
    file: UploadFile = File(...),
    current_user: QCUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """从 CSV 文件批量导入波次数据"""
    import pandas as pd
    import io
    
    try:
        # 读取 CSV 文件
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents), encoding='utf-8-sig')
        
        success_count = 0
        error_count = 0
        errors = []
        
        for idx, row in df.iterrows():
            try:
                batch_no = str(row.get('波次号', '')).strip()
                factory_name = str(row.get('工厂', '')).strip()
                goods_no = str(row.get('货品编码', '')).strip()
                merchandiser = str(row.get('订单跟单员', '')).strip() if pd.notna(row.get('订单跟单员')) else None
                designer = str(row.get('设计师', '')).strip() if pd.notna(row.get('设计师')) else None
                
                if not batch_no or not factory_name or not goods_no:
                    error_count += 1
                    errors.append({"row": idx + 1, "error": "缺少必填字段"})
                    continue
                
                # 检查是否已存在
                existing = db.query(ProductBatch).filter(
                    ProductBatch.batch_no == batch_no
                ).first()
                
                if existing:
                    existing.factory_name = factory_name
                    existing.goods_no = goods_no
                    existing.merchandiser = merchandiser
                    existing.designer = designer
                else:
                    new_batch = ProductBatch(
                        batch_no=batch_no,
                        factory_name=factory_name,
                        goods_no=goods_no,
                        merchandiser=merchandiser,
                        designer=designer
                    )
                    db.add(new_batch)
                
                success_count += 1
                
            except Exception as e:
                error_count += 1
                errors.append({"row": idx + 1, "error": str(e)})
        
        db.commit()
        
        return {
            "success": True,
            "message": f"导入完成！成功：{success_count}, 失败：{error_count}",
            "success_count": success_count,
            "error_count": error_count,
            "errors": errors[:10]
        }
        
    except Exception as e:
        db.rollback()
        return {"success": False, "message": f"导入失败：{str(e)}"}


@app.get("/api/init-db")
@app.post("/api/init-db")
async def initialize_database(
    db: Session = Depends(get_db)
):
    """初始化数据库 - 创建表和 admin 账号"""
    try:
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        
        # 检查是否已有 admin 账号
        admin = db.query(QCUser).filter(QCUser.username == "admin").first()
        
        if not admin:
            # 创建 admin 账号（密码：admin123）
            admin = QCUser(
                username="admin",
                password_hash=hash_password("admin123"),
                real_name="系统管理员",
                role="admin",
                status=1
            )
            db.add(admin)
            db.commit()
            
            return {
                "success": True,
                "message": "数据库初始化成功！admin 账号已创建。",
                "admin": {
                    "username": "admin",
                    "password": "admin123"
                }
            }
        else:
            return {
                "success": True,
                "message": "数据库已初始化，admin 账号已存在。"
            }
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": f"初始化失败：{str(e)}"
        }


@app.put("/api/user/nickname", response_model=UserResponse)
async def update_nickname(
    nickname_data: dict,
    current_user: QCUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新用户昵称"""
    nickname = nickname_data.get("nickname", "").strip()
    
    if not nickname:
        raise HTTPException(status_code=400, detail="昵称不能为空")
    
    if len(nickname) > 32:
        raise HTTPException(status_code=400, detail="昵称长度不能超过 32 个字符")
    
    current_user.nickname = nickname
    db.commit()
    db.refresh(current_user)
    
    return current_user


# ==================== Batch Query Endpoints ====================
# 注意：/api/batches/options 必须在 /api/batches/{batch_no} 之前定义

@app.get("/api/batches/options", response_model=Dict[str, List[str]])
async def get_batch_options(
    current_user: QCUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取所有唯一的工厂、设计师、波次号、跟单员选项"""
    # 查询所有波次数据
    batches = db.query(ProductBatch).all()
    
    # 提取唯一值
    factories = sorted(list(set([b.factory_name for b in batches if b.factory_name])))
    designers = sorted(list(set([b.designer for b in batches if b.designer])))
    merchandisers = sorted(list(set([b.merchandiser for b in batches if b.merchandiser])))
    batch_nos = sorted(list(set([b.batch_no for b in batches if b.batch_no])))
    
    return {
        "factories": factories,
        "designers": designers,
        "merchandisers": merchandisers,
        "batch_nos": batch_nos
    }


@app.get("/api/batches/search", response_model=List[BatchResponse])
async def search_batches(
    batch_no: Optional[str] = None,
    goods_no: Optional[str] = None,
    current_user: QCUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """搜索波次（添加缓存）"""
    if not batch_no and not goods_no:
        return []
    
    # 简单的内存缓存（生产环境建议用 Redis）
    cache_key = f"search:{batch_no}:{goods_no}"
    if hasattr(search_batches, 'cache') and cache_key in search_batches.cache:
        return search_batches.cache[cache_key]
    
    query = db.query(ProductBatch)
    
    if batch_no:
        query = query.filter(ProductBatch.batch_no.like(f"%{batch_no}%"))
    if goods_no:
        query = query.filter(ProductBatch.goods_no.like(f"%{goods_no}%"))
    
    # 限制返回数量，提高查询速度
    results = query.order_by(ProductBatch.id.desc()).limit(10).all()
    
    response_data = [
        {
            "batch_no": r.batch_no,
            "factory_name": r.factory_name,
            "goods_no": r.goods_no,
            "merchandiser": r.merchandiser,
            "designer": r.designer
        }
        for r in results
    ]
    
    # 缓存结果（最多保留 100 条）
    if not hasattr(search_batches, 'cache'):
        search_batches.cache = {}
    search_batches.cache[cache_key] = response_data
    if len(search_batches.cache) > 100:
        # 删除最旧的缓存
        oldest_key = next(iter(search_batches.cache))
        del search_batches.cache[oldest_key]
    
    return response_data


# ==================== Batch CRUD Endpoints ====================

@app.get("/api/batches/list", response_model=BatchListResponse)
async def list_batches(
    page: int = 1,
    page_size: int = 20,
    batch_no: Optional[str] = None,
    factory_name: Optional[str] = None,
    goods_no: Optional[str] = None,
    current_user: QCUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """分页查询波次工厂商品编码关系列表"""
    query = db.query(ProductBatch)
    
    if batch_no:
        query = query.filter(ProductBatch.batch_no.like(f"%{batch_no}%"))
    if factory_name:
        query = query.filter(ProductBatch.factory_name.like(f"%{factory_name}%"))
    if goods_no:
        query = query.filter(ProductBatch.goods_no.like(f"%{goods_no}%"))
    
    total = query.count()
    results = query.order_by(ProductBatch.id.desc())\
                   .offset((page - 1) * page_size)\
                   .limit(page_size)\
                   .all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "data": [
            {
                "batch_no": r.batch_no,
                "factory_name": r.factory_name,
                "goods_no": r.goods_no,
                "merchandiser": r.merchandiser,
                "designer": r.designer
            }
            for r in results
        ]
    }


@app.get("/api/batches/batch/test")
async def test_batch_endpoint(
    current_user: QCUser = Depends(get_current_user)
):
    """测试端点"""
    return {"message": "Batch API is working", "user": current_user.username}


@app.get("/api/batches/{batch_no}", response_model=BatchResponse)
async def get_batch_by_no(
    batch_no: str,
    current_user: QCUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """根据波次号查询单个波次信息（必须在所有具体路径之后）"""
    batch = db.query(ProductBatch).filter(
        ProductBatch.batch_no == batch_no
    ).first()
    
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    return {
        "batch_no": batch.batch_no,
        "factory_name": batch.factory_name,
        "goods_no": batch.goods_no,
        "merchandiser": batch.merchandiser,
        "designer": batch.designer
    }


@app.post("/api/batches/batch")
async def batch_import_batches(
    batches: List[BatchCreate],
    current_user: QCUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """批量导入/更新波次关系"""
    success_count = 0
    error_count = 0
    errors = []
    
    for idx, batch_data in enumerate(batches):
        try:
            existing = db.query(ProductBatch).filter(
                ProductBatch.batch_no == batch_data.batch_no
            ).first()
            
            if existing:
                existing.factory_name = batch_data.factory_name
                existing.goods_no = batch_data.goods_no
            else:
                new_batch = ProductBatch(
                    batch_no=batch_data.batch_no,
                    factory_name=batch_data.factory_name,
                    goods_no=batch_data.goods_no
                )
                db.add(new_batch)
            
            success_count += 1
        except Exception as e:
            error_count += 1
            errors.append({
                "index": idx,
                "batch_no": batch_data.batch_no,
                "error": str(e)
            })
    
    db.commit()
    
    return {
        "message": "Batch import completed",
        "success_count": success_count,
        "error_count": error_count,
        "errors": errors
    }


@app.post("/api/batches", response_model=BatchResponse)
async def create_or_update_batch(
    batch_data: BatchCreate,
    current_user: QCUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建或更新波次关系（波次号唯一，存在则更新）"""
    try:
        existing = db.query(ProductBatch).filter(
            ProductBatch.batch_no == batch_data.batch_no
        ).first()
        
        if existing:
            # 更新现有记录
            existing.factory_name = batch_data.factory_name
            existing.goods_no = batch_data.goods_no
            db.commit()
            db.refresh(existing)
            return BatchResponse(
                batch_no=existing.batch_no,
                factory_name=existing.factory_name,
                goods_no=existing.goods_no
            )
        else:
            # 创建新记录
            new_batch = ProductBatch(
                batch_no=batch_data.batch_no,
                factory_name=batch_data.factory_name,
                goods_no=batch_data.goods_no
            )
            db.add(new_batch)
            db.commit()
            db.refresh(new_batch)
            return BatchResponse(
                batch_no=new_batch.batch_no,
                factory_name=new_batch.factory_name,
                goods_no=new_batch.goods_no
            )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建失败：{str(e)}")


@app.put("/api/batches/{batch_no}", response_model=BatchResponse)
async def update_batch(
    batch_no: str,
    batch_data: BatchUpdate,
    current_user: QCUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新波次关系（部分更新）"""
    batch = db.query(ProductBatch).filter(
        ProductBatch.batch_no == batch_no
    ).first()
    
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    if batch_data.factory_name is not None:
        batch.factory_name = batch_data.factory_name
    if batch_data.goods_no is not None:
        batch.goods_no = batch_data.goods_no
    
    db.commit()
    db.refresh(batch)
    
    return BatchResponse(
        batch_no=batch.batch_no,
        factory_name=batch.factory_name,
        goods_no=batch.goods_no
    )


@app.delete("/api/batches/{batch_no}")
async def delete_batch(
    batch_no: str,
    current_user: QCUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除波次关系"""
    batch = db.query(ProductBatch).filter(
        ProductBatch.batch_no == batch_no
    ).first()
    
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    db.delete(batch)
    db.commit()
    
    return {"message": "Batch deleted successfully", "batch_no": batch_no}


# ==================== Issue Endpoints ====================

@app.get("/api/issues", response_model=Dict[str, Any])
async def get_issues(
    page: int = 1,
    page_size: int = 100,  # 增加到 100 用于前端筛选
    factory: Optional[str] = None,
    issue_type: Optional[str] = None,
    current_user: QCUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(QualityIssue)
    
    if factory:
        query = query.filter(QualityIssue.factory_name == factory)
    if issue_type:
        query = query.filter(QualityIssue.issue_type == issue_type)
    
    total = query.count()
    # 使用 ID 降序排序（ID 越大越新），确保排序稳定
    issues = query.order_by(QualityIssue.id.desc())\
                  .offset((page - 1) * page_size)\
                  .limit(page_size)\
                  .all()
    
    # 批量查询波次号对应的跟单员和设计师
    batch_nos = list(set([i.batch_no for i in issues if i.batch_no]))
    batch_info_map = {}
    if batch_nos:
        batch_infos = db.query(ProductBatch).filter(ProductBatch.batch_no.in_(batch_nos)).all()
        for bi in batch_infos:
            batch_info_map[bi.batch_no] = bi
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "data": [
            {
                "issue_no": i.issue_no,
                "goods_no": i.goods_no,
                "factory_name": i.factory_name,
                "batch_no": i.batch_no,
                "designer": i.designer or (batch_info_map.get(i.batch_no).designer if batch_info_map.get(i.batch_no) else None) or '-',
                "merchandiser": batch_info_map.get(i.batch_no).merchandiser if batch_info_map.get(i.batch_no) else '-',
                "issue_type": i.issue_type,
                "issue_desc": i.issue_desc,
                "solution_type": i.solution_type,
                "compensation_amount": float(i.compensation_amount) if i.compensation_amount else 0,
                "product_image": i.product_image,
                "issue_images": i.issue_images,
                "qc_username": i.qc_username,
                "created_at": i.created_at.isoformat() if i.created_at else None
            }
            for i in issues
        ]
    }


@app.post("/api/issues", response_model=IssueResponse)
async def create_issue(
    issue_data: IssueCreate,
    current_user: QCUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    import uuid
    import time
    
    try:
        # 确保 issue_no 唯一性：时间戳 + 随机数 + 用户 ID
        issue_no = f"Q{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:6].upper()}{current_user.id:02d}"
        
        # 如果重复，重试生成
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # 检查是否已存在
                existing = db.query(QualityIssue).filter(QualityIssue.issue_no == issue_no).first()
                if existing:
                    issue_no = f"Q{datetime.now().strftime('%Y%m%d%H%M%S%f')}{str(uuid.uuid4())[:4].upper()}{current_user.id:02d}"
                    time.sleep(0.001)  # 微_sleep 避免重复
                else:
                    break
            except:
                issue_no = f"Q{int(time.time()*1000000)}{str(uuid.uuid4())[:6].upper()}"
        
        db_issue = QualityIssue(
            issue_no=issue_no,
            goods_no=issue_data.goods_no,
            factory_name=issue_data.factory_name,
            batch_no=issue_data.batch_no,
            issue_type=issue_data.issue_type,
            issue_desc=issue_data.issue_desc,
            solution_type=issue_data.solution_type,
            compensation_amount=issue_data.compensation_amount,
            status="pending",
            product_image=issue_data.product_image,
            issue_images=issue_data.issue_images,
            qc_user_id=current_user.id,
            qc_username=current_user.username
        )
        
        db.add(db_issue)
        db.commit()
        db.refresh(db_issue)
        
        # 从波次号查询 merchandiser 和 designer
        merchandiser = ''
        designer = ''
        if db_issue.batch_no:
            batch = db.query(ProductBatch).filter(ProductBatch.batch_no == db_issue.batch_no).first()
            if batch:
                merchandiser = batch.merchandiser or ''
                designer = batch.designer or ''
                
                # 更新问题记录的 merchandiser 和 designer
                db_issue.merchandiser = merchandiser
                db_issue.designer = designer
                db.commit()
        
        # 获取问题图片列表
        issue_images = db_issue.issue_images or []
        
        # 发送企业微信通知
        await send_wechat_notification(
            issue_no=db_issue.issue_no,
            batch_no=db_issue.batch_no,
            factory_name=db_issue.factory_name,
            goods_no=db_issue.goods_no,
            merchandiser=merchandiser,
            designer=designer,
            issue_type=db_issue.issue_type,
            product_image=db_issue.product_image,
            issue_images=issue_images,
            username=current_user.username,
            created_at=db_issue.created_at
        )
        
        return db_issue
        
    except Exception as e:
        db.rollback()
        # 返回 JSON 格式的错误
        raise HTTPException(status_code=500, detail=f"提交失败：{str(e)}")


@app.get("/api/issues/{issue_id}")
async def get_issue_detail(
    issue_id: int,
    current_user: QCUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单个问题详情（兼容数字 ID）"""
    issue = db.query(QualityIssue).filter(QualityIssue.id == issue_id).first()
    
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    return {
        "id": issue.id,
        "issue_no": issue.issue_no,
        "status": issue.status or "pending",
        "sku_no": issue.goods_no,
        "platform": issue.platform,
        "order_no": issue.order_no,
        "buyer_wangwang": issue.buyer_wangwang,
        "issue_type": issue.issue_type,
        "issue_desc": issue.issue_desc,
        "solution_type": issue.solution_type,
        "compensation_amount": float(issue.compensation_amount) if issue.compensation_amount else 0,
        "factory_name": issue.factory_name,
        "batch_no": issue.batch_no,
        "pattern_batch": issue.pattern_batch,
        "designer": issue.designer,
        "handler": issue.handler,
        "batch_source": issue.batch_source,
        "created_at": issue.created_at.isoformat() if issue.created_at else None,
        "product_image": issue.product_image,
        "issue_images": issue.issue_images or []
    }


@app.get("/api/issues-by-no/{issue_no}")
async def get_issue_by_number(
    issue_no: str,
    current_user: QCUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单个问题详情（使用问题编码 - 更安全）"""
    issue = db.query(QualityIssue).filter(QualityIssue.issue_no == issue_no).first()
    
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    # 根据波次号查询 product_batches 表获取 merchandiser 和 designer
    merchandiser = '-'
    designer = issue.designer or '-'
    
    if issue.batch_no:
        batch_info = db.query(ProductBatch).filter(ProductBatch.batch_no == issue.batch_no).first()
        if batch_info:
            merchandiser = batch_info.merchandiser or '-'
            # 如果问题表没有设计师，使用波次表的设计师
            if not issue.designer:
                designer = batch_info.designer or '-'
    
    # 不暴露数字 ID，只返回问题编码和业务数据
    return {
        "issue_no": issue.issue_no,
        "status": issue.status or "pending",
        "sku_no": issue.goods_no,
        "platform": issue.platform,
        "order_no": issue.order_no,
        "buyer_wangwang": issue.buyer_wangwang,
        "issue_type": issue.issue_type,
        "issue_desc": issue.issue_desc,
        "solution_type": issue.solution_type,
        "compensation_amount": float(issue.compensation_amount) if issue.compensation_amount else 0,
        "factory_name": issue.factory_name,
        "batch_no": issue.batch_no,
        "pattern_batch": issue.pattern_batch,
        "designer": designer,
        "merchandiser": merchandiser,  # 新增订单跟单员字段
        "handler": issue.handler,
        "batch_source": issue.batch_source,
        "created_at": issue.created_at.isoformat() if issue.created_at else None,
        "product_image": issue.product_image,
        "issue_images": issue.issue_images or []
    }


@app.put("/api/issues/{issue_id}")
async def update_issue(
    issue_id: int,
    issue_data: IssueCreate,
    current_user: QCUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新问题"""
    issue = db.query(QualityIssue).filter(QualityIssue.id == issue_id).first()
    
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    # 更新字段
    issue.goods_no = issue_data.goods_no
    issue.factory_name = issue_data.factory_name
    issue.batch_no = issue_data.batch_no
    issue.issue_type = issue_data.issue_type
    issue.issue_desc = issue_data.issue_desc
    issue.solution_type = issue_data.solution_type
    issue.compensation_amount = issue_data.compensation_amount
    issue.product_image = issue_data.product_image
    issue.issue_images = issue_data.issue_images
    
    db.commit()
    db.refresh(issue)
    
    return issue


# ==================== Comment Model ====================

class CommentCreate(BaseModel):
    content: str

class CommentResponse(BaseModel):
    id: int
    issue_id: int
    user_id: int
    username: str  # 保留字段名兼容前端，实际返回昵称
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# 数据库评论模型
class IssueComment(Base):
    __tablename__ = "issue_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("quality_issues.id"), index=True)
    user_id = Column(Integer, ForeignKey("qc_users.id"), index=True)
    username = Column(String(32))
    nickname = Column(String(32))
    content = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

# ==================== Comment Endpoints ====================

@app.get("/api/issues/{issue_no}/comments", response_model=List[CommentResponse])
async def get_issue_comments(
    issue_no: str,
    current_user: QCUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取问题的评论列表"""
    # 获取问题 ID
    issue = db.query(QualityIssue).filter(QualityIssue.issue_no == issue_no).first()
    if not issue:
        raise HTTPException(status_code=404, detail="问题不存在")
    
    # 从数据库获取评论，按时间排序
    issue_comments = db.query(IssueComment).filter(
        IssueComment.issue_id == issue.id
    ).order_by(IssueComment.created_at.asc()).all()
    
    # 转换为响应格式（使用昵称或用户名）
    return [
        CommentResponse(
            id=c.id,
            issue_id=c.issue_id,
            user_id=c.user_id,
            username=c.nickname or c.username,
            content=c.content,
            created_at=c.created_at
        )
        for c in issue_comments
    ]

@app.post("/api/issues/{issue_no}/comments", response_model=CommentResponse)
async def create_issue_comment(
    issue_no: str,
    comment_data: CommentCreate,
    current_user: QCUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建问题评论"""
    # 获取问题 ID
    issue = db.query(QualityIssue).filter(QualityIssue.issue_no == issue_no).first()
    if not issue:
        raise HTTPException(status_code=404, detail="问题不存在")
    
    # 检查评论者是否是订单跟单员
    is_merchandiser = False
    if issue.batch_no:
        batch_info = db.query(ProductBatch).filter(ProductBatch.batch_no == issue.batch_no).first()
        if batch_info and batch_info.merchandiser:
            # 检查当前用户的昵称或用户名是否匹配订单跟单员
            if (current_user.nickname and current_user.nickname == batch_info.merchandiser) or \
               (current_user.username == batch_info.merchandiser):
                is_merchandiser = True
    
    # 创建评论并保存到数据库
    new_comment = IssueComment(
        issue_id=issue.id,
        user_id=current_user.id,
        username=current_user.username,
        nickname=current_user.nickname,
        content=comment_data.content
    )
    db.add(new_comment)
    
    # 如果是订单跟单员评论，自动将问题状态改为"已处理"
    if is_merchandiser and issue.status != 'resolved':
        issue.status = 'resolved'
    
    db.commit()
    db.refresh(new_comment)
    
    # 返回评论（使用昵称或用户名）
    return CommentResponse(
        id=new_comment.id,
        issue_id=new_comment.issue_id,
        user_id=new_comment.user_id,
        username=new_comment.nickname or new_comment.username,
        content=new_comment.content,
        created_at=new_comment.created_at
    )

# ==================== Qiniu Upload Token Endpoint ====================

@app.get("/api/qiniu/upload-token")
async def get_qiniu_upload_token(
    current_user: QCUser = Depends(get_current_user)
):
    """
    获取七牛云上传凭证
    
    前端拿到 token 后直接上传到七牛云，返回 CDN 链接
    """
    if not QINIU_ACCESS_KEY or not QINIU_SECRET_KEY:
        raise HTTPException(status_code=500, detail="七牛云配置缺失")
    
    try:
        import qiniu.auth
        import qiniu.zone
        from qiniu import Auth
        
        # 初始化七牛云 Auth
        auth = Auth(QINIU_ACCESS_KEY, QINIU_SECRET_KEY)
        
        # 设置上传策略
        # 只允许上传到指定前缀目录
        put_policy = {
            'scope': f"{QINIU_BUCKET}:{QINIU_PREFIX}",
            'deadline': int(datetime.now().timestamp()) + 3600,  # 1 小时有效期
            'insertOnly': 0,  # 允许覆盖同名文件
            'saveKey': f"{QINIU_PREFIX}$(etag)"  # 使用文件 hash 作为文件名
        }
        
        # 生成上传凭证
        upload_token = auth.upload_token(QINIU_BUCKET, policy=put_policy)
        
        return {
            "token": upload_token,
            "bucket": QINIU_BUCKET,
            "domain": QINIU_DOMAIN,
            "prefix": QINIU_PREFIX,
            "expire": 3600
        }
    except ImportError:
        raise HTTPException(status_code=500, detail="请安装七牛云 SDK: pip install qiniu")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成上传凭证失败：{str(e)}")


# ==================== Upload Endpoint (Local) ====================

@app.post("/uploads")
async def upload_file(
    file: UploadFile = File(...),
    current_user: QCUser = Depends(get_current_user)
):
    """
    上传图片文件
    
    限制:
    - 文件大小：最大 5MB
    - 文件类型：JPEG, PNG, GIF, WebP
    - 分辨率：最大 4096x4096
    """
    # 1. 验证文件类型
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的图片类型。允许的类型：{', '.join(ALLOWED_IMAGE_TYPES)}"
        )
    
    # 2. 读取文件内容并验证大小
    content = await file.read()
    file_size = len(content)
    
    if file_size > MAX_IMAGE_SIZE:
        size_mb = file_size / (1024 * 1024)
        max_mb = MAX_IMAGE_SIZE / (1024 * 1024)
        raise HTTPException(
            status_code=413,  # Payload Too Large
            detail=f"图片过大 ({size_mb:.1f}MB)，最大允许 {max_mb}MB"
        )
    
    if file_size == 0:
        raise HTTPException(status_code=400, detail="空文件")
    
    # 3. 验证图片尺寸（可选，需要 PIL）
    try:
        from PIL import Image
        import io
        
        img = Image.open(io.BytesIO(content))
        width, height = img.size
        
        if width > MAX_IMAGE_WIDTH or height > MAX_IMAGE_HEIGHT:
            raise HTTPException(
                status_code=400,
                detail=f"图片分辨率过大 ({width}x{height})，最大允许 {MAX_IMAGE_WIDTH}x{MAX_IMAGE_HEIGHT}"
            )
    except ImportError:
        # PIL 未安装，跳过尺寸验证
        pass
    except HTTPException:
        raise
    except Exception as e:
        # 图片损坏或无法读取 - 仅记录日志，不阻止上传
        import logging
        logging.warning(f'图片验证失败：{e}，但允许上传')
        # 不抛出异常，允许上传
    
    # 4. 保存文件
    file_ext = os.path.splitext(file.filename)[1]
    if not file_ext:
        # 根据内容类型推断扩展名
        ext_map = {
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/webp': '.webp'
        }
        file_ext = ext_map.get(file.content_type, '.jpg')
    
    filename = f"{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}{file_ext}"
    filepath = UPLOAD_DIR / filename
    
    with open(filepath, "wb") as buffer:
        buffer.write(content)
    
    file_url = f"/uploads/{filename}"
    
    return {
        "url": file_url,
        "filename": filename,
        "size": file_size,
        "content_type": file.content_type
    }


# ==================== Statistics Endpoints ====================

@app.get("/api/stats/summary")
async def get_stats_summary(
    days: Optional[int] = None,
    current_user: QCUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取统计摘要 - 支持时间范围筛选"""
    query = db.query(QualityIssue)
    
    # 时间范围筛选
    if days:
        from datetime import timedelta
        start_date = datetime.now() - timedelta(days=days)
        query = query.filter(QualityIssue.created_at >= start_date)
    
    # 总数
    total_count = query.count()
    
    # 总补偿金额
    total_compensation = db.query(func.sum(QualityIssue.compensation_amount)).scalar() or 0
    
    # 工厂数量
    factory_count = query.filter(QualityIssue.factory_name != None).distinct(QualityIssue.factory_name).count()
    
    # 解决率
    solved_count = query.filter(QualityIssue.status.in_(['solved', 'completed', '已解决'])).count()
    solve_rate = (solved_count / total_count * 100) if total_count > 0 else 0
    
    return {
        "total_issues": total_count,
        "total_compensation": float(total_compensation),
        "factory_count": factory_count,
        "solve_rate": round(solve_rate, 2),
        "period_days": days
    }


@app.get("/api/stats/by-factory")
async def get_stats_by_factory(
    top: int = 10,
    days: Optional[int] = None,
    current_user: QCUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """按工厂统计 - TOP N"""
    query = db.query(
        QualityIssue.factory_name,
        func.count(QualityIssue.id).label('count'),
        func.sum(QualityIssue.compensation_amount).label('total_compensation')
    )
    
    # 时间范围筛选
    if days:
        from datetime import timedelta
        start_date = datetime.now() - timedelta(days=days)
        query = query.filter(QualityIssue.created_at >= start_date)
    
    results = query.filter(
        QualityIssue.factory_name != None
    ).group_by(
        QualityIssue.factory_name
    ).order_by(
        func.count(QualityIssue.id).desc()
    ).limit(top).all()
    
    return [
        {
            "factory": r.factory_name,
            "count": r.count,
            "total_compensation": float(r.total_compensation) if r.total_compensation else 0
        }
        for r in results
    ]


@app.get("/api/stats/by-type")
async def get_stats_by_type(
    days: Optional[int] = None,
    current_user: QCUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """按问题类型统计"""
    # 先获取总数
    base_query = db.query(QualityIssue)
    if days:
        from datetime import timedelta
        start_date = datetime.now() - timedelta(days=days)
        base_query = base_query.filter(QualityIssue.created_at >= start_date)
    
    total_count = base_query.count()
    
    # 按类型分组统计
    results = db.query(
        QualityIssue.issue_type,
        func.count(QualityIssue.id).label('count'),
        func.sum(QualityIssue.compensation_amount).label('total_compensation')
    )
    
    if days:
        results = results.filter(QualityIssue.created_at >= start_date)
    
    results = results.group_by(QualityIssue.issue_type).order_by(
        func.count(QualityIssue.id).desc()
    ).all()
    
    return [
        {
            "type": r.issue_type or "unknown",
            "count": r.count,
            "percentage": round(r.count / total_count * 100, 2) if total_count > 0 else 0,
            "total_compensation": float(r.total_compensation) if r.total_compensation else 0
        }
        for r in results
    ]


@app.get("/api/stats/by-platform")
async def get_stats_by_platform(
    days: Optional[int] = None,
    current_user: QCUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """按平台统计"""
    from sqlalchemy import distinct
    
    # 先获取总数
    base_query = db.query(QualityIssue)
    if days:
        from datetime import timedelta
        start_date = datetime.now() - timedelta(days=days)
        base_query = base_query.filter(QualityIssue.created_at >= start_date)
    
    total_count = base_query.count()
    
    # 按平台分组统计 - 使用明确的 group_by
    results = db.query(
        QualityIssue.platform,
        func.count(QualityIssue.id).label('count')
    )
    
    if days:
        results = results.filter(QualityIssue.created_at >= start_date)
    
    results = results.group_by(QualityIssue.platform).order_by(
        func.count(QualityIssue.id).desc()
    ).all()
    
    return [
        {
            "platform": r.platform or "unknown",
            "count": r.count,
            "percentage": round(r.count / total_count * 100, 2) if total_count > 0 else 0
        }
        for r in results
    ]


@app.get("/api/stats/monthly-trend")
async def get_monthly_trend(
    months: int = 12,
    current_user: QCUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """按月趋势统计 - 近 N 个月"""
    from sqlalchemy import extract
    
    cutoff_date = datetime.now() - timedelta(days=months * 30)
    
    results = db.query(
        extract('year', QualityIssue.created_at).label('year'),
        extract('month', QualityIssue.created_at).label('month'),
        func.count(QualityIssue.id).label('count'),
        func.sum(QualityIssue.compensation_amount).label('total_compensation')
    ).filter(
        QualityIssue.created_at >= cutoff_date
    ).group_by(
        extract('year', QualityIssue.created_at),
        extract('month', QualityIssue.created_at)
    ).order_by(
        extract('year', QualityIssue.created_at),
        extract('month', QualityIssue.created_at)
    ).all()
    
    return [
        {
            "year": int(r.year),
            "month": int(r.month),
            "count": r.count,
            "total_compensation": float(r.total_compensation) if r.total_compensation else 0
        }
        for r in results
    ]


@app.get("/api/stats/by-status")
async def get_stats_by_status(
    current_user: QCUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """按状态统计"""
    results = db.query(
        QualityIssue.status,
        func.count(QualityIssue.id).label('count')
    ).group_by(
        QualityIssue.status
    ).all()
    
    total = sum(r.count for r in results)
    
    return [
        {
            "status": r.status or "unknown",
            "count": r.count,
            "percentage": round(r.count / total * 100, 2) if total > 0 else 0
        }
        for r in results
    ]


# ==================== Health Check ====================

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/")
async def root():
    return {
        "name": "QC Quality Management System API",
        "version": "1.0.0",
        "docs": "/docs",
        "uploads": "/uploads/"
    }


# ==================== WeChat Work Notification ====================

async def send_wechat_notification(issue_no: str, batch_no: str, factory_name: str, goods_no: str, merchandiser: str, designer: str, issue_type: str, product_image: str, issue_images: list, username: str, created_at: datetime):
    """发送企业微信通知"""
    if not WECHAT_WEBHOOK_URL:
        return
    
    try:
        # 获取第一张问题图片
        first_issue_image = issue_images[0] if issue_images and len(issue_images) > 0 else None
        
        # 构建消息内容
        content = f"""📝 新问题通知

🔢 波次号：{batch_no or '无'}
🏭 工厂：{factory_name or '未知'}
👔 跟单：{merchandiser or '无'}
👨‍🎨 设计师：{designer or '无'}
📦 货品编码：{goods_no or '未知'}
🏷️ 问题类型：{issue_type}
👤 提交人：{username}
🕐 提交时间：{created_at.strftime('%Y-%m-%d %H:%M') if created_at else '刚刚'}

🔗 查看详情：{WECHAT_REDIRECT_URI}/qc-mobile/issue-detail.html?no={urllib.parse.quote(issue_no)}"""
        
        # 如果有图片，发送图文消息
        if first_issue_image:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    WECHAT_WEBHOOK_URL,
                    json={
                        "msgtype": "news",
                        "news": {
                            "articles": [
                                {
                                    "title": f"📝 新问题通知 - {factory_name or '未知工厂'}",
                                    "description": f"波次号：{batch_no or '无'}\n问题类型：{issue_type}\n提交人：{username}",
                                    "url": f"{WECHAT_REDIRECT_URI}/qc-mobile/issue-detail.html?no={urllib.parse.quote(issue_no)}",
                                    "picurl": first_issue_image
                                }
                            ]
                        }
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("errcode") == 0:
                        print(f"✅ 企业微信推送成功（带图）：{issue_no}")
                    else:
                        print(f"❌ 企业微信推送失败：{result}")
        else:
            # 没有图片，发送文本消息
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    WECHAT_WEBHOOK_URL,
                    json={
                        "msgtype": "text",
                        "text": {
                            "content": content
                        }
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("errcode") == 0:
                        print(f"✅ 企业微信推送成功（文本）：{issue_no}")
                    else:
                        print(f"❌ 企业微信推送失败：{result}")
    except Exception as e:
        print(f"❌ 发送企业微信通知失败：{e}")


# 挂载静态文件目录（在 app 创建后）
# 使用 ONCE 标记确保只挂载一次
if not hasattr(app, '_uploads_mounted'):
    try:
        app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
        app._uploads_mounted = True
    except Exception as e:
        print(f"Warning: Could not mount uploads directory: {e}")


# ==================== Startup ====================

if __name__ == "__main__":
    import uvicorn
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Start server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
