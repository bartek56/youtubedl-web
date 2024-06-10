from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/index.html')
def index():
    return render_template('index.html')