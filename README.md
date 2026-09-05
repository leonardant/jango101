# jango101


typically inside WSL or on Ubuntu/Linux!

do
```
git clone https://github.com/leonardant/jango101.git
```
## Enter the project folder
```
cd jango101
```
## Create a uv virtual environment
```
uv venv
```
## Enter/activate the environment
```
source .venv/bin/activate
```
## Django
```
...$ uv pip install django \
...$ django-admin --version \
...$ django-admin startproject demo \
...$ cd demo \
...$ python manage.py startapp my1stapp \
...$ python manage.py runserver 0.0.0.0:8000
```


## Architecture

/api

api/
│
├── admin.py
│       Django admin entry point
│
├── admin_forms.py
│       User creation/change forms
│
├── credential_admin.py
│       API credential admin
│
├── user_admin.py
│       Custom User admin
│
└── services/
    └── credentials.py
            API credential business logic