import os
from datetime import timedelta
from dotenv import load_dotenv


load_dotenv()


DB_URL = os.getenv("DB_URL")


MAIL_USERNAME = os.getenv("MAIL_USERNAME")

MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

MAIL_FROM = os.getenv("MAIL_FROM")

MAIL_PORT = int(os.getenv("MAIL_PORT"))

MAIL_SERVER = os.getenv("MAIL_SERVER")

MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME")

MAIL_STARTTLS = os.getenv("MAIL_STARTTLS") == "True"

MAIL_SSL_TLS = os.getenv("MAIL_SSL_TLS") == "True"



JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=15)

JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)



api_key = os.getenv("api_key")
print("数据库:", DB_URL)
print("邮箱:", MAIL_USERNAME)
print("JWT:", JWT_SECRET_KEY)
print("AI KEY:", api_key[:10])