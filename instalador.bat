py -m pip install -r requirements.txt --upgrade
py -m uvicorn main:app --reload --env-file local.env