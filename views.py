from flask import render_template
from settings import CPU
from database import database

def cpu():
    # Include settings
    context = {
        'CPU' : CPU
    }
    return render_template('cpu.html', context=context)

def hardware():
    device_types = database()['devices'].find({},{'type':1})
    context = {'device_types': device_types}
    return render_template('hardware.html', context = context)

def index():
    return render_template('index.html')
