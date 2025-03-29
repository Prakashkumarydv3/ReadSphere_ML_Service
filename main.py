from fastapi import FastAPI
import pickle
import pandas as pd
import os
import uvicorn

app = FastAPI()

# Load Popularity Model
with open("models/popular.pkl", "rb") as f:
    popularity_model = pickle.load(f)

# Load Books Dataset & Similarity Model
with open("models/books.pkl", "rb") as f:
    books = pickle.load(f)

with open("models/similarity.pkl", "rb") as f:
    similarity = pickle.load(f)


@app.get("/recommend/popularity")
def get_popular_books():
    """
    Returns the top 10 most popular books based on the popularity model.
    """
    top_books = popularity_model[["BOOK_TITLE", "BOOK_AURTHOR", "GENERE", "A_RATINGS","F_PAGE","LINK"]].head(10)
    print(popularity_model.columns)

    return {"popular_books": top_books.to_dict(orient="records")}


@app.post("/recommend/personalized")
def get_personalized_recommendation(user_input: dict):
    """
    Recommends books based on user preferences.
    Example input: {"genre": "Fiction", "author": "J.K. Rowling", "min_rating": 4.0}
    """
    genre = user_input.get("genre", "").lower()  # FIXED: Correct key
    author = user_input.get("author", "").lower()
    min_rating = float(user_input.get("min_rating", 0))  # FIXED: Ensure float value

    # Filter books based on user input
    filtered_books = books[  # ✅ FIXED: Using correct dataset
        (books["GENERE"].str.lower().str.contains(genre, na=False)) &
        (books["BOOK_AURTHOR"].str.lower().str.contains(author, na=False)) &
        (books["A_RATINGS"] >= min_rating)
    ]

    # If no books match, return an error
    if filtered_books.empty:
        return {"error": "No books found matching your preferences"}

    # Get top recommended books based on similarity
    recommended_books = filtered_books[["BOOK_ID","BOOK_TITLE", "BOOK_AURTHOR", "GENERE", "A_RATINGS","F_PAGE","LINK"]].head(5)

    return {"recommended_books": recommended_books.to_dict(orient="records")}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Default to 10000 for Render
    uvicorn.run(app, host="0.0.0.0", port=port)


