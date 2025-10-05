from databases import Database # type: ignore
import sqlalchemy # type: ignore
from dotenv import load_dotenv # type: ignore
load_dotenv()
import os
DATABASE_URL = os.getenv("DATABASE_URL")

database = Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

books_table = sqlalchemy.Table(
    "books", metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("BOOK_TITLE", sqlalchemy.String),
    sqlalchemy.Column("BOOK_AUTHOR", sqlalchemy.String),
    sqlalchemy.Column("GENRE", sqlalchemy.String),
    sqlalchemy.Column("RATERS", sqlalchemy.Integer),
    sqlalchemy.Column("A_RATINGS", sqlalchemy.Float),
    sqlalchemy.Column("F_PAGE", sqlalchemy.String),
    sqlalchemy.Column("LINK", sqlalchemy.String),
    sqlalchemy.Column("slug", sqlalchemy.String),
)
