/**
 * Bootstrap 5 Compatibility Fixes for SB Admin 2
 * This script helps bridge the gap between Bootstrap 4 (used in SB Admin 2) 
 * and Bootstrap 5, especially for dropdown menus and modals.
 */

document.addEventListener('DOMContentLoaded', function() {
  // Fix for dropdown toggles
  const dropdowns = document.querySelectorAll('.dropdown-toggle');
  
  dropdowns.forEach(dropdown => {
    dropdown.setAttribute('data-bs-toggle', 'dropdown');
    dropdown.removeAttribute('data-toggle');
  });

  // Fix for modals
  const modalTriggers = document.querySelectorAll('[data-toggle="modal"]');
  
  modalTriggers.forEach(trigger => {
    const targetModal = trigger.getAttribute('data-target');
    if (targetModal) {
      trigger.setAttribute('data-bs-toggle', 'modal');
      trigger.setAttribute('data-bs-target', targetModal);
      trigger.removeAttribute('data-toggle');
      trigger.removeAttribute('data-target');
    }
  });

  // Fix close buttons in alerts
  const alertCloseButtons = document.querySelectorAll('.alert .close');
  
  alertCloseButtons.forEach(button => {
    button.classList.add('btn-close');
    button.setAttribute('data-bs-dismiss', 'alert');
    button.removeAttribute('data-dismiss');
    
    // Remove the × character if it exists
    if (button.innerHTML.includes('×')) {
      button.innerHTML = '';
    }
  });

  // Fix for accordion/collapse elements
  const collapseToggles = document.querySelectorAll('[data-toggle="collapse"]');
  
  collapseToggles.forEach(toggle => {
    const targetCollapse = toggle.getAttribute('data-target');
    if (targetCollapse) {
      toggle.setAttribute('data-bs-toggle', 'collapse');
      toggle.setAttribute('data-bs-target', targetCollapse);
      toggle.removeAttribute('data-toggle');
      toggle.removeAttribute('data-target');
    }
  });

  // Thêm CSS để điều chỉnh sidebar và hiệu ứng dropdown
  const styleElement = document.createElement('style');
  styleElement.textContent = `
    /* CSS cho sidebar và dropdown */
    .sidebar .nav-item .collapse {
      margin: 0;
      transition: height 0.2s ease;
    }
    
    /* Loại bỏ hoàn toàn hiệu ứng trượt sang phải */
    .sidebar .nav-item .collapse, 
    .sidebar .nav-item .collapsing {
      margin-left: 0 !important;
      left: 0;
      position: relative;
      transform: none !important;
      transition: height 0.2s ease !important;
    }
    
    /* Hiệu ứng hover cho menu chính */
    .sidebar .nav-item:not(.active) .nav-link:hover {
      background-color: rgba(255, 255, 255, 0.1);
    }
    
    /* Ẩn tất cả mũi tên khi thu gọn sidebar */
    .sidebar.toggled .nav-item .nav-link i.fa-angle-down,
    .sidebar.toggled .nav-item .nav-link i.fa-chevron-right,
    .sidebar.toggled .nav-item .nav-link i.fa-angle-right,
    .sidebar.toggled .nav-item .nav-link i.fa-caret-down,
    .sidebar.toggled .nav-item .nav-link i.fa-caret-right,
    .sidebar.toggled .nav-item .nav-link i.fa-chevron-down {
      display: none !important;
    }
    
    /* Hiệu ứng hover cho dropdown items */
    .sidebar .collapse-item:hover {
      background-color: #eaecf4;
    }
    
    /* Active menu item */
    .sidebar .nav-item .nav-link.active,
    .sidebar .nav-item .nav-link.active:hover {
      background-color: rgba(255, 255, 255, 0.2);
    }
    
    /* Active dropdown item */
    .sidebar .collapse-item.active {
      background-color: #dddfeb;
      border-left: 3px solid #4e73df;
      margin-left: -3px;
    }
  `;
  document.head.appendChild(styleElement);

  // Xử lý tương thích Bootstrap 5 cho dropdown và modal
  const dropdownToggles = document.querySelectorAll('[data-bs-toggle="dropdown"]');
  const modalToggles = document.querySelectorAll('[data-bs-toggle="modal"]');
  
  dropdownToggles.forEach(toggle => {
    toggle.addEventListener('click', function(e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('data-bs-target'));
      if (target) {
        bootstrap.Dropdown.getOrCreateInstance(toggle).toggle();
      }
    });
  });
  
  modalToggles.forEach(toggle => {
    toggle.addEventListener('click', function(e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('data-bs-target'));
      if (target) {
        bootstrap.Modal.getOrCreateInstance(target).toggle();
      }
    });
  });

  // Xử lý đóng mở sidebar menu
  const sidebarItems = document.querySelectorAll('.sidebar .nav-item .nav-link[data-bs-toggle="collapse"]');
  
  // Xử lý sự kiện hover cho desktop
  if (window.innerWidth > 768) {
    sidebarItems.forEach(item => {
      const parent = item.parentElement;
      const target = document.querySelector(item.getAttribute('data-bs-target'));
      
      // Hover mở dropdown
      parent.addEventListener('mouseenter', function() {
        // Không mở hover nếu sidebar thu gọn
        if (document.querySelector('.sidebar').classList.contains('toggled')) {
          return;
        }
        
        // Chỉ mở khi không có menu nào đang được giữ mở
        if (!document.querySelector('.sidebar .nav-item.keep-open') || parent.classList.contains('keep-open')) {
          // Lấy collapse instance từ Bootstrap
          const bsCollapse = bootstrap.Collapse.getOrCreateInstance(target, {toggle: false});
          bsCollapse.show();
        }
      });
      
      // Hover đóng dropdown 
      parent.addEventListener('mouseleave', function() {
        // Không đóng nếu có class 'keep-open' (được thiết lập khi click)
        if (parent.classList.contains('keep-open')) {
          return;
        }
        
        // Lấy collapse instance từ Bootstrap
        const bsCollapse = bootstrap.Collapse.getOrCreateInstance(target, {toggle: false});
        bsCollapse.hide();
      });
    });
  }
  
  // Xử lý sự kiện click
  sidebarItems.forEach(item => {
    const parent = item.parentElement;
    
    item.addEventListener('click', function(e) {
      e.preventDefault();
      
      // Không xử lý click nếu sidebar đang thu gọn
      if (document.querySelector('.sidebar').classList.contains('toggled')) {
        return;
      }
      
      const target = document.querySelector(this.getAttribute('data-bs-target'));
      const bsCollapse = bootstrap.Collapse.getOrCreateInstance(target, {toggle: false});
      
      const isOpen = target.classList.contains('show');
      
      // Nếu giữ Ctrl, cho phép mở nhiều dropdown cùng lúc
      if (!e.ctrlKey) {
        // Đóng tất cả dropdown khác
        sidebarItems.forEach(otherItem => {
          if (otherItem !== item) {
            const otherTarget = document.querySelector(otherItem.getAttribute('data-bs-target'));
            if (otherTarget && otherTarget.classList.contains('show')) {
              bootstrap.Collapse.getInstance(otherTarget)?.hide();
              otherItem.parentElement.classList.remove('keep-open');
            }
          }
        });
      }
      
      // Toggle trạng thái hiện tại
      if (isOpen) {
        bsCollapse.hide();
        parent.classList.remove('keep-open');
      } else {
        bsCollapse.show();
        parent.classList.add('keep-open');
      }
    });
  });
  
  // Xử lý đóng/mở sidebar toggle
  const sidebarToggle = document.querySelector('#sidebarToggle');
  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', function() {
      document.body.classList.toggle('sidebar-toggled');
      const sidebar = document.querySelector('.sidebar');
      sidebar.classList.toggle('toggled');
      
      // Đóng tất cả dropdown khi thu gọn sidebar
      if (sidebar.classList.contains('toggled')) {
        sidebarItems.forEach(item => {
          const target = document.querySelector(item.getAttribute('data-bs-target'));
          if (target && target.classList.contains('show')) {
            bootstrap.Collapse.getInstance(target)?.hide();
            item.parentElement.classList.remove('keep-open');
          }
        });
      }
    });
  }
  
  // Đảm bảo đóng tất cả dropdown khi resize xuống kích thước nhỏ
  window.addEventListener('resize', function() {
    const sidebar = document.querySelector('.sidebar');
    if (window.innerWidth < 768 && sidebar.classList.contains('toggled')) {
      sidebarItems.forEach(item => {
        const target = document.querySelector(item.getAttribute('data-bs-target'));
        if (target && target.classList.contains('show')) {
          bootstrap.Collapse.getInstance(target)?.hide();
          item.parentElement.classList.remove('keep-open');
        }
      });
    }
  });
  
  // Đánh dấu menu item hiện tại là active
  const currentUrl = window.location.pathname;
  const menuItems = document.querySelectorAll('.sidebar .collapse-item');
  menuItems.forEach(item => {
    const href = item.getAttribute('href');
    if (href && currentUrl.includes(href.split('?')[0])) {
      item.classList.add('active');
      
      // Mở dropdown cha
      const parentCollapse = item.closest('.collapse');
      if (parentCollapse) {
        bootstrap.Collapse.getOrCreateInstance(parentCollapse).show();
        
        // Đánh dấu nav-link cha là active
        const parentNavLink = document.querySelector(`[data-bs-target="#${parentCollapse.id}"]`);
        if (parentNavLink) {
          parentNavLink.classList.add('active');
          parentNavLink.parentElement.classList.add('keep-open');
        }
      }
    }
  });
}); 