import time
import requests as req
from flask import Blueprint, request, jsonify, url_for
from flask_login import login_required, current_user
from models import Contact

geocode_bp = Blueprint('geocode', __name__)

NOMINATIM_URL = 'https://nominatim.openstreetmap.org/search'
_last_request_time = 0

HEADERS = {'User-Agent': 'AddressBookApp/1.0 (personal address manager)'}


def _rate_limit():
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < 1.0:
        time.sleep(1.0 - elapsed)
    _last_request_time = time.time()


def _extract_address(result):
    """Pull structured fields out of a Nominatim result with addressdetails=1."""
    addr = result.get('address', {})

    # Street: prefer road + house_number, fall back to display_name first segment
    road   = addr.get('road') or addr.get('pedestrian') or addr.get('footway') or ''
    house  = addr.get('house_number', '')
    street = (f'{house} {road}'.strip() if house else road) or ''

    city = (
        addr.get('city') or addr.get('town') or addr.get('village') or
        addr.get('municipality') or addr.get('county') or ''
    )
    state       = addr.get('state') or addr.get('province') or addr.get('region') or ''
    postal_code = addr.get('postcode') or ''
    country     = addr.get('country') or ''

    return {
        'display_name': result.get('display_name', ''),
        'street':       street,
        'city':         city,
        'state':        state,
        'postal_code':  postal_code,
        'country':      country,
        'lat':          float(result['lat']),
        'lon':          float(result['lon']),
    }


@geocode_bp.route('/suggest')
@login_required
def suggest():
    """Return up to 5 address suggestions with full structured fields."""
    q = request.args.get('q', '').strip()
    if len(q) < 3:
        return jsonify([])

    _rate_limit()
    try:
        resp = req.get(
            NOMINATIM_URL,
            params={'q': q, 'format': 'json', 'addressdetails': 1, 'limit': 5},
            headers=HEADERS,
            timeout=8
        )
        resp.raise_for_status()
        results = [_extract_address(r) for r in resp.json()]
        return jsonify(results)
    except req.exceptions.Timeout:
        return jsonify(error='Geocoding service timed out'), 504
    except Exception:
        return jsonify(error='Geocoding service unavailable'), 503


@geocode_bp.route('/geocode')
@login_required
def geocode():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify(error='No query provided'), 400

    _rate_limit()
    try:
        resp = req.get(
            NOMINATIM_URL,
            params={'q': q, 'format': 'json', 'addressdetails': 1, 'limit': 1},
            headers=HEADERS,
            timeout=8
        )
        resp.raise_for_status()
        data = resp.json()
        if data:
            return jsonify(_extract_address(data[0]))
        return jsonify(error='Address not found'), 404
    except req.exceptions.Timeout:
        return jsonify(error='Geocoding service timed out'), 504
    except Exception:
        return jsonify(error='Geocoding service unavailable'), 503


@geocode_bp.route('/contacts/geojson')
@login_required
def contacts_geojson():
    contacts = (Contact.query
                .filter_by(user_id=current_user.id)
                .filter(Contact.latitude.isnot(None), Contact.longitude.isnot(None))
                .all())

    features = []
    for c in contacts:
        features.append({
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [c.longitude, c.latitude]
            },
            'properties': {
                'id': c.id,
                'name': c.name,
                'address': c.display_address,
                'phone': c.phone or '',
                'email': c.email or '',
                'url': url_for('contacts.detail', id=c.id)
            }
        })

    return jsonify({'type': 'FeatureCollection', 'features': features})
