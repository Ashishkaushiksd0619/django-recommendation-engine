# Recommendation Engine

This Django-based recommendation engine uses **matrix factorization (ALS)** to generate personalized food recommendations alongside "New & Specials" and active promotions.

---

## Table of Contents

1. [Features](#features)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Database Migrations](#database-migrations)
6. [Running the Server](#running-the-server)
7. [API Endpoints](#api-endpoints)
8. [Running Tests](#running-tests)
9. [License](#license)

---

## Features

* **Collaborative Filtering (ALS)**: Generates personalized recommendations based on user order history.
* **Fallback to Popular Items**: Ensures a full list of recommendations by including popular foods if ALS model is unavailable or excludes already-ordered items.
* **"New & Specials"**: Highlights newly added or special menu items per canteen.
* **Promotions**: Fetches active local and national promotions for a user's home canteen.

---

## Requirements

* Python 3.10+
* Django 5.2
* implicit (ALS implementation)
* scipy
* django-rest-framework (if using extended API)

Dependencies are listed in `requirements.txt`.

---

## Installation

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd recommendation_engine
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Install `implicit`** (matrix factorization):

   ```bash
   pip install implicit>=0.7.2
   ```

---

## Configuration

1. Copy `.env.example` to `.env` and set any environment variables (e.g., `DATABASE_URL`, `SECRET_KEY`).
2. Adjust `settings.py` as needed:

   * `INSTALLED_APPS` includes `'recommendation'`.
   * `DATABASES` configuration (default: SQLite for development).

---

## Database Migrations

Apply migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Running the Server

Start the Django development server:

```bash
python manage.py runserver
```

Visit `http://localhost:8000/api/recommendation/contextual/` for personalized recommendations.

---

## API Endpoints

### 1. Contextual Recommendations

* **URL:** `/api/recommendation/contextual/`
* **Method:** `GET`
* **Description:** Returns:

  * `recommendations`: List of ALS-based personalized items.
  * `specials`: "New & Specials" for user’s home canteen.
  * `promotions`: Active local and national promotions.
* **Authentication:** Requires logged-in user (session or token).

Example response:

```json
{
  "recommendations": [
    {"title": "Burger", "score": 2.45, "price": 8.00},
    {"title": "Salad", "score": 1.75, "price": 6.00}
  ],
  "specials": [
    {"title": "Pizza", "price": 10.00}
  ],
  "promotions": [
    {"code": "LOCAL10", "discount_percent": 10.0, "level": "local"},
    {"code": "NAT20", "discount_percent": 20.0, "level": "national"}
  ]
}
```

---

## Running Tests

Execute the test suite:

```bash
python manage.py test
```

The tests cover:

* ALS recommendation logic (`get_cf_recommendations`).
* "New & Specials" (`get_new_and_specials`).
* Promotions (`get_promotions`).

---

## License

This project is open-source under the [MIT License](LICENSE).
