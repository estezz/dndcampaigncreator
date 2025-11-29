ps aux | grep 'python' | grep -v grep | grep -v 'run-jedi-language-server.py' |  awk '{print $2}' | xargs kill -9
