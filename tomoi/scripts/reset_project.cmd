@echo off
echo === Đang reset toàn bộ dự án ===

echo === Xóa database ===
if exist db.sqlite3 (
    del db.sqlite3
)

echo === Xóa tất cả migrations ===
for /r %%i in (*\migrations\*.py) do (
    echo %%i | findstr /v "__init__.py" > nul
    if not errorlevel 1 (
        del "%%i"
    )
)

echo === Tạo migrations mới ===
python manage.py makemigrations accounts
python manage.py makemigrations store
python manage.py makemigrations dashboard
python manage.py makemigrations payment
python manage.py makemigrations blog

echo === Thực hiện migrate ===
python manage.py migrate

echo === Khởi tạo dữ liệu mẫu ===
python manage.py init_db

echo === Hoàn tất! === 