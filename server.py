import settings
from settings import SERVER
from utilities import update_css
from flask import Flask, jsonify, request, render_template

import views

app = Flask(__name__)

# URL routers
@app.route('/cpu')
def cpu():
    context = views.cpu()
    return render_template('cpu.html', context=context)

@app.route('/hardware')
def hardware():
    context = views.hardware()
    return render_template('hardware.html', context = context)

@app.route('/device')
def device():
    device_type = request.args.get('type','')
    document = views.get_device(device_type)
    context = {
        'status': 'success',
        'device': document
    }
    return jsonify(**context)

    # abort(500) and errorhandler if failed

@app.route('/')
def index():
    return render_template('index.html')

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
