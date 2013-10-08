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
    devices = database()['devices'].find({},{'type':1})
    context = {'devices': devices}
    return render_template('hardware.html', context = context)

def index():
    return render_template('index.html')
