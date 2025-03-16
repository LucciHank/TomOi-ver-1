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
}); 