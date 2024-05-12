@echo off

echo Running make.bat ...

echo running python manage.py makemigrations
python manage.py makemigrations

echo running python manage.py migrate 
python manage.py migrate

@REM echo running python manage.py createsuperuser
@REM python manage.py createsuperuser

echo Make.bat finished running - press any key to continue ...
pause