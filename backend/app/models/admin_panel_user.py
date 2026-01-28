from __future__ import annotations

from sqlalchemy import Boolean, Column, DateTime, Integer, String, func

from app.database import Base


class AdminPanelUser(Base):
    __tablename__ = "admin_panel_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(500), nullable=False)

    # Free-form role name (e.g. developer/admin/support/custom)
    role = Column(String(80), nullable=False, default="developer")

    # Optional comma-separated scopes, e.g. "posts,webinars,tickets,data" or "*"
    scopes = Column(String(500), nullable=True)

    is_active = Column(Boolean, nullable=False, default=True)

    # Increment to invalidate existing sessions on password reset
    session_version = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

