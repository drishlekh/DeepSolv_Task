
# Shopify Web Store Scraper 

This project is a Python application built with FastAPI that scrapes and organizes data from Shopify websites. It is designed to extract key business insights from a brand's web store without using the official Shopify API and persist the collected data in a SQL database.

The application exposes a single RESTful API endpoint that accepts a Shopify store's URL and returns a structured JSON object containing the scraped brand data.

## Key Features

-   **Scrapes Shopify Stores**: Fetches and parses HTML content from a given store URL.
-   **Comprehensive Data Extraction**: Gathers key business insights, including:
    -   **Whole Product Catalog**: A simplified list of all products (title, price, URL, image).
    -   **Hero Products**: Products featured on the homepage.
    -   **Policies**: Extracts Privacy and Return/Refund policy text using an LLM.
    -   **FAQs**: Intelligently scrapes FAQ pages by either parsing HTML structure or using an LLM as a fallback.
    -   **Brand Information**: Gathers social media handles, contact details (email/phone), and "About Us" text.
    -   **Important Links**: Collects URLs for order tracking, contact pages, and blogs.
-   **Database Persistence**: Saves all extracted data into a MySQL database using SQLAlchemy.
-   **RESTful API**: Provides a clean, well-documented API endpoint to trigger the scraping process.

## Tech Stack

-   **Backend Framework**: FastAPI
-   **Web Server**: Uvicorn
-   **Database ORM**: SQLAlchemy
-   **Database**: MySQL
-   **Data Validation**: Pydantic
-   **Web Scraping**: `requests` & `BeautifulSoup4`
-   **AI / LLM Integration**: Groq API (using the `llama2-70b-4096` model for unstructured text).
-   **Environment Management**: `python-dotenv`

## Setup and Installation

1.  **Clone the repository** (or ensure you are in the project's root directory).

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Create a file named `.env` in the project root directory and add your credentials. Use the following template:

    ```env
    # Example for MySQL
    DATABASE_URL="mysql+pymysql://USER:PASSWORD@HOST:PORT/DeepSolv"

    # Your Groq API Key
    GROQ_API_KEY="YOUR_GROQ_API_KEY"
    ```

## Running the Application

Once the setup is complete, run the Uvicorn server from the project's root directory:

```bash
uvicorn app.main:app --reload
```

The application will be running at `http://127.0.0.1:8000`.

## API Usage

The application provides an interactive API documentation page via FastAPI.

-   **URL**: `http://127.0.0.1:8000/docs`

#### Endpoint: `POST /fetch-brand-data/`

-   **Description**: Triggers the scraping process for a given website URL.
-   **Request Body**:
    ```json
    {
      "website_url": "https://memy.co.in"
    }
    ```
-   **Success Response (`200 OK`)**: A JSON object containing the structured brand data.
-   **Error Responses**:
    -   `404 Not Found`: If the initial website URL cannot be reached.
    -   `500 Internal Server Error`: If an unexpected error occurs during scraping or data processing.
