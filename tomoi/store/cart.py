from decimal import Decimal
from django.conf import settings
from .models import Product

class Cart:
    def __init__(self, request):
        """
        Khởi tạo giỏ hàng
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # Lưu một giỏ hàng trống vào session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def __iter__(self):
        """
        Duyệt qua các sản phẩm trong giỏ hàng và lấy dữ liệu từ database
        """
        product_ids = self.cart.keys()
        # Lấy các sản phẩm và thêm vào giỏ hàng
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        
        for product in products:
            cart[str(product.id)]['product'] = product
            cart[str(product.id)]['id'] = product.id
            cart[str(product.id)]['name'] = product.name
            cart[str(product.id)]['price'] = float(product.price)
            cart[str(product.id)]['stock'] = product.stock
            cart[str(product.id)]['image'] = product.get_primary_image().url if product.get_primary_image() else None

        for item in cart.values():
            item['price'] = float(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Đếm tất cả các sản phẩm trong giỏ hàng
        """
        return sum(item['quantity'] for item in self.cart.values())

    def add(self, product, quantity=1, override_quantity=False):
        """
        Thêm sản phẩm vào giỏ hàng hoặc cập nhật số lượng
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': float(product.price),
                'name': product.name,
                'id': product.id,
                'stock': product.stock,
                'image': product.get_primary_image().url if product.get_primary_image() else None
            }
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def update(self, product_id, quantity):
        """
        Cập nhật số lượng cho sản phẩm
        """
        if str(product_id) in self.cart:
            self.cart[str(product_id)]['quantity'] = quantity
            self.save()

    def remove(self, product_id):
        """
        Xóa sản phẩm khỏi giỏ hàng
        """
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def get_total_price(self):
        """
        Tính tổng giá trị giỏ hàng
        """
        return sum(float(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        """
        Xóa giỏ hàng khỏi session
        """
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def save(self):
        """
        Đánh dấu session là "đã thay đổi" để đảm bảo nó được lưu
        """
        self.session.modified = True 