from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve the DATABASE_URL from the environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:admin@localhost/testtt")

# Ensure DATABASE_URL is set
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set.")

Base = declarative_base()

# Define the CriminalBackgroundVerification model/table
class BackgroundVerification(Base):
    __tablename__ = 'criminal_background_verification'
    __table_args__ = {'schema': 'public'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    # employee_id = Column(Integer, ForeignKey('employees.employee_id'), nullable=True)  # Assuming there is an 'employees' table
    employee_id = Column(Integer,nullable=True)
    verification_file_path = Column(String(255), nullable=True)
    file_type = Column(String(100), nullable=True)
    
class Employee(Base):
    __tablename__ = 'employees'
    __table_args__ = {'schema': 'public'}

    id = Column(Integer, primary_key=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    

# Set up the database connection and sessionmaker
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)

# Create the table (if it doesn't already exist)
Base.metadata.create_all(engine)
