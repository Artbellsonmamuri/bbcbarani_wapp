/**
 * Analytics JavaScript for Bible Baptist Church Barani
 */

(function() {
    'use strict';

    let analyticsInitialized = false;

    // Initialize analytics when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        initializeAnalytics();
    });

    // Initialize analytics system
    function initializeAnalytics() {
        if (analyticsInitialized) return;

        setupPageViewTracking();
        setupEventTracking();
        setupUserActivityTracking();
        setupPerformanceTracking();

        analyticsInitialized = true;
    }

    // Track page views
    function setupPageViewTracking() {
        // Track initial page view
        trackPageView({
            url: window.location.href,
            path: window.location.pathname,
            title: document.title,
            referrer: document.referrer
        });

        // Track page views for single-page app navigation (if applicable)
        window.addEventListener('popstate', function() {
            trackPageView({
                url: window.location.href,
                path: window.location.pathname,
                title: document.title,
                referrer: document.referrer
            });
        });
    }

    // Track page view
    function trackPageView(data) {
        // Add additional data
        const pageViewData = {
            ...data,
            user_agent: navigator.userAgent,
            screen_resolution: `${screen.width}x${screen.height}`,
            viewport_size: `${window.innerWidth}x${window.innerHeight}`,
            timestamp: new Date().toISOString(),
            session_id: getOrCreateSessionId(),
            device_type: getDeviceType(),
            browser: getBrowser(),
            os: getOperatingSystem()
        };

        // Send to server
        sendAnalyticsData('/api/analytics/track-page-view/', pageViewData);
    }

    // Setup event tracking
    function setupEventTracking() {
        // Track clicks on important elements
        document.addEventListener('click', function(e) {
            const target = e.target.closest('[data-track]');
            if (target) {
                const eventData = {
                    event_type: 'click',
                    element_type: target.tagName.toLowerCase(),
                    element_id: target.id,
                    element_class: target.className,
                    element_text: target.textContent.substring(0, 100),
                    track_data: target.getAttribute('data-track'),
                    page_url: window.location.href,
                    timestamp: new Date().toISOString()
                };

                trackEvent('element_click', eventData);
            }
        });

        // Track form submissions
        document.addEventListener('submit', function(e) {
            const form = e.target;
            if (form.tagName === 'FORM') {
                const formData = {
                    form_id: form.id,
                    form_action: form.action,
                    form_method: form.method,
                    page_url: window.location.href,
                    timestamp: new Date().toISOString()
                };

                trackEvent('form_submit', formData);
            }
        });

        // Track external links
        document.addEventListener('click', function(e) {
            const link = e.target.closest('a');
            if (link && link.hostname !== window.location.hostname) {
                const linkData = {
                    url: link.href,
                    text: link.textContent.substring(0, 100),
                    page_url: window.location.href,
                    timestamp: new Date().toISOString()
                };

                trackEvent('external_link_click', linkData);
            }
        });

        // Track downloads
        document.addEventListener('click', function(e) {
            const link = e.target.closest('a');
            if (link && isDownloadLink(link.href)) {
                const downloadData = {
                    file_url: link.href,
                    file_name: link.href.split('/').pop(),
                    file_type: getFileExtension(link.href),
                    page_url: window.location.href,
                    timestamp: new Date().toISOString()
                };

                trackEvent('file_download', downloadData);
            }
        });

        // Track scroll depth
        let maxScrollDepth = 0;
        let scrollTimer = null;

        window.addEventListener('scroll', function() {
            const scrollDepth = Math.round((window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100);

            if (scrollDepth > maxScrollDepth) {
                maxScrollDepth = scrollDepth;

                // Debounce scroll tracking
                clearTimeout(scrollTimer);
                scrollTimer = setTimeout(function() {
                    trackEvent('scroll_depth', {
                        max_depth: maxScrollDepth,
                        page_url: window.location.href,
                        timestamp: new Date().toISOString()
                    });
                }, 1000);
            }
        });
    }

    // Track custom events
    function trackEvent(eventName, eventData) {
        const data = {
            event_name: eventName,
            event_data: eventData,
            session_id: getOrCreateSessionId(),
            user_agent: navigator.userAgent,
            timestamp: new Date().toISOString()
        };

        sendAnalyticsData('/api/analytics/track-event/', data);
    }

    // Setup user activity tracking
    function setupUserActivityTracking() {
        let startTime = Date.now();
        let isActive = true;
        let activityTimer = null;

        // Track time on page
        window.addEventListener('beforeunload', function() {
            const timeOnPage = Math.round((Date.now() - startTime) / 1000);

            // Use sendBeacon for reliable sending on page unload
            if (navigator.sendBeacon) {
                const data = JSON.stringify({
                    event_name: 'time_on_page',
                    event_data: {
                        duration: timeOnPage,
                        page_url: window.location.href,
                        timestamp: new Date().toISOString()
                    }
                });

                navigator.sendBeacon('/api/analytics/track-event/', data);
            }
        });

        // Track user activity/inactivity
        const activityEvents = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];

        function resetActivityTimer() {
            isActive = true;
            clearTimeout(activityTimer);

            activityTimer = setTimeout(function() {
                isActive = false;
                trackEvent('user_inactive', {
                    page_url: window.location.href,
                    timestamp: new Date().toISOString()
                });
            }, 300000); // 5 minutes of inactivity
        }

        activityEvents.forEach(function(event) {
            document.addEventListener(event, resetActivityTimer, true);
        });

        resetActivityTimer();
    }

    // Setup performance tracking
    function setupPerformanceTracking() {
        // Track page load performance
        window.addEventListener('load', function() {
            setTimeout(function() {
                const perfData = window.performance.timing;
                const loadTime = perfData.loadEventEnd - perfData.navigationStart;
                const domContentLoadedTime = perfData.domContentLoadedEventEnd - perfData.navigationStart;
                const firstPaintTime = perfData.responseStart - perfData.navigationStart;

                trackEvent('page_performance', {
                    load_time: loadTime,
                    dom_content_loaded_time: domContentLoadedTime,
                    first_paint_time: firstPaintTime,
                    page_url: window.location.href,
                    timestamp: new Date().toISOString()
                });
            }, 1000);
        });

        // Track JavaScript errors
        window.addEventListener('error', function(e) {
            trackEvent('javascript_error', {
                message: e.message,
                filename: e.filename,
                lineno: e.lineno,
                colno: e.colno,
                stack: e.error ? e.error.stack : '',
                page_url: window.location.href,
                timestamp: new Date().toISOString()
            });
        });
    }

    // Send analytics data to server
    function sendAnalyticsData(endpoint, data) {
        // Don't track in development or for admin users if configured
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            console.log('Analytics (dev):', endpoint, data);
            return;
        }

        fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify(data)
        }).catch(function(error) {
            console.warn('Analytics tracking failed:', error);
        });
    }

    // Utility functions
    function getOrCreateSessionId() {
        let sessionId = sessionStorage.getItem('church_session_id');
        if (!sessionId) {
            sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            sessionStorage.setItem('church_session_id', sessionId);
        }
        return sessionId;
    }

    function getDeviceType() {
        const userAgent = navigator.userAgent.toLowerCase();

        if (/tablet|ipad|playbook|silk/i.test(userAgent)) {
            return 'tablet';
        } else if (/mobile|iphone|ipod|android|blackberry|opera|mini|windows\s?phone|palm|smartphone|iemobile/i.test(userAgent)) {
            return 'mobile';
        } else if (/bot|crawler|spider|crawling/i.test(userAgent)) {
            return 'bot';
        } else {
            return 'desktop';
        }
    }

    function getBrowser() {
        const userAgent = navigator.userAgent;

        if (userAgent.indexOf('Chrome') > -1) return 'Chrome';
        if (userAgent.indexOf('Firefox') > -1) return 'Firefox';
        if (userAgent.indexOf('Safari') > -1) return 'Safari';
        if (userAgent.indexOf('Edge') > -1) return 'Edge';
        if (userAgent.indexOf('Opera') > -1) return 'Opera';
        if (userAgent.indexOf('MSIE') > -1) return 'Internet Explorer';

        return 'Unknown';
    }

    function getOperatingSystem() {
        const userAgent = navigator.userAgent;

        if (userAgent.indexOf('Windows') > -1) return 'Windows';
        if (userAgent.indexOf('Mac OS') > -1) return 'macOS';
        if (userAgent.indexOf('Linux') > -1) return 'Linux';
        if (userAgent.indexOf('Android') > -1) return 'Android';
        if (userAgent.indexOf('iOS') > -1) return 'iOS';

        return 'Unknown';
    }

    function isDownloadLink(url) {
        const downloadExtensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.zip', '.rar', '.mp3', '.mp4', '.avi', '.mov'];
        return downloadExtensions.some(ext => url.toLowerCase().includes(ext));
    }

    function getFileExtension(url) {
        return url.split('.').pop().split(/\#|\?/)[0];
    }

    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }

    // Global function for manual tracking
    window.trackPageView = trackPageView;
    window.trackEvent = trackEvent;

    // Export analytics functions
    window.ChurchAnalytics = {
        trackPageView: trackPageView,
        trackEvent: trackEvent,
        getSessionId: getOrCreateSessionId,
        getDeviceType: getDeviceType
    };

})();