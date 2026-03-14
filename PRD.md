# Product Requirements Document
## Address Book Application

**Version:** 1.0
**Date:** March 14, 2026
**Status:** Implemented

---

## 1. Overview

### 1.1 Purpose

Address Book is a web application for storing, searching, and visualizing contact information with international address support. It is designed for individuals or small teams who need a self-hosted, browser-accessible contact manager with map-based geographic visualization.

### 1.2 Goals

- Provide a fast, simple interface for managing contacts with full international address support
- Eliminate duplicate contacts via phone number uniqueness enforcement
- Enable geographic visualization of contacts on an interactive world map
- Require zero third-party accounts or API keys — all geocoding powered by OpenStreetMap

### 1.3 Non-Goals

- Not a multi-user or multi-tenant system (no authentication or access control in v1)
- Not a CRM — no notes, tasks, activity history, or relationship tracking
- Not a mobile app — web only
- Not a cloud service — self-hosted on the user's machine or server

---

## 2. Users

### 2.1 Primary User

An individual (professional or personal) who maintains a list of contacts across multiple countries and wants to:

- Quickly look up a contact's address, phone, or email
- Visualize where their contacts are located geographically
- Add contacts without manually looking up latitude/longitude

### 2.2 Assumptions

- Single user; no login required
- User has access to a machine capable of running Python 3.9+
- User has an internet connection for geocoding and map tile loading

---

## 3. Features

### 3.1 Contact Management

#### 3.1.1 Add Contact
- User can create a new contact from a form
- Required field: **Full Name**
- Optional fields: Street Address, City, State/Province, Postal Code, Country, Phone, Email, Latitude, Longitude
- On submit, the contact is saved to the database and the user is redirected to the contact list with a success message

#### 3.1.2 Edit Contact
- User can edit any field of an existing contact
- The form is pre-populated with existing values
- On submit, changes are saved and the user is redirected to the contact detail page

#### 3.1.3 Delete Contact
- User can delete a contact from the edit form or the contact list
- A confirmation dialog is shown before deletion to prevent accidental data loss
- On confirmation, the contact is permanently removed

#### 3.1.4 View Contact Detail
- Displays all stored fields for a single contact
- If coordinates are stored, shows a mini interactive map centered on the contact's location
- Provides links to edit the contact or return to the list

### 3.2 International Address Support

The address model supports any international address format through discrete, optional fields:

| Field | Description |
|---|---|
| Street | Street name and number, including apartment or suite |
| City | City, town, or locality |
| State / Province | State, province, prefecture, canton, or equivalent |
| Postal Code | ZIP code, postcode, PIN, or equivalent |
| Country | Country name in any language |

No field is required except Name, allowing partial addresses from any country's format.

### 3.3 Address Autocomplete and Geocoding

#### 3.3.1 Street Field Autocomplete
- As the user types in the Street Address field (minimum 3 characters), a dropdown appears with up to 5 address suggestions sourced from Nominatim/OpenStreetMap
- Suggestions include the full display name for disambiguation
- Selecting a suggestion automatically fills in: Street, City, State/Province, Postal Code, Country, Latitude, Longitude
- Keyboard navigation: Arrow keys to move through suggestions, Enter to select, Escape to close
- 400ms debounce prevents excessive API calls while typing

#### 3.3.2 Manual Geocode Button
- A "Geocode Address" button assembles all address fields and queries Nominatim
- On success, fills in Latitude, Longitude, and any empty address fields returned by the geocoder
- Displays a status message (success, not found, or service unavailable)

#### 3.3.3 Geocoding Infrastructure
- All geocoding requests are proxied server-side (never directly from the browser)
- Nominatim's 1 request/second rate limit is enforced in the server proxy
- A `User-Agent` header identifying the application is sent on every request, per Nominatim's usage policy
- Coordinates are stored persistently in the database after geocoding; the map does not require re-geocoding on each visit

### 3.4 Contact List

- Displays all contacts in a paginated table (20 per page by default)
- Columns: Name, City, Country, Email, Phone, Geocoded status indicator, Actions
- Each column header (Name, City, Country, Email) is clickable to sort ascending or descending
- Geocoded status shows a filled green pin icon if coordinates are stored, or a grey outline pin if not
- Edit and Delete actions available inline per row
- Empty state prompts the user to add their first contact

### 3.5 Search

- A search bar is available in the navbar on every page for quick access
- A dedicated Search page provides a full-page search experience
- Search is case-insensitive and matches any substring across: Name, Street, City, State, Country, Email, Phone, Postal Code
- Results are displayed in the same table format as the contact list
- Shows a result count and the query term
- Shows a prompt message if no query has been entered
- Shows a "no results" message with an "Add contact" link if the query returns nothing

### 3.6 Map View

#### 3.6.1 Layout
- Full-screen split layout: collapsible sidebar on the left, interactive map on the right
- The map fills the remaining viewport height below the navbar

#### 3.6.2 Sidebar
- Lists all contacts sorted alphabetically by name
- Each row shows name, address summary, and geocoded status icon
- A filter input at the top filters the sidebar list by name in real time, showing a `visible / total` count
- Clicking a geocoded contact: map flies smoothly to the marker and opens its popup
- Clicking a non-geocoded contact: a toast notification appears with a direct link to edit and geocode the contact

#### 3.6.3 Map Markers
- A marker is plotted for every contact with stored coordinates
- Clicking a marker opens a popup showing: Name, Address, Phone (with `tel:` link), Email (with `mailto:` link), and a "View Detail" link
- On load, the map auto-fits its zoom and pan to show all markers
- Tile layer: OpenStreetMap (free, no API key)

### 3.7 Phone Number Uniqueness

- Phone number is enforced as unique across all contacts at the database level
- Before saving (on both add and edit), the application checks for an existing contact with the same phone number
- If a duplicate is found, an error message is shown that names the conflicting contact and links to their detail page
- Empty/blank phone numbers are not subject to the uniqueness constraint (multiple contacts may have no phone)

---

## 4. Data Model

### Contact

| Field | Type | Constraints | Description |
|---|---|---|---|
| id | Integer | Primary key | Auto-incremented unique identifier |
| name | String(200) | Required, indexed | Full name |
| street | String(300) | Optional | Street address |
| city | String(100) | Optional, indexed | City or locality |
| state | String(100) | Optional | State, province, or equivalent |
| postal_code | String(20) | Optional | Postal or ZIP code |
| country | String(100) | Optional, indexed | Country |
| phone | String(50) | Optional, unique | Phone number |
| email | String(150) | Optional, indexed | Email address |
| latitude | Float | Optional | Decimal latitude (-90 to 90) |
| longitude | Float | Optional | Decimal longitude (-180 to 180) |
| created_at | DateTime | Auto | Record creation timestamp (UTC) |
| updated_at | DateTime | Auto | Last modification timestamp (UTC) |

---

## 5. API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/` | Redirect to contact list |
| GET | `/contacts` | Paginated, sortable contact list |
| GET/POST | `/contacts/new` | Add contact form and submission |
| GET | `/contacts/<id>` | Contact detail view |
| GET/POST | `/contacts/<id>/edit` | Edit contact form and submission |
| POST | `/contacts/<id>/delete` | Delete contact |
| GET | `/map` | Full-screen map view |
| GET | `/search` | Search form and results |
| GET | `/api/suggest?q=` | Address autocomplete suggestions (up to 5) |
| GET | `/api/geocode?q=` | Geocode a single address query |
| GET | `/api/contacts/geojson` | All geocoded contacts as GeoJSON FeatureCollection |

---

## 6. Technical Requirements

### 6.1 Stack

| Component | Technology |
|---|---|
| Language | Python 3.9+ |
| Web framework | Flask 3.1+ |
| ORM | SQLAlchemy 2.0+ via Flask-SQLAlchemy |
| Database | SQLite (default); PostgreSQL-compatible via `DATABASE_URL` |
| Maps | Leaflet.js 1.9 + OpenStreetMap tiles |
| Geocoding | Nominatim (OpenStreetMap) |
| UI | Bootstrap 5.3 + Bootstrap Icons 1.11 |
| HTTP client | Python `requests` library (server-side Nominatim proxy) |

### 6.2 Browser Support

Any modern browser with JavaScript enabled (Chrome, Firefox, Safari, Edge).

### 6.3 Configuration

| Variable | Default | Description |
|---|---|---|
| `FLASK_ENV` | `development` | `development` or `production` |
| `SECRET_KEY` | Insecure default | Must be overridden in production |
| `DATABASE_URL` | SQLite file in project dir | SQLAlchemy URI for production databases |
| `CONTACTS_PER_PAGE` | 20 | Number of contacts per page on the list view |

### 6.4 Performance

- Contact list is paginated to avoid loading unbounded rows
- Geocoding results are cached in the database; no live geocoding occurs during map or list page loads
- Street autocomplete uses a 400ms debounce to limit Nominatim requests

---

## 7. Non-Functional Requirements

| Requirement | Target |
|---|---|
| Nominatim compliance | ≤ 1 request/second, valid User-Agent header sent on all geocoding requests |
| Data persistence | All contact data stored in SQLite (or configured database); survives application restarts |
| Input validation | Name required on add/edit; phone uniqueness checked before write; lat/lon parsed as floats |
| XSS prevention | All user-supplied data escaped in templates via Jinja2 auto-escaping and explicit `esc()` in JavaScript |
| Error handling | Geocoding failures (timeout, not found, service down) shown to user as non-blocking status messages |

---

## 8. Future Considerations

The following are out of scope for v1 but are natural extensions:

- **Authentication** — login/logout to protect the address book from unauthorized access when hosted on a server
- **Import / Export** — bulk import from CSV or vCard (.vcf); export to CSV or vCard
- **Contact photo** — upload or link a profile photo per contact
- **Groups / Tags** — categorize contacts (family, work, etc.) with filterable tags
- **Duplicate detection** — warn when a new contact's name closely matches an existing one
- **Database migrations** — Alembic integration to handle schema changes without data loss
- **Mobile layout** — responsive design improvements for small screens, particularly the map/sidebar split
- **Offline map tiles** — cached tile layer for use without internet access
