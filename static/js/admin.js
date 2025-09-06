/**
 * Admin Panel JavaScript for Bible Baptist Church Barani
 */

(function() {
    'use strict';

    // Initialize admin features when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        initializeAdminPanel();
    });

    // Initialize admin panel
    function initializeAdminPanel() {
        setupSidebarToggle();
        setupDataTables();
        setupFileUploads();
        setupFormEnhancements();
        setupConfirmations();
        setupBulkActions();
        setupCharts();
        loadAdminNotifications();
    }

    // Setup sidebar toggle for mobile
    function setupSidebarToggle() {
        const sidebarToggle = document.querySelector('[data-sidebar-toggle]');
        const sidebar = document.querySelector('.admin-sidebar');

        if (sidebarToggle && sidebar) {
            sidebarToggle.addEventListener('click', function() {
                sidebar.classList.toggle('show');
            });

            // Close sidebar when clicking outside on mobile
            document.addEventListener('click', function(e) {
                if (window.innerWidth < 768 && sidebar.classList.contains('show')) {
                    if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
                        sidebar.classList.remove('show');
                    }
                }
            });
        }
    }

    // Setup DataTables for admin lists
    function setupDataTables() {
        const tables = document.querySelectorAll('.admin-datatable');

        tables.forEach(function(table) {
            // Initialize DataTable if library is available
            if (typeof DataTable !== 'undefined') {
                new DataTable(table, {
                    responsive: true,
                    pageLength: 25,
                    language: {
                        search: 'Search:',
                        lengthMenu: 'Show _MENU_ entries',
                        info: 'Showing _START_ to _END_ of _TOTAL_ entries',
                        infoEmpty: 'Showing 0 to 0 of 0 entries',
                        infoFiltered: '(filtered from _MAX_ total entries)',
                        paginate: {
                            first: 'First',
                            last: 'Last',
                            next: 'Next',
                            previous: 'Previous'
                        }
                    }
                });
            }
        });
    }

    // Setup file uploads with drag and drop
    function setupFileUploads() {
        const uploadAreas = document.querySelectorAll('.admin-file-upload');

        uploadAreas.forEach(function(area) {
            const fileInput = area.querySelector('input[type="file"]');
            if (!fileInput) return;

            // Handle drag and drop
            area.addEventListener('dragover', function(e) {
                e.preventDefault();
                area.classList.add('drag-over');
            });

            area.addEventListener('dragleave', function(e) {
                e.preventDefault();
                area.classList.remove('drag-over');
            });

            area.addEventListener('drop', function(e) {
                e.preventDefault();
                area.classList.remove('drag-over');

                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    fileInput.files = files;
                    handleFileUpload(fileInput, files[0]);
                }
            });

            // Handle click to select file
            area.addEventListener('click', function() {
                fileInput.click();
            });

            // Handle file selection
            fileInput.addEventListener('change', function() {
                if (fileInput.files.length > 0) {
                    handleFileUpload(fileInput, fileInput.files[0]);
                }
            });
        });
    }

    // Handle file upload
    function handleFileUpload(input, file) {
        const uploadArea = input.closest('.admin-file-upload');
        if (!uploadArea) return;

        // Show file info
        const fileInfo = uploadArea.querySelector('.file-info') || document.createElement('div');
        fileInfo.className = 'file-info mt-2';
        fileInfo.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-file me-2"></i>
                <span class="file-name">${file.name}</span>
                <span class="file-size text-muted ms-2">(${formatFileSize(file.size)})</span>
            </div>
        `;

        if (!uploadArea.querySelector('.file-info')) {
            uploadArea.appendChild(fileInfo);
        }

        // Show preview if image
        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const preview = document.createElement('img');
                preview.src = e.target.result;
                preview.className = 'img-thumbnail mt-2';
                preview.style.maxWidth = '200px';
                preview.style.maxHeight = '200px';

                const existingPreview = uploadArea.querySelector('img');
                if (existingPreview) {
                    existingPreview.remove();
                }

                uploadArea.appendChild(preview);
            };
            reader.readAsDataURL(file);
        }
    }

    // Setup form enhancements
    function setupFormEnhancements() {
        // Auto-save drafts
        const autoSaveForms = document.querySelectorAll('[data-auto-save]');
        autoSaveForms.forEach(function(form) {
            const formId = form.id || 'form_' + Math.random().toString(36).substr(2, 9);
            let saveTimer = null;

            form.addEventListener('input', function() {
                clearTimeout(saveTimer);
                saveTimer = setTimeout(function() {
                    saveDraft(formId, new FormData(form));
                }, 2000);
            });

            // Load draft on page load
            loadDraft(formId, form);
        });

        // Character counters
        const textFields = document.querySelectorAll('textarea[maxlength], input[maxlength]');
        textFields.forEach(function(field) {
            const maxLength = field.getAttribute('maxlength');
            const counter = document.createElement('small');
            counter.className = 'form-text text-muted';
            counter.id = field.id + '_counter';

            function updateCounter() {
                const remaining = maxLength - field.value.length;
                counter.textContent = `${remaining} characters remaining`;

                if (remaining < 50) {
                    counter.classList.add('text-warning');
                    counter.classList.remove('text-muted');
                } else {
                    counter.classList.add('text-muted');
                    counter.classList.remove('text-warning');
                }
            }

            field.parentNode.appendChild(counter);
            field.addEventListener('input', updateCounter);
            updateCounter();
        });

        // Rich text editors
        const richTextAreas = document.querySelectorAll('[data-rich-text]');
        richTextAreas.forEach(function(textarea) {
            // Initialize rich text editor (would require a library like TinyMCE or CKEditor)
            // For now, just add some styling
            textarea.style.minHeight = '200px';
            textarea.style.fontFamily = 'monospace';
        });
    }

    // Setup confirmations
    function setupConfirmations() {
        const confirmButtons = document.querySelectorAll('[data-confirm]');

        confirmButtons.forEach(function(button) {
            button.addEventListener('click', function(e) {
                const message = button.getAttribute('data-confirm');
                const isDestructive = button.classList.contains('btn-danger') || button.classList.contains('admin-btn-danger');

                if (isDestructive) {
                    e.preventDefault();
                    showConfirmationModal(message, function() {
                        // If it's a form button, submit the form
                        if (button.type === 'submit') {
                            button.form.submit();
                        } else if (button.href) {
                            window.location.href = button.href;
                        }
                    });
                } else {
                    if (!confirm(message)) {
                        e.preventDefault();
                    }
                }
            });
        });
    }

    // Show confirmation modal
    function showConfirmationModal(message, onConfirm) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Confirmation Required</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p>${message}</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-danger" id="confirm-action">Confirm</button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();

        modal.querySelector('#confirm-action').addEventListener('click', function() {
            onConfirm();
            bsModal.hide();
        });

        modal.addEventListener('hidden.bs.modal', function() {
            document.body.removeChild(modal);
        });
    }

    // Setup bulk actions
    function setupBulkActions() {
        const bulkActionForms = document.querySelectorAll('[data-bulk-actions]');

        bulkActionForms.forEach(function(form) {
            const selectAllCheckbox = form.querySelector('[data-select-all]');
            const itemCheckboxes = form.querySelectorAll('[data-item-checkbox]');
            const actionSelect = form.querySelector('[data-bulk-action]');
            const actionButton = form.querySelector('[data-bulk-submit]');

            if (!selectAllCheckbox || !actionSelect || !actionButton) return;

            // Select/deselect all
            selectAllCheckbox.addEventListener('change', function() {
                itemCheckboxes.forEach(function(checkbox) {
                    checkbox.checked = selectAllCheckbox.checked;
                });
                updateBulkActionButton();
            });

            // Update select all when individual checkboxes change
            itemCheckboxes.forEach(function(checkbox) {
                checkbox.addEventListener('change', function() {
                    const checkedCount = form.querySelectorAll('[data-item-checkbox]:checked').length;
                    selectAllCheckbox.checked = checkedCount === itemCheckboxes.length;
                    selectAllCheckbox.indeterminate = checkedCount > 0 && checkedCount < itemCheckboxes.length;
                    updateBulkActionButton();
                });
            });

            function updateBulkActionButton() {
                const checkedCount = form.querySelectorAll('[data-item-checkbox]:checked').length;
                actionButton.disabled = checkedCount === 0 || !actionSelect.value;

                if (checkedCount > 0) {
                    actionButton.textContent = `Apply to ${checkedCount} selected`;
                } else {
                    actionButton.textContent = 'Apply Action';
                }
            }

            actionSelect.addEventListener('change', updateBulkActionButton);
            updateBulkActionButton();
        });
    }

    // Setup charts
    function setupCharts() {
        const chartElements = document.querySelectorAll('[data-chart]');

        chartElements.forEach(function(element) {
            const chartType = element.getAttribute('data-chart');
            const chartData = JSON.parse(element.getAttribute('data-chart-data') || '{}');

            // Initialize chart (would require Chart.js or similar library)
            // For now, just show placeholder
            element.innerHTML = `
                <div class="chart-placeholder text-center py-5">
                    <i class="fas fa-chart-${chartType} fa-3x text-muted mb-3"></i>
                    <div class="text-muted">Chart: ${chartType}</div>
                </div>
            `;
        });
    }

    // Load admin notifications
    function loadAdminNotifications() {
        fetch('/api/notifications/recent/')
            .then(response => response.json())
            .then(data => {
                updateNotificationBadge(data.notifications);
            })
            .catch(error => {
                console.error('Error loading admin notifications:', error);
            });
    }

    // Update notification badge
    function updateNotificationBadge(notifications) {
        const badge = document.getElementById('notification-count');
        if (badge && notifications) {
            const unreadCount = notifications.filter(n => !n.is_read).length;
            if (unreadCount > 0) {
                badge.textContent = unreadCount > 99 ? '99+' : unreadCount;
                badge.style.display = 'inline';
            } else {
                badge.style.display = 'none';
            }
        }
    }

    // Utility functions
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';

        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));

        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    function saveDraft(formId, formData) {
        const draftData = {};
        for (let [key, value] of formData.entries()) {
            draftData[key] = value;
        }

        localStorage.setItem(`draft_${formId}`, JSON.stringify(draftData));

        // Show save indicator
        showSaveIndicator('Draft saved');
    }

    function loadDraft(formId, form) {
        const draftData = localStorage.getItem(`draft_${formId}`);
        if (!draftData) return;

        try {
            const data = JSON.parse(draftData);
            for (let [key, value] of Object.entries(data)) {
                const field = form.querySelector(`[name="${key}"]`);
                if (field) {
                    field.value = value;
                }
            }

            showSaveIndicator('Draft loaded');
        } catch (error) {
            console.error('Error loading draft:', error);
        }
    }

    function showSaveIndicator(message) {
        const indicator = document.createElement('div');
        indicator.className = 'alert alert-info position-fixed';
        indicator.style.cssText = 'top: 20px; right: 20px; z-index: 9999;';
        indicator.textContent = message;

        document.body.appendChild(indicator);

        setTimeout(function() {
            indicator.classList.add('fade');
            setTimeout(function() {
                if (indicator.parentNode) {
                    indicator.parentNode.removeChild(indicator);
                }
            }, 500);
        }, 2000);
    }

    // Export admin functions
    window.ChurchAdmin = {
        showConfirmationModal: showConfirmationModal,
        formatFileSize: formatFileSize,
        saveDraft: saveDraft,
        loadDraft: loadDraft
    };

})();