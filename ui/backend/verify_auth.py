"""Quick verification of the auth system."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['DATABASE_URL'] = 'postgresql://postgres:abdoreda12@localhost:5432/ai_software_db'
os.environ['SECRET_KEY'] = 'test-secret-key-32chars-long-abcdef'

from auth.database import engine
from sqlalchemy import text

# Check users table columns
with engine.connect() as conn:
    result = conn.execute(text(
        "SELECT column_name, data_type FROM information_schema.columns "
        "WHERE table_name='users' ORDER BY ordinal_position"
    ))
    rows = result.fetchall()
    print('users table columns:')
    for row in rows:
        print(f'  {row[0]}: {row[1]}')

# Test auth utilities
from auth.utils import hash_password, verify_password, create_access_token, decode_token

h = hash_password('testpassword123')
assert verify_password('testpassword123', h), 'password verify failed'
assert not verify_password('wrongpassword', h), 'should fail on wrong pass'

token = create_access_token({'sub': 'test-uuid-1234'})
payload = decode_token(token)
assert payload['sub'] == 'test-uuid-1234', 'token decode failed'

print()
print('[OK] Password hashing + verification works')
print('[OK] JWT create + decode works')
print('[OK] All auth utilities verified')
print()
print('[DONE] System is ready. Start the backend with: python app.py')
