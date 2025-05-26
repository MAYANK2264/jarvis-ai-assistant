# Jarvis AI Website

This is the official website for the Jarvis AI project. It provides information about the project, documentation, and a live demo of the AI assistant.

## Features

- Modern, responsive design
- Interactive demo of Jarvis AI
- Comprehensive documentation
- Installation guide
- Mobile-friendly interface

## Local Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the development server:
```bash
python app.py
```

The site will be available at `http://localhost:5000`

## Deployment

### Deploying to Heroku

1. Create a new Heroku app:
```bash
heroku create jarvis-ai-website
```

2. Add the Python buildpack:
```bash
heroku buildpacks:set heroku/python
```

3. Deploy the application:
```bash
git push heroku main
```

### Deploying to Other Platforms

The website can be deployed to any platform that supports Python/Flask applications. Make sure to:

1. Set the appropriate environment variables
2. Configure the web server (e.g., Gunicorn)
3. Set up SSL certificates for HTTPS

## Project Structure

```
website/
├── app.py              # Flask application
├── requirements.txt    # Python dependencies
├── static/            # Static assets (CSS, JS, images)
├── templates/         # HTML templates
│   ├── base.html     # Base template
│   ├── index.html    # Home page
│   ├── demo.html     # Demo page
│   ├── docs.html     # Documentation
│   └── install.html  # Installation guide
└── README.md         # This file
```

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 