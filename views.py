from flask import render_template
from settings import CPU

def cpu():
    # Include settings
    context = {
        'CPU' : CPU
    }
    return render_template('cpu.html', context=context)

def index():
    return render_template('index.html')
