from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from sqlalchemy import or_
from models import Contact

search_bp = Blueprint('search', __name__)


@search_bp.route('/')
@login_required
def search():
    q = request.args.get('q', '').strip()
    results = []

    if q:
        term = f'%{q}%'
        results = (Contact.query
                   .filter_by(user_id=current_user.id)
                   .filter(or_(
                       Contact.name.ilike(term),
                       Contact.street.ilike(term),
                       Contact.city.ilike(term),
                       Contact.state.ilike(term),
                       Contact.country.ilike(term),
                       Contact.email.ilike(term),
                       Contact.phone.ilike(term),
                       Contact.postal_code.ilike(term),
                   ))
                   .order_by(Contact.name)
                   .all())

    return render_template('search/results.html', q=q, results=results)
