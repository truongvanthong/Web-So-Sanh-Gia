@REM Kích hoạt môi trường ảo Env\Scripts\activate
echo "Activating Virtual Environment"
call .venv\Scripts\activate
@REM cd vào thư mục chứa file manage.py DjPriceCompare
echo "Changing Directory to DjPriceCompare"
cd DjPriceCompare
@REM Chạy server
echo "Running Django Server"
python manage.py runserver
