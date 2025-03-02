@echo off
echo === Đang xóa các file migrations cũ ===
for /r %%i in (*\migrations\*.py) do (
    echo %%i | findstr /v "__init__.py" > nul
    if not errorlevel 1 (
        echo Xóa: %%i
        del "%%i"
    )
)

echo === Đang xóa file database.db ===
if exist db.sqlite3 (
    echo Xóa db.sqlite3
    del db.sqlite3
)

echo === Tạo migration mới ===
python manage.py makemigrations accounts
python manage.py makemigrations store
python manage.py makemigrations dashboard
python manage.py makemigrations payment
python manage.py makemigrations blog

echo === Thực hiện migrate ===
python manage.py migrate --fake-initial
python manage.py migrate

echo === Khởi tạo dữ liệu mẫu ===
python manage.py init_db

echo === Hoàn tất! === 