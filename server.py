import settings
from settings import SERVER
from utilities import update_css
from flask import Flask

import views

app = Flask(__name__)

# URL routers
@app.route('/cpu')
def cpu():
    return views.cpu()

@app.route('/hardware')
def hardware():
    return views.hardware()

@app.route('/')
def index():
    return views.index()

# Before request is sent
@app.before_request
def before_request():
    if settings.DEBUG:
        update_css()

#@app.template_filter('settings')
def get_settings():
    return settings

if __name__ == '__main__':
    if settings.DEBUG:
        app.debug = True

    app.jinja_env.globals.update(get_settings=get_settings)
    app.run(host=SERVER['HOST'], port=SERVER['PORT'])
