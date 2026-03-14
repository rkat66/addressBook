# Address Book

A Flask web application for managing an international address book with map support.

## Features

- **Add / Edit / Delete** contacts with full international address fields
- **Search** across name, street, city, state, country, email, phone, and postal code
- **Geocode** any address with one click — powered by OpenStreetMap Nominatim (free, no API key required)
- **Map view** — all geocoded contacts plotted on an interactive Leaflet map with clickable popups
- **Mini-map** on each contact's detail and edit page
- **Pagination** and sortable columns on the contact list

## Tech Stack

| Layer | Technology |
|---|---|
| Web framework | [Flask](https://flask.palletsprojects.com/) 3.0 |
| Database ORM | [SQLAlchemy](https://www.sqlalchemy.org/) via Flask-SQLAlchemy |
| Database | SQLite (zero-config, file-based) |
| Maps | [Leaflet.js](https://leafletjs.com/) + [OpenStreetMap](https://www.openstreetmap.org/) tiles |
| Geocoding | [Nominatim](https://nominatim.openstreetmap.org/) (OpenStreetMap, free) |
| UI | [Bootstrap 5](https://getbootstrap.com/) + [Bootstrap Icons](https://icons.getbootstrap.com/) |

## Project Structure

```
addressBook/
├── app.py                      # Application factory and entry point
├── extensions.py               # Shared SQLAlchemy db instance
├── models.py                   # Contact database model
├── config.py                   # Development / production configuration
├── requirements.txt
├── routes/
│   ├── contacts.py             # CRUD routes: list, add, edit, delete, detail, map
│   ├── search.py               # Full-text search
│   └── geocode.py              # Nominatim proxy + GeoJSON API endpoint
├── templates/
│   ├── base.html               # Base layout with navbar
│   ├── contacts/
│   │   ├── list.html           # Paginated, sortable contact list
│   │   ├── form.html           # Add / edit form (shared)
│   │   └── detail.html         # Contact detail with mini-map
│   ├── search/
│   │   └── results.html        # Search results
│   └── map/
│       └── view.html           # Full-screen map view
└── static/
    ├── css/app.css
    └── js/geocode.js           # Client-side geocode button handler
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

### Adding a Contact

1. Click **Add New** in the navbar.
2. Fill in any combination of fields — only **Name** is required.
3. Click **Geocode Address** to automatically look up latitude/longitude from the address fields.
4. Click **Add Contact** to save.

### Searching

Use the search bar in the navbar for a quick search, or go to **Search** for a full-page search. Matches on name, street, city, state, country, email, phone, and postal code are all returned.

### Map View

Click **Map** in the navbar to see all geocoded contacts on an interactive world map. Click any marker to see the contact's name, address, and a link to their detail page.

Contacts without coordinates (the map pin icon is grey on the list page) will not appear on the map until geocoded. Open the contact's edit page and click **Geocode Address**.

## Address Fields

All fields except Name are optional, supporting international addresses of any format.

| Field | Description |
|---|---|
| Name | Full name (required) |
| Street | Street address, including apartment/suite |
| City | City or locality |
| State / Province | State, province, prefecture, or equivalent |
| Postal Code | ZIP, postcode, or equivalent |
| Country | Country name |
| Phone | Any format, including international (`+81 3-...`) |
| Email | Email address |
| Latitude / Longitude | Auto-filled by Geocode button, or enter manually |

## API Endpoints

These are used internally by the frontend but are also accessible directly.

| Endpoint | Description |
|---|---|
| `GET /api/geocode?q=<address>` | Geocode an address string via Nominatim. Returns `{"lat": ..., "lon": ...}` |
| `GET /api/contacts/geojson` | All geocoded contacts as a GeoJSON FeatureCollection |

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
- The app proxies all geocoding requests server-side to comply with Nominatim's [Usage Policy](https://operations.osmfoundation.org/policies/nominatim/): a `User-Agent` header is sent and requests are rate-limited to one per second.
- No API key or account is required.
- Coordinates are stored in the database after geocoding, so the map works offline once contacts are geocoded.

## License

MIT
