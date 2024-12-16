from dotenv import load_dotenv
import os
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = f"postgresql://{os.getenv('USERNAME')}:{os.getenv('DATABASE_PASSWORD')}@{os.getenv('HOST')}:{os.getenv('PORT')}/{os.getenv('DATABASE')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False