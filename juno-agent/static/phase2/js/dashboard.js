// JUNO Phase 2 Dashboard JavaScript

class JUNODashboard {
    constructor() {
        this.currentSection = 'dashboard';
        this.apiBase = '/api/v2';
        this.refreshInterval = 30000; // 30 seconds
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDashboardData();
        this.startAutoRefresh();
        this.setupRealtimeUpdates();
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const section = item.dataset.section;
                this.switchSection(section);
            });
        });

        // Filter buttons
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.handleFilterChange(e.target);
            });
        });

        // Approval buttons
        document.querySelectorAll('.approve-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.handleApprovalAction(e.target);
            });
        });

        // Apply insight buttons
        document.querySelectorAll('.apply-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.handleInsightApplication(e.target);
            });
        });

        // Notification click
        document.querySelector('.notifications').addEventListener('click', () => {
            this.showNotifications();
        });

        // Modal close
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.closeModal();
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e);
        });
    }

    switchSection(section) {
        // Update navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-section="${section}"]`).classList.add('active');

        // Update content
        this.currentSection = section;
        this.loadSectionContent(section);
    }

    async loadSectionContent(section) {
        const contentArea = document.getElementById('dashboard-content');
        
        try {
            switch (section) {
                case 'dashboard':
                    await this.loadDashboardData();
                    break;
                case 'risk-forecast':
                    await this.loadRiskForecast();
                    break;
                case 'triage':
                    await this.loadTriageAnalysis();
                    break;
                case 'governance':
                    await this.loadGovernanceDashboard();
                    break;
                case 'velocity':
                    await this.loadVelocityAnalysis();
                    break;
                case 'memory':
                    await this.loadMemoryInsights();
                    break;
                case 'reasoning':
                    await this.loadReasoningHistory();
                    break;
                case 'phase1':
                    await this.loadPhase1Analytics();
                    break;
            }
        } catch (error) {
            console.error(`Error loading ${section}:`, error);
            this.showError(`Failed to load ${section} data`);
        }
    }

    async loadDashboardData() {
        try {
            // Load multiple data sources in parallel
            const [statusData, actionsData, insightsData] = await Promise.all([
                this.fetchAPI('/status'),
                this.fetchAPI('/governance/pending'),
                this.fetchAPI('/memory/insights')
            ]);

            this.updateStatusCards(statusData);
            this.updateRecentActions(actionsData);
            this.updateInsights(insightsData);
            
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.showError('Failed to load dashboard data');
        }
    }

    async loadRiskForecast() {
        const contentArea = document.getElementById('dashboard-content');
        contentArea.innerHTML = `
            <div class="section-card">
                <div class="section-header">
                    <h2>Sprint Risk Forecast</h2>
                    <div class="section-controls">
                        <select id="team-selector" class="team-selector">
                            <option value="all">All Teams</option>
                            <option value="alpha">Team Alpha</option>
                            <option value="beta">Team Beta</option>
                            <option value="gamma">Team Gamma</option>
                        </select>
                    </div>
                </div>
                <div id="risk-content">
                    <div class="loading-spinner">Loading risk forecasts...</div>
                </div>
            </div>
        `;

        try {
            const riskData = await this.fetchAPI('/risk/forecast/current');
            this.renderRiskForecast(riskData);
        } catch (error) {
            console.error('Error loading risk forecast:', error);
            this.showError('Failed to load risk forecast');
        }
    }

    async loadTriageAnalysis() {
        const contentArea = document.getElementById('dashboard-content');
        contentArea.innerHTML = `
            <div class="section-card">
                <div class="section-header">
                    <h2>Smart Triage Analysis</h2>
                    <div class="section-controls">
                        <button class="analyze-btn" onclick="dashboard.runTriageAnalysis()">
                            <i class="fas fa-play"></i>
                            Run Analysis
                        </button>
                    </div>
                </div>
                <div id="triage-content">
                    <div class="loading-spinner">Loading triage analysis...</div>
                </div>
            </div>
        `;

        try {
            const triageData = await this.fetchAPI('/triage/recent');
            this.renderTriageAnalysis(triageData);
        } catch (error) {
            console.error('Error loading triage analysis:', error);
            this.showError('Failed to load triage analysis');
        }
    }

    async loadGovernanceDashboard() {
        const contentArea = document.getElementById('dashboard-content');
        contentArea.innerHTML = `
            <div class="governance-dashboard">
                <div class="governance-header">
                    <h2>Governance Dashboard</h2>
                    <div class="governance-stats">
                        <div class="stat-item">
                            <span class="stat-value" id="pending-count">-</span>
                            <span class="stat-label">Pending Approvals</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value" id="approved-today">-</span>
                            <span class="stat-label">Approved Today</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-value" id="avg-response-time">-</span>
                            <span class="stat-label">Avg Response Time</span>
                        </div>
                    </div>
                </div>
                <div id="governance-content">
                    <div class="loading-spinner">Loading governance data...</div>
                </div>
            </div>
        `;

        try {
            const governanceData = await this.fetchAPI('/governance/dashboard/current');
            this.renderGovernanceDashboard(governanceData);
        } catch (error) {
            console.error('Error loading governance dashboard:', error);
            this.showError('Failed to load governance dashboard');
        }
    }

    updateStatusCards(statusData) {
        // Update AI status
        const aiCard = document.querySelector('.ai-card');
        if (aiCard && statusData.ai_metrics) {
            const metrics = aiCard.querySelectorAll('.metric-value');
            metrics[0].textContent = `${statusData.ai_metrics.confidence}%`;
            metrics[1].textContent = statusData.ai_metrics.actions_today;
            metrics[2].textContent = `${statusData.ai_metrics.approval_rate}%`;
        }

        // Update risk forecast
        const riskCard = document.querySelector('.risk-card');
        if (riskCard && statusData.current_sprint_risk) {
            const riskLevel = riskCard.querySelector('.risk-level');
            const riskFill = riskCard.querySelector('.risk-fill');
            const riskPercentage = riskCard.querySelector('.risk-percentage');
            
            const risk = statusData.current_sprint_risk;
            riskLevel.textContent = risk.level;
            riskLevel.className = `risk-level ${risk.level.toLowerCase()}`;
            riskFill.style.width = `${risk.completion_probability}%`;
            riskPercentage.textContent = `${risk.completion_probability}% Completion Probability`;
        }

        // Update governance queue
        const governanceCard = document.querySelector('.governance-card');
        if (governanceCard && statusData.governance) {
            const pendingCount = governanceCard.querySelector('.pending-count');
            pendingCount.textContent = `${statusData.governance.pending_count} Pending`;
        }

        // Update triage summary
        const triageCard = document.querySelector('.triage-card');
        if (triageCard && statusData.triage_summary) {
            const triageCount = triageCard.querySelector('.triage-count');
            const actions = triageCard.querySelectorAll('.action-count');
            
            triageCount.textContent = `${statusData.triage_summary.total_analyzed} Analyzed`;
            actions[0].textContent = statusData.triage_summary.reassign_count;
            actions[1].textContent = statusData.triage_summary.escalate_count;
            actions[2].textContent = statusData.triage_summary.defer_count;
        }
    }

    updateRecentActions(actionsData) {
        const actionsList = document.querySelector('.actions-list');
        if (!actionsList || !actionsData.recent_actions) return;

        actionsList.innerHTML = actionsData.recent_actions.map(action => `
            <div class="action-item ${action.status}">
                <div class="action-icon">
                    <i class="fas ${this.getActionIcon(action.type)}"></i>
                </div>
                <div class="action-details">
                    <h4>${action.title}</h4>
                    <p>${action.description}</p>
                    <div class="action-meta">
                        <span class="confidence">Confidence: ${action.confidence}%</span>
                        <span class="timestamp">${this.formatTimestamp(action.timestamp)}</span>
                        ${action.approver ? `<span class="approver">Approved by: ${action.approver}</span>` : ''}
                        ${action.deadline ? `<span class="deadline">Deadline: ${this.formatDeadline(action.deadline)}</span>` : ''}
                    </div>
                </div>
                <div class="action-status ${action.status}">
                    <i class="fas ${action.status === 'approved' ? 'fa-check' : 'fa-clock'}"></i>
                    <span>${action.status.charAt(0).toUpperCase() + action.status.slice(1)}</span>
                </div>
                <button class="reasoning-btn" onclick="dashboard.showReasoning('${action.id}')">
                    <i class="fas fa-lightbulb"></i>
                    Why?
                </button>
            </div>
        `).join('');
    }

    updateInsights(insightsData) {
        const insightsGrid = document.querySelector('.insights-grid');
        if (!insightsGrid || !insightsData.insights) return;

        insightsGrid.innerHTML = insightsData.insights.map(insight => `
            <div class="insight-card">
                <div class="insight-icon">
                    <i class="fas ${this.getInsightIcon(insight.type)}"></i>
                </div>
                <div class="insight-content">
                    <h4>${insight.title}</h4>
                    <p>${insight.description}</p>
                    <div class="insight-actions">
                        <button class="apply-btn" onclick="dashboard.applyInsight('${insight.id}')">
                            ${insight.action_text}
                        </button>
                        <button class="learn-more-btn" onclick="dashboard.showInsightDetails('${insight.id}')">
                            Learn More
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    async showReasoning(actionId) {
        try {
            const reasoningData = await this.fetchAPI(`/reasoning/explain/${actionId}`);
            this.displayReasoningModal(reasoningData);
        } catch (error) {
            console.error('Error loading reasoning:', error);
            this.showError('Failed to load reasoning explanation');
        }
    }

    displayReasoningModal(reasoningData) {
        const modal = document.getElementById('reasoning-modal');
        const confidenceFill = document.getElementById('confidence-fill');
        const confidenceValue = document.getElementById('confidence-value');
        const factorList = document.getElementById('factor-list');
        const explanationText = document.getElementById('explanation-text');
        const sourceList = document.getElementById('source-list');

        // Update confidence score
        const confidence = Math.round(reasoningData.reasoning.confidence * 100);
        confidenceFill.style.width = `${confidence}%`;
        confidenceValue.textContent = `${confidence}%`;

        // Update factors
        factorList.innerHTML = reasoningData.reasoning.factors.map(factor => `
            <div class="factor-item">
                <div class="factor-icon">
                    <i class="fas fa-chart-bar"></i>
                </div>
                <div class="factor-text">${factor.description}</div>
                <div class="factor-weight">${Math.round(factor.weight * 100)}%</div>
            </div>
        `).join('');

        // Update explanation
        explanationText.textContent = reasoningData.reasoning.explanation;

        // Update data sources
        sourceList.innerHTML = reasoningData.reasoning.data_sources.map(source => `
            <div class="source-item">
                <div class="source-icon">
                    <i class="fas fa-database"></i>
                </div>
                <div class="source-text">${source}</div>
            </div>
        `).join('');

        // Show modal
        modal.classList.add('active');
    }

    closeReasoning() {
        const modal = document.getElementById('reasoning-modal');
        modal.classList.remove('active');
    }

    async runTriageAnalysis() {
        const analyzeBtn = document.querySelector('.analyze-btn');
        const originalText = analyzeBtn.innerHTML;
        
        analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
        analyzeBtn.disabled = true;

        try {
            const result = await this.fetchAPI('/triage/analyze', {
                method: 'POST',
                body: JSON.stringify({ team_id: 'current' })
            });

            this.renderTriageAnalysis(result);
            this.showSuccess('Triage analysis completed successfully');
        } catch (error) {
            console.error('Error running triage analysis:', error);
            this.showError('Failed to run triage analysis');
        } finally {
            analyzeBtn.innerHTML = originalText;
            analyzeBtn.disabled = false;
        }
    }

    renderTriageAnalysis(triageData) {
        const triageContent = document.getElementById('triage-content');
        
        triageContent.innerHTML = `
            <div class="triage-summary-grid">
                <div class="summary-card">
                    <h3>Tickets Analyzed</h3>
                    <div class="summary-value">${triageData.analyzed_tickets}</div>
                </div>
                <div class="summary-card">
                    <h3>Actions Recommended</h3>
                    <div class="summary-value">${triageData.recommendations.length}</div>
                </div>
                <div class="summary-card">
                    <h3>High Priority</h3>
                    <div class="summary-value">${triageData.recommendations.filter(r => r.urgency_score > 0.8).length}</div>
                </div>
            </div>
            
            <div class="recommendations-list">
                <h3>Recommendations</h3>
                ${triageData.recommendations.map(rec => `
                    <div class="recommendation-item">
                        <div class="rec-header">
                            <h4>Ticket: ${rec.ticket_id}</h4>
                            <div class="urgency-score ${this.getUrgencyClass(rec.urgency_score)}">
                                Urgency: ${Math.round(rec.urgency_score * 100)}%
                            </div>
                        </div>
                        <div class="rec-content">
                            <div class="rec-action">
                                <strong>Recommended Action:</strong> ${rec.recommended_action}
                            </div>
                            <div class="rec-reasoning">
                                <strong>Reasoning:</strong> ${rec.reasoning}
                            </div>
                            <div class="rec-confidence">
                                <strong>Confidence:</strong> ${Math.round(rec.confidence * 100)}%
                            </div>
                        </div>
                        <div class="rec-actions">
                            ${rec.approval_required ? 
                                `<button class="approve-action-btn" onclick="dashboard.approveTriageAction('${rec.ticket_id}', '${rec.recommended_action}')">
                                    Request Approval
                                </button>` :
                                `<button class="execute-action-btn" onclick="dashboard.executeTriageAction('${rec.ticket_id}', '${rec.recommended_action}')">
                                    Execute Action
                                </button>`
                            }
                            <button class="reasoning-btn" onclick="dashboard.showTriageReasoning('${rec.ticket_id}')">
                                <i class="fas fa-lightbulb"></i>
                                Why?
                            </button>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    async approveTriageAction(ticketId, action) {
        try {
            const result = await this.fetchAPI('/triage/execute', {
                method: 'POST',
                body: JSON.stringify({
                    ticket_id: ticketId,
                    action: action,
                    team_id: 'current'
                })
            });

            this.showSuccess(`Action submitted for approval: ${result.request_id}`);
            this.loadDashboardData(); // Refresh dashboard
        } catch (error) {
            console.error('Error submitting action for approval:', error);
            this.showError('Failed to submit action for approval');
        }
    }

    async executeTriageAction(ticketId, action) {
        try {
            const result = await this.fetchAPI('/triage/execute', {
                method: 'POST',
                body: JSON.stringify({
                    ticket_id: ticketId,
                    action: action,
                    auto_execute: true
                })
            });

            this.showSuccess(`Action executed successfully on ${ticketId}`);
            this.loadDashboardData(); // Refresh dashboard
        } catch (error) {
            console.error('Error executing action:', error);
            this.showError('Failed to execute action');
        }
    }

    handleFilterChange(button) {
        // Update active filter
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        button.classList.add('active');

        // Filter actions based on selection
        const filter = button.textContent.toLowerCase();
        const actionItems = document.querySelectorAll('.action-item');
        
        actionItems.forEach(item => {
            if (filter === 'all' || item.classList.contains(filter)) {
                item.style.display = 'flex';
            } else {
                item.style.display = 'none';
            }
        });
    }

    handleApprovalAction(button) {
        const actionItem = button.closest('.queue-item');
        const actionTitle = actionItem.querySelector('.item-title').textContent;
        
        // Show approval modal or handle directly
        this.showApprovalModal(actionTitle, button);
    }

    showApprovalModal(actionTitle, button) {
        const modal = document.createElement('div');
        modal.className = 'modal active';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Approve Action</h3>
                    <button class="close-btn" onclick="this.closest('.modal').remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <p><strong>Action:</strong> ${actionTitle}</p>
                    <div class="approval-actions">
                        <button class="approve-btn" onclick="dashboard.processApproval(true, this)">
                            <i class="fas fa-check"></i>
                            Approve
                        </button>
                        <button class="reject-btn" onclick="dashboard.processApproval(false, this)">
                            <i class="fas fa-times"></i>
                            Reject
                        </button>
                    </div>
                    <div class="approval-reason">
                        <label for="reason">Reason (optional):</label>
                        <textarea id="reason" placeholder="Enter reason for your decision..."></textarea>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }

    async processApproval(approved, button) {
        const modal = button.closest('.modal');
        const reason = modal.querySelector('#reason').value;
        
        try {
            const result = await this.fetchAPI('/governance/approve', {
                method: 'POST',
                body: JSON.stringify({
                    request_id: 'current', // This would be dynamic in real implementation
                    approved: approved,
                    reason: reason
                })
            });

            this.showSuccess(`Action ${approved ? 'approved' : 'rejected'} successfully`);
            modal.remove();
            this.loadDashboardData(); // Refresh dashboard
        } catch (error) {
            console.error('Error processing approval:', error);
            this.showError('Failed to process approval');
        }
    }

    handleInsightApplication(button) {
        const insightCard = button.closest('.insight-card');
        const insightTitle = insightCard.querySelector('h4').textContent;
        
        this.showSuccess(`Applied insight: ${insightTitle}`);
        // In real implementation, this would trigger the actual insight application
    }

    showNotifications() {
        // Create notifications panel
        const panel = document.createElement('div');
        panel.className = 'notifications-panel';
        panel.innerHTML = `
            <div class="panel-header">
                <h3>Notifications</h3>
                <button class="close-panel" onclick="this.closest('.notifications-panel').remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="panel-content">
                <div class="notification-item">
                    <i class="fas fa-exclamation-triangle"></i>
                    <div class="notification-text">
                        <strong>Sprint Risk Alert</strong>
                        <p>Team Alpha sprint completion probability dropped to 65%</p>
                        <span class="notification-time">2 hours ago</span>
                    </div>
                </div>
                <div class="notification-item">
                    <i class="fas fa-check-circle"></i>
                    <div class="notification-text">
                        <strong>Action Approved</strong>
                        <p>Ticket reassignment for JIRA-1234 has been approved</p>
                        <span class="notification-time">4 hours ago</span>
                    </div>
                </div>
                <div class="notification-item">
                    <i class="fas fa-lightbulb"></i>
                    <div class="notification-text">
                        <strong>New Insight</strong>
                        <p>AI detected new team performance pattern</p>
                        <span class="notification-time">6 hours ago</span>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(panel);
    }

    handleKeyboardShortcuts(e) {
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            this.showSearchModal();
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            this.closeModal();
        }
    }

    showSearchModal() {
        // Implementation for search functionality
        console.log('Search modal would open here');
    }

    closeModal() {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.classList.remove('active');
        });
    }

    startAutoRefresh() {
        setInterval(() => {
            if (this.currentSection === 'dashboard') {
                this.loadDashboardData();
            }
        }, this.refreshInterval);
    }

    setupRealtimeUpdates() {
        // In a real implementation, this would setup WebSocket connections
        // for real-time updates from the backend
        console.log('Real-time updates would be setup here');
    }

    async fetchAPI(endpoint, options = {}) {
        const url = `${this.apiBase}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        const response = await fetch(url, { ...defaultOptions, ...options });
        
        if (!response.ok) {
            throw new Error(`API request failed: ${response.statusText}`);
        }

        return await response.json();
    }

    // Utility functions
    getActionIcon(actionType) {
        const icons = {
            'reassignment': 'fa-user-check',
            'escalation': 'fa-arrow-up',
            'scope_change': 'fa-edit',
            'priority_change': 'fa-exclamation-triangle',
            'default': 'fa-cog'
        };
        return icons[actionType] || icons.default;
    }

    getInsightIcon(insightType) {
        const icons = {
            'pattern': 'fa-brain',
            'optimization': 'fa-chart-line',
            'prediction': 'fa-crystal-ball',
            'default': 'fa-lightbulb'
        };
        return icons[insightType] || icons.default;
    }

    getUrgencyClass(urgencyScore) {
        if (urgencyScore > 0.8) return 'high-urgency';
        if (urgencyScore > 0.6) return 'medium-urgency';
        return 'low-urgency';
    }

    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 3600000) { // Less than 1 hour
            return `${Math.floor(diff / 60000)} minutes ago`;
        } else if (diff < 86400000) { // Less than 1 day
            return `${Math.floor(diff / 3600000)} hours ago`;
        } else {
            return date.toLocaleDateString();
        }
    }

    formatDeadline(deadline) {
        const date = new Date(deadline);
        const now = new Date();
        const diff = date - now;
        
        if (diff < 3600000) { // Less than 1 hour
            return `${Math.floor(diff / 60000)} minutes`;
        } else if (diff < 86400000) { // Less than 1 day
            return `${Math.floor(diff / 3600000)} hours`;
        } else {
            return `${Math.floor(diff / 86400000)} days`;
        }
    }

    showSuccess(message) {
        this.showToast(message, 'success');
    }

    showError(message) {
        this.showToast(message, 'error');
    }

    showToast(message, type) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
            <span>${message}</span>
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, 3000);
    }
}

// Global functions for onclick handlers
window.showReasoning = function(actionId) {
    dashboard.showReasoning(actionId);
};

window.closeReasoning = function() {
    dashboard.closeReasoning();
};

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new JUNODashboard();
});

// Add toast styles
const toastStyles = `
    .toast {
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        padding: 16px 20px;
        border-radius: 8px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        display: flex;
        align-items: center;
        gap: 12px;
        transform: translateX(100%);
        transition: transform 0.3s ease;
        z-index: 3000;
        border-left: 4px solid;
    }
    
    .toast.show {
        transform: translateX(0);
    }
    
    .toast-success {
        border-left-color: #10b981;
        color: #065f46;
    }
    
    .toast-error {
        border-left-color: #ef4444;
        color: #991b1b;
    }
    
    .toast i {
        font-size: 18px;
    }
    
    .notifications-panel {
        position: fixed;
        top: 80px;
        right: 20px;
        width: 400px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
        z-index: 2000;
        animation: slideIn 0.3s ease;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .panel-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px;
        border-bottom: 1px solid #e5e7eb;
    }
    
    .panel-content {
        max-height: 400px;
        overflow-y: auto;
    }
    
    .notification-item {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        padding: 16px 20px;
        border-bottom: 1px solid #f3f4f6;
    }
    
    .notification-item:last-child {
        border-bottom: none;
    }
    
    .notification-item i {
        margin-top: 2px;
        color: #6b7280;
    }
    
    .notification-text {
        flex: 1;
    }
    
    .notification-text strong {
        display: block;
        margin-bottom: 4px;
        color: #111827;
    }
    
    .notification-text p {
        margin: 0 0 4px 0;
        color: #6b7280;
        font-size: 14px;
    }
    
    .notification-time {
        font-size: 12px;
        color: #9ca3af;
    }
`;

// Inject toast styles
const styleSheet = document.createElement('style');
styleSheet.textContent = toastStyles;
document.head.appendChild(styleSheet);

