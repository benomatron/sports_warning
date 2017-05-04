- install redis

wget http://download.redis.io/releases/redis-3.2.4.tar.gz
tar xzf redis-3.2.4.tar.gz
cd redis-3.2.4
make

- build changes

### authy-python is not python3 compatible
changes:

 lib/python3.5/site-packages/authy/api/resources.python
 from urllib.parse import quote

 line 37ish..
 
        #headers = dict(self.def_headers.items() + headers.items())
        copy_headers = self.def_headers.copy()
        copy_headers.update(headers)
        headers = copy_headers

### smsish tries to import django_rq

to fix:
comment out everything in lib/python3.5/site-packages/smsish/tasks.py
