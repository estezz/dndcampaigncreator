if [ ! -d .venv ]; then
    python -m venv .venv
fi 

source .venv/bin/activate
python -m ensurepip --upgrade
pip install -r requirements.txt

export PORT=8080
python src/main.py




