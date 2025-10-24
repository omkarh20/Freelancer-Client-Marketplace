// Enhanced JavaScript for interactive features

console.log('Freelancer Marketplace Enhanced Version loaded');

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.flash');
    flashMessages.forEach(function(message) {
        setTimeout(function() {
            message.style.opacity = '0';
            setTimeout(function() {
                message.remove();
            }, 300);
        }, 5000);
    });
    
    // Confirm before accepting/rejecting proposals
    const acceptLinks = document.querySelectorAll('a[href*="accept_proposal"]');
    acceptLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to accept this proposal? All other proposals for this project will be rejected.')) {
                e.preventDefault();
            }
        });
    });
    
    const rejectLinks = document.querySelectorAll('a[href*="reject_proposal"]');
    rejectLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to reject this proposal?')) {
                e.preventDefault();
            }
        });
    });
    
    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let valid = true;
            
            requiredFields.forEach(function(field) {
                if (!field.value.trim()) {
                    valid = false;
                    field.style.borderColor = '#f44336';
                } else {
                    field.style.borderColor = '#4d4d4d';
                }
            });
            
            if (!valid) {
                e.preventDefault();
                alert('Please fill in all required fields');
            }
        });
    });
});
