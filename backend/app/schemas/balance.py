from __future__ import annotations

from pydantic import BaseModel, Field


class BalanceResponse(BaseModel):
    balance_cents: int
    balance_formatted: str
    currency: str


class DepositAddressResponse(BaseModel):
    address: str
    network_label: str
    qr_payload: str


class BalanceRequestCreate(BaseModel):
    tx_ref: str = Field(..., min_length=1, max_length=2048)


class BalanceRequestResponse(BaseModel):
    id: int
    status: str


class BalanceRequestItem(BaseModel):
    id: int
    user_id: int
    tx_ref: str
    status: str
    admin_comment: str | None
    created_at: str
    reviewed_at: str | None


class BalanceAdjustRequest(BaseModel):
    delta_cents: int
    comment: str | None = None


class BalanceApproveRequest(BaseModel):
    amount_cents: int
    comment: str | None = None


class BalanceRejectRequest(BaseModel):
    comment: str | None = None


class LedgerItem(BaseModel):
    id: int
    user_id: int
    type: str
    delta_cents: int
    balance_after_cents: int
    comment: str | None
    ref_request_id: int | None
    admin_id: int | None
    created_at: str
