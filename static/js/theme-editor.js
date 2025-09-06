/**
 * Theme Editor JavaScript
 */

class ThemeEditor {
    constructor() {
        this.currentThemeId = null;
        this.previewFrame = null;
        this.isLoading = false;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadActiveTheme();
    }

    bindEvents() {
        // Color input changes
        document.querySelectorAll('.color-input').forEach(input => {
            input.addEventListener('change', () => this.updatePreview());
            input.addEventListener('input', () => this.debouncePreview());
        });

        // Select changes
        document.querySelectorAll('select[data-setting]').forEach(select => {
            select.addEventListener('change', () => this.updatePreview());
        });

        // Range inputs
        document.querySelectorAll('input[type="range"]').forEach(range => {
            range.addEventListener('input', () => this.debouncePreview());
        });

        // Custom CSS changes
        const customCssTextarea = document.getElementById('custom-css');
        if (customCssTextarea) {
            customCssTextarea.addEventListener('input', () => this.debouncePreview());
        }

        // Save button
        const saveButton = document.getElementById('save-theme');
        if (saveButton) {
            saveButton.addEventListener('click', () => this.saveTheme());
        }

        // Theme selection
        document.querySelectorAll('.theme-card').forEach(card => {
            card.addEventListener('click', (e) => {
                const themeId = e.currentTarget.dataset.themeId;
                this.selectTheme(themeId);
            });
        });
    }

    debouncePreview() {
        if (this.previewTimeout) {
            clearTimeout(this.previewTimeout);
        }
        this.previewTimeout = setTimeout(() => this.updatePreview(), 500);
    }

    updatePreview() {
        if (this.isLoading) return;

        const settings = this.getFormSettings();
        const customCss = document.getElementById('custom-css')?.value || '';

        const previewUrl = `/themes/${this.currentThemeId}/preview/` +
            `?settings=${encodeURIComponent(JSON.stringify(settings))}` +
            `&custom_css=${encodeURIComponent(customCss)}`;

        const previewFrame = document.getElementById('theme-preview');
        if (previewFrame) {
            previewFrame.src = previewUrl;
        }
    }

    getFormSettings() {
        const settings = {};

        // Color inputs
        document.querySelectorAll('.color-input').forEach(input => {
            settings[input.name] = input.value;
        });

        // Select inputs
        document.querySelectorAll('select[data-setting]').forEach(select => {
            settings[select.dataset.setting] = select.value;
        });

        // Range inputs
        document.querySelectorAll('input[type="range"]').forEach(range => {
            settings[range.name] = range.value + (range.dataset.unit || '');
        });

        return settings;
    }

    selectTheme(themeId) {
        this.currentThemeId = themeId;

        // Update visual selection
        document.querySelectorAll('.theme-card').forEach(card => {
            card.classList.remove('active');
        });
        document.querySelector(`[data-theme-id="${themeId}"]`).classList.add('active');

        // Load theme settings
        this.loadThemeSettings(themeId);
    }

    loadThemeSettings(themeId) {
        this.isLoading = true;

        fetch(`/api/themes/${themeId}/`)
            .then(response => response.json())
            .then(data => {
                this.populateForm(data.css_settings || {});
                document.getElementById('custom-css').value = data.custom_css || '';
                this.updatePreview();
                this.isLoading = false;
            })
            .catch(error => {
                console.error('Error loading theme settings:', error);
                this.isLoading = false;
            });
    }

    populateForm(settings) {
        Object.keys(settings).forEach(key => {
            const input = document.querySelector(`[name="${key}"]`);
            if (input) {
                input.value = settings[key];

                // Update range display values
                if (input.type === 'range') {
                    const display = document.querySelector(`[data-range-display="${key}"]`);
                    if (display) {
                        display.textContent = settings[key];
                    }
                }
            }
        });
    }

    saveTheme() {
        const settings = this.getFormSettings();
        const customCss = document.getElementById('custom-css').value;

        const data = {
            theme_id: this.currentThemeId,
            css_settings: JSON.stringify(settings),
            custom_css: customCss
        };

        fetch('/themes/save-settings/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken()
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showNotification('Theme saved successfully!', 'success');
            } else {
                this.showNotification('Error saving theme: ' + data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Save error:', error);
            this.showNotification('Error saving theme', 'error');
        });
    }

    activateTheme(themeId) {
        fetch(`/themes/${themeId}/activate/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': this.getCsrfToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showNotification('Theme activated successfully!', 'success');
                // Refresh page to show new active state
                setTimeout(() => location.reload(), 1000);
            } else {
                this.showNotification('Error activating theme', 'error');
            }
        });
    }

    loadActiveTheme() {
        const activeCard = document.querySelector('.theme-card.active');
        if (activeCard) {
            this.currentThemeId = activeCard.dataset.themeId;
            this.loadThemeSettings(this.currentThemeId);
        }
    }

    getCsrfToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : 'success'} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(notification);

        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }
}

// Initialize theme editor when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    new ThemeEditor();
});
