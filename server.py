import settings
from settings import SERVER
from shared.utilities import update_css
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
    documents = views.get_device_documents(device_type)
    context = {
        'status': 'success',
        'device': documents
    }
    return jsonify(**context)

    # abort(500) and errorhandler if failed

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tests')
def tests():
    tests = views.get_tests()
    context = {
        'status': 'success',
        'test_packages': tests
    }
    return jsonify(**context)

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
