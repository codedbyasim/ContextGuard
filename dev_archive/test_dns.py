import socket

try:
    ip = socket.gethostbyname('db.wfkilhwghdkddxgcljyq.supabase.co')
    print('db.wfkilhwghdkddxgcljyq.supabase.co resolved to:', ip)
except Exception as e:
    print('db.wfkilhwghdkddxgcljyq.supabase.co resolution failed:', e)

