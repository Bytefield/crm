from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    phone = Column(String)
    company = Column(String)
    position = Column(String)
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    source = Column(String)  # How the contact was acquired
    
    # UTM Parameters from when the contact was acquired
    utm_source = Column(String)
    utm_medium = Column(String)
    utm_campaign = Column(String)
    utm_term = Column(String)
    utm_content = Column(String)
    
    # Relationships
    campaigns = relationship(
        "Campaign", 
        secondary="campaign_contacts", 
        back_populates="contacts"
    )

# Association table for many-to-many relationship between Campaign and Contact
class CampaignContact(Base):
    __tablename__ = "campaign_contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), primary_key=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), primary_key=True)
    
    # Additional fields specific to the relationship
    is_converted = Column(Boolean, default=False)
    converted_at = Column(DateTime(timezone=True))
    conversion_value = Column(Integer)  # In cents
    
    # Relationships
    campaign = relationship("Campaign", back_populates="campaign_contacts")
    contact = relationship("Contact", back_populates="campaign_contacts")
