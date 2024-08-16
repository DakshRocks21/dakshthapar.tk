from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import Click, db, User, URLMapping
import string
import random
import requests


main = Blueprint('main', __name__)

# Helper function to generate random short URLs
def generate_short_url(length=6):
    characters = string.ascii_letters + string.digits
    short_url = ''.join(random.choice(characters) for _ in range(length))
    return short_url

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Login failed. Check your credentials and try again.', 'danger')

    return render_template('login.html')

@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        user = User(username=username, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('main.login'))

    return render_template('signup.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))

@main.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        original_url = request.form['url']
        custom_url = request.form.get('custom_url')

        if custom_url:
            existing_custom = URLMapping.query.filter_by(custom_url=custom_url).first()
            if existing_custom:
                flash('Custom URL already exists, please choose another one.', 'danger')
                return render_template('index.html', urls=current_user.urls)

            short_url = custom_url
        else:
            short_url = generate_short_url()

        # Ensure the short URL is unique
        existing_url = URLMapping.query.filter_by(short_url=short_url).first()
        while existing_url:
            short_url = generate_short_url()
            existing_url = URLMapping.query.filter_by(short_url=short_url).first()

        # Save the new URL mapping to the database
        url_mapping = URLMapping(short_url=short_url, original_url=original_url, custom_url=custom_url, user_id=current_user.id)
        db.session.add(url_mapping)
        db.session.commit()

        flash('URL shortened successfully!', 'success')
        return redirect(url_for('main.home'))
    
    return render_template('index.html', urls=current_user.urls)

@main.route('/urls', methods=['GET', 'POST'])
@login_required
def view_urls():
    if request.method == 'POST':
        original_url = request.form['original_url']
        short_url = request.form['short_url']

        url_mapping = URLMapping.query.get(request.form['id'])
        if url_mapping and url_mapping.user_id == current_user.id:
            url_mapping.original_url = original_url
            if short_url:
                existing_custom = URLMapping.query.filter_by(custom_url=short_url).first()
                if existing_custom and existing_custom.id != url_mapping.id:
                    flash('Custom URL already exists, please choose another one.', 'danger')
                else:
                    url_mapping.custom_url = short_url
                    url_mapping.short_url = short_url
            db.session.commit()
            flash('URL updated successfully!', 'success')

        return redirect(url_for('main.view_urls'))

    urls = URLMapping.query.filter_by(user_id=current_user.id).all()
    return render_template('urls.html', urls=urls)

def get_country_from_ip(ip_address):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip_address}")
        data = response.json()
        return data.get('country', 'Unknown')
    except:
        return 'Unknown'

@main.route('/<short_url>')
def redirect_url(short_url):
    url_mapping = URLMapping.query.filter_by(short_url=short_url).first() or URLMapping.query.filter_by(custom_url=short_url).first()
    
    if url_mapping:
        # Track the click
        ip_address = request.remote_addr
        country = get_country_from_ip(ip_address)
        user_agent = request.headers.get('User-Agent')

        click = Click(ip_address=ip_address, country=country, user_agent=user_agent, url_mapping=url_mapping)
        db.session.add(click)
        db.session.commit()

        return redirect(url_mapping.original_url)
    else:
        return "URL not found", 404
    
@main.route('/url/<int:url_id>')
@login_required
def url_stats(url_id):
    url_mapping = URLMapping.query.get_or_404(url_id)
    
    if url_mapping.user_id != current_user.id:
        flash('You do not have access to this URL\'s statistics.', 'danger')
        return redirect(url_for('main.view_urls'))
    
    return render_template('url_stats.html', url_mapping=url_mapping)

@main.route('/url/logs')
@login_required
def all_logs():
    urls = URLMapping.query.filter_by(user_id=current_user.id).all()
    return render_template('all_logs.html', urls=urls)
