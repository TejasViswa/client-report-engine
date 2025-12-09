/**
 * Client Report Engine - Frontend Application
 */

const API_BASE = '';

// ============================================
// State
// ============================================

let clients = [];
let templates = [];
let editingClientId = null;

// ============================================
// Initialization
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initForms();
    checkApiHealth();
    loadClients();
    loadTemplates();
    initColorPickers();
});

function initNavigation() {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', () => {
            const view = item.dataset.view;
            switchView(view);
        });
    });
}

function switchView(viewName) {
    // Update nav
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.toggle('active', item.dataset.view === viewName);
    });
    
    // Update views
    document.querySelectorAll('.view').forEach(view => {
        view.classList.toggle('active', view.id === `${viewName}-view`);
    });
    
    // Refresh data when switching views
    if (viewName === 'clients') loadClients();
    if (viewName === 'templates') loadTemplates();
    if (viewName === 'generate') {
        loadClientsForSelect();
        loadTemplatesForSelect();
    }
}

function initForms() {
    // Client form
    document.getElementById('client-form').addEventListener('submit', handleClientSubmit);
    
    // Report form
    document.getElementById('report-form').addEventListener('submit', handleReportSubmit);
}

function initColorPickers() {
    const primaryPicker = document.getElementById('primary-color-picker');
    const primaryInput = document.getElementById('primary-color');
    const secondaryPicker = document.getElementById('secondary-color-picker');
    const secondaryInput = document.getElementById('secondary-color');
    
    primaryPicker.addEventListener('input', (e) => {
        primaryInput.value = e.target.value;
    });
    primaryInput.addEventListener('input', (e) => {
        if (/^#[0-9A-Fa-f]{6}$/.test(e.target.value)) {
            primaryPicker.value = e.target.value;
        }
    });
    
    secondaryPicker.addEventListener('input', (e) => {
        secondaryInput.value = e.target.value;
    });
    secondaryInput.addEventListener('input', (e) => {
        if (/^#[0-9A-Fa-f]{6}$/.test(e.target.value)) {
            secondaryPicker.value = e.target.value;
        }
    });
}

// ============================================
// API Health Check
// ============================================

async function checkApiHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();
        
        if (data.status === 'healthy') {
            document.getElementById('api-status').textContent = 'Connected';
            document.querySelector('.status-dot').classList.add('connected');
        }
    } catch (error) {
        document.getElementById('api-status').textContent = 'Disconnected';
        showToast('Failed to connect to API', 'error');
    }
}

// ============================================
// Clients
// ============================================

async function loadClients() {
    try {
        const response = await fetch(`${API_BASE}/clients`);
        clients = await response.json();
        renderClients();
    } catch (error) {
        showToast('Failed to load clients', 'error');
    }
}

function renderClients() {
    const grid = document.getElementById('clients-grid');
    
    if (clients.length === 0) {
        grid.innerHTML = `
            <div class="empty-state">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                    <circle cx="9" cy="7" r="4"/>
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                    <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                </svg>
                <h3>No clients yet</h3>
                <p>Add your first client to get started</p>
            </div>
        `;
        return;
    }
    
    grid.innerHTML = clients.map(client => `
        <div class="card client-card">
            <div class="client-card-header">
                <div class="client-logo" style="${client.primary_color ? `background: ${client.primary_color}; color: white;` : ''}">
                    ${client.logo_path 
                        ? `<img src="${client.logo_path}" alt="${client.display_name}">`
                        : client.display_name.charAt(0).toUpperCase()
                    }
                </div>
                <div class="client-info">
                    <h3>${escapeHtml(client.display_name)}</h3>
                    <span class="client-id">${escapeHtml(client.client_id)}</span>
                </div>
            </div>
            ${(client.primary_color || client.secondary_color) ? `
                <div class="client-colors">
                    ${client.primary_color ? `<div class="color-swatch" style="background: ${client.primary_color}" title="Primary: ${client.primary_color}"></div>` : ''}
                    ${client.secondary_color ? `<div class="color-swatch" style="background: ${client.secondary_color}" title="Secondary: ${client.secondary_color}"></div>` : ''}
                </div>
            ` : ''}
            <div class="client-card-actions">
                <button class="btn btn-secondary btn-sm" onclick="editClient('${client.client_id}')">
                    Edit
                </button>
                <button class="btn btn-secondary btn-sm" onclick="uploadLogoPrompt('${client.client_id}')">
                    Logo
                </button>
                <button class="btn btn-danger btn-sm" onclick="deleteClient('${client.client_id}')">
                    Delete
                </button>
            </div>
        </div>
    `).join('');
}

function openClientModal(clientId = null) {
    editingClientId = clientId;
    const modal = document.getElementById('client-modal');
    const title = document.getElementById('modal-title');
    const form = document.getElementById('client-form');
    const clientIdInput = document.getElementById('client-id');
    
    if (clientId) {
        const client = clients.find(c => c.client_id === clientId);
        if (client) {
            title.textContent = 'Edit Client';
            clientIdInput.value = client.client_id;
            clientIdInput.readOnly = true;
            document.getElementById('display-name').value = client.display_name;
            document.getElementById('primary-color').value = client.primary_color || '';
            document.getElementById('primary-color-picker').value = client.primary_color || '#0066cc';
            document.getElementById('secondary-color').value = client.secondary_color || '';
            document.getElementById('secondary-color-picker').value = client.secondary_color || '#ffffff';
            document.getElementById('font-family').value = client.font_family || '';
            document.getElementById('website-url').value = client.website_url || '';
        }
    } else {
        title.textContent = 'Add Client';
        clientIdInput.readOnly = false;
        form.reset();
        document.getElementById('primary-color-picker').value = '#0066cc';
        document.getElementById('secondary-color-picker').value = '#ffffff';
    }
    
    modal.classList.add('active');
}

function closeClientModal() {
    document.getElementById('client-modal').classList.remove('active');
    editingClientId = null;
}

async function handleClientSubmit(e) {
    e.preventDefault();
    
    const data = {
        client_id: document.getElementById('client-id').value.toLowerCase().replace(/\s+/g, '_'),
        display_name: document.getElementById('display-name').value,
        primary_color: document.getElementById('primary-color').value || null,
        secondary_color: document.getElementById('secondary-color').value || null,
        font_family: document.getElementById('font-family').value || null,
        website_url: document.getElementById('website-url').value || null,
    };
    
    try {
        const response = await fetch(`${API_BASE}/clients`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        
        if (!response.ok) throw new Error('Failed to save client');
        
        showToast(editingClientId ? 'Client updated!' : 'Client created!', 'success');
        closeClientModal();
        loadClients();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

function editClient(clientId) {
    openClientModal(clientId);
}

async function deleteClient(clientId) {
    if (!confirm(`Are you sure you want to delete client "${clientId}"?`)) return;
    
    try {
        const response = await fetch(`${API_BASE}/clients/${clientId}`, {
            method: 'DELETE',
        });
        
        if (!response.ok) throw new Error('Failed to delete client');
        
        showToast('Client deleted', 'success');
        loadClients();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

function uploadLogoPrompt(clientId) {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.onchange = (e) => uploadLogo(clientId, e.target.files[0]);
    input.click();
}

async function uploadLogo(clientId, file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`${API_BASE}/clients/${clientId}/logo`, {
            method: 'POST',
            body: formData,
        });
        
        if (!response.ok) throw new Error('Failed to upload logo');
        
        showToast('Logo uploaded!', 'success');
        loadClients();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// ============================================
// Templates
// ============================================

async function loadTemplates() {
    try {
        const response = await fetch(`${API_BASE}/templates`);
        const data = await response.json();
        templates = data.templates || [];
        renderTemplates();
    } catch (error) {
        showToast('Failed to load templates', 'error');
    }
}

function renderTemplates() {
    const grid = document.getElementById('templates-grid');
    
    if (templates.length === 0) {
        grid.innerHTML = `
            <div class="empty-state">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                    <line x1="3" y1="9" x2="21" y2="9"/>
                    <line x1="9" y1="21" x2="9" y2="9"/>
                </svg>
                <h3>No templates found</h3>
                <p>Run the template creation script to add templates</p>
            </div>
        `;
        return;
    }
    
    grid.innerHTML = templates.map(template => `
        <div class="card template-card">
            <div class="template-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14,2 14,8 20,8"/>
                    <line x1="16" y1="13" x2="8" y2="13"/>
                    <line x1="16" y1="17" x2="8" y2="17"/>
                </svg>
            </div>
            <h3>${escapeHtml(template)}</h3>
            <p>DOCX Template</p>
        </div>
    `).join('');
}

async function loadTemplatesForSelect() {
    const select = document.getElementById('report-template');
    select.innerHTML = '<option value="">Select a template...</option>';
    
    templates.forEach(template => {
        const option = document.createElement('option');
        option.value = template;
        option.textContent = template;
        select.appendChild(option);
    });
}

async function loadClientsForSelect() {
    const select = document.getElementById('report-client');
    select.innerHTML = '<option value="">Select a client...</option>';
    
    clients.forEach(client => {
        const option = document.createElement('option');
        option.value = client.client_id;
        option.textContent = client.display_name;
        select.appendChild(option);
    });
}

// ============================================
// Report Generation
// ============================================

let metricCount = 0;
let highlightCount = 0;
let recommendationCount = 0;

function addMetric() {
    const container = document.getElementById('metrics-container');
    const id = ++metricCount;
    
    const item = document.createElement('div');
    item.className = 'metric-item';
    item.id = `metric-${id}`;
    item.innerHTML = `
        <div class="form-grid">
            <div class="form-group">
                <input type="text" name="metric_name_${id}" placeholder="Name" required>
            </div>
            <div class="form-group">
                <input type="text" name="metric_value_${id}" placeholder="Value" required>
            </div>
            <div class="form-group">
                <input type="text" name="metric_change_${id}" placeholder="Change">
            </div>
            <div class="form-group">
                <select name="metric_status_${id}">
                    <option value="positive">Positive</option>
                    <option value="neutral">Neutral</option>
                    <option value="negative">Negative</option>
                </select>
            </div>
        </div>
        <button type="button" class="remove-btn" onclick="removeItem('metric-${id}')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
        </button>
    `;
    container.appendChild(item);
}

function addHighlight() {
    const container = document.getElementById('highlights-container');
    const id = ++highlightCount;
    
    const item = document.createElement('div');
    item.className = 'highlight-item';
    item.id = `highlight-${id}`;
    item.innerHTML = `
        <div class="form-group" style="flex: 1;">
            <input type="text" name="highlight_${id}" placeholder="Enter a highlight..." required>
        </div>
        <button type="button" class="remove-btn" onclick="removeItem('highlight-${id}')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
        </button>
    `;
    container.appendChild(item);
}

function addRecommendation() {
    const container = document.getElementById('recommendations-container');
    const id = ++recommendationCount;
    
    const item = document.createElement('div');
    item.className = 'recommendation-item';
    item.id = `recommendation-${id}`;
    item.innerHTML = `
        <div class="form-grid">
            <div class="form-group">
                <select name="rec_priority_${id}">
                    <option value="High">High</option>
                    <option value="Medium" selected>Medium</option>
                    <option value="Low">Low</option>
                </select>
            </div>
            <div class="form-group">
                <input type="text" name="rec_title_${id}" placeholder="Title" required>
            </div>
            <div class="form-group">
                <input type="text" name="rec_description_${id}" placeholder="Description" required>
            </div>
        </div>
        <button type="button" class="remove-btn" onclick="removeItem('recommendation-${id}')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
        </button>
    `;
    container.appendChild(item);
}

function removeItem(id) {
    document.getElementById(id)?.remove();
}

async function handleReportSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData(form);
    
    // Collect metrics
    const metrics = [];
    document.querySelectorAll('.metric-item').forEach((item, index) => {
        const id = item.id.split('-')[1];
        const name = form.querySelector(`[name="metric_name_${id}"]`)?.value;
        if (name) {
            metrics.push({
                name,
                value: form.querySelector(`[name="metric_value_${id}"]`)?.value || '',
                change: form.querySelector(`[name="metric_change_${id}"]`)?.value || '',
                status: form.querySelector(`[name="metric_status_${id}"]`)?.value || 'neutral',
            });
        }
    });
    
    // Collect highlights
    const highlights = [];
    document.querySelectorAll('.highlight-item').forEach(item => {
        const id = item.id.split('-')[1];
        const value = form.querySelector(`[name="highlight_${id}"]`)?.value;
        if (value) highlights.push(value);
    });
    
    // Collect recommendations
    const recommendations = [];
    document.querySelectorAll('.recommendation-item').forEach(item => {
        const id = item.id.split('-')[1];
        const title = form.querySelector(`[name="rec_title_${id}"]`)?.value;
        if (title) {
            recommendations.push({
                priority: form.querySelector(`[name="rec_priority_${id}"]`)?.value || 'Medium',
                title,
                description: form.querySelector(`[name="rec_description_${id}"]`)?.value || '',
            });
        }
    });
    
    // Build request
    const request = {
        client_id: document.getElementById('report-client').value,
        template_name: document.getElementById('report-template').value,
        report_date: document.getElementById('report-date').value || undefined,
        report_period: document.getElementById('report-period').value || undefined,
        prepared_by: document.getElementById('report-prepared-by').value || undefined,
        executive_summary: document.getElementById('report-summary').value || undefined,
        metrics,
        highlights,
        recommendations,
        generate_pdf: document.getElementById('generate-pdf').checked,
    };
    
    // Add contact if any field is filled
    const contactName = document.getElementById('contact-name').value;
    const contactTitle = document.getElementById('contact-title').value;
    const contactEmail = document.getElementById('contact-email').value;
    const contactPhone = document.getElementById('contact-phone').value;
    
    if (contactName || contactTitle || contactEmail || contactPhone) {
        request.contact = {
            name: contactName || '',
            title: contactTitle || undefined,
            email: contactEmail || undefined,
            phone: contactPhone || undefined,
        };
    }
    
    try {
        const response = await fetch(`${API_BASE}/reports/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request),
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to generate report');
        }
        
        const result = await response.json();
        showReportResult(result);
    } catch (error) {
        showToast(error.message, 'error');
    }
}

function showReportResult(result) {
    const modal = document.getElementById('result-modal');
    const buttons = document.getElementById('download-buttons');
    
    const docxFilename = result.docx_path.split('/').pop();
    let html = `
        <a href="${API_BASE}/reports/download/${docxFilename}" class="btn btn-primary" download>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7,10 12,15 17,10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            Download DOCX
        </a>
    `;
    
    if (result.pdf_path) {
        const pdfFilename = result.pdf_path.split('/').pop();
        html += `
            <a href="${API_BASE}/reports/download/${pdfFilename}" class="btn btn-secondary" download>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                    <polyline points="7,10 12,15 17,10"/>
                    <line x1="12" y1="15" x2="12" y2="3"/>
                </svg>
                Download PDF
            </a>
        `;
    }
    
    buttons.innerHTML = html;
    modal.classList.add('active');
}

function closeResultModal() {
    document.getElementById('result-modal').classList.remove('active');
}

// ============================================
// Utilities
// ============================================

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            ${type === 'success' 
                ? '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22,4 12,14.01 9,11.01"/>'
                : '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>'
            }
        </svg>
        <span class="toast-message">${escapeHtml(message)}</span>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.25s ease reverse';
        setTimeout(() => toast.remove(), 250);
    }, 4000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Close modals on backdrop click
document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('active');
        }
    });
});

// Close modals on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal.active').forEach(modal => {
            modal.classList.remove('active');
        });
    }
});

