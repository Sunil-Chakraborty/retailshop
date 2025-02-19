This is a new app for retail shop .
pip install whitenoise
pip install gunicorn
pip install psycopg2
pip install django==3.2.1
pip install django==5.1.5 earlier install

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
