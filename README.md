# TV Shows App

A simple web application built with Flask that lets users explore TV shows, leave comments, and like or dislike their favorites. Registered users can unlock a secret page to manage their liked shows.

## Features

- **User Authentication**: Register, log in, and log out securely
- **Browse Shows**: View a list of available TV shows
- **Like/Dislike Shows**: Interact with shows by liking or disliking them
- **Commenting**: Leave comments on shows
- **Secret Page**: Logged-in users can access a hidden page that displays only their liked shows
- **Access Control**: Only users can comment, like, or access the secret content

## Technologies Used

- **Backend**: Python, Flask, HTML, CSS, Bootstrap
- **Database**: SQLite (via SQLAlchemy)
- **Authentication**: Flask-Login

## Installation

1. Clone the repository:

git clone https://github.com/mntrrycecilia/TVShows.git cd TVShows


2. Create and activate a virtual environment (optional but recommended):

python -m venv venv source venv/bin/activate # On Windows use venv\Scripts\activate


3. Install dependencies:

pip install -r requirements.txt


5. Open your browser and navigate to `http://localhost:5000`

## Usage

1. Register with a username and password
2. Log in to unlock full access to the app
3. Browse shows and click the like button to save favorites
4. Leave comments on your favorite shows
5. Visit the secret page to view your liked shows
6. Log out when you're done

## License

This project is for educational and personal use.

## Acknowledgements

- Flask
- SQLAlchemy
- Flask-Login
- Bootstrap
