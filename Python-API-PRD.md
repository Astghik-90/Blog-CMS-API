# Blog/CMS REST API - Backend Technical Specification

## Project Overview

Build a REST API for a Blog/Content Management System using Flask, SQLAlchemy, and JWT authentication. This project will serve as the backend for a future React frontend application.

## Technology Stack

- **Framework**: Flask
- **Database ORM**: SQLAlchemy with Flask-SQLAlchemy
- **Authentication**: Flask-JWT-Extended
- **Database**: PostgreSQL (recommended) or MySQL
- **Migrations**: Flask-Migrate (Alembic)
- **Password Hashing**: Werkzeug or bcrypt

## User Roles & Permissions

### Author Role

- Create, read, update, and delete their posts
- Read all published posts
- Create, update, and delete their comments
- Update their profile

### Admin Role

- All Author permissions
- Removing other Users’ posts
- Manage users
  - Delete User
  - Make other Users Admin
- Manage categories
- Delete comments

### Authentication / User

- Login
- Sign Up
- Update Profile
- Remove themself

## Posts

- Should have Headings and then content
- Can have categories, even more than one

## Categories

- Can be created only by admins
- Seen and used by anyone (for posts)

## Comments

- Should be connected to posts
- All users can post comments

## Deliverables

1. **Functional REST API** with all specified functionality
2. **Setup instructions** and requirements file
