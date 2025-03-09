# File này là để đánh dấu thư mục views là một package Python
# Sử dụng đường dẫn tương đối để import file views.py
from .. import views

# Bạn có thể expose tất cả các functions từ file views chính
# để có thể import chúng từ package mới
from ..views import * 