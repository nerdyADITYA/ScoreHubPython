# 🏟️ Score Hub

**Score Hub** is a lightweight Flask web application that enables users to manage and track scores and player statistics for Football and Basketball games. It uses SQLite for storage and provides dynamic, real-time updates via a web interface.

---

## 📌 Table of Contents

* [Features](#features)
* [Folder and File Structure](#folder-and-file-structure)
* [Setup Instructions](#setup-instructions)
* [How It Works](#how-it-works)
* [API Routes](#api-routes)
* [Planned Improvements](#planned-improvements)
* [License](#license)

---

## 🚀 Features

* ⚽ Track Football games: players, goals, penalties, final scores.
* 🏀 Track Basketball games: players, points, shot types (2-pointers, 3-pointers, free throws).
* 🧠 Intelligent player stat aggregation with top scorer detection.
* 💾 Persistent storage using separate SQLite databases (`football.db` and `basketball.db`).
* 🧩 Clean modular route handling via Flask.
* 🎯 Minimal UI through Jinja templates (`football.html`, `basketball.html`).

---

## 📁 Folder and File Structure

```
/
├── app.py                 # Main Flask application with route and logic definitions
├── football.db            # SQLite database to store football player stats
├── basketball.db          # SQLite database to store basketball player stats
├── templates/
│   ├── football.html      # Frontend template for football match interaction
│   └── basketball.html    # Frontend template for basketball match interaction
├── static/                # (Optional) for CSS/JS if UI enhancement is added
└── README.md              # You're reading it!
```

### 🔍 Detailed Breakdown

* **`app.py`**: Core file that:

  * Initializes both databases.
  * Manages state in-memory and persists it to SQLite.
  * Defines all endpoints for football and basketball interactions.

* **`football.db`**:

  * Contains a `football` table with fields:

    ```
    id | team | player_name | goals | penalties
    ```

* **`basketball.db`**:

  * Contains a `basketball` table with fields:

    ```
    id | team | player_name | points | twoPointers | threePointers | freeThrows
    ```

* **`templates/`**:

  * Contains Jinja2 HTML templates rendered for football and basketball views.
  * These templates use variables like `team1`, `team2`, `match_ended`, etc., passed from the Flask routes.

---

## 🛠️ Setup Instructions

1. **Clone the Repository**

   ```bash
   git clone https://github.com/nerdyADITYA/SmartGrocer
   cd SmartGrocer
   ```

2. **Install Requirements**

   > No external libraries are needed beyond Flask and SQLite (included with Python).

   ```bash
   pip install flask
   ```

3. **Run the Application**

   ```bash
   python app.py
   ```

4. **Access in Browser**

   * Football: [http://localhost:5000/football](http://localhost:5000/football)
   * Basketball: [http://localhost:5000/basketball](http://localhost:5000/basketball)

---

## 🔁 How It Works

* When the app starts, `init_db()` ensures both `.db` files exist with appropriate schemas.
* In-memory `football_games` and `basketball_games` dictionaries hold real-time match states.
* Actions like adding players or updating scores reflect both in the UI and the database.
* When a match ends, the result is computed and the top scorer is determined dynamically.

---

## 🌐 API Routes

| Route                    | Method | Description                          |
| ------------------------ | ------ | ------------------------------------ |
| `/`                      | GET    | Welcome message                      |
| `/football`              | GET    | Render football score tracker        |
| `/football/add_player`   | POST   | Add a new player to football         |
| `/football/update_score` | POST   | Update a player’s score or penalties |
| `/football/end_match`    | POST   | End football match & show result     |
| `/basketball`            | GET    | Render basketball score tracker      |
| `/basketball/add_player` | POST   | Add a new basketball player          |
| `/basketball/add_points` | POST   | Add 1/2/3 points to player           |
| `/basketball/end_game`   | POST   | End basketball game & show result    |

---

## 💡 Planned Improvements

* 🖼️ Add CSS for better UI experience.
* 🧾 Export match summary to PDF/CSV.
* 🗃️ Add login/authentication for persistent user sessions.
* 📊 Add match history page from database.
* 🌍 Deploy on Render/Vercel/Heroku for public access.

