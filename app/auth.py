"""Application security: local admin password and signed session tokens."""
import hashlib,hmac,secrets,time,sqlite3
from . import data
SESSION_SECONDS=8*3600

def initialize():
    with data.connect() as c:
        c.execute('CREATE TABLE IF NOT EXISTS admin_auth (id INTEGER PRIMARY KEY CHECK(id=1), salt TEXT NOT NULL, password_hash TEXT NOT NULL, session_secret TEXT NOT NULL)')

def configured():
    with data.connect() as c:return c.execute('SELECT 1 FROM admin_auth WHERE id=1').fetchone() is not None

def _hash(password,salt):return hashlib.scrypt(password.encode(),salt=bytes.fromhex(salt),n=2**14,r=8,p=1).hex()

def setup(password):
    if not isinstance(password,str) or len(password)<12 or len(password)>256:raise ValueError('Admin password must contain 12–256 characters')
    salt=secrets.token_hex(16)
    with data.connect() as c:
        try:c.execute('INSERT INTO admin_auth VALUES(1,?,?,?)',(salt,_hash(password,salt),secrets.token_hex(32)))
        except sqlite3.IntegrityError:raise ValueError('Admin already configured')
        except Exception as exc:
            if 'UNIQUE' in str(exc).upper():raise ValueError('Admin already configured') from exc
            raise

def login(password):
    with data.connect() as c:row=c.execute('SELECT * FROM admin_auth WHERE id=1').fetchone()
    if not row or not isinstance(password,str) or not hmac.compare_digest(_hash(password,row['salt']),row['password_hash']):return None
    expires=str(int(time.time())+SESSION_SECONDS)
    nonce=secrets.token_hex(12)
    message=f'{expires}.{nonce}'
    signature=hmac.new(bytes.fromhex(row['session_secret']),message.encode(),'sha256').hexdigest()
    return f'{message}.{signature}'

def authorized(token):
    try:
        expires,nonce,signature=token.split('.')
        if int(expires)<time.time() or int(expires)>time.time()+SESSION_SECONDS+60:return False
        with data.connect() as c:row=c.execute('SELECT session_secret FROM admin_auth WHERE id=1').fetchone()
        if not row:return False
        expected=hmac.new(bytes.fromhex(row['session_secret']),f'{expires}.{nonce}'.encode(),'sha256').hexdigest()
        return hmac.compare_digest(expected,signature)
    except (ValueError,AttributeError):return False

def logout_all():
    with data.connect() as c:c.execute('UPDATE admin_auth SET session_secret=? WHERE id=1',(secrets.token_hex(32),))
