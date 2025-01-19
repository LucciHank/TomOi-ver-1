document.addEventListener('DOMContentLoaded', function () {
  const addToCartButtons = document.querySelectorAll('.add-to-cart');

  addToCartButtons.forEach(button => {
    button.addEventListener('click', function () {
      const productId = this.getAttribute('data-product-id');
      if (!productId) {
        console.error('Thiếu product ID!');
        return;
      }

      const stock = this.getAttribute('data-product-stock');
      const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

      fetch(`/store/add-to-cart/${productId}/`, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({ product_id: productId, stock: stock }),
      })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            alert('Sản phẩm đã được thêm vào giỏ hàng!');
            updateCartDropdown(data.cart);
          } else {
            alert('Có lỗi xảy ra.');
          }
        })
        .catch(error => {
          console.error('Lỗi khi thêm vào giỏ hàng:', error);
          alert('Có lỗi xảy ra, vui lòng thử lại.');
        });
    });
  });
});

// Hàm cập nhật giỏ hàng trong giao diện người dùng
function updateCartDropdown(cart) {
  const cartItemsList = document.querySelector("#cart-items-list");
  cartItemsList.innerHTML = "";  // Xóa giỏ hàng cũ

  if (Object.keys(cart).length === 0) {
    cartItemsList.innerHTML = "<li>Giỏ hàng trống</li>";
  } else {
    // Hiển thị lại giỏ hàng với sản phẩm và số lượng mới
    for (let productId in cart) {
      const item = cart[productId];
      const li = document.createElement("li");
      li.textContent = `${item.name} x ${item.quantity} - ${item.price * item.quantity} VNĐ`;
      cartItemsList.appendChild(li);
    }
  }
}

document.getElementById('cartDropdown').addEventListener('mouseover', function () {
  fetch('/cart/api/')
    .then(response => response.json())
    .then(data => {
      const cartItemsList = document.getElementById('cart-items-list');
      cartItemsList.innerHTML = ''; // Xóa các sản phẩm cũ trong giỏ hàng khi hover

      // Hiển thị sản phẩm trong giỏ hàng
      data.cart.forEach(item => {
        const li = document.createElement('li');

        // Sử dụng Intl.NumberFormat để định dạng giá tiền với dấu phẩy
        const formattedPrice = new Intl.NumberFormat('vi-VN').format(item.total_price);
        li.textContent = `${item.name} x${item.quantity} - ${formattedPrice} VND`;

        cartItemsList.appendChild(li);
      });

      // Cập nhật tổng số lượng
      document.getElementById('cart-count').textContent = data.total_items;
    });
});


function updateCartDropdown(cart) {
  const cartItemsList = document.querySelector("#cart-items-list");
  cartItemsList.innerHTML = "";  // Xóa giỏ hàng cũ

  if (Object.keys(cart).length === 0) {
    cartItemsList.innerHTML = "<li>Giỏ hàng trống</li>";
  } else {
    // Cập nhật giỏ hàng dưới dạng card bo góc
    for (let productId in cart) {
      const item = cart[productId];
      const card = document.createElement("div");
      card.classList.add("cart-card");
      card.innerHTML = `
                <div class="card">
                    <img src="${item.image}" class="card-img-top" alt="${item.name}">
                    <div class="card-body">
                        <h5 class="card-title">${item.name}</h5>
                        <p class="card-text">Số lượng: ${item.quantity}</p>
                        <p class="card-text">Giá: ${item.price * item.quantity} VND</p>
                    </div>
                </div>
            `;
      cartItemsList.appendChild(card);
    }
  }
}

function formatCurrency(number) {
  return number.toLocaleString();  // Format giá thành dạng tiền tệ (sử dụng dấu phẩy)
}

// Cập nhật trong cart.js hoặc trong HTML để hiển thị giá
document.querySelectorAll('.product-price').forEach(function (element) {
  let price = parseFloat(element.textContent);
  element.textContent = formatCurrency(price) + ' VND';  // Hiển thị dưới dạng tiền tệ
});

document.querySelectorAll('.cart-price').forEach(function (element) {
  let price = parseFloat(element.textContent);
  element.textContent = formatCurrency(price) + ' VND';  // Hiển thị dưới dạng tiền tệ
});

// Trong phần cập nhật giỏ hàng (bên trong forEach):
fetch('/cart/api/')
  .then(response => response.json())
  .then(data => {
    // Cập nhật giỏ hàng
    const cartItemsList = document.getElementById('cart-items-list');
    cartItemsList.innerHTML = '';  // Xóa nội dung cũ
    data.cart.forEach(item => {
      const li = document.createElement('li');
      // Sử dụng formatCurrency để hiển thị giá
      const formattedPrice = formatCurrency(item.price * item.quantity);
      li.textContent = `${item.name} x${item.quantity} - ${formattedPrice} VND`;
      cartItemsList.appendChild(li);
    });

    // Cập nhật tổng số lượng và tổng giá trị
    document.getElementById('cart-count').textContent = data.total_items;
  });