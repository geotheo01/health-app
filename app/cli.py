"""
Database Seeding Script for Administrative User Initialization.

This module provides a custom Flask Command Line Interface (CLI) command designed to 
initialize the database tables and insert a default administrator user. Within the 
MVC architecture of this web application, this script serves as a utility tool that 
interacts directly with the Database Layer (Models) to ensure system bootstrapping 
and administrative access upon deployment.
"""

import click
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash
from app import db
from app.models.user import User

@click.command('seed-admin')
@with_appcontext
def seed_admin_command():
    """
    Flask CLI command to seed the database with an initial administrator account.

    This function performs an idempotent seeding process:
    1. Ensures all defined database tables are created via SQLAlchemy ORM.
    2. Queries the database to verify if the default administrator already exists.
    3. If absent, creates and commits a new User record with hashed credentials 
       and administrative privileges.
    """
    # Ensure that all database tables defined in the ORM models exist prior to querying
    db.create_all()
    
    # Define default credentials for the system administrator account
    email = 'admin@smarthealth.local'
    
    # Check if an admin account with this email already exists to preserve idempotency
    existing_admin = User.query.filter_by(email=email).first()
    
    # If the admin already exists, abort the process to prevent duplicate record errors
    if existing_admin:
        click.echo(f'Admin user {email} already exists. Skipping.')
        return

    # Instantiate a new User model object with administrator privileges
    # Secure password hashing is applied using Werkzeug's security module
    admin = User(
        email=email,
        full_name='System Admin',
        password_hash=generate_password_hash('123'),
        role='admin',
        is_active=True
    )
    
    # Stage the new user object and commit the transaction to the database
    db.session.add(admin)
    db.session.commit()
    
    # Console feedback to inform the user that the operation succeeded
    click.echo(f'Successfully created admin user: {email}')
