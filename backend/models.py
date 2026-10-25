from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    brand = Column(String, default="")
    category = Column(String, default="")
    description = Column(String, default="")
    prices = relationship("Price", back_populates="product", cascade="all, delete-orphan")

class Store(Base):
    __tablename__ = "stores"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    website = Column(String, default="")
    prices = relationship("Price", back_populates="store")

class Price(Base):
    __tablename__ = "prices"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    price = Column(Float, nullable=False)
    discount = Column(Float, default=0)
    delivery_charge = Column(Float, default=0)
    rating = Column(Float, default=0)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    product = relationship("Product", back_populates="prices")
    store = relationship("Store", back_populates="prices")

class Wishlist(Base):
    __tablename__ = "wishlist"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

class PriceAlert(Base):
    __tablename__ = "price_alerts"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    target_price = Column(Float, nullable=False)
    active = Column(Boolean, default=True)
