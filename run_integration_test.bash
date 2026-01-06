export PYTHONPATH=$PYTHONPATH:$PWD/src:$PWD/test
pytest --rootdir=/home/user/dndcampaigncreator  --log-cli-level=DEBUG test/integration -vvv
