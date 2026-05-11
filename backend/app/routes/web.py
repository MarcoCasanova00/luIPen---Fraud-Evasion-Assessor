from flask import Blueprint, render_template, jsonify, current_app
from .security.headers import set_cache_control

web_bp = Blueprint('web', __name__)


@web_bp.route('/')
def index():
    return render_template('index.html')


@web_bp.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'version': current_app.config.get('VERSION', '1.0.0'),
        'project': current_app.config.get('PROJECT_NAME', 'Fraud Evasion Penetration Testing Tool')
    })


@web_bp.route('/about')
def about():
    return render_template('about.html')


@web_bp.route('/static/<path:filename>')
def serve_static(filename):
    from flask import send_from_directory
    import os
    static_dir = os.path.join(current_app.root_path, 'static')
    response = send_from_directory(static_dir, filename)
    return set_cache_control(response, max_age=86400)