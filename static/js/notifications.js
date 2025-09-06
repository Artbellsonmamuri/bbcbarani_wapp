/**
 * Notifications JavaScript for Bible Baptist Church Barani
 */

(function() {
    'use strict';

    let notificationCount = 0;
    let notificationSocket = null;

    // Initialize notifications when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        initializeNotifications();
        loadNotificationCount();
        setupNotificationPolling();
    });

    // Initialize notification system
    function initializeNotifications() {
        setupNotificationBell();
        loadActiveBanners();
        setupMarkAsReadButtons();
    }

    // Setup notification bell in header
    function setupNotificationBell() {
        const notificationBell = document.getElementById('notification-bell');
        if (!notificationBell) return;

        notificationBell.addEventListener('click', function(e) {
            e.preventDefault();
            toggleNotificationDropdown();
        });

        // Create dropdown if it doesn't exist
        if (!document.getElementById('notification-dropdown')) {
            createNotificationDropdown();
        }
    }

    // Create notification dropdown
    function createNotificationDropdown() {
        const dropdown = document.createElement('div');
        dropdown.id = 'notification-dropdown';
        dropdown.className = 'notification-dropdown position-absolute bg-white shadow-lg border rounded';
        dropdown.style.cssText = 'top: 100%; right: 0; width: 350px; max-height: 400px; overflow-y: auto; z-index: 1050; display: none;';

        dropdown.innerHTML = `
            <div class="notification-header p-3 border-bottom bg-light">
                <div class="d-flex justify-content-between align-items-center">
                    <h6 class="mb-0">Notifications</h6>
                    <button class="btn btn-sm btn-link text-primary" onclick="markAllAsRead()">
                        Mark all read
                    </button>
                </div>
            </div>
            <div id="notification-list" class="notification-list">
                <div class="text-center p-4">
                    <div class="loading-spinner-large mx-auto mb-2"></div>
                    <small class="text-muted">Loading notifications...</small>
                </div>
            </div>
            <div class="notification-footer p-2 border-top bg-light text-center">
                <a href="/notifications/" class="btn btn-sm btn-link">View all notifications</a>
            </div>
        `;

        const bellContainer = document.getElementById('notification-bell').parentNode;
        bellContainer.style.position = 'relative';
        bellContainer.appendChild(dropdown);

        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            const bell = document.getElementById('notification-bell');
            const dropdown = document.getElementById('notification-dropdown');

            if (!bell.contains(e.target) && !dropdown.contains(e.target)) {
                dropdown.style.display = 'none';
            }
        });
    }

    // Toggle notification dropdown
    function toggleNotificationDropdown() {
        const dropdown = document.getElementById('notification-dropdown');
        if (!dropdown) return;

        if (dropdown.style.display === 'none' || !dropdown.style.display) {
            dropdown.style.display = 'block';
            loadRecentNotifications();
        } else {
            dropdown.style.display = 'none';
        }
    }

    // Load notification count
    function loadNotificationCount() {
        fetch('/api/notifications/count/')
            .then(response => response.json())
            .then(data => {
                updateNotificationCount(data.count);
            })
            .catch(error => {
                console.error('Error loading notification count:', error);
            });
    }

    // Update notification count in UI
    function updateNotificationCount(count) {
        notificationCount = count;

        const countElements = document.querySelectorAll('#notification-count, #header-notification-count');
        countElements.forEach(element => {
            if (count > 0) {
                element.textContent = count > 99 ? '99+' : count;
                element.style.display = 'inline';
            } else {
                element.style.display = 'none';
            }
        });
    }

    // Load recent notifications
    function loadRecentNotifications() {
        const notificationList = document.getElementById('notification-list');
        if (!notificationList) return;

        fetch('/api/notifications/recent/')
            .then(response => response.json())
            .then(data => {
                displayNotifications(data.notifications);
            })
            .catch(error => {
                console.error('Error loading notifications:', error);
                notificationList.innerHTML = `
                    <div class="text-center p-4">
                        <i class="fas fa-exclamation-triangle text-warning mb-2"></i>
                        <div class="text-muted">Failed to load notifications</div>
                    </div>
                `;
            });
    }

    // Display notifications in dropdown
    function displayNotifications(notifications) {
        const notificationList = document.getElementById('notification-list');
        if (!notificationList) return;

        if (notifications.length === 0) {
            notificationList.innerHTML = `
                <div class="text-center p-4">
                    <i class="fas fa-bell-slash text-muted mb-2"></i>
                    <div class="text-muted">No notifications</div>
                </div>
            `;
            return;
        }

        notificationList.innerHTML = notifications.map(notification => `
            <div class="notification-item ${notification.is_read ? '' : 'unread'}" data-id="${notification.id}">
                <div class="d-flex p-3 border-bottom">
                    <div class="notification-icon me-3">
                        <i class="${notification.icon} ${notification.color_class}"></i>
                    </div>
                    <div class="notification-content flex-grow-1">
                        <div class="notification-title fw-bold">${notification.title}</div>
                        <div class="notification-message text-muted small">${notification.message}</div>
                        <div class="notification-time text-muted small">
                            ${timeAgo(notification.created_at)}
                        </div>
                    </div>
                    ${!notification.is_read ? `
                        <div class="notification-actions">
                            <button class="btn btn-sm btn-link text-primary" onclick="markAsRead(${notification.id})">
                                <i class="fas fa-check"></i>
                            </button>
                        </div>
                    ` : ''}
                </div>
            </div>
        `).join('');
    }

    // Mark notification as read
    window.markAsRead = function(notificationId) {
        fetch(`/api/notifications/${notificationId}/mark_read/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': ChurchUtils.getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update UI
                const notificationItem = document.querySelector(`[data-id="${notificationId}"]`);
                if (notificationItem) {
                    notificationItem.classList.remove('unread');
                    const actions = notificationItem.querySelector('.notification-actions');
                    if (actions) {
                        actions.remove();
                    }
                }

                // Update count
                updateNotificationCount(Math.max(0, notificationCount - 1));
            }
        })
        .catch(error => {
            console.error('Error marking notification as read:', error);
        });
    };

    // Mark all notifications as read
    window.markAllAsRead = function() {
        fetch('/api/notifications/mark_all_read/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': ChurchUtils.getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update UI
                const unreadItems = document.querySelectorAll('.notification-item.unread');
                unreadItems.forEach(item => {
                    item.classList.remove('unread');
                    const actions = item.querySelector('.notification-actions');
                    if (actions) {
                        actions.remove();
                    }
                });

                // Update count
                updateNotificationCount(0);

                ChurchUtils.showToast('All notifications marked as read', 'success');
            }
        })
        .catch(error => {
            console.error('Error marking all notifications as read:', error);
        });
    };

    // Load active banners
    function loadActiveBanners() {
        fetch('/api/notifications/banners/')
            .then(response => response.json())
            .then(data => {
                displayBanners(data.banners);
            })
            .catch(error => {
                console.error('Error loading banners:', error);
            });
    }

    // Display announcement banners
    function displayBanners(banners) {
        const bannersContainer = document.getElementById('notification-banners');
        if (!bannersContainer || banners.length === 0) return;

        banners.forEach(banner => {
            const bannerElement = createBannerElement(banner);
            bannersContainer.appendChild(bannerElement);
        });
    }

    // Create banner element
    function createBannerElement(banner) {
        const div = document.createElement('div');
        const alertClass = `alert-${banner.banner_type}`;
        const dismissible = banner.is_dismissible ? 'alert-dismissible' : '';

        div.className = `alert ${alertClass} ${dismissible} mb-0 rounded-0`;
        div.setAttribute('role', 'alert');

        let html = `
            <div class="container">
                <div class="row align-items-center">
                    <div class="col">
                        <strong>${banner.title}</strong>
                        ${banner.message ? ` - ${banner.message}` : ''}
                    </div>
        `;

        if (banner.action_url && banner.action_text) {
            const target = banner.action_opens_new_tab ? 'target="_blank"' : '';
            html += `
                    <div class="col-auto">
                        <a href="${banner.action_url}" class="btn btn-sm btn-outline-${banner.banner_type}" ${target}>
                            ${banner.action_text}
                        </a>
                    </div>
            `;
        }

        html += '</div></div>';

        if (banner.is_dismissible) {
            html += '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>';
        }

        div.innerHTML = html;

        return div;
    }

    // Setup mark as read buttons on notification pages
    function setupMarkAsReadButtons() {
        const markReadButtons = document.querySelectorAll('.mark-read-btn');
        markReadButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const notificationId = button.getAttribute('data-id');
                markAsRead(notificationId);
            });
        });
    }

    // Setup notification polling for real-time updates
    function setupNotificationPolling() {
        // Poll every 30 seconds for new notifications
        setInterval(function() {
            loadNotificationCount();
        }, 30000);

        // Try to establish WebSocket connection for real-time updates
        // This would require WebSocket support on the backend
        // For now, we'll stick with polling
    }

    // Utility function to format time ago
    function timeAgo(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const seconds = Math.floor((now - date) / 1000);

        const intervals = {
            year: 31536000,
            month: 2592000,
            week: 604800,
            day: 86400,
            hour: 3600,
            minute: 60
        };

        for (const [unit, value] of Object.entries(intervals)) {
            const count = Math.floor(seconds / value);
            if (count >= 1) {
                return `${count} ${unit}${count !== 1 ? 's' : ''} ago`;
            }
        }

        return 'Just now';
    }

    // Show desktop notification (if permitted)
    function showDesktopNotification(notification) {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(notification.title, {
                body: notification.message,
                icon: '/static/images/logo-small.png',
                tag: `notification-${notification.id}`
            });
        }
    }

    // Request notification permission
    function requestNotificationPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission().then(function(permission) {
                if (permission === 'granted') {
                    ChurchUtils.showToast('Desktop notifications enabled', 'success');
                }
            });
        }
    }

    // Expose functions for admin use
    window.ChurchNotifications = {
        loadCount: loadNotificationCount,
        markAsRead: markAsRead,
        markAllAsRead: markAllAsRead,
        requestPermission: requestNotificationPermission,
        showToast: ChurchUtils.showToast
    };

})();

// Add notification-specific CSS
const notificationCSS = `
.notification-dropdown {
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}

.notification-item.unread {
    background-color: #f8f9ff;
    border-left: 3px solid var(--primary-color);
}

.notification-item:hover {
    background-color: #f8f9fa;
}

.notification-icon {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #f8f9fa;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
}

.notification-title {
    font-size: 0.9rem;
    margin-bottom: 0.25rem;
}

.notification-message {
    font-size: 0.8rem;
    line-height: 1.3;
    margin-bottom: 0.25rem;
}

.notification-time {
    font-size: 0.75rem;
}

.loading-spinner-large {
    width: 40px;
    height: 40px;
    border: 4px solid #f3f4f6;
    border-top: 4px solid var(--primary-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
`;

// Inject notification CSS
const notificationStyle = document.createElement('style');
notificationStyle.textContent = notificationCSS;
document.head.appendChild(notificationStyle);