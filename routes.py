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

        # Use parameterized query
        user = User.query.filter(User.username == username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Login failed. Check your credentials and try again.', 'danger')

    return render_template('login.html')


@main.route('/signup', methods=['GET', 'POST'])
def signup():
    flash('Signups are disabled.', 'danger')
    return redirect(url_for('main.login'))


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
                # check for blacklisted words
                elif any(word in short_url for word in ['admin', 'dashboard', 'login', 'signup', 'logout', 'url', 'urls', ":", "/", "?", "&", "=", "#", "!", "@", "$", "%", "^", "&", "*", "(", ")", "{", "}", "[", "]", "<", ">", "|", "\\", ";", "'", '"', "`", "~", ",", ".", " ", "\t", "\n", "\r", "\f", "\v"]):
                    flash('Custom URL contains blacklisted words. Please choose another one.', 'danger')
                else:
                    # if no change in any field, don't update the short_url
                    if url_mapping.custom_url != short_url:
                        url_mapping.custom_url = short_url
                        url_mapping.short_url = short_url
                        flash('URL updated successfully!', 'success')
                    else:
                        flash('No changes made!', 'info')
            db.session.commit()
            

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
    
@main.route('/admin/urls')
@login_required
def admin_urls():
    if current_user.id != 1:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.home'))

    # Query to get all URLs along with the user who created them and the number of clicks
    urls = URLMapping.query.all()
    url_data = []

    for url in urls:
        user = User.query.get(url.user_id)
        clicks_count = Click.query.filter_by(url_mapping_id=url.id).count()
        url_data.append({
            'short_url': url.short_url,
            'original_url': url.original_url,
            'created_by': user.username if user else'Unknown',
            'created_at': url.created_at,
            'clicks_count': clicks_count
        })

    return render_template('admin_urls.html', url_data=url_data)

@main.route('/<short_url>')
def redirect_url(short_url):
    # Use parameterized queries
    url_mapping = URLMapping.query.filter(
        (URLMapping.short_url == short_url) | 
        (URLMapping.custom_url == short_url)
    ).first()
    
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
        return render_template('404.html'), 404
    
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

@main.route('/dashboard')
@login_required
def dashboard():
    urls = URLMapping.query.filter_by(user_id=current_user.id).all()
    
    # Aggregating statistics
    total_clicks = sum(len(url.clicks) for url in urls)
    clicks_per_url = {url.short_url: len(url.clicks) for url in urls}

    # You can also add more detailed statistics like:
    clicks_by_country = {}
    for url in urls:
        for click in url.clicks:
            country = click.country
            clicks_by_country[country] = clicks_by_country.get(country, 0) + 1

    return render_template('dashboard.html', urls=urls, total_clicks=total_clicks, clicks_per_url=clicks_per_url, clicks_by_country=clicks_by_country)
