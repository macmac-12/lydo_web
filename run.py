from app import create_app
import os

app = create_app()


def ensure_admin_user():
    env_user = os.environ.get('ADMIN_USER')
    env_pass = os.environ.get('ADMIN_PASS')
    # Do NOT create a default weak admin account. Only create admin when env vars provided.

    from app.models import User
    from app import db

    with app.app_context():
        # Only create an admin user when both env vars are provided.
        if env_user and env_pass:
            existing = User.query.filter_by(username=env_user).first()
            if not existing:
                user = User(username=env_user, role='admin')
                user.set_password(env_pass)
                db.session.add(user)
                db.session.commit()
                print(f'Created admin user from env: {env_user}')
        else:
            # Do not create any default admin. Notify the operator.
            print('No ADMIN_USER/ADMIN_PASS provided; no admin user was created.\n' \
                  'Create an admin by setting ADMIN_USER and ADMIN_PASS before starting,\n' \
                  'or create one via the Manage Users UI after logging in as an existing admin.')


if __name__ == '__main__':
    ensure_admin_user()
    app.run(debug=True)