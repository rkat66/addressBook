from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from extensions import db
from models import Contact

contacts_bp = Blueprint('contacts', __name__)


@contacts_bp.route('/')
@login_required
def index():
    return redirect(url_for('contacts.list_contacts'))


@contacts_bp.route('/contacts')
@login_required
def list_contacts():
    sort = request.args.get('sort', 'name')
    direction = request.args.get('dir', 'asc')
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('CONTACTS_PER_PAGE', 20)

    sort_columns = {
        'name': Contact.name,
        'city': Contact.city,
        'country': Contact.country,
        'email': Contact.email,
    }
    col = sort_columns.get(sort, Contact.name)
    order = col.asc() if direction == 'asc' else col.desc()

    pagination = (Contact.query
                  .filter_by(user_id=current_user.id)
                  .order_by(order)
                  .paginate(page=page, per_page=per_page, error_out=False))
    return render_template(
        'contacts/list.html',
        pagination=pagination,
        contacts=pagination.items,
        sort=sort,
        direction=direction,
    )


def _check_duplicate_phone(phone, exclude_id=None):
    """Return conflicting contact for the current user, or None."""
    if not phone:
        return None
    q = Contact.query.filter_by(user_id=current_user.id).filter(Contact.phone == phone)
    if exclude_id:
        q = q.filter(Contact.id != exclude_id)
    return q.first()


@contacts_bp.route('/contacts/new', methods=['GET', 'POST'])
@login_required
def new_contact():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Name is required.', 'error')
            return render_template('contacts/form.html', contact=None, action='Add')

        phone = request.form.get('phone', '').strip() or None
        duplicate = _check_duplicate_phone(phone)
        if duplicate:
            flash(
                f'Phone number {phone} is already used by '
                f'<a href="{url_for("contacts.detail", id=duplicate.id)}">'
                f'{duplicate.name}</a>.',
                'error'
            )
            return render_template('contacts/form.html', contact=None, action='Add')

        contact = Contact(
            user_id=current_user.id,
            name=name,
            street=request.form.get('street', '').strip() or None,
            city=request.form.get('city', '').strip() or None,
            state=request.form.get('state', '').strip() or None,
            postal_code=request.form.get('postal_code', '').strip() or None,
            country=request.form.get('country', '').strip() or None,
            phone=phone,
            email=request.form.get('email', '').strip() or None,
        )

        lat = request.form.get('latitude', '').strip()
        lon = request.form.get('longitude', '').strip()
        if lat and lon:
            try:
                contact.latitude = float(lat)
                contact.longitude = float(lon)
            except ValueError:
                pass

        db.session.add(contact)
        db.session.commit()
        flash(f'Contact "{contact.name}" added successfully.', 'success')
        return redirect(url_for('contacts.list_contacts'))

    return render_template('contacts/form.html', contact=None, action='Add')


@contacts_bp.route('/contacts/<int:id>')
@login_required
def detail(id):
    contact = Contact.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    return render_template('contacts/detail.html', contact=contact)


@contacts_bp.route('/contacts/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_contact(id):
    contact = Contact.query.filter_by(id=id, user_id=current_user.id).first_or_404()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Name is required.', 'error')
            return render_template('contacts/form.html', contact=contact, action='Edit')

        phone = request.form.get('phone', '').strip() or None
        duplicate = _check_duplicate_phone(phone, exclude_id=contact.id)
        if duplicate:
            flash(
                f'Phone number {phone} is already used by '
                f'<a href="{url_for("contacts.detail", id=duplicate.id)}">'
                f'{duplicate.name}</a>.',
                'error'
            )
            return render_template('contacts/form.html', contact=contact, action='Edit')

        contact.name        = name
        contact.street      = request.form.get('street', '').strip() or None
        contact.city        = request.form.get('city', '').strip() or None
        contact.state       = request.form.get('state', '').strip() or None
        contact.postal_code = request.form.get('postal_code', '').strip() or None
        contact.country     = request.form.get('country', '').strip() or None
        contact.phone       = phone
        contact.email       = request.form.get('email', '').strip() or None

        lat = request.form.get('latitude', '').strip()
        lon = request.form.get('longitude', '').strip()
        if lat and lon:
            try:
                contact.latitude  = float(lat)
                contact.longitude = float(lon)
            except ValueError:
                contact.latitude  = None
                contact.longitude = None
        else:
            contact.latitude  = None
            contact.longitude = None

        db.session.commit()
        flash(f'Contact "{contact.name}" updated successfully.', 'success')
        return redirect(url_for('contacts.detail', id=contact.id))

    return render_template('contacts/form.html', contact=contact, action='Edit')


@contacts_bp.route('/contacts/<int:id>/delete', methods=['POST'])
@login_required
def delete_contact(id):
    contact = Contact.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    name = contact.name
    db.session.delete(contact)
    db.session.commit()
    flash(f'Contact "{name}" deleted.', 'success')
    return redirect(url_for('contacts.list_contacts'))


@contacts_bp.route('/map')
@login_required
def map_view():
    contacts = (Contact.query
                .filter_by(user_id=current_user.id)
                .order_by(Contact.name)
                .all())
    return render_template('map/view.html', contacts=contacts)
