📚 My Digital Book Library (Full-Stack API)
A professional, full-stack Library Management System built with a modern technology stack. This project implements a complete book lifecycle, from fetching metadata via external APIs to managing user-specific borrowing transactions.

🚀 Key Features
External API Integration: Automatically fetches book details (Title, Author, Description) from the Google Books API using ISBN.

User Authentication: Secure user registration and login using JWT (JSON Web Tokens) and password hashing with bcrypt.

Transaction Management: Users can Borrow (Issue) and Return books. The system tracks issue dates and status in real-time.

Interactive Dashboard: A user-friendly frontend built with Streamlit for seamless library management.

Containerized Environment: Fully dockerized application with separate containers for the App, Database (PostgreSQL), and Frontend.

🛠️ Tech Stack
Backend: FastAPI (Python)

Frontend: Streamlit

Database: PostgreSQL

ORM: SQLAlchemy

Containerization: Docker & Docker Compose

⚙️ Installation & Setup
1. Clone the Repository:
    git clone <your-repo-url>
    cd booklib-api


2. Run with Docker Compose: Ensure you have Docker installed, then run:
    docker-compose up --build

3. Access the Application:

    Frontend UI: http://localhost:8501

    Interactive API Docs (Swagger): http://localhost:8000/docs


📖 API Usage Guide
1. Registration & Login
    Register a new user via the /register endpoint or the Sidebar in the UI.

    Login to receive a JWT token, which authorizes all library actions.

2. Managing Books
    Add Book: Enter a 13-digit ISBN to fetch and save book details.

    Search: Search the library catalog by title or author.

3. Borrowing Flow
    Click Borrow on any book in the collection.

    The book will move to your "My Borrowed Books" dashboard.

    Click Return to update the transaction and release the book.

📂 Project Structure:

├── app/
│   ├── main.py          # FastAPI application & routes
│   ├── models.py        # Database schemas (User, Book, Transaction)
│   ├── crud.py          # Database operations
│   ├── auth.py          # JWT & Security logic
│   └── database.py      # SQLAlchemy connection setup
├── frontend/
│   └── app.py           # Streamlit UI logic
└── docker-compose.yml   # Multi-container orchestration