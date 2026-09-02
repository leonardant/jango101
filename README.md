# jango101


typically inside WSL or on Ubuntu/Linx

do

git clone https://github.com/leonardant/jango101.git

## Enter the project folder
cd jango101

## Create a uv virtual environment
uv venv

## Enter/activate the environment
source .venv/bin/activate

## Django
uv pip install django \
then \
django-admin --version \
django-admin startproject demo \
cd demo \
python manage.py startapp my1stapp \
python manage.py runserver 0.0.0.0:8000
