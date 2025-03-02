// Fix for Bootstrap 5 compatibility
document.addEventListener('DOMContentLoaded', function() {
    // Convert data-parent to data-bs-parent
    document.querySelectorAll('[data-parent]').forEach(function(element) {
        var parent = element.getAttribute('data-parent');
        element.setAttribute('data-bs-parent', parent);
        element.removeAttribute('data-parent');
    });
    
    // Initialize Bootstrap 5 components
    // Dropdowns
    var dropdownElementList = [].slice.call(document.querySelectorAll('.dropdown-toggle'));
    dropdownElementList.forEach(function(dropdownToggleEl) {
        new bootstrap.Dropdown(dropdownToggleEl);
    });
    
    // Collapses
    var collapseElementList = [].slice.call(document.querySelectorAll('.collapse'));
    collapseElementList.forEach(function(collapseEl) {
        // Don't initialize if it's already shown
        if (!collapseEl.classList.contains('show')) {
            new bootstrap.Collapse(collapseEl, {toggle: false});
        }
    });
    
    // Tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(function(tooltipTriggerEl) {
        new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.forEach(function(popoverTriggerEl) {
        new bootstrap.Popover(popoverTriggerEl);
    });
}); 