from settings import LESS_DIR, CSS_DIR
import shlex
import subprocess

def update_css():
    '''
    If any less files changed, recompile css.
    Currently does not suport subdirectories.
    '''
    names = {}
    for filepath in LESS_DIR.files('*.less'):
        name = filepath.name.split('.')[0]
        names[name] = filepath

    for name in names:
        css_path = CSS_DIR / (name + '.css')
        if css_path.exists():
            css_time = css_path.getmtime()
        else:
            css_time = -1  # no css file, so create it
        less_path = names[name]
        if less_path.getmtime() >= css_time:
            command = "recess {0} --compress".format(less_path)
            print "calling command: {0}".format(command)
            process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, shell=False)
            (stdout, stderr) = process.communicate()
            exit_status = process.wait()
            if exit_status != 0 or stderr:
                print "Error during compilation of less: {0}".format(less_path)
                continue
            with open(css_path, 'w') as css_file:
                css_file.write(stdout)
            #print "calling recess on {0} and {1}".format(less_path, css_path)
            #subprocess.call(['recess', less_path, '--compress', '>', css_path], shell=False)
