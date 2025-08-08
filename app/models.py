from datetime import datetime
from sqlalchemy import text
from sqlalchemy.dialects import mysql
from .extensions import db

CATEGORY_ENUM = ("POLITICS","ECONOMY","IT","WORLD","SPORTS","CULTURE","ETC")
DEDUP_ENUM    = ("RAW","CLEAN","DUP","CLUSTERED")

class News(db.Model):
    __tablename__ = "news"
    __table_args__ = {"sqlite_autoincrement": True}

    news_id = db.Column(
        db.BigInteger().with_variant(db.Integer, "sqlite"),
        primary_key=True, autoincrement=True, nullable=False
    )
    oid_aid = db.Column(db.Text, unique=True, nullable=False)
    title = db.Column(db.Text, nullable=False)
    category_name = db.Column(db.Enum(*CATEGORY_ENUM, name="category_name", native_enum=False), nullable=False)
    content = db.Column(db.Text().with_variant(mysql.MEDIUMTEXT(), "mysql"), nullable=False)
    press = db.Column(db.Text, nullable=False)
    published_at = db.Column(db.Text, nullable=True)
    reporter = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)
    dedup_state = db.Column(db.Enum(*DEDUP_ENUM, name="dedup_state", native_enum=False), nullable=False)
    image_url = db.Column(db.Text, nullable=True)
    trusted = db.Column(db.Boolean, nullable=False, server_default=text("1"))

class NewsSummary(db.Model):
    __tablename__ = "news_summary"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    news_id = db.Column(
        db.BigInteger().with_variant(db.Integer, "sqlite"),
        db.ForeignKey("news.news_id"), index=True, nullable=True
    )
    type = db.Column(db.String(30), nullable=False)  # AIBOT / NEWSLETTER
    summary_text = db.Column(db.Text().with_variant(mysql.MEDIUMTEXT(), "mysql"), nullable=False)
    source_model = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    news = db.relationship("News", backref=db.backref("summaries", lazy=True))
