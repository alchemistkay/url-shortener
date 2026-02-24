// ============================================
// CONFIGURATION
// ============================================

// API base URL - change this if deploying elsewhere
const API_BASE_URL = 'https://short.k4scloud.com/api/v1';

// LocalStorage key for recent URLs
const STORAGE_KEY = 'recentUrls';

// Current short code (for stats viewing)
let currentShortCode = null;

// ============================================
// ON PAGE LOAD
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // Load recent URLs from localStorage
    loadRecentUrls();
    
    // Setup form submission
    document.getElementById('shortenForm').addEventListener('submit', handleSubmit);
});

// ============================================
// HANDLE FORM SUBMISSION
// ============================================

async function handleSubmit(event) {
    // Prevent page reload
    event.preventDefault();
    
    // Get form values
    const originalUrl = document.getElementById('originalUrl').value;
    const customSlug = document.getElementById('customSlug').value;
    const expiryHours = document.getElementById('expiryHours').value;
    
    // Hide previous results/errors
    document.getElementById('resultCard').style.display = 'none';
    document.getElementById('errorCard').style.display = 'none';
    
    // Build request body
    const requestBody = {
        original_url: originalUrl
    };
    
    // Add optional fields if provided
    if (customSlug) {
        requestBody.custom_slug = customSlug;
    }
    
    if (expiryHours) {
        requestBody.expires_in_hours = parseInt(expiryHours);
    }
    
    // Show loading state
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = '⏳ Shortening...';
    submitBtn.disabled = true;
    
    try {
        // Call API
        const response = await fetch(`${API_BASE_URL}/shorten`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Success!
            showSuccess(data);
            
            // Save to recent URLs
            saveToRecent(data);
            
            // Reload recent URLs list
            loadRecentUrls();
            
        } else {
            // API returned error
            showError(data.detail || 'An error occurred');
        }
        
    } catch (error) {
        // Network error
        showError('Network error: ' + error.message);
        
    } finally {
        // Reset button
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }
}

// ============================================
// SHOW SUCCESS RESULT
// ============================================

function showSuccess(data) {
    currentShortCode = data.short_code;
    
    // Show result card
    const resultCard = document.getElementById('resultCard');
    resultCard.style.display = 'block';
    
    // Set short URL
    document.getElementById('shortUrl').value = data.short_url;
    
    // Build info text
    let info = `<strong>Original URL:</strong> ${data.original_url}<br>`;
    info += `<strong>Short Code:</strong> ${data.short_code}<br>`;
    info += `<strong>Created:</strong> ${new Date(data.created_at).toLocaleString()}<br>`;
    
    if (data.expires_at) {
        info += `<strong>Expires:</strong> ${new Date(data.expires_at).toLocaleString()}<br>`;
    }
    
    document.getElementById('urlInfo').innerHTML = info;
    
    // Scroll to result
    resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// ============================================
// SHOW ERROR MESSAGE
// ============================================

function showError(message) {
    const errorCard = document.getElementById('errorCard');
    errorCard.style.display = 'block';
    
    document.getElementById('errorMessage').textContent = message;
    
    // Scroll to error
    errorCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// ============================================
// COPY TO CLIPBOARD
// ============================================

function copyToClipboard() {
    const shortUrlInput = document.getElementById('shortUrl');
    
    // Select text
    shortUrlInput.select();
    shortUrlInput.setSelectionRange(0, 99999); // For mobile
    
    // Copy to clipboard
    navigator.clipboard.writeText(shortUrlInput.value).then(() => {
        // Show feedback
        alert('✅ Copied to clipboard!');
    }).catch(err => {
        alert('❌ Failed to copy: ' + err);
    });
}

// ============================================
// VIEW STATS
// ============================================

async function viewStats() {
    if (!currentShortCode) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/stats/${currentShortCode}`);
        const data = await response.json();
        
        if (response.ok) {
            let statsHtml = `
                <strong>📊 Statistics for ${data.short_code}</strong><br><br>
                <strong>Total Clicks:</strong> ${data.total_clicks}<br>
                <strong>Original URL:</strong> ${data.original_url}<br>
                <strong>Active:</strong> ${data.is_active ? 'Yes ✅' : 'No ❌'}<br>
                <strong>Created:</strong> ${new Date(data.created_at).toLocaleString()}<br>
            `;
            
            if (data.expires_at) {
                statsHtml += `<strong>Expires:</strong> ${new Date(data.expires_at).toLocaleString()}<br>`;
            }
            
            document.getElementById('urlInfo').innerHTML = statsHtml;
        } else {
            alert('Failed to load stats: ' + data.detail);
        }
        
    } catch (error) {
        alert('Network error: ' + error.message);
    }
}

// ============================================
// SAVE TO RECENT URLS (LocalStorage)
// ============================================

function saveToRecent(data) {
    // Get existing URLs
    let recent = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    
    // Add new URL at the beginning
    recent.unshift({
        short_code: data.short_code,
        original_url: data.original_url,
        short_url: data.short_url,
        clicks: data.clicks,
        created_at: data.created_at
    });
    
    // Keep only last 10
    recent = recent.slice(0, 10);
    
    // Save back to localStorage
    localStorage.setItem(STORAGE_KEY, JSON.stringify(recent));
}

// ============================================
// LOAD RECENT URLS (with live click counts)
// ============================================

async function loadRecentUrls() {
    const recent = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    const container = document.getElementById('recentUrls');
    
    if (recent.length === 0) {
        container.innerHTML = '<p class="hint">Your shortened URLs will appear here...</p>';
        return;
    }
    
    // Show loading state
    container.innerHTML = '<p class="hint">Loading stats...</p>';
    
    // Fetch live stats for each URL
    const urlsWithStats = await Promise.all(
        recent.map(async (url) => {
            try {
                // Fetch latest stats from API
                const response = await fetch(`${API_BASE_URL}/stats/${url.short_code}`);
                
                if (response.ok) {
                    const stats = await response.json();
                    // Return URL with updated click count
                    return {
                        ...url,
                        clicks: stats.total_clicks,  // Live data!
                        is_active: stats.is_active
                    };
                } else {
                    // API error - return original data
                    return url;
                }
            } catch (error) {
                // Network error - return original data
                console.error('Failed to fetch stats:', error);
                return url;
            }
        })
    );
    
    // Build HTML for recent URLs
    let html = '';
    
    for (const url of urlsWithStats) {
        // Gray out inactive URLs
        const cardStyle = url.is_active === false ? 'opacity: 0.6;' : '';
        const statusBadge = url.is_active === false ? '<span style="color: red; font-size: 0.8rem;"> (Inactive)</span>' : '';
        
        html += `
            <div class="url-item" style="${cardStyle}">
                <div class="url-item-header">
                    <span class="url-code">${url.short_code}${statusBadge}</span>
                    <span class="url-clicks">${url.clicks} clicks</span>
                </div>
                <div class="url-original">${url.original_url}</div>
                <small style="color: #999;">
                    Created: ${new Date(url.created_at).toLocaleString()}
                </small>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

// ============================================
// FOOTER LINKS
// ============================================

function openApiDocs() {
    window.open(`${API_BASE_URL}/docs`, '_blank');
}

function openHealthCheck() {
    window.open(`${API_BASE_URL}/health`, '_blank');
}