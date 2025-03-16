"""
Tệp này được tạo ra để kiểm tra các import trong ứng dụng dashboard
"""

try:
    from tomoi.dashboard.views import (
        product_list,
        add_product,
        edit_product,
        delete_product,
        category_list,
        add_category,
        edit_category,
        import_products
    )
    
    print("All imports from tomoi.dashboard.views successful")
    
    import inspect
    print("\nproduct_list() function signature:")
    print(inspect.signature(product_list))
    print("\nproduct_list() source code first 5 lines:")
    source = inspect.getsource(product_list).splitlines()
    for line in source[:5]:
        print(line)
    
except ImportError as e:
    print(f"Import error: {e}")
except Exception as e:
    print(f"Other error: {e}")

print("\nNow trying to import from tomoi.dashboard.views.product")

try:
    from tomoi.dashboard.views.product import (
        update_product_status,
        manage_product_images,
        delete_product_image,
        set_primary_image,
        product_detail,
        product_history,
        get_product
    )
    
    print("All imports from tomoi.dashboard.views.product successful")
    
    print("\nproduct_detail() function signature:")
    print(inspect.signature(product_detail))
    
except ImportError as e:
    print(f"Import error: {e}")
except Exception as e:
    print(f"Other error: {e}") 