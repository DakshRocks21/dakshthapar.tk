# URL Shortener - Powering [go.dakshthapar.com](https://go.dakshthapar.com)

## Overview

This project is a full-fledged URL shortening service designed to be user-friendly, secure, and highly customizable. It enables users to create short and custom URLs, track the number of clicks, and view detailed analytics on URL usage, including geographical location of clicks, user agents, and more. The service is built using Flask, SQLAlchemy, and Flask-Login for user authentication and session management.

## Key Features

- **User Authentication:** Secure user management with login, logout, and session handling. The system uses hashed passwords for added security.
- **URL Shortening:** Users can create short URLs with randomly generated strings or custom aliases. The system ensures that each short URL is unique and does not contain blacklisted words or characters.
- **Click Tracking:** Each URL tracks the number of clicks, along with the IP address, country, and user agent of the visitor. This data is stored in the database for later analysis.
- **Admin Interface:** Admin users can view all URLs created by all users, along with the number of clicks each URL has received. Regular users can only view and manage their own URLs.
- **Dashboard:** A user-specific dashboard displays aggregated statistics, including the total number of clicks, clicks per URL, and clicks by country.
- **Custom URL Alias:** Users can choose a custom alias for their URLs, allowing for branded and memorable links.
- **Responsive Design:** The service is designed to be fully responsive and works seamlessly across different devices and screen sizes.

## Environment and Deployment

To set up and run the service, make sure to configure your environment and then simply run:

```bash
docker-compose up
```
This command will launch the service with all the necessary components, including the database and the web server.

## Contribution
This project powers go.dakshthapar.com and is actively maintained. Contributions are welcome through pull requests. Please ensure that all new features include appropriate tests and documentation.

## License
This project is licensed under the MIT License. Feel free to use, modify, and distribute it as per the terms of the license.
