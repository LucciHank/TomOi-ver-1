// Chức năng mở rộng/thu gọn sidebar - được cải thiện
$(document).ready(function() {
    $("#sidebarToggle, #sidebarToggleTop").on('click', function(e) {
        e.preventDefault();
        $("body").toggleClass("sidebar-toggled");
        $(".sidebar").toggleClass("toggled");
        
        // Đảm bảo icon được thay đổi khi sidebar được thu gọn/mở rộng
        if ($(".sidebar").hasClass("toggled")) {
            $("#sidebarToggle i").removeClass("fa-angle-left").addClass("fa-angle-right");
            localStorage.setItem("sidebar-toggled", "true");
        } else {
            $("#sidebarToggle i").removeClass("fa-angle-right").addClass("fa-angle-left");
            localStorage.setItem("sidebar-toggled", "false");
        }
    });

    // Kiểm tra trạng thái đã lưu
    if (localStorage.getItem("sidebar-toggled") === "true") {
        $("body").addClass("sidebar-toggled");
        $(".sidebar").addClass("toggled");
        $("#sidebarToggle i").removeClass("fa-angle-left").addClass("fa-angle-right");
    }

    // Đảm bảo sidebar luôn hiển thị đúng cách trên các màn hình khác nhau
    $(window).resize(function() {
        if ($(window).width() < 768) {
            $(".sidebar").addClass("toggled");
            $("#sidebarToggle i").removeClass("fa-angle-left").addClass("fa-angle-right");
        } else {
            if (localStorage.getItem("sidebar-toggled") !== "true") {
                $(".sidebar").removeClass("toggled");
                $("#sidebarToggle i").removeClass("fa-angle-right").addClass("fa-angle-left");
            }
        }
    });
    
    // Hiệu ứng active cho menu item hiện tại
    var currentPath = window.location.pathname;
    $(".sidebar .nav-link").each(function() {
        var linkPath = $(this).attr("href");
        if (currentPath.indexOf(linkPath) !== -1 && linkPath !== "#" && linkPath !== "") {
            $(this).addClass("active");
            $(this).closest(".nav-item").addClass("active");
            
            // Mở rộng collapse nếu menu item thuộc collapse
            if ($(this).closest(".collapse").length) {
                $(this).closest(".collapse").addClass("show");
                $(this).closest(".collapse").prev(".nav-link").removeClass("collapsed");
            }
        }
    });
}); 