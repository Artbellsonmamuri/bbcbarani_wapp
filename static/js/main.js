// BBC Barani CMS Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Prayer Request Form Enhancement
    const prayerForm = document.getElementById('prayer-request-form');
    if (prayerForm) {
        prayerForm.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...';
            submitBtn.disabled = true;
        });
    }

    // CSRF token for AJAX requests
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfToken) {
        window.csrfToken = csrfToken.value;
    }

    // Theme preview functionality
    const themeInputs = document.querySelectorAll('.theme-input');
    themeInputs.forEach(input => {
        input.addEventListener('change', function() {
            updateThemePreview();
        });
    });
});

// Theme Preview Function
function updateThemePreview() {
    const previewFrame = document.getElementById('theme-preview');
    if (!previewFrame) return;

    const formData = new FormData(document.getElementById('theme-form'));

    fetch('/api/themes/preview/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': window.csrfToken
        }
    })
    .then(response => response.text())
    .then(html => {
        previewFrame.srcdoc = html;
    })
    .catch(error => {
        console.error('Theme preview error:', error);
    });
}

// Notification Functions
function markNotificationRead(notificationId) {
    fetch(`/api/notifications/${notificationId}/mark-read/`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': window.csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const notificationElement = document.querySelector(`[data-notification-id="${notificationId}"]`);
            if (notificationElement) {
                notificationElement.classList.remove('unread');
            }
        }
    });
}

// Media Library Functions
function deleteMedia(mediaId) {
    if (confirm('Are you sure you want to delete this media file?')) {
        fetch(`/api/media/${mediaId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': window.csrfToken
            }
        })
        .then(response => {
            if (response.ok) {
                location.reload();
            }
        });
    }
}

// Comment moderation
function moderateComment(commentId, action) {
    fetch(`/api/comments/${commentId}/moderate/`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': window.csrfToken
        },
        body: JSON.stringify({ action: action })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        }
    });
}
