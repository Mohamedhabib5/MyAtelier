from sqlalchemy import create_engine, Column, Integer, String, Numeric, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import os

# Define Base
Base = declarative_base()

# --- Connection Config ---
# Default to SQLite for local development, but ready for Postgres
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///atelier.db")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Models ---

class User(Base):
    __tablename__ = "users"
    username = Column(String, primary_key=True, index=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(String)
    created_date = Column(String)


class AppSetting(Base):
    __tablename__ = "app_settings"
    key = Column(String, primary_key=True, index=True)
    value = Column(String)

class Department(Base):
    __tablename__ = "departments"
    department_name = Column(String, primary_key=True)

class Customer(Base):
    __tablename__ = "customers"
    customer_id = Column(String, primary_key=True) # C-101
    reg_date = Column(String)
    name = Column(String, index=True)
    groom_name = Column(String)
    address = Column(String)
    phone1 = Column(String, index=True)
    phone2 = Column(String)
    notes = Column(String)
    
    # Relationships
    bookings = relationship("Booking", back_populates="customer")

class Service(Base):
    __tablename__ = "services"
    service_id = Column(String, primary_key=True) # S-101
    department = Column(String, index=True)
    name = Column(String)
    price = Column(Numeric(12, 2))

class Dress(Base):
    __tablename__ = "dresses"
    dress_code = Column(String, primary_key=True)
    d_type = Column(String)
    buy_date = Column(String)
    description = Column(String)
    image_path = Column(String)
    status = Column(String) # Available, Rented, Maintenance

class Booking(Base):
    __tablename__ = "bookings"
    booking_id = Column(String, primary_key=True) # HR-123456
    booking_date = Column(String)
    customer_name = Column(String) # Keeping name for easy display, though ID relation is better in strict SQL
    # Linking to Customer ID would be better but we migrate from CSV usage where name was key-like.
    # We will try to link strictly if possible, but for CSV compat, we keep fields.
    # Let's add customer_id FK for future proofing if we can match it.
    customer_id = Column(String, ForeignKey("customers.customer_id"), nullable=True) 
    
    department = Column(String)
    service_id = Column(String, ForeignKey("services.service_id"), nullable=True)
    service = Column(String)
    dress_code = Column(String, nullable=True)
    event_date = Column(String)
    price = Column(Numeric(12, 2))
    paid = Column(Numeric(12, 2))
    remaining = Column(Numeric(12, 2))
    status = Column(String)
    notes = Column(String)
    
    customer = relationship("Customer", back_populates="bookings")
    payments = relationship("Payment", back_populates="booking")

class Payment(Base):
    __tablename__ = "payments"
    payment_id = Column(String, primary_key=True) # PAY-123456
    payment_date = Column(String)
    booking_id = Column(String, ForeignKey("bookings.booking_id"))
    amount = Column(Numeric(12, 2))
    customer_name = Column(String) 
    groom_name = Column(String)
    remaining_after = Column(Numeric(12, 2))
    notes = Column(String)
    
    booking = relationship("Booking", back_populates="payments")

# --- Init DB ---
def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
