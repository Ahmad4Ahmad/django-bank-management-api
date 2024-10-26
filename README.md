# Bank Management System API

## Overview

The Bank Management System API is a Django-based application that provides a RESTful API for managing bank operations. This API allows users to create accounts, make transactions, and perform various banking operations securely.

## Features

- User authentication and authorization
- Create and manage bank accounts
- Deposit and withdraw funds
- View transaction history
- Transfer funds between accounts
- Account balance inquiries

## Technologies Used

- Django
- Django REST Framework
- sqlite
- Python
- Git

### Prerequisites

- Python 3.x
- Django
- Django REST Framework
- pip

### Installation

1. **Clone the repository:**

   git clone https://github.com/yourusername/bank-management-system-api.git
   cd bank-management-system-api

2. **Create a virtual environment:**

    # Linux
    sudo apt-get install python3-venv    # If needed
    python3 -m venv .venv
    source .venv/bin/activate

    # macOS
    python3 -m venv .venv
    source .venv/bin/activate

    # Windows
    py -3 -m venv .venv
    .venv\scripts\activate

3. **Install the requirements:**

    pip install -r requirements.txt

4. **Run migrations:**

    python manage.py migrate

5. **Run the server:**

    python manage.py runserver