
from datetime import datetime

from sqlalchemy import (Boolean, Column, DateTime, Float, ForeignKey,Integer, String, Text)

from sqlalchemy.orm import relationship

from app.database.db import Base





class User(Base):
    __tablename__ = "users"

    id = Column(Integer,primary_key=True,index= True)
    name = Column(String(100), nullable = False)
    email = Column(String(150),unique=True,index = True, nullable=False)
    hashed_password = Column(String, nullable = False)
    role = Column(String(50),nullable=False)
    is_active = Column(Boolean,default= True)
    created_at = Column(DateTime,default=datetime.utcnow)

    orders = relationship("Order",back_populates="billed_by",foreign_keys="Order.billed_by_id")
    refresh_tokens = relationship("UserRefreshToken",back_populates="user")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable= False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    phone = Column(String(20),nullable=True)
    hashed_password = Column(String,nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime,default=datetime.utcnow)

    refresh_tokens = relationship("CustomerRefreshToken",back_populates="customer")



class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer,primary_key=True,index=True)
    name = Column(String(100),unique=True,nullable=False)
    description = Column(Text,nullable=True)
    created_at = Column(DateTime,default=datetime.utcnow)

    products = relationship("Product",back_populates="category")



class Product(Base):
        
        __tablename__ = "products"

        id = Column(Integer,primary_key=True,index = True)
        name = Column(String(200),nullable=False)
        description = Column(Text,nullable=True)
        image = Column(String(500), nullable=True)   
        price = Column(Float,nullable = False)
        stock = Column(Integer,default=0)
        is_active = Column(Boolean,default=True)
        category_id = Column(Integer,ForeignKey("categories.id"),nullable=False)
        created_at = Column(DateTime,default=datetime.utcnow)

        category = relationship("Category",back_populates="products")
        order_items = relationship("OrderItem",back_populates="product")




class Order(Base):
     __tablename__ = "orders"

     id = Column(Integer,primary_key=True,index=True)
     customer_name = Column(String(100),nullable = False)
     customer_phone = Column(String(20),nullable=True)
     billed_by_id = Column(Integer,ForeignKey("users.id"))
     status = Column(String(50),default= "pending")
     total_amount = Column(Float,default=0.0)
     created_at = Column(DateTime,default = datetime.utcnow)
     updated_at = Column(DateTime,default= datetime.utcnow,onupdate=datetime.utcnow)

     billed_by = relationship("User",back_populates="orders",foreign_keys = [billed_by_id])
     items = relationship("OrderItem",back_populates="order",cascade="all, delete-orphan")
     invoice = relationship("Invoice",back_populates="order",uselist=False)




class OrderItem(Base):
     __tablename__ = "order_items"

     id = Column(Integer,primary_key=True,index = True)
     order_id = Column(Integer,ForeignKey("orders.id"))
     product_id = Column(Integer,ForeignKey("products.id"))
     quantity = Column(Integer,nullable=False)
     unit_price = Column(Float,nullable=False)


     order = relationship("Order",back_populates="items")
     product = relationship("Product",back_populates="order_items")



class Invoice(Base):
     __tablename__ = "invoices"

     id = Column(Integer,primary_key=True,index = True)
     order_id = Column(Integer,ForeignKey("orders.id"),unique=True)
     invoice_number = Column(String(50),unique=True)
     amount = Column(Float,nullable=False)
     status = Column(String(50),default="unpaid")
     issued_at = Column(DateTime,default=datetime.utcnow)
     due_date = Column(DateTime,nullable = True)
     paid_at = Column(DateTime,nullable=True)

     order = relationship("Order",back_populates="invoice")



class UserRefreshToken(Base):
     __tablename__ = "user_refresh_tokens"

     id = Column(Integer,primary_key=True,index = True)
     user_id = Column(Integer, ForeignKey("users.id"),nullable=False)
     token = Column(String,nullable=False,unique=True)
     expires_at = Column(DateTime, nullable=False)
     is_revoked = Column(Boolean,default=False)
     created_at = Column(DateTime, default=datetime.utcnow)

     user = relationship("User",back_populates="refresh_tokens")


class CustomerRefreshToken(Base):
     __tablename__ = "customer_refresh_tokens"

     id = Column(Integer, primary_key=True, index=True)
     customer_id = Column(Integer, ForeignKey("customers.id"),nullable=False)
     token = Column(String, nullable=False, unique=False)
     expire_at = Column(DateTime,nullable=False)
     is_revoked = Column(Boolean, default=False)
     created_at = Column(DateTime, default=datetime.utcnow)


     customer = relationship("Customer",back_populates="refresh_tokens")


class BusinessProfile(Base):
     __tablename__ = "business_profile"

     id = Column(Integer, primary_key=True)
     business_name = Column(String(200),nullable=False, default="ElectroMart")
     address = Column(Text,nullable=True)
     phone = Column(String(20),nullable=True)
     email = Column(String(150),nullable=True)
     gst_number = Column(String(50),nullable=True)
     gst_percentage = Column(Float, default=18.0)
     logo_url = Column(String(500),nullable=True)

     

     






