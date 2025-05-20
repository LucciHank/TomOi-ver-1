# TomOi - Web Application

## Overview
TomOi is a Django-based web application that integrates features like user accounts, blog, dashboard, payment processing, and an online store. The platform utilizes AI capabilities through Google's Generative AI, OpenAI, and Anthropic services.

## Features
- **User Account Management**: Registration, authentication, and profile management
- **Dashboard**: Admin and user dashboards with analytics
- **Blog System**: Content management system
- **Payment Processing**: Secure online payment integration
- **Store**: E-commerce functionality
- **AI Integration**: Chatbot and intelligent features

## Technology Stack
- **Backend**: Django 5.1.7
- **Database**: SQLite (development)
- **Frontend**: HTML, CSS, JavaScript
- **AI Services**: Google Generative AI, OpenAI, Anthropic
- **Additional Libraries**: See requirements.txt for a full list

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment tool (venv, virtualenv)

### Installation
1. Clone the repository:
   ```
   git clone https://github.com/LucciHank/TomOi-ver-1.git
   cd TomOi-ver-1
   ```

2. Create a virtual environment:
   ```
   python -m venv .venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```
     .venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source .venv/bin/activate
     ```

4. Install dependencies:
   ```
   pip install -r tomoi/requirements.txt
   ```

5. Run migrations:
   ```
   cd tomoi
   python manage.py migrate
   ```

6. Start the development server:
   ```
   python manage.py runserver
   ```

7. Access the application at `http://127.0.0.1:8000/`

## Configuration
- Create a `.env` file in the project root for environment variables
- Configure AI service credentials in `chatbot_settings.json` 

## Project Structure
- `accounts/`: User authentication and profile management
- `blog/`: Blog functionality
- `dashboard/`: Admin and user dashboard
- `payment/`: Payment processing
- `store/`: E-commerce functionality
- `media/`: User uploaded files
- `static/`: Static assets
- `templates/`: HTML templates
- `tomoi/`: Project core settings

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License
[Specify your license here]

## Contact
[Your contact information]