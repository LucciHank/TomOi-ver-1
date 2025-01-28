const categoriesSwiper = new Swiper('.categories-slider', {
    slidesPerView: 'auto',
    spaceBetween: 20,
    
    // Loop config
    loop: true,
    loopAdditionalSlides: 4, // Thêm 4 slides ảo ở cuối
    loopedSlides: 4, // Số slides thật cần clone
    loopPreventsSlide: false, // Cho phép slide tự do
    
    // Tốc độ và hiệu ứng
    speed: 800,
    effect: 'slide',
    
    // Tắt các tính năng gây giật
    rewind: false,
    freeMode: false,
    
    // Cấu hình nhóm slides
    slidesPerGroup: 1,
    loopFillGroupWithBlank: false,
    
    // Navigation
    navigation: {
        nextEl: '.nav-btn.next',
        prevEl: '.nav-btn.prev',
    },

    // Responsive breakpoints
    breakpoints: {
        320: {
            slidesPerView: 2,
            loopedSlides: 2, // Clone 2 slides cho mobile
            loopAdditionalSlides: 2
        },
        480: {
            slidesPerView: 3,
            loopedSlides: 3,
            loopAdditionalSlides: 3
        },
        768: {
            slidesPerView: 4,
            loopedSlides: 4, // Clone 4 slides cho desktop
            loopAdditionalSlides: 4
        }
    }
});