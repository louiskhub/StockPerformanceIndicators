import random
import requests_cache
import urllib

def session_header():
    lines = open("user-agents.txt").read().splitlines()
    session = requests_cache.CachedSession('yfinance.cache')
    session.headers['User-agent'] = random.choice(lines)
    return session

"""def proxy():
    lines = open("proxies.txt").read().splitlines()
    return random.choice(lines)"""