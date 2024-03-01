from flask import Flask, request, jsonify, send_from_directory, abort
import re
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)

@app.route('/analyze-text', methods=['POST'])
def analyze_text():
    if 'file' not in request.files or 'string' not in request.form:
        return "Missing file or string", 400
    file = request.files['file']
    search_string = request.form['string'].lower()
    text = file.read().decode('utf-8')

    alphanumeric_count = len(re.findall(r'\w', text))
    occurrences = text.lower().count(search_string)

    response = {
        'length': len(text),
        'alphanumeric_count': alphanumeric_count,
        'occurrences_of_string': occurrences
    }

    return jsonify(response)

@app.route('/parse-url', methods=['POST'])
def parse_url():
    data = request.get_json()
    url = data.get('url', '')

    try:
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError("Invalid URL: Missing scheme or domain")

        domain = parsed_url.netloc
        path = parsed_url.path.lstrip('/').split('/') if parsed_url.path else []
        query_params = parse_qs(parsed_url.query)

        response = {
            'protocol': parsed_url.scheme,
            'domain': domain,
            'path_steps': path if path else ["No path specified"],
            'query_parameters': query_params if query_params else "No query parameters"
        }
    except ValueError as e:
        response = {'error': str(e)}

    return jsonify(response)

@app.route('/images/<path:filename>')
def serve_image(filename):
    try:
        return send_from_directory('static/images', filename)
    except FileNotFoundError:
        abort(404, description="Image not found")

@app.route('/')
def documentation():
    docs = {
        'endpoints': {
            '/analyze-text': 'POST - accepts a text file and a string, returns metadata about the file',
            '/parse-url': 'POST - accepts a url, returns a human-readable analysis',
            '/images/<filename>': 'GET - gets an image if it exists',
            '/': 'GET - returns this documentation'
        }
    }
    return jsonify(docs)

if __name__ == '__main__':
    app.run(debug=True)
