from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pickle
import pandas as pd
import os
import uvicorn
from pydantic import BaseModel
import numpy as np
from db import database , books_table

app = FastAPI()

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://readaura.vercel.app"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Book(BaseModel):
    BOOK_ID: int
    BOOK_TITLE: str
    BOOK_AUTHOR: str
    GENRE: str
    LANGUAGE: str
    A_RATINGS: float
    RATERS: int
    F_PAGE: str
    LINK: str

# Load models and data
with open("models/popular10.pkl", "rb") as f:
    popularity_model = pickle.load(f)

with open("models/books10.pkl", "rb") as f:
    books = pickle.load(f)

with open("models/similarity10.pkl", "rb") as f:
    similarity = pickle.load(f)

@app.get("/recommend/all_books")
async def get_all_books():
    try:
        query = books_table.select()
        rows = await database.fetch_all(query)

        all_books = []
        for row in rows:
            book = dict(row)
            book["BOOK_ID"] = book.get("BOOK_ID", 0)
            book["BOOK_TITLE"] = book.get("BOOK_TITLE", "Unknown")
            book["BOOK_AUTHOR"] = book.get("BOOK_AUTHOR", "Unknown")  # corrected typo here
            book["GENRE"] = book.get("GENRE", "Unknown")
            book["RATERS"] = int(book.get("RATERS", 0))
            book["A_RATINGS"] = float(book.get("A_RATINGS", 0.0))
            book["F_PAGE"] = book.get("F_PAGE", "placeholder.svg")
            book["LINK"] = book.get("LINK", "#")
            all_books.append(book)

        return {"all_books": all_books}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

@app.post("/admin/add_book")
async def add_book(book: Book):
    try:
        query = books_table.insert().values(
            BOOK_ID=book.BOOK_ID,
            BOOK_TITLE=book.BOOK_TITLE,
            BOOK_AUTHOR=book.BOOK_AUTHOR,
            GENRE=book.GENRE,
            RATERS=book.RATERS,
            A_RATINGS=book.A_RATINGS,
            F_PAGE=book.F_PAGE,
            LINK=book.LINK,
        )
        await database.execute(query)
        return {"message": "Book added successfully", "book": book.dict()}
    except Exception as e:
        return {"error": str(e)}

@app.get("/recommend/popularity")
async def get_popular_books():
    try:
        query = books_table.select().order_by(books_table.c.RATERS.desc()).limit(10)
        rows = await database.fetch_all(query)

        popular_books = []
        for row in rows:
            book = dict(row)
            book["BOOK_ID"] = book.get("BOOK_ID", 0)
            book["BOOK_TITLE"] = book.get("BOOK_TITLE", "Unknown")
            book["BOOK_AUTHOR"] = book.get("BOOK_AUTHOR", "Unknown")
            book["GENRE"] = book.get("GENRE", "Unknown")
            book["A_RATINGS"] = float(book.get("A_RATINGS", 0.0))
            book["F_PAGE"] = book.get("F_PAGE", "placeholder.svg")
            book["LINK"] = book.get("LINK", "#")
            popular_books.append(book)

        return {"popular_books": popular_books}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

@app.post("/recommend/personalized")
def get_personalized_recommendation(user_input: dict):
    genre = user_input.get("genre", "").lower().strip()
    author = user_input.get("author", "").lower().strip()
    min_rating = float(user_input.get("min_rating", 0))

    books["GENERE"] = books["GENERE"].str.strip().str.lower()
    books["BOOK_AURTHOR"] = books["BOOK_AURTHOR"].str.strip().str.lower()

    filtered_books = books[books["GENERE"] == genre]

    if author:
        filtered_books = filtered_books[filtered_books["BOOK_AURTHOR"].str.contains(author, na=False)]

    if min_rating > 0:
        filtered_books = filtered_books[filtered_books["A_RATINGS"] >= min_rating]

    filtered_books = filtered_books.fillna({
        "BOOK_ID": 0,
        "BOOK_TITLE": "Unknown",
        "BOOK_AURTHOR": "Unknown",
        "GENERE": "Unknown",
        "A_RATINGS": 0.0,
        "F_PAGE": "placeholder.svg",
        "LINK": "#"
    })

    filtered_books["A_RATINGS"] = filtered_books["A_RATINGS"].replace([np.nan, None], 0.0).astype(float)

    if filtered_books.empty:
        return {"error": "No books found matching your preferences"}

    recommended_books = filtered_books[["BOOK_ID", "BOOK_TITLE", "BOOK_AURTHOR", "GENERE", "A_RATINGS", "F_PAGE", "LINK"]]

    return {"recommended_books": recommended_books.to_dict(orient="records")}

@app.post("/recommend/similar")
def get_similar_books(user_input: dict):
    book_title = user_input.get("book_title", "").strip()
    try:
        index = books[books['BOOK_TITLE'] == book_title].index[0]
        distances = list(enumerate(similarity[index]))
        distances = sorted(distances, reverse=True, key=lambda x: x[1])

        recommended_books = []
        for i in distances[1:6]:
            book = books.iloc[i[0]]
            recommended_books.append({
                "BOOK_ID": book["BOOK_ID"],
                "BOOK_TITLE": book["BOOK_TITLE"],
                "BOOK_AURTHOR": book["BOOK_AURTHOR"],
                "GENERE": book["GENERE"],
                "A_RATINGS": float(book["A_RATINGS"]),
                "F_PAGE": book["F_PAGE"],
                "LINK": book["LINK"]
            })
        return {"recommended_books": recommended_books}
    except Exception as e:
        return {"error": f"Book '{book_title}' not found or internal error occurred: {str(e)}"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
