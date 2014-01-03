import re
regex = re.compile('[a-zA-Z0-9]+')
m = regex.match('hello john')
m.group() # hello
l = regex.findall('hello john') # ['hello', 'john']

