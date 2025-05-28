choco feature enable -n=allowGlobalConfirmation
choco install python
choco install pip
pip install -r requrements.txt
python -m flask --app server run --host=0.0.0.0
