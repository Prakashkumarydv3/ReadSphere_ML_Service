from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pickle
import pandas as pd
import os
import uvicorn
from pydantic import BaseModel
import numpy

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://readaura.vercel.app"],  # Allow all origins 
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

class Book(BaseModel):
    BOOK_ID: int
    BOOK_TITLE: str
    BOOK_AURTHOR: str
    GENERE: str
    LANGUAGE: str
    A_RATINGS: float
    RATERS: int
    F_PAGE: str
    LINK: str

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
    try:
        # Columns you want to return
        columns = ["BOOK_ID", "BOOK_TITLE", "BOOK_AURTHOR", "GENERE", "RATERS", "A_RATINGS", "F_PAGE", "LINK"]

        # Fill NaN values to avoid serialization issues
        all_books = books[columns].fillna({
            "BOOK_ID": 0,
            "BOOK_TITLE": "Unknown",
            "BOOK_AURTHOR": "Unknown",
            "GENERE": "Unknown",
            "RATERS": 0,
            "A_RATINGS": 0.0,
            "F_PAGE": "placeholder.svg",
            "LINK": "#"
        })

        # Ensure types are consistent (especially for ratings)
        all_books["A_RATINGS"] = all_books["A_RATINGS"].astype(float)
        all_books["RATERS"] = all_books["RATERS"].astype(int)

        return {"all_books": all_books.to_dict(orient="records")}

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

@app.post("/admin/add_book")
def add_book(book: Book):
    global books  # Use the in-memory DataFrame

    try:
        # Convert new book to a DataFrame row
        new_book_df = pd.DataFrame([book.dict()])

        # Append the new book
        books = pd.concat([books, new_book_df], ignore_index=True)

        # Save the updated books back to the pickle file
        with open("models/books7.pkl", "wb") as f:
            pickle.dump(books, f)
        
        # Save the updated books back to the xlsx file as well
        books.to_excel("data/books6.xlsx", index=False)


        return {"message": "Book added successfully", "book": book.dict()}
    except Exception as e:
        return {"error": str(e)}



@app.get("/recommend/popularity")
def get_popular_books():
    """
    Returns the top 10 most popular books based on the popularity model.
    """
    top_books = popularity_model[["BOOK_ID","BOOK_TITLE", "BOOK_AURTHOR", "GENERE", "A_RATINGS","F_PAGE","LINK"]].head(10)
    print(popularity_model.columns)

    return {"popular_books": top_books.to_dict(orient="records")}




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


