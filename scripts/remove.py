import subprocess

if __name__ == '__main__':
    #subprocess.call('ls .', shell=True)
    #subprocess.call('ls descriptions/tests/mux16dualtest999*', shell=True)
    for index in range(100,999):
        command = 'rm descriptions/tests/mux16dualtest'+str(index)+'*'
        try:
            subprocess.call(command, shell=True)
        except:
            print "failed rm for: " % command
