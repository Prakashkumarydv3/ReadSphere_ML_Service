from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pickle
import pandas as pd
import os
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow all origins (change to ["http://localhost:3000"] for security)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Load Popularity Model
with open("models/popular2.pkl", "rb") as f:
    popularity_model = pickle.load(f)

# Load Books Dataset & Similarity Model
with open("models/books7.pkl", "rb") as f:
    books = pickle.load(f)

with open("models/similarity2.pkl", "rb") as f:
    similarity = pickle.load(f)

@app.get("/recommend/all_books")
def get_all_books():
    """
    Returns all books in the dataset.
    """
    all_books = books[["BOOK_ID","BOOK_TITLE", "BOOK_AURTHOR", "GENERE","RATERS" ,"A_RATINGS","F_PAGE","LINK"]]
    return {"all_books": all_books.to_dict(orient="records")}

@app.get("/recommend/popularity")
def get_popular_books():
    """
    Returns the top 10 most popular books based on the popularity model.
    """
    top_books = popularity_model[["BOOK_ID","BOOK_TITLE", "BOOK_AURTHOR", "GENERE", "A_RATINGS","F_PAGE","LINK"]].head(10)
    print(popularity_model.columns)

    return {"popular_books": top_books.to_dict(orient="records")}


import numpy as np

@app.post("/recommend/personalized")
def get_personalized_recommendation(user_input: dict):
    """
    Recommends books based on user preferences.
    Example input: {"genre": "Fiction", "author": "J.K. Rowling", "min_rating": 4.0}
    """
    genre = user_input.get("genre", "").lower().strip()
    author = user_input.get("author", "").lower().strip()
    min_rating = float(user_input.get("min_rating", 0))

    # 🔹 Standardizing Dataset for Consistency
    books["GENERE"] = books["GENERE"].str.strip().str.lower()
    books["BOOK_AURTHOR"] = books["BOOK_AURTHOR"].str.strip().str.lower()

    # 🔹 Step 1: Filter by Genre (Always Required)
    filtered_books = books[books["GENERE"] == genre]

    # 🔹 Step 2: Apply Additional Filters Only If Provided
    if author:
        filtered_books = filtered_books[filtered_books["BOOK_AURTHOR"].str.contains(author, na=False)]

    if min_rating > 0:
        filtered_books = filtered_books[filtered_books["A_RATINGS"] >= min_rating]

    # 🔹 Fix: Fill NaN values to avoid JSON errors
    filtered_books = filtered_books.fillna({
        "BOOK_ID": 0,
        "BOOK_TITLE": "Unknown",
        "BOOK_AURTHOR": "Unknown",
        "GENERE": "Unknown",
        "A_RATINGS": 0.0,  # Ensure it's a float
        "F_PAGE": "placeholder.svg",
        "LINK": "#"
    })

    # 🔹 Convert Ratings to Float & Handle NaN issues
    filtered_books["A_RATINGS"] = filtered_books["A_RATINGS"].replace([np.nan, None], 0.0).astype(float)

    # 🔹 Debugging: Check If Books Were Filtered
    print("Filtered Books:", filtered_books[["BOOK_TITLE", "GENERE"]].head())

    if filtered_books.empty:
        return {"error": "No books found matching your preferences"}

    recommended_books = filtered_books[["BOOK_ID", "BOOK_TITLE", "BOOK_AURTHOR", "GENERE", "A_RATINGS", "F_PAGE", "LINK"]]

    return {"recommended_books": recommended_books.to_dict(orient="records")}




if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Default to 10000 for Render
    uvicorn.run(app, host="0.0.0.0", port=port)


