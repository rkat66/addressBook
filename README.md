# Address Book

A Flask web application for managing an international address book with per-user accounts, map support, and address autocomplete.

## Features

- **Multi-user accounts** — each user has a private, isolated address book; sign up, log in, and log out
- **Add / Edit / Delete** contacts with full international address fields
- **Street address autocomplete** — type to get live suggestions that auto-fill all address fields and coordinates
- **Search** across name, street, city, state, country, email, phone, and postal code
- **Geocode** any address with one click — powered by OpenStreetMap Nominatim (free, no API key required)
- **Map view** — all geocoded contacts plotted on an interactive Leaflet map with a contacts sidebar
- **Mini-map** on each contact's detail and edit page
- **Pagination** and sortable columns on the contact list
- **Unique phone numbers** enforced per user account

## Tech Stack

| Layer | Technology |
|---|---|
| Web framework | [Flask](https://flask.palletsprojects.com/) 3.1+ |
| Authentication | [Flask-Login](https://flask-login.readthedocs.io/) |
| Database ORM | [SQLAlchemy](https://www.sqlalchemy.org/) via Flask-SQLAlchemy |
| Database | SQLite (zero-config, file-based) |
| Maps | [Leaflet.js](https://leafletjs.com/) + [OpenStreetMap](https://www.openstreetmap.org/) tiles |
| Geocoding | [Nominatim](https://nominatim.openstreetmap.org/) (OpenStreetMap, free) |
| UI | [Bootstrap 5](https://getbootstrap.com/) + [Bootstrap Icons](https://icons.getbootstrap.com/) |

## Project Structure

```
addressBook/
├── app.py                      # Application factory and entry point
├── extensions.py               # Shared db and LoginManager instances
├── models.py                   # User and Contact database models
├── config.py                   # Development / production configuration
├── requirements.txt
├── routes/
│   ├── auth.py                 # Signup, login, logout
│   ├── contacts.py             # CRUD routes: list, add, edit, delete, detail, map
│   ├── search.py               # Full-text search
│   └── geocode.py              # Nominatim proxy + GeoJSON API endpoint
├── templates/
│   ├── base.html               # Base layout with navbar
│   ├── auth/
│   │   ├── login.html          # Login form
│   │   └── signup.html         # Sign up form
│   ├── contacts/
│   │   ├── list.html           # Paginated, sortable contact list
│   │   ├── form.html           # Add / edit form (shared)
│   │   └── detail.html         # Contact detail with mini-map
│   ├── search/
│   │   └── results.html        # Search results
│   └── map/
│       └── view.html           # Full-screen map view with sidebar
└── static/
    ├── css/app.css
    └── js/geocode.js           # Address autocomplete and geocode button
```

## Setup

**Requirements:** Python 3.9+

```bash
# Clone or download the project
cd addressBook

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt
```

## Running

```bash
python app.py
```

Open **http://127.0.0.1:5000** in your browser. The SQLite database (`addressbook.db`) is created automatically on first run.

## Usage

### Creating an Account

1. Click **Sign Up** in the navbar.
2. Choose a username (minimum 3 characters) and password (minimum 6 characters).
3. You are logged in immediately and taken to your (empty) address book.

### Logging In

Click **Log In**, enter your username and password. Check **Remember me** to stay logged in across browser sessions.

### Adding a Contact

1. Click **Add New** in the navbar.
2. Start typing in the **Street Address** field — a dropdown of suggestions appears automatically.
3. Select a suggestion to auto-fill the street, city, state, postal code, country, and coordinates all at once.
4. Alternatively, fill in address fields manually and click **Geocode Address**.
5. Only **Name** is required. Click **Add Contact** to save.

### Searching

Use the search bar in the navbar for a quick search, or go to **Search** for a full-page search. Matches on name, street, city, state, country, email, phone, and postal code are all returned.

### Map View

Click **Map** in the navbar to see all your geocoded contacts on an interactive world map.

- The **sidebar** lists every contact — click one to fly to its marker on the map.
- Contacts without coordinates show a grey pin; clicking them shows a link to edit and geocode them.
- Use the **filter box** at the top of the sidebar to narrow the list by name.

### Data Isolation

Each user account has a completely separate address book. Contacts created by one user are never visible to another user.

## Address Fields

All fields except Name are optional, supporting international addresses of any format.

| Field | Description |
|---|---|
| Name | Full name (required) |
| Street | Street address, including apartment/suite — supports autocomplete |
| City | City or locality |
| State / Province | State, province, prefecture, or equivalent |
| Postal Code | ZIP, postcode, or equivalent |
| Country | Country name |
| Phone | Any format, including international (`+81 3-...`) — unique per account |
| Email | Email address |
| Latitude / Longitude | Auto-filled by autocomplete or Geocode button, or enter manually |

## API Endpoints

All endpoints require an active login session.

| Endpoint | Description |
|---|---|
| `GET /api/suggest?q=<query>` | Address autocomplete — returns up to 5 structured suggestions |
| `GET /api/geocode?q=<address>` | Geocode a single address, returns all structured fields + coordinates |
| `GET /api/contacts/geojson` | Current user's geocoded contacts as a GeoJSON FeatureCollection |

## Configuration

Environment variables:

| Variable | Default | Description |
|---|---|---|
| `FLASK_ENV` | `development` | Set to `production` for production mode |
| `SECRET_KEY` | `dev-secret-key-...` | Flask session secret — **change this in production** |
| `DATABASE_URL` | SQLite file in project dir | SQLAlchemy database URI (production only) |

To switch to PostgreSQL in production, set:

```bash
export DATABASE_URL=postgresql://user:password@host/dbname
export SECRET_KEY=your-random-secret
export FLASK_ENV=production
python app.py
```

## Geocoding Notes

- Geocoding is powered by [Nominatim](https://nominatim.openstreetmap.org/), the geocoding service behind OpenStreetMap.
- All requests are proxied server-side to comply with Nominatim's [Usage Policy](https://operations.osmfoundation.org/policies/nominatim/): a `User-Agent` header is sent and requests are rate-limited to one per second.
- The street autocomplete uses a 400ms debounce to avoid excessive requests while typing.
- No API key or account is required.
- Coordinates are stored in the database after geocoding, so the map works offline once contacts are geocoded.

## License

MIT
