# LYDO Web Application

A Flask-based web portal for the Local Youth Development Office (LYDO), supporting youth profiling, organization directory (RYO), and administrative management.

## Features

- **Youth Profiling**: Registration and tracking of youth demographics, educational status, and background.
- **Registered Youth Organizations (RYO)**: Directory of local youth organizations and officials.
- **Admin Management**: Secure dashboard for user administration, youth profile verification, and record exports.
- **Authentication & Rate Limiting**: Role-based access control with Flask-Login and brute-force protection via Flask-Limiter.

## Tech Stack

- **Framework**: Flask
- **Database**: SQLite (via SQLAlchemy)
- **Authentication**: Flask-Login, Werkzeug security
- **Styling**: Bootstrap / Custom CSS

## Getting Started

### Prerequisites

- Python 3.10+
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd lydo_web
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # Linux/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create an admin user:**
   ```bash
   python create_admin.py -u admin -p yourpassword
   ```

5. **Run the application:**
   ```bash
   python run.py
   ```
   Open your browser at [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Project Structure

```text
lydo_web/
├── app/
│   ├── static/          # Static assets (CSS, JS, portraits)
│   ├── templates/       # Jinja2 HTML templates
│   ├── __init__.py      # App factory & extension initialization
│   ├── models.py        # SQLAlchemy database models
│   └── routes.py        # Application endpoints & view logic
├── instance/            # Local SQLite database (git-ignored)
├── config.py            # App configuration
├── create_admin.py      # CLI script to create admin user
├── requirements.txt     # Python package requirements
└── run.py               # Application entry point
```
