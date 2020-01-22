"""
Controls the homepage
"""
from os import listdir
from os.path import isfile
from flask import render_template
from app.home import bp

@bp.route('/')
@bp.route('/index')
def index():
    """Landing page"""
    if isfile("app/home/templates/custom-index.html"):
        try:
            filelist = listdir("app/home/files")
        except FileNotFoundError:
            filelist = []
        return render_template('custom-index.html', title='Home', files=filelist)
    return render_template('index.html', title='Home')
