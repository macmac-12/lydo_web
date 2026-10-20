#!/usr/bin/env python
import argparse
import getpass
from app import create_app, db
from app.models import User


def main():
    parser = argparse.ArgumentParser(description='Create an admin user interactively')
    parser.add_argument('-u', '--username', help='Admin username')
    parser.add_argument('-p', '--password', help='Admin password (avoid on shared terminals)')
    parser.add_argument('--force', action='store_true', help='Create admin even if one exists')
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        existing_admin = User.query.filter_by(role='admin').first()
        if existing_admin and not args.force:
            print('An admin user already exists. Use --force to create another one.')
            return

        username = args.username or input('Admin username: ')
        password = args.password or getpass.getpass('Admin password: ')

        if not username or not password:
            print('Username and password are required.')
            return

        if User.query.filter_by(username=username).first():
            print('A user with that username already exists.')
            return

        user = User(username=username, role='admin')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f'Created admin user: {username}')


if __name__ == '__main__':
    main()
