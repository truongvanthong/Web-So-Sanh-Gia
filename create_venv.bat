@REM Tạo môi trường ảo
echo "Creating Virtual Environment"
python -m venv .venv
@REM Kích hoạt môi trường ảo
echo "Activating Virtual Environment"
call .venv\Scripts\activate
@REM Cài đặt các thư viện cần thiết
echo "Installing Required Libraries"
pip install -r requirements.txt