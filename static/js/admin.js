// Admin-specific JavaScript - No form interference
// This file only contains admin-specific functionality that doesn't interfere with form submissions

document.addEventListener('DOMContentLoaded', function() {
    console.log('Admin JavaScript loaded - no form interference');
    
    // Initialize tooltips for admin pages
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers for admin pages
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Image preview functionality for admin forms
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    imageInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const preview = input.parentNode.querySelector('.image-preview');
                    if (preview) {
                        preview.innerHTML = '<img src="' + e.target.result + '" class="img-thumbnail" style="max-width: 200px;">';
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    });

    // PDF preview functionality for admin forms
    const pdfInputs = document.querySelectorAll('input[type="file"][accept*="pdf"]');
    pdfInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const preview = input.parentNode.querySelector('.pdf-preview');
                if (preview) {
                    preview.innerHTML = '<div class="alert alert-info"><i class="fas fa-file-pdf me-2"></i>PDF selected: ' + file.name + '</div>';
                }
            }
        });
    });

    // Back to top button for admin pages
    const backToTopButton = document.createElement('button');
    backToTopButton.innerHTML = '<i class="fas fa-arrow-up"></i>';
    backToTopButton.className = 'btn btn-primary position-fixed';
    backToTopButton.style.cssText = 'bottom: 20px; right: 20px; z-index: 1000; border-radius: 50%; width: 50px; height: 50px; display: none;';
    backToTopButton.setAttribute('aria-label', 'Back to top');
    document.body.appendChild(backToTopButton);

    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTopButton.style.display = 'block';
        } else {
            backToTopButton.style.display = 'none';
        }
    });

    backToTopButton.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    // Copy to clipboard functionality for admin pages
    const copyButtons = document.querySelectorAll('[data-copy]');
    copyButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const text = this.dataset.copy;
            navigator.clipboard.writeText(text).then(function() {
                const originalText = button.innerHTML;
                button.innerHTML = '<i class="fas fa-check"></i> Copied!';
                button.classList.add('btn-success');
                button.classList.remove('btn-outline-secondary');
                
                setTimeout(function() {
                    button.innerHTML = originalText;
                    button.classList.remove('btn-success');
                    button.classList.add('btn-outline-secondary');
                }, 2000);
            });
        });
    });

    // QR Code generation for admin pages
    window.generateQRCode = function(data, containerId) {
        if (typeof QRCode !== 'undefined') {
            const container = document.getElementById(containerId);
            if (container) {
                container.innerHTML = '';
                new QRCode(container, {
                    text: data,
                    width: 200,
                    height: 200,
                    colorDark: '#000000',
                    colorLight: '#ffffff',
                    correctLevel: QRCode.CorrectLevel.H
                });
            }
        }
    };

    // Mobile menu enhancement for admin pages
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        // Close mobile menu when clicking on a link
        const navLinks = navbarCollapse.querySelectorAll('.nav-link');
        navLinks.forEach(function(link) {
            link.addEventListener('click', function() {
                if (window.innerWidth < 992) {
                    navbarCollapse.classList.remove('show');
                }
            });
        });
    }

    console.log('Admin JavaScript initialized successfully - forms will submit normally');
});
