import os
from flask import Blueprint, render_template, request, redirect, url_for, current_app, abort, flash
from werkzeug.utils import secure_filename
from .models import db, Organization, YouthProfile, Official, User, LydoStructure
from flask_login import login_user, logout_user, login_required, current_user
from . import limiter
from .models import User
from flask import get_flashed_messages

main = Blueprint('main', __name__)

@main.route('/')
def index():
    lydo_structure = LydoStructure.query.first()
    return render_template('index.html', lydo_structure=lydo_structure)

@main.route('/ryo')
def ryo_directory():
    orgs = Organization.query.all()
    return render_template('ryo.html', orgs=orgs)

@main.route('/profiling', methods=['GET', 'POST'])
def profiling():
    if request.method == 'POST':
        if not current_user.is_authenticated:
            return redirect(url_for('main.login', next=url_for('main.profiling')))

        new_youth = YouthProfile(
            full_name=request.form.get('name'),
            barangay=request.form.get('barangay'),
            education=request.form.get('education'),
            employment=request.form.get('employment')
        )
        db.session.add(new_youth)
        db.session.commit()
        flash('Profile registered successfully', 'success')
        return redirect(url_for('main.index'))
    return render_template('profiling.html')


@main.route('/ryo/add', methods=['GET', 'POST'])
@login_required
def add_organization():
    # both admin and normal authenticated users can add organizations
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        mission = request.form.get('mission')
        president = request.form.get('president')
        vice_president = request.form.get('vice_president')
        secretary = request.form.get('secretary')
        members = request.form.get('members')
        if not name:
            flash('Organization name is required', 'danger')
            return redirect(url_for('main.add_organization'))
        org = Organization(name=name, category=category, mission=mission, president=president, vice_president=vice_president, secretary=secretary, members=members)
        db.session.add(org)
        db.session.commit()
        flash('Organization added', 'success')
        return redirect(url_for('main.ryo_directory'))
    return render_template('add_org.html')


@main.route('/admin/edit-org/<int:org_id>', methods=['GET', 'POST'])
@login_required
def edit_organization(org_id):
    if not current_user.is_admin:
        abort(403)
    org = Organization.query.get_or_404(org_id)
    if request.method == 'POST':
        org.name = request.form.get('name')
        org.category = request.form.get('category')
        org.mission = request.form.get('mission')
        org.president = request.form.get('president')
        org.vice_president = request.form.get('vice_president')
        org.secretary = request.form.get('secretary')
        org.members = request.form.get('members')
        db.session.commit()
        flash('Organization updated', 'success')
        return redirect(url_for('main.ryo_directory'))
    return render_template('edit_org.html', org=org)


@main.route('/admin/delete-org/<int:org_id>', methods=['POST'])
@login_required
def delete_organization(org_id):
    if not current_user.is_admin:
        abort(403)
    org = Organization.query.get_or_404(org_id)
    db.session.delete(org)
    db.session.commit()
    flash('Organization deleted', 'info')
    return redirect(url_for('main.ryo_directory'))

@main.route('/dashboard')
def dashboard():
    stats = db.session.query(YouthProfile.barangay, db.func.count(YouthProfile.id)).group_by(YouthProfile.barangay).all()
    labels = [s[0] for s in stats]
    values = [s[1] for s in stats]
    lydo_structure = LydoStructure.query.first()
    return render_template('dashboard.html', labels=labels, values=values, lydo_structure=lydo_structure)


@main.route('/login', methods=['GET', 'POST'])
@limiter.limit('5 per minute')
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html')


@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@main.route('/register', methods=['GET', 'POST'])
@limiter.limit('2 per minute')
def register():
    # Guarded registration: only allow creating the first admin when none exists
    existing_admin = User.query.filter_by(role='admin').first()
    if existing_admin:
        flash('Admin already exists. Registration is closed.', 'warning')
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            flash('Username and password are required', 'danger')
            return redirect(url_for('main.register'))

        if User.query.filter_by(username=username).first():
            flash('User already exists', 'warning')
            return redirect(url_for('main.register'))

        new_user = User(username=username, role='admin')
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Admin account created. Please sign in.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html')


@main.route('/admin/users')
@login_required
def users():
    if not current_user.is_admin:
        abort(403)
    all_users = User.query.order_by(User.username).all()
    return render_template('users.html', users=all_users)


@main.route('/admin/create-user', methods=['GET', 'POST'])
@login_required
def create_user():
    if not current_user.is_admin:
        abort(403)
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role') or 'user'
        if not username or not password:
            flash('Username and password are required', 'danger')
            return redirect(url_for('main.create_user'))

        existing = User.query.filter_by(username=username).first()
        if existing:
            flash('User already exists', 'warning')
            return redirect(url_for('main.create_user'))

        new_user = User(username=username, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash(f'Created user {username}', 'success')
        return redirect(url_for('main.users'))

    return render_template('create_user.html')


@main.route('/admin/edit-user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.is_admin:
        abort(403)
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        username = request.form.get('username')
        role = request.form.get('role') or 'user'
        password = request.form.get('password')
        email = request.form.get('email')
        if username:
            user.username = username
        user.role = role
        user.email = email
        if password:
            user.set_password(password)
        db.session.commit()
        flash('User updated', 'success')
        return redirect(url_for('main.users'))
    return render_template('edit_user.html', user=user)


@main.route('/admin/delete-user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        abort(403)
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted', 'info')
    return redirect(url_for('main.users'))


@main.route('/profile/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old = request.form.get('old_password')
        new = request.form.get('new_password')
        if not current_user.check_password(old):
            flash('Current password incorrect', 'danger')
            return redirect(url_for('main.change_password'))
        current_user.set_password(new)
        db.session.commit()
        flash('Password changed', 'success')
        return redirect(url_for('main.index'))
    return render_template('change_password.html')


@main.route('/confirm/<token>')
def confirm_email(token):
    email_or_username = User.confirm_token(token)
    if not email_or_username:
        flash('Confirmation link is invalid or expired.', 'danger')
        return redirect(url_for('main.index'))
    user = User.query.filter((User.email == email_or_username) | (User.username == email_or_username)).first()
    if not user:
        flash('User not found for confirmation.', 'warning')
        return redirect(url_for('main.index'))
    user.confirmed = True
    db.session.commit()
    flash('Email confirmed. Thank you!', 'success')
    return redirect(url_for('main.login'))

# --- OFFICIALS SECTION ---

@main.route('/officials')
def meet_leaders():  # <--- This MUST be named exactly 'meet_leaders'
    leaders = Official.query.all()
    return render_template('officials.html', leaders=leaders)

@main.route('/admin/add-official', methods=['GET', 'POST'])
@login_required
def add_official():  # <--- This MUST be named exactly 'add_official'
    if not current_user.is_admin:
        abort(403)
    if request.method == 'POST':
        name = request.form.get('name')
        barangay = request.form.get('barangay')
        file = request.files.get('photo')

        # Prevent duplicate officials for the same barangay
        if barangay:
            existing = Official.query.filter_by(barangay=barangay).first()
            if existing:
                flash('An official for this barangay already exists.', 'danger')
                return redirect(url_for('main.add_official'))

        if file and name:
            filename = secure_filename(f"{barangay}_{name}.jpg")
            upload_path = os.path.join(current_app.root_path, 'static', 'portraits')
            
            # Create the folder if it doesn't exist
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
                
            file.save(os.path.join(upload_path, filename))
            
            new_official = Official(name=name, barangay=barangay, photo_url=filename)
            db.session.add(new_official)
            db.session.commit()
            return redirect(url_for('main.meet_leaders'))
            
    return render_template('add_official.html')


@main.route('/admin/edit-official/<int:official_id>', methods=['GET', 'POST'])
@login_required
def edit_official(official_id):
    if not current_user.is_admin:
        abort(403)
    official = Official.query.get_or_404(official_id)
    if request.method == 'POST':
        name = request.form.get('name')
        barangay = request.form.get('barangay')
        file = request.files.get('photo')

        # Prevent duplicate barangay assignment (exclude current official)
        if barangay:
            existing = Official.query.filter(Official.barangay == barangay, Official.id != official.id).first()
            if existing:
                flash('An official for this barangay already exists.', 'danger')
                return redirect(url_for('main.edit_official', official_id=official.id))

        if file and name:
            filename = secure_filename(f"{barangay}_{name}.jpg")
            upload_path = os.path.join(current_app.root_path, 'static', 'portraits')
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
            file.save(os.path.join(upload_path, filename))
            official.photo_url = filename

        official.name = name
        official.barangay = barangay
        db.session.commit()
        flash('Official updated', 'success')
        return redirect(url_for('main.meet_leaders'))

    return render_template('edit_official.html', official=official)


@main.route('/admin/delete-official/<int:official_id>', methods=['POST'])
@login_required
def delete_official(official_id):
    if not current_user.is_admin:
        abort(403)
    official = Official.query.get_or_404(official_id)
    # remove portrait file if exists
    if official.photo_url:
        try:
            os.remove(os.path.join(current_app.root_path, 'static', 'portraits', official.photo_url))
        except Exception:
            pass
    db.session.delete(official)
    db.session.commit()
    flash('Official deleted', 'info')
    return redirect(url_for('main.meet_leaders'))


@main.route('/admin/lydo-structure', methods=['GET', 'POST'])
@login_required
def lydo_structure():
    if not current_user.is_admin:
        abort(403)
    
    structure = LydoStructure.query.first()
    if not structure:
        structure = LydoStructure()
        db.session.add(structure)
        db.session.commit()
    
    if request.method == 'POST':
        structure.lydo_head = request.form.get('lydo_head')
        # Get admin staff as comma-separated values
        admin_staff_input = request.form.get('admin_staff', '').strip()
        structure.admin_staff = admin_staff_input
        structure.lydc_members = request.form.get('lydc_members')
        db.session.commit()
        flash('LYDO Organizational Structure updated', 'success')
        return redirect(url_for('main.lydo_structure'))
    
    return render_template('lydo_structure.html', structure=structure)