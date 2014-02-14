import settings
from settings import SERVER
from shared.utilities import update_css
from flask import Flask, jsonify, request, render_template

import views

app = Flask(__name__)

# URL routers
@app.route('/testkeyboard')
def test_keyboard():
    context = {}
    return render_template('test_keyboard.html', context=context)

@app.route('/cpuconsole')
def test_keyboard():
    context = {}
    return render_template('cpu_console.html', context=context)

@app.route('/cpu')
def cpu():
    context = views.cpu()
    return render_template('cpu.html', context=context)

@app.route('/cputest', methods=['GET', 'POST'])
def cputest():
    # if it is POST, then add a new program
    if request.method == 'POST':
        print request.files
        file = request.files['file']
        if file:
            name = file.filename
            data = file.read()
            document = {
                'name': name,
                'data': data
            }
            print "received document: {0}".format(document)
            views.new_binary(document)
    context = views.cputest()
    return render_template('cputest.html', context=context)

@app.route('/binary')
def binary():
    # if get, get it.
    filename = request.args.get('name','')
    context = views.binary(filename)
    return jsonify(**context)


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

@app.route('/test/<test_name>')
def test(test_name):
    test = views.get_test(test_name)
    context = {
        'status': 'success',
        'test_package': test
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
