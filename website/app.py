from flask import Flask, render_template, jsonify, request
import os
import sys
from datetime import datetime

# Add the parent directory to sys.path to import from commands
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from commands.offline_ai import chat_with_gpt

app = Flask(__name__)

# Create static and templates directories if they don't exist
os.makedirs(os.path.join(app.root_path, 'static'), exist_ok=True)
os.makedirs(os.path.join(app.root_path, 'templates'), exist_ok=True)

# Context processor to add variables to all templates
@app.context_processor
def inject_year():
    return {'year': datetime.now().year}

# Route for the home page
@app.route('/')
def home():
    return render_template('index.html')

# Route for the documentation page
@app.route('/docs')
def docs():
    return render_template('docs.html')

# Route for the demo page
@app.route('/demo')
def demo():
    return render_template('demo.html')

# Route for the installation page
@app.route('/install')
def install():
    return render_template('install.html')

# API endpoint for the demo
@app.route('/api/demo', methods=['POST'])
def demo_api():
    command = request.json.get('command', '')
    ai_response = chat_with_gpt(command)
    return jsonify({
        'status': 'success',
        'response': ai_response
    })

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True) 