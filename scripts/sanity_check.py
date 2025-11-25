import os, socket, sys
def check_host(host, port, name):
    try:
        s = socket.create_connection((host, int(port)), timeout=2)
        s.close()
        print(f'{name} reachable at {host}:{port}')
    except Exception as e:
        print(f'{name} NOT reachable at {host}:{port} ({e})')

if __name__ == '__main__':
    check_host(os.getenv('PG_HOST','postgres'), os.getenv('PG_PORT',5432), 'Postgres')
    check_host(os.getenv('REDIS_HOST','redis'), os.getenv('REDIS_PORT',6379), 'Redis')
    check_host(os.getenv('LAVALINK_HOST','lavalink'), os.getenv('LAVALINK_PORT',2333), 'Lavalink')
