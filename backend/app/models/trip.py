"""行程数据模型"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from ..database import Base


class TripTask(Base):
    """旅行规划任务 - 存储行程数据"""
    __tablename__ = "trip_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(32), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 请求信息
    request_data = Column(JSON, nullable=True, comment="原始请求参数")
    
    # 行程摘要（首页列表用）
    city = Column(String(128), nullable=True, comment="城市")
    cities = Column(JSON, nullable=True, comment="多城市列表")
    start_date = Column(String(16), nullable=True)
    end_date = Column(String(16), nullable=True)
    travel_days = Column(Integer, nullable=True)
    overall_suggestions = Column(Text, nullable=True)
    
    # 完整行程数据（JSON）
    plan_data = Column(JSON, nullable=True, comment="完整行程JSON")
    graph_data = Column(JSON, nullable=True, comment="知识图谱数据")
    
    # 状态
    status = Column(String(16), default="completed", nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 关联用户
    user = relationship("User", backref="trip_tasks")
