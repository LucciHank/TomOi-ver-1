(function($) {
  "use strict"; // Start of use strict

  // Toggle the side navigation
  $("#sidebarToggle, #sidebarToggleTop").on('click', function(e) {
    $("body").toggleClass("sidebar-toggled");
    $(".sidebar").toggleClass("toggled");
    if ($(".sidebar").hasClass("toggled")) {
      $('.sidebar .collapse').collapse('hide');
    }
  });

  // Close any open menu accordions when window is resized below 768px
  $(window).resize(function() {
    if ($(window).width() < 768) {
      $('.sidebar .collapse').collapse('hide');
    }
    
    // Toggle the side navigation when window is resized below 480px
    if ($(window).width() < 480 && !$(".sidebar").hasClass("toggled")) {
      $("body").addClass("sidebar-toggled");
      $(".sidebar").addClass("toggled");
      $('.sidebar .collapse').collapse('hide');
    }
  });

  // Đảm bảo các dropdown menu hoạt động đúng
  $(document).ready(function() {
    // Sửa lỗi Bootstrap 5 với jQuery
    $('[data-toggle="collapse"]').on('click', function() {
      var target = $(this).data('target');
      $(target).toggleClass('show');
    });
    
    // Kích hoạt dropdown khi click
    $('.nav-link').on('click', function(e) {
      if ($(this).attr('data-toggle') === 'collapse' || $(this).attr('data-toggle') === 'dropdown') {
        e.preventDefault();
      }
    });
    
    // Kích hoạt dropdown thông báo và user
    $('[data-toggle="dropdown"]').on('click', function() {
      var target = $(this).next('.dropdown-menu');
      target.toggleClass('show');
    });
  });

})(jQuery); // End of use strict 