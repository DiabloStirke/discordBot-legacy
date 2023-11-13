from app.app import app, db
import argparse
from app.models import User, RoleEnum

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the Flask app')
    parser.add_argument('--db-create-all', action='store_true',
                        help='Create all tables in the database')
    parser.add_argument('--create-admin', action='store',
                        help='Create an admin user with the given discord id')
    args = parser.parse_args()

    if args.db_create_all:
        with app.app_context():
            db.create_all()

    if args.create_admin:
        with app.app_context():
            user = User.get_by_id(args.create_admin)
            if user:
                user.update(role=RoleEnum.ADMIN)
            else:
                User.new(args.create_admin, role=RoleEnum.ADMIN)

    app.run('0.0.0.0', 8000, debug=True)
