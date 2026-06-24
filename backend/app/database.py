"""数据库配置 - MySQL + SQLAlchemy 异步引擎"""

import asyncio
import os
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

# 数据库连接配置（优先从环境变量读取，方便部署时切换）
_DB_HOST = os.getenv("DB_HOST", "localhost")
_DB_PORT = os.getenv("DB_PORT", "3306")
_DB_USER = os.getenv("DB_USER", "root")
_DB_PASSWORD = os.getenv("DB_PASSWORD", "123456")
_DB_NAME = os.getenv("DB_NAME", "tripstar")

# 数据库类型: mysql 或 sqlite（通过 DB_TYPE 环境变量切换）
_DB_TYPE = os.getenv("DB_TYPE", "mysql")

if _DB_TYPE == "sqlite":
    _DB_DIR = Path(__file__).resolve().parent.parent.parent / "data"
    _DB_DIR.mkdir(parents=True, exist_ok=True)
    _DB_PATH = _DB_DIR / "tripstar.db"
    DATABASE_URL = f"sqlite+aiosqlite:///{_DB_PATH}"
else:
    DATABASE_URL = f"mysql+aiomysql://{_DB_USER}:{_DB_PASSWORD}@{_DB_HOST}:{_DB_PORT}/{_DB_NAME}?charset=utf8mb4"

# 创建异步引擎
engine = create_async_engine(DATABASE_URL, echo=False, pool_recycle=3600)

# 创建异步 Session 工厂
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    """SQLAlchemy 基类"""
    pass


async def get_db() -> AsyncSession:
    """获取数据库会话（依赖注入用）。"""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def _wait_for_db(retries: int = 15, delay: float = 2.0) -> None:
    """等待数据库就绪（Docker 启动时 MySQL 可能还没完全准备好）。"""
    for attempt in range(1, retries + 1):
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            print(f"✅ 数据库连接就绪（尝试 {attempt} 次后）")
            return
        except (OperationalError, Exception) as e:
            if attempt < retries:
                print(f"⏳ 等待数据库就绪...（{attempt}/{retries}）: {e}")
                await asyncio.sleep(delay)
            else:
                raise RuntimeError(f"❌ 数据库连接失败（已重试 {retries} 次）: {e}")


async def init_db():
    """创建所有表（应用启动时调用）。"""
    if _DB_TYPE == "mysql":
        await _wait_for_db()

    async with engine.begin() as conn:
        from .models.user import User  # noqa: F401 — 确保模型被加载
        await conn.run_sync(Base.metadata.create_all)
    print(f"📦 数据库已初始化 ({_DB_TYPE}): {DATABASE_URL}")
