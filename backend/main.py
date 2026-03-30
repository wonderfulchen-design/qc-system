#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QC Quality Management System - Backend API
All error messages in English to avoid encoding issues
"""

# MySQL 鍏煎灞?- 浣跨敤 PyMySQL 鏇夸唬 MySQLdb
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

# 涓冪墰浜戦厤缃?
QINIU_ACCESS_KEY = os.getenv("QINIU_ACCESS_KEY", "")
QINIU_SECRET_KEY = os.getenv("QINIU_SECRET_KEY", "")
QINIU_BUCKET = os.getenv("QINIU_BUCKET", "lswsampleimg")
QINIU_DOMAIN = os.getenv("QINIU_DOMAIN", "https://lswsampleimg.qiniudn.com").rstrip("/") + "/"
QINIU_PREFIX = os.getenv("QINIU_PREFIX", "qcImg/")

# 浼佷笟寰俊閰嶇疆
WECHAT_CORP_ID = os.getenv("WECHAT_CORP_ID", "")
WECHAT_AGENT_ID = os.getenv("WECHAT_AGENT_ID", "")
WECHAT_SECRET = os.getenv("WECHAT_SECRET", "")
WECHAT_REDIRECT_URI = os.getenv("WECHAT_REDIRECT_URI", "")
WECHAT_WEBHOOK_URL = os.getenv("WECHAT_WEBHOOK_URL", "")

# 鍥剧墖涓婁紶闄愬埗
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_IMAGE_WIDTH = 4096  # 鏈€澶у搴?
MAX_IMAGE_HEIGHT = 4096  # 鏈€澶ч珮搴?
ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']

# ==================== Database Models ====================

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class QCUser(Base):
    __tablename__ = "qc_users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(32), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    real_name = Column(String(32))
    nickname = Column(String(32))  # 鏄电О锛岀敤浜庤瘎璁烘樉绀?
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
    merchandiser = Column(String(32))  # 璁㈠崟璺熷崟鍛?
    designer = Column(String(32))  # 璁捐甯?


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
    merchandiser = Column(String(32))  # 璁㈠崟璺熷崟鍛?
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
    batch_no: str  # 娉㈡鍙峰繀濉?
    issue_type: str
    issue_desc: Optional[str] = None
    solution_type: Optional[str] = None
    compensation_amount: Optional[float] = 0
    product_image: Optional[str] = None
    issue_images: Optional[List[str]] = None
    # QC 淇℃伅鐢卞悗绔嚜鍔ㄥ～鍏咃紝涓嶉渶瑕佸墠绔紶閫?


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

# 闈欐€佹枃浠舵寕杞?
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
app.mount("/qc-mobile", StaticFiles(directory="mobile", html=True), name="mobile")

# 浼佷笟寰俊楠岃瘉鏂囦欢闇€瑕佹斁鍦ㄦ牴鐩綍
# 鍗曠嫭鎸傝浇楠岃瘉鏂囦欢鍒版牴璺緞
from pathlib import Path
import os

@app.get("/WW_verify_bNelEDV6Mj48InFj.txt")
async def wechat_verification_file():
    """浼佷笟寰俊鍩熷悕楠岃瘉鏂囦欢"""
    from fastapi.responses import PlainTextResponse
    verification_file = Path("mobile") / "WW_verify_bNelEDV6Mj48InFj.txt"
    if verification_file.exists():
        content = verification_file.read_text().strip()
        return PlainTextResponse(content, media_type="text/plain")
    else:
        return PlainTextResponse("bNelEDV6Mj48InFj", media_type="text/plain")

# 鏍硅矾寰勯噸瀹氬悜鍒伴棶棰樺垪琛ㄩ〉
@app.get("/")
async def root_redirect():
    """鏍硅矾寰勮嚜鍔ㄨ烦杞埌闂鍒楄〃椤?""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/qc-mobile/issue-list.html")


# ==================== Exception Handler ====================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """鍏ㄥ眬寮傚父澶勭悊锛岀‘淇濊繑鍥?JSON 鏍煎紡"""
    return JSONResponse(
        status_code=500,
        content={"detail": f"鏈嶅姟鍣ㄩ敊璇細{str(exc)}"}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP 寮傚父澶勭悊"""
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
    璺宠浆鍒颁紒涓氬井淇℃巿鏉冮〉闈?
    """
    import uuid
    redirect_uri = f"{WECHAT_REDIRECT_URI}/auth/wechat/callback"
    state = str(uuid.uuid4())  # 鐢熸垚闅忔満 state 闃叉 CSRF
    
    # 瀛樺偍 state 鍒?session 鎴栫紦瀛橈紙杩欓噷绠€鍖栧鐞嗭紝瀹為檯搴旇瀛樺偍锛?
    oauth_url = get_wechat_oauth2_url(redirect_uri, state)
    
    return RedirectResponse(url=oauth_url)


@app.get("/auth/wechat/callback")
async def wechat_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    """
    浼佷笟寰俊鍥炶皟澶勭悊
    
    1. 鐢?code 鎹㈠彇鐢ㄦ埛淇℃伅
    2. 鑷姩鍒涘缓鎴栨洿鏂扮敤鎴?
    3. 鐧诲綍骞惰烦杞洖棣栭〉
    """
    try:
        # 1. 鑾峰彇鐢ㄦ埛淇℃伅
        user_info = await get_user_info(code)
        wechat_userid = user_info.get('userid')
        
        if not wechat_userid:
            return JSONResponse(
                status_code=400,
                content={"detail": "鑾峰彇鐢ㄦ埛淇℃伅澶辫触"}
            )
        
        # 2. 灏濊瘯鑾峰彇璇︾粏淇℃伅锛堥渶瑕佽鍙栨潈闄愶級
        try:
            detail_info = await get_user_detail(wechat_userid)
            user_name = detail_info.get('name', wechat_userid)
            user_department = detail_info.get('department', [])
            user_mobile = detail_info.get('mobile', '')
            user_email = detail_info.get('email', '')
        except:
            # 濡傛灉娌℃湁鏉冮檺锛屽彧鐢ㄥ熀鏈俊鎭?
            user_name = wechat_userid
            user_department = []
            user_mobile = ''
            user_email = ''
        
        # 3. 鏌ユ壘鎴栧垱寤虹敤鎴?
        user = db.query(QCUser).filter(QCUser.username == wechat_userid).first()
        
        if not user:
            # 鍒涘缓鏂扮敤鎴?
            import hashlib
            random_password = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
            
            user = QCUser(
                username=wechat_userid,
                password_hash=random_password,  # 闅忔満瀵嗙爜锛屽疄闄呯敤浼佷笟寰俊鐧诲綍
                real_name=user_name,
                nickname=user_name,
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
            # 鏇存柊鐢ㄦ埛淇℃伅
            user.real_name = user_name
            user.nickname = user_name
            if user_department:
                user.department = str(user_department[0])
            if user_mobile:
                user.phone = user_mobile
            if user_email:
                user.email = user_email
            db.commit()
        
        # 4. 鐢熸垚鐧诲綍 token
        from datetime import timedelta
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username, "role": user.role},
            expires_delta=timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
        )
        
        # 5. 璺宠浆鍒扮櫥褰曟垚鍔熼〉闈紙甯︿笂 token锛?
        redirect_url = f"{WECHAT_REDIRECT_URI}/qc-mobile/index.html?token={access_token}&wechat_login=1"
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"detail": f"鐧诲綍澶辫触锛歿str(e)}"}
        )


@app.post("/api/batches/import-csv")
async def import_batches_from_csv(
    file: UploadFile = File(...),
    current_user: QCUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """浠?CSV 鏂囦欢鎵归噺瀵煎叆娉㈡鏁版嵁"""
    import pandas as pd
    import io
    
    try:
        # 璇诲彇 CSV 鏂囦欢
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents), encoding='utf-8-sig')
        
        success_count = 0
        error_count = 0
        errors = []
        
        for idx, row in df.iterrows():
            try:
                batch_no = str(row.get('娉㈡鍙?, '')).strip()
                factory_name = str(row.get('宸ュ巶', '')).strip()
                goods_no = str(row.get('璐у搧缂栫爜', '')).strip()
                merchandiser = str(row.get('璁㈠崟璺熷崟鍛?, '')).strip() if pd.notna(row.get('璁㈠崟璺熷崟鍛?)) else None
                designer = str(row.get('璁捐甯?, '')).strip() if pd.notna(row.get('璁捐甯?)) else None
                
                if not batch_no or not factory_name or not goods_no:
                    error_count += 1
                    errors.append({"row": idx + 1, "error": "缂哄皯蹇呭～瀛楁"})
                    continue
                
                # 妫€鏌ユ槸鍚﹀凡瀛樺湪
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
            "message": f"瀵煎叆瀹屾垚锛佹垚鍔燂細{success_count}, 澶辫触锛歿error_count}",
            "success_count": success_count,
            "error_count": error_count,
            "errors": errors[:10]
        }
        
    except Exception as e:
        db.rollback()
        return {"success": False, "message": f"瀵煎叆澶辫触锛歿str(e)}"}


@app.get("/api/init-db")
@app.post("/api/init-db")
async def initialize_database(
    db: Session = Depends(get_db)
):
    """鍒濆鍖栨暟鎹簱 - 鍒涘缓琛ㄥ拰 admin 璐﹀彿"""
    try:
        # 鍒涘缓鎵€鏈夎〃
        Base.metadata.create_all(bind=engine)
        
        # 妫€鏌ユ槸鍚﹀凡鏈?admin 璐﹀彿
        admin = db.query(QCUser).filter(QCUser.username == "admin").first()
        
        if not admin:
            # 鍒涘缓 admin 璐﹀彿锛堝瘑鐮侊細admin123锛?
            admin = QCUser(
                username="admin",
                password_hash=hash_password("admin123"),
                real_name="绯荤粺绠＄悊鍛?,
                role="admin",
                status=1
            )
            db.add(admin)
            db.commit()
            
            return {
                "success": True,
                "message": "鏁版嵁搴撳垵濮嬪寲鎴愬姛锛乤dmin 璐﹀彿宸插垱寤恒€?,
                "admin": {
                    "username": "admin",
                    "password": "admin123"
                }
            }
        else:
            return {
                "success": True,
                "message": "鏁版嵁搴撳凡鍒濆鍖栵紝admin 璐﹀彿宸插瓨鍦ㄣ€?
            }
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": f"鍒濆鍖栧け璐ワ細{str(e)}"
        }


@app.put("/api/user/nickname", response_model=UserResponse)
async def update_nickname(
    nickname_data: dict,
    current_user: QCUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """鏇存柊鐢ㄦ埛鏄电О"""
    nickname = nickname_data.get("nickname", "").strip()
    
    if not nickname:
        raise HTTPException(status_code=400, detail="鏄电О涓嶈兘涓虹┖")
    
    if len(nickname) > 32:
        raise HTTPException(status_code=400, detail="鏄电О闀垮害涓嶈兘瓒呰繃 32 涓瓧绗?)
    
    current_user.nickname = nickname
    db.commit()
    db.refresh(current_user)
    
    return current_user


# ==================== Batch Query Endpoints ====================
# 娉ㄦ剰锛?api/batches/options 蹇呴』鍦?/api/batches/{batch_no} 涔嬪墠瀹氫箟

@app.get("/api/batches/options", response_model=Dict[str, List[str]])
async def get_batch_options(
    current_user: QCUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """鑾峰彇鎵€鏈夊敮涓€鐨勫伐鍘傘€佽璁″笀銆佹尝娆″彿銆佽窡鍗曞憳閫夐」"""
    # 鏌ヨ鎵€鏈夋尝娆℃暟鎹?
    batches = db.query(ProductBatch).all()
    
    # 鎻愬彇鍞竴鍊?
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
    """鎼滅储娉㈡锛堟坊鍔犵紦瀛橈級"""
    if not batch_no and not goods_no:
        return []
    
    # 绠€鍗曠殑鍐呭瓨缂撳瓨锛堢敓浜х幆澧冨缓璁敤 Redis锛?
    cache_key = f"search:{batch_no}:{goods_no}"
    if hasattr(search_batches, 'cache') and cache_key in search_batches.cache:
        return search_batches.cache[cache_key]
    
    query = db.query(ProductBatch)
    
    if batch_no:
        query = query.filter(ProductBatch.batch_no.like(f"%{batch_no}%"))
    if goods_no:
        query = query.filter(ProductBatch.goods_no.like(f"%{goods_no}%"))
    
    # 闄愬埗杩斿洖鏁伴噺锛屾彁楂樻煡璇㈤€熷害
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
    
    # 缂撳瓨缁撴灉锛堟渶澶氫繚鐣?100 鏉★級
    if not hasattr(search_batches, 'cache'):
        search_batches.cache = {}
    search_batches.cache[cache_key] = response_data
    if len(search_batches.cache) > 100:
        # 鍒犻櫎鏈€鏃х殑缂撳瓨
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
    """鍒嗛〉鏌ヨ娉㈡宸ュ巶鍟嗗搧缂栫爜鍏崇郴鍒楄〃"""
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
    """娴嬭瘯绔偣"""
    return {"message": "Batch API is working", "user": current_user.username}


@app.get("/api/batches/{batch_no}", response_model=BatchResponse)
async def get_batch_by_no(
    batch_no: str,
    current_user: QCUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """鏍规嵁娉㈡鍙锋煡璇㈠崟涓尝娆′俊鎭紙蹇呴』鍦ㄦ墍鏈夊叿浣撹矾寰勪箣鍚庯級"""
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
    """鎵归噺瀵煎叆/鏇存柊娉㈡鍏崇郴"""
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
    """鍒涘缓鎴栨洿鏂版尝娆″叧绯伙紙娉㈡鍙峰敮涓€锛屽瓨鍦ㄥ垯鏇存柊锛?""
    try:
        existing = db.query(ProductBatch).filter(
            ProductBatch.batch_no == batch_data.batch_no
        ).first()
        
        if existing:
            # 鏇存柊鐜版湁璁板綍
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
            # 鍒涘缓鏂拌褰?
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
        raise HTTPException(status_code=500, detail=f"鍒涘缓澶辫触锛歿str(e)}")


@app.put("/api/batches/{batch_no}", response_model=BatchResponse)
async def update_batch(
    batch_no: str,
    batch_data: BatchUpdate,
    current_user: QCUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """鏇存柊娉㈡鍏崇郴锛堥儴鍒嗘洿鏂帮級"""
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
    """鍒犻櫎娉㈡鍏崇郴"""
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
    page_size: int = 100,  # 澧炲姞鍒?100 鐢ㄤ簬鍓嶇绛涢€?
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
    # 浣跨敤 ID 闄嶅簭鎺掑簭锛圛D 瓒婂ぇ瓒婃柊锛夛紝纭繚鎺掑簭绋冲畾
    issues = query.order_by(QualityIssue.id.desc())\
                  .offset((page - 1) * page_size)\
                  .limit(page_size)\
                  .all()
    
    # 鎵归噺鏌ヨ娉㈡鍙峰搴旂殑璺熷崟鍛樺拰璁捐甯?
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
        # 纭繚 issue_no 鍞竴鎬э細鏃堕棿鎴?+ 闅忔満鏁?+ 鐢ㄦ埛 ID
        issue_no = f"Q{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:6].upper()}{current_user.id:02d}"
        
        # 濡傛灉閲嶅锛岄噸璇曠敓鎴?
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # 妫€鏌ユ槸鍚﹀凡瀛樺湪
                existing = db.query(QualityIssue).filter(QualityIssue.issue_no == issue_no).first()
                if existing:
                    issue_no = f"Q{datetime.now().strftime('%Y%m%d%H%M%S%f')}{str(uuid.uuid4())[:4].upper()}{current_user.id:02d}"
                    time.sleep(0.001)  # 寰甠sleep 閬垮厤閲嶅
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
        
        # 浠庢尝娆″彿鏌ヨ merchandiser 鍜?designer
        merchandiser = ''
        designer = ''
        if db_issue.batch_no:
            batch = db.query(ProductBatch).filter(ProductBatch.batch_no == db_issue.batch_no).first()
            if batch:
                merchandiser = batch.merchandiser or ''
                designer = batch.designer or ''
                
                # 鏇存柊闂璁板綍鐨?merchandiser 鍜?designer
                db_issue.merchandiser = merchandiser
                db_issue.designer = designer
                db.commit()
        
        # 鑾峰彇闂鍥剧墖鍒楄〃
        issue_images = db_issue.issue_images or []
        
        # 鍙戦€佷紒涓氬井淇￠€氱煡
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
        # 杩斿洖 JSON 鏍煎紡鐨勯敊璇?
        raise HTTPException(status_code=500, detail=f"鎻愪氦澶辫触锛歿str(e)}")


@app.get("/api/issues/{issue_id}")
async def get_issue_detail(
    issue_id: int,
    current_user: QCUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """鑾峰彇鍗曚釜闂璇︽儏锛堝吋瀹规暟瀛?ID锛?""
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
    """鑾峰彇鍗曚釜闂璇︽儏锛堜娇鐢ㄩ棶棰樼紪鐮?- 鏇村畨鍏級"""
    issue = db.query(QualityIssue).filter(QualityIssue.issue_no == issue_no).first()
    
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    # 鏍规嵁娉㈡鍙锋煡璇?product_batches 琛ㄨ幏鍙?merchandiser 鍜?designer
    merchandiser = '-'
    designer = issue.designer or '-'
    
    if issue.batch_no:
        batch_info = db.query(ProductBatch).filter(ProductBatch.batch_no == issue.batch_no).first()
        if batch_info:
            merchandiser = batch_info.merchandiser or '-'
            # 濡傛灉闂琛ㄦ病鏈夎璁″笀锛屼娇鐢ㄦ尝娆¤〃鐨勮璁″笀
            if not issue.designer:
                designer = batch_info.designer or '-'
    
    # 涓嶆毚闇叉暟瀛?ID锛屽彧杩斿洖闂缂栫爜鍜屼笟鍔℃暟鎹?
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
        "merchandiser": merchandiser,  # 鏂板璁㈠崟璺熷崟鍛樺瓧娈?
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
    """鏇存柊闂"""
    issue = db.query(QualityIssue).filter(QualityIssue.id == issue_id).first()
    
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    # 鏇存柊瀛楁
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
    username: str  # 淇濈暀瀛楁鍚嶅吋瀹瑰墠绔紝瀹為檯杩斿洖鏄电О
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# 鏁版嵁搴撹瘎璁烘ā鍨?
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
    """鑾峰彇闂鐨勮瘎璁哄垪琛?""
    # 鑾峰彇闂 ID
    issue = db.query(QualityIssue).filter(QualityIssue.issue_no == issue_no).first()
    if not issue:
        raise HTTPException(status_code=404, detail="闂涓嶅瓨鍦?)
    
    # 浠庢暟鎹簱鑾峰彇璇勮锛屾寜鏃堕棿鎺掑簭
    issue_comments = db.query(IssueComment).filter(
        IssueComment.issue_id == issue.id
    ).order_by(IssueComment.created_at.asc()).all()
    
    # 杞崲涓哄搷搴旀牸寮忥紙浣跨敤鏄电О鎴栫敤鎴峰悕锛?
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
    """鍒涘缓闂璇勮"""
    # 鑾峰彇闂 ID
    issue = db.query(QualityIssue).filter(QualityIssue.issue_no == issue_no).first()
    if not issue:
        raise HTTPException(status_code=404, detail="闂涓嶅瓨鍦?)
    
    # 妫€鏌ヨ瘎璁鸿€呮槸鍚︽槸璁㈠崟璺熷崟鍛?
    is_merchandiser = False
    if issue.batch_no:
        batch_info = db.query(ProductBatch).filter(ProductBatch.batch_no == issue.batch_no).first()
        if batch_info and batch_info.merchandiser:
            # 妫€鏌ュ綋鍓嶇敤鎴风殑鏄电О鎴栫敤鎴峰悕鏄惁鍖归厤璁㈠崟璺熷崟鍛?
            if (current_user.nickname and current_user.nickname == batch_info.merchandiser) or \
               (current_user.username == batch_info.merchandiser):
                is_merchandiser = True
    
    # 鍒涘缓璇勮骞朵繚瀛樺埌鏁版嵁搴?
    new_comment = IssueComment(
        issue_id=issue.id,
        user_id=current_user.id,
        username=current_user.username,
        nickname=current_user.nickname,
        content=comment_data.content
    )
    db.add(new_comment)
    
    # 濡傛灉鏄鍗曡窡鍗曞憳璇勮锛岃嚜鍔ㄥ皢闂鐘舵€佹敼涓?宸插鐞?
    if is_merchandiser and issue.status != 'resolved':
        issue.status = 'resolved'
    
    db.commit()
    db.refresh(new_comment)
    
    # 杩斿洖璇勮锛堜娇鐢ㄦ樀绉版垨鐢ㄦ埛鍚嶏級
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
    鑾峰彇涓冪墰浜戜笂浼犲嚟璇?
    
    鍓嶇鎷垮埌 token 鍚庣洿鎺ヤ笂浼犲埌涓冪墰浜戯紝杩斿洖 CDN 閾炬帴
    """
    if not QINIU_ACCESS_KEY or not QINIU_SECRET_KEY:
        raise HTTPException(status_code=500, detail="涓冪墰浜戦厤缃己澶?)
    
    try:
        import qiniu.auth
        import qiniu.zone
        from qiniu import Auth
        
        # 鍒濆鍖栦竷鐗涗簯 Auth
        auth = Auth(QINIU_ACCESS_KEY, QINIU_SECRET_KEY)
        
        # 璁剧疆涓婁紶绛栫暐
        # 鍙厑璁镐笂浼犲埌鎸囧畾鍓嶇紑鐩綍
        put_policy = {
            'scope': f"{QINIU_BUCKET}:{QINIU_PREFIX}",
            'deadline': int(datetime.now().timestamp()) + 3600,  # 1 灏忔椂鏈夋晥鏈?
            'insertOnly': 0,  # 鍏佽瑕嗙洊鍚屽悕鏂囦欢
            'saveKey': f"{QINIU_PREFIX}$(etag)"  # 浣跨敤鏂囦欢 hash 浣滀负鏂囦欢鍚?
        }
        
        # 鐢熸垚涓婁紶鍑瘉
        upload_token = auth.upload_token(QINIU_BUCKET, policy=put_policy)
        
        return {
            "token": upload_token,
            "bucket": QINIU_BUCKET,
            "domain": QINIU_DOMAIN,
            "prefix": QINIU_PREFIX,
            "expire": 3600
        }
    except ImportError:
        raise HTTPException(status_code=500, detail="璇峰畨瑁呬竷鐗涗簯 SDK: pip install qiniu")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"鐢熸垚涓婁紶鍑瘉澶辫触锛歿str(e)}")


# ==================== Upload Endpoint (Local) ====================

@app.post("/uploads")
async def upload_file(
    file: UploadFile = File(...),
    current_user: QCUser = Depends(get_current_user)
):
    """
    涓婁紶鍥剧墖鏂囦欢
    
    闄愬埗:
    - 鏂囦欢澶у皬锛氭渶澶?5MB
    - 鏂囦欢绫诲瀷锛欽PEG, PNG, GIF, WebP
    - 鍒嗚鲸鐜囷細鏈€澶?4096x4096
    """
    # 1. 楠岃瘉鏂囦欢绫诲瀷
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"涓嶆敮鎸佺殑鍥剧墖绫诲瀷銆傚厑璁哥殑绫诲瀷锛歿', '.join(ALLOWED_IMAGE_TYPES)}"
        )
    
    # 2. 璇诲彇鏂囦欢鍐呭骞堕獙璇佸ぇ灏?
    content = await file.read()
    file_size = len(content)
    
    if file_size > MAX_IMAGE_SIZE:
        size_mb = file_size / (1024 * 1024)
        max_mb = MAX_IMAGE_SIZE / (1024 * 1024)
        raise HTTPException(
            status_code=413,  # Payload Too Large
            detail=f"鍥剧墖杩囧ぇ ({size_mb:.1f}MB)锛屾渶澶у厑璁?{max_mb}MB"
        )
    
    if file_size == 0:
        raise HTTPException(status_code=400, detail="绌烘枃浠?)
    
    # 3. 楠岃瘉鍥剧墖灏哄锛堝彲閫夛紝闇€瑕?PIL锛?
    try:
        from PIL import Image
        import io
        
        img = Image.open(io.BytesIO(content))
        width, height = img.size
        
        if width > MAX_IMAGE_WIDTH or height > MAX_IMAGE_HEIGHT:
            raise HTTPException(
                status_code=400,
                detail=f"鍥剧墖鍒嗚鲸鐜囪繃澶?({width}x{height})锛屾渶澶у厑璁?{MAX_IMAGE_WIDTH}x{MAX_IMAGE_HEIGHT}"
            )
    except ImportError:
        # PIL 鏈畨瑁咃紝璺宠繃灏哄楠岃瘉
        pass
    except HTTPException:
        raise
    except Exception as e:
        # 鍥剧墖鎹熷潖鎴栨棤娉曡鍙?- 浠呰褰曟棩蹇楋紝涓嶉樆姝笂浼?
        import logging
        logging.warning(f'鍥剧墖楠岃瘉澶辫触锛歿e}锛屼絾鍏佽涓婁紶')
        # 涓嶆姏鍑哄紓甯革紝鍏佽涓婁紶
    
    # 4. 淇濆瓨鏂囦欢
    file_ext = os.path.splitext(file.filename)[1]
    if not file_ext:
        # 鏍规嵁鍐呭绫诲瀷鎺ㄦ柇鎵╁睍鍚?
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
    """鑾峰彇缁熻鎽樿 - 鏀寔鏃堕棿鑼冨洿绛涢€?""
    query = db.query(QualityIssue)
    
    # 鏃堕棿鑼冨洿绛涢€?
    if days:
        from datetime import timedelta
        start_date = datetime.now() - timedelta(days=days)
        query = query.filter(QualityIssue.created_at >= start_date)
    
    # 鎬绘暟
    total_count = query.count()
    
    # 鎬昏ˉ鍋块噾棰?
    total_compensation = db.query(func.sum(QualityIssue.compensation_amount)).scalar() or 0
    
    # 宸ュ巶鏁伴噺
    factory_count = query.filter(QualityIssue.factory_name != None).distinct(QualityIssue.factory_name).count()
    
    # 瑙ｅ喅鐜?
    solved_count = query.filter(QualityIssue.status.in_(['solved', 'completed', '宸茶В鍐?])).count()
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
    """鎸夊伐鍘傜粺璁?- TOP N"""
    query = db.query(
        QualityIssue.factory_name,
        func.count(QualityIssue.id).label('count'),
        func.sum(QualityIssue.compensation_amount).label('total_compensation')
    )
    
    # 鏃堕棿鑼冨洿绛涢€?
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
    """鎸夐棶棰樼被鍨嬬粺璁?""
    # 鍏堣幏鍙栨€绘暟
    base_query = db.query(QualityIssue)
    if days:
        from datetime import timedelta
        start_date = datetime.now() - timedelta(days=days)
        base_query = base_query.filter(QualityIssue.created_at >= start_date)
    
    total_count = base_query.count()
    
    # 鎸夌被鍨嬪垎缁勭粺璁?
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
    """鎸夊钩鍙扮粺璁?""
    from sqlalchemy import distinct
    
    # 鍏堣幏鍙栨€绘暟
    base_query = db.query(QualityIssue)
    if days:
        from datetime import timedelta
        start_date = datetime.now() - timedelta(days=days)
        base_query = base_query.filter(QualityIssue.created_at >= start_date)
    
    total_count = base_query.count()
    
    # 鎸夊钩鍙板垎缁勭粺璁?- 浣跨敤鏄庣‘鐨?group_by
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
    """鎸夋湀瓒嬪娍缁熻 - 杩?N 涓湀"""
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
    """鎸夌姸鎬佺粺璁?""
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
    """鍙戦€佷紒涓氬井淇￠€氱煡"""
    if not WECHAT_WEBHOOK_URL:
        return
    
    try:
        # 鑾峰彇绗竴寮犻棶棰樺浘鐗?
        first_issue_image = issue_images[0] if issue_images and len(issue_images) > 0 else None
        
        # 鏋勫缓娑堟伅鍐呭
        content = f"""馃摑 鏂伴棶棰橀€氱煡

馃敘 娉㈡鍙凤細{batch_no or '鏃?}
馃彮 宸ュ巶锛歿factory_name or '鏈煡'}
馃憯 璺熷崟锛歿merchandiser or '鏃?}
馃懆鈥嶐煄?璁捐甯堬細{designer or '鏃?}
馃摝 璐у搧缂栫爜锛歿goods_no or '鏈煡'}
馃彿锔?闂绫诲瀷锛歿issue_type}
馃懁 鎻愪氦浜猴細{username}
馃晲 鎻愪氦鏃堕棿锛歿created_at.strftime('%Y-%m-%d %H:%M') if created_at else '鍒氬垰'}

馃敆 鏌ョ湅璇︽儏锛歿WECHAT_REDIRECT_URI}/qc-mobile/issue-detail.html?no={urllib.parse.quote(issue_no)}"""
        
        # 濡傛灉鏈夊浘鐗囷紝鍙戦€佸浘鏂囨秷鎭?
        if first_issue_image:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    WECHAT_WEBHOOK_URL,
                    json={
                        "msgtype": "news",
                        "news": {
                            "articles": [
                                {
                                    "title": f"馃摑 鏂伴棶棰橀€氱煡 - {factory_name or '鏈煡宸ュ巶'}",
                                    "description": f"娉㈡鍙凤細{batch_no or '鏃?}\n闂绫诲瀷锛歿issue_type}\n鎻愪氦浜猴細{username}",
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
                        print(f"鉁?浼佷笟寰俊鎺ㄩ€佹垚鍔燂紙甯﹀浘锛夛細{issue_no}")
                    else:
                        print(f"鉂?浼佷笟寰俊鎺ㄩ€佸け璐ワ細{result}")
        else:
            # 娌℃湁鍥剧墖锛屽彂閫佹枃鏈秷鎭?
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
                        print(f"鉁?浼佷笟寰俊鎺ㄩ€佹垚鍔燂紙鏂囨湰锛夛細{issue_no}")
                    else:
                        print(f"鉂?浼佷笟寰俊鎺ㄩ€佸け璐ワ細{result}")
    except Exception as e:
        print(f"鉂?鍙戦€佷紒涓氬井淇￠€氱煡澶辫触锛歿e}")


# 鎸傝浇闈欐€佹枃浠剁洰褰曪紙鍦?app 鍒涘缓鍚庯級
# 浣跨敤 ONCE 鏍囪纭繚鍙寕杞戒竴娆?
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
