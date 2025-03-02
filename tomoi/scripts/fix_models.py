import os
import sys
import re

# Thêm đường dẫn project vào sys.path
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_path)

# Path tới file models.py
models_file = os.path.join(project_path, 'dashboard', 'models.py')

def fix_model_order():
    """Di chuyển định nghĩa Discount lên trước UserDiscount"""
    with open(models_file, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Tìm định nghĩa của UserDiscount và Discount
    discount_class = re.search(r'class Discount\(models\.Model\):.*?def __str__.*?\):.*?\n', content, re.DOTALL)
    if not discount_class:
        print("Không tìm thấy model Discount!")
        return False
    
    user_discount_class = re.search(r'class UserDiscount\(models\.Model\):.*?def __str__.*?\):.*?\n', content, re.DOTALL)
    if not user_discount_class:
        print("Không tìm thấy model UserDiscount!")
        return False
    
    # Xóa cả hai định nghĩa
    content = content.replace(discount_class.group(0), '')
    content = content.replace(user_discount_class.group(0), '')
    
    # Tìm vị trí để thêm lại (sau ReferralTransaction)
    insert_point = re.search(r'class ReferralTransaction\(models\.Model\):.*?def __str__.*?\):.*?\n', content, re.DOTALL)
    if not insert_point:
        print("Không tìm thấy điểm chèn thích hợp!")
        return False
    
    # Chèn lại các định nghĩa theo thứ tự đúng
    insert_index = content.find(insert_point.group(0)) + len(insert_point.group(0))
    new_content = content[:insert_index] + "\n" + discount_class.group(0) + "\n" + user_discount_class.group(0) + content[insert_index:]
    
    # Lưu lại file
    with open(models_file, 'w', encoding='utf-8') as file:
        file.write(new_content)
    
    print("Đã sửa lại thứ tự định nghĩa model thành công!")
    return True

if __name__ == "__main__":
    fix_model_order() 