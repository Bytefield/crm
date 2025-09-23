from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class ContactBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    company: Optional[str] = Field(None, max_length=100)
    position: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    source: Optional[str] = Field(None, max_length=100, description="How the contact was acquired")
    
    # UTM Parameters
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_term: Optional[str] = None
    utm_content: Optional[str] = None

class ContactCreate(ContactBase):
    pass

class ContactUpdate(ContactBase):
    email: Optional[EmailStr] = None
    
    class Config:
        from_attributes = True

class Contact(ContactBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ContactInDB(Contact):
    pass

class ContactCampaignAssociation(BaseModel):
    campaign_id: int
    is_converted: bool = False
    converted_at: Optional[datetime] = None
    conversion_value: Optional[int] = Field(None, description="Conversion value in cents")
    
    class Config:
        from_attributes = True
