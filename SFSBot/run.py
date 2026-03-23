import subprocess
import sys

bot = subprocess.Popen([sys.executable, 'bot.py'])
server = subprocess.Popen([sys.executable, 'server.py'])

bot.wait()
server.wait()