from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl

class CampaignStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class CampaignBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    status: CampaignStatus = CampaignStatus.DRAFT
    start_date: datetime
    end_date: Optional[datetime] = None
    budget: Optional[int] = Field(None, ge=0, description="Budget in cents")
    
    # UTM Parameters
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_term: Optional[str] = None
    utm_content: Optional[str] = None

class CampaignCreate(CampaignBase):
    pass

class CampaignUpdate(CampaignBase):
    name: Optional[str] = Field(None, max_length=100)
    status: Optional[CampaignStatus] = None
    start_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class Campaign(CampaignBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CampaignInDB(Campaign):
    pass

class CampaignMetrics(BaseModel):
    total_contacts: int = 0
    converted_contacts: int = 0
    conversion_rate: float = 0.0
    total_revenue: int = 0  # in cents
    
    class Config:
        from_attributes = True
