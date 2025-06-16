import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { 
  BarChart3, 
  Brain, 
  Bug, 
  Clock, 
  TrendingUp, 
  Search, 
  Settings, 
  Download,
  MessageSquare,
  Activity,
  Users,
  Target,
  Zap,
  ChevronRight,
  Sparkles,
  Shield,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Eye,
  Database,
  Cpu,
  Network,
  FileText,
  GitBranch,
  Timer,
  Gauge,
  Bot,
  Workflow,
  Lock,
  Unlock,
  Play,
  Pause,
  RotateCcw
} from 'lucide-react'
import './App.css'

// Mock data for demonstration
const mockProjects = [
  { key: 'DEMO', name: 'Demo Project', issues: 245 },
  { key: 'WEB', name: 'Web Application', issues: 189 },
  { key: 'API', name: 'API Service', issues: 156 },
  { key: 'MOBILE', name: 'Mobile App', issues: 98 }
]

const mockMetrics = {
  totalIssues: 688,
  avgVelocity: 42.5,
  defectRate: 8.2,
  avgLeadTime: 5.3
}

// Phase 2 Agentic AI Mock Data
const mockAgenticMetrics = {
  memoryUtilization: 78,
  reasoningAccuracy: 89.3,
  riskPredictionScore: 92.1,
  autonomousActions: 156,
  governanceCompliance: 94.7,
  activeAgents: 3,
  decisionsToday: 47,
  interventionsRequired: 2
}

const mockRiskForecasts = [
  {
    id: 1,
    sprint: 'Sprint 23',
    riskLevel: 'high',
    probability: 87,
    impact: 'Schedule delay of 3-5 days',
    factors: ['Team capacity reduced', 'Critical dependency blocked'],
    recommendation: 'Reassign 2 tickets to next sprint, escalate dependency'
  },
  {
    id: 2,
    sprint: 'Sprint 24',
    riskLevel: 'medium',
    probability: 64,
    impact: 'Quality issues in 2-3 features',
    factors: ['New team member onboarding', 'Complex integration work'],
    recommendation: 'Increase code review coverage, pair programming'
  },
  {
    id: 3,
    sprint: 'Sprint 25',
    riskLevel: 'low',
    probability: 23,
    impact: 'Minor velocity reduction',
    factors: ['Holiday period approaching'],
    recommendation: 'Plan lighter sprint, focus on documentation'
  }
]

const mockMemoryLayers = {
  episodic: {
    totalEvents: 1247,
    recentEvents: 23,
    retention: '30 days',
    status: 'healthy'
  },
  semantic: {
    concepts: 456,
    relationships: 1834,
    accuracy: 94.2,
    status: 'healthy'
  },
  procedural: {
    workflows: 89,
    automations: 34,
    successRate: 91.7,
    status: 'healthy'
  },
  working: {
    activeContexts: 12,
    capacity: '85%',
    responseTime: '127ms',
    status: 'optimal'
  }
}

const mockReasoningDecisions = [
  {
    id: 1,
    timestamp: '2025-06-15T14:30:00Z',
    decision: 'Auto-assign critical bug to senior developer',
    confidence: 94.2,
    factors: ['Severity: Critical', 'Expertise match: 98%', 'Availability: High'],
    outcome: 'approved',
    impact: 'Reduced resolution time by 2.3 hours'
  },
  {
    id: 2,
    timestamp: '2025-06-15T13:15:00Z',
    decision: 'Recommend sprint scope reduction',
    confidence: 87.6,
    factors: ['Velocity trend: -15%', 'Team capacity: 80%', 'Risk score: High'],
    outcome: 'pending_review',
    impact: 'Awaiting product owner approval'
  },
  {
    id: 3,
    timestamp: '2025-06-15T12:45:00Z',
    decision: 'Escalate blocked dependency',
    confidence: 96.1,
    factors: ['Block duration: 3 days', 'Impact: 5 tickets', 'Priority: High'],
    outcome: 'approved',
    impact: 'Dependency resolved in 4 hours'
  }
]

const mockGovernanceRules = [
  {
    id: 1,
    name: 'Critical Bug Auto-Assignment',
    status: 'active',
    compliance: 98.2,
    triggers: 47,
    violations: 1
  },
  {
    id: 2,
    name: 'Sprint Capacity Management',
    status: 'active',
    compliance: 94.7,
    triggers: 23,
    violations: 2
  },
  {
    id: 3,
    name: 'Risk Escalation Protocol',
    status: 'active',
    compliance: 96.8,
    triggers: 12,
    violations: 0
  }
]

const mockRecentQueries = [
  "How many tickets are assigned to John Doe?",
  "Show me the status distribution for project DEMO",
  "List all bugs from last month",
  "What's the velocity trend for the last 3 sprints?",
  "What risks does JUNO predict for next sprint?",
  "Show me recent autonomous decisions",
  "How is the memory layer performing?"
]

function App() {
  const [selectedProject, setSelectedProject] = useState('DEMO')
  const [query, setQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [queryResults, setQueryResults] = useState(null)
  const [activeTab, setActiveTab] = useState('overview')
  const [agenticMode, setAgenticMode] = useState(true)

  const handleQuerySubmit = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    setIsLoading(true)
    
    // Simulate API call
    setTimeout(() => {
      setQueryResults({
        query: query,
        intent: 'assignee_count',
        results: {
          type: 'summary',
          data: {
            total_assignees: 12,
            top_assignee: 'John Doe (23 tickets)',
            avg_tickets_per_assignee: 8.5
          }
        }
      })
      setIsLoading(false)
    }, 1500)
  }

  const handleSampleQuery = (sampleQuery) => {
    setQuery(sampleQuery)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm dark:bg-slate-900/80 sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                  <Brain className="w-5 h-5 text-white" />
                </div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  JUNO Phase 2
                </h1>
              </div>
              <div className="flex items-center space-x-2">
                <Badge variant="secondary" className="hidden sm:inline-flex">
                  <Sparkles className="w-3 h-3 mr-1" />
                  Agentic AI
                </Badge>
                <Badge 
                  variant={agenticMode ? "default" : "outline"} 
                  className="hidden sm:inline-flex cursor-pointer"
                  onClick={() => setAgenticMode(!agenticMode)}
                >
                  <Bot className="w-3 h-3 mr-1" />
                  {agenticMode ? 'Autonomous' : 'Manual'}
                </Badge>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <Select value={selectedProject} onValueChange={setSelectedProject}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder="Select project" />
                </SelectTrigger>
                <SelectContent>
                  {mockProjects.map((project) => (
                    <SelectItem key={project.key} value={project.key}>
                      <div className="flex items-center justify-between w-full">
                        <span>{project.name}</span>
                        <Badge variant="outline" className="ml-2">
                          {project.issues}
                        </Badge>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              
              <Button variant="outline" size="icon">
                <Settings className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </header>

        {/* Agentic AI Status Bar */}
        {agenticMode && (
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950/20 dark:to-purple-950/20 border-b">
            <div className="container mx-auto px-6 py-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-6">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="text-sm font-medium">Agentic AI Active</span>
                  </div>
                  <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                    <span>Memory: {mockAgenticMetrics.memoryUtilization}%</span>
                    <span>Accuracy: {mockAgenticMetrics.reasoningAccuracy}%</span>
                    <span>Decisions Today: {mockAgenticMetrics.decisionsToday}</span>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge variant="outline" className="text-xs">
                    <Shield className="w-3 h-3 mr-1" />
                    Governance: {mockAgenticMetrics.governanceCompliance}%
                  </Badge>
                  <Badge variant="outline" className="text-xs">
                    <AlertTriangle className="w-3 h-3 mr-1" />
                    {mockAgenticMetrics.interventionsRequired} Interventions
                  </Badge>
                </div>
              </div>
            </div>
          </div>
        )}

      <div className="container mx-auto px-6 py-8">
        {/* Natural Language Query Interface */}
        <Card className="mb-8 shadow-lg border-0 bg-gradient-to-r from-white to-slate-50 dark:from-slate-800 dark:to-slate-900">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <MessageSquare className="w-5 h-5 text-blue-600" />
              <span>Ask Anything About Your Jira Data</span>
            </CardTitle>
            <CardDescription>
              Use natural language to query your Jira data and get instant insights
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleQuerySubmit} className="space-y-4">
              <div className="relative">
                <Search className="absolute left-3 top-3 w-4 h-4 text-muted-foreground" />
                <Input
                  placeholder="e.g., How many tickets are assigned to John Doe?"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="pl-10 h-12 text-base"
                />
                <Button 
                  type="submit" 
                  className="absolute right-2 top-2 h-8"
                  disabled={isLoading || !query.trim()}
                >
                  {isLoading ? (
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <ChevronRight className="w-4 h-4" />
                  )}
                </Button>
              </div>
              
              {/* Sample Queries */}
              <div className="flex flex-wrap gap-2">
                <span className="text-sm text-muted-foreground">Try:</span>
                {mockRecentQueries.map((sampleQuery, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    size="sm"
                    onClick={() => handleSampleQuery(sampleQuery)}
                    className="text-xs h-7"
                  >
                    {sampleQuery}
                  </Button>
                ))}
              </div>
            </form>

            {/* Query Results */}
            {queryResults && (
              <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-950/20 rounded-lg border border-blue-200 dark:border-blue-800">
                <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">
                  Query: "{queryResults.query}"
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-600">
                      {queryResults.results.data.total_assignees}
                    </div>
                    <div className="text-sm text-muted-foreground">Total Assignees</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-semibold text-green-600">
                      {queryResults.results.data.top_assignee}
                    </div>
                    <div className="text-sm text-muted-foreground">Top Assignee</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-600">
                      {queryResults.results.data.avg_tickets_per_assignee}
                    </div>
                    <div className="text-sm text-muted-foreground">Avg per Assignee</div>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Enhanced Key Metrics Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="hover:shadow-lg transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Total Issues</p>
                  <p className="text-2xl font-bold">{mockMetrics.totalIssues}</p>
                </div>
                <Activity className="w-8 h-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Reasoning Accuracy</p>
                  <p className="text-2xl font-bold">{mockAgenticMetrics.reasoningAccuracy}%</p>
                </div>
                <Brain className="w-8 h-8 text-purple-600" />
              </div>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Risk Prediction</p>
                  <p className="text-2xl font-bold">{mockAgenticMetrics.riskPredictionScore}%</p>
                </div>
                <AlertTriangle className="w-8 h-8 text-orange-600" />
              </div>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Autonomous Actions</p>
                  <p className="text-2xl font-bold">{mockAgenticMetrics.autonomousActions}</p>
                </div>
                <Bot className="w-8 h-8 text-green-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Phase 2 Agentic Dashboard */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="overview" className="flex items-center space-x-2">
              <Gauge className="w-4 h-4" />
              <span>Overview</span>
            </TabsTrigger>
            <TabsTrigger value="memory" className="flex items-center space-x-2">
              <Database className="w-4 h-4" />
              <span>Memory</span>
            </TabsTrigger>
            <TabsTrigger value="reasoning" className="flex items-center space-x-2">
              <Brain className="w-4 h-4" />
              <span>Reasoning</span>
            </TabsTrigger>
            <TabsTrigger value="risk" className="flex items-center space-x-2">
              <AlertTriangle className="w-4 h-4" />
              <span>Risk Forecast</span>
            </TabsTrigger>
            <TabsTrigger value="governance" className="flex items-center space-x-2">
              <Shield className="w-4 h-4" />
              <span>Governance</span>
            </TabsTrigger>
            <TabsTrigger value="analytics" className="flex items-center space-x-2">
              <BarChart3 className="w-4 h-4" />
              <span>Analytics</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Agentic AI Status */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Bot className="w-5 h-5 text-blue-600" />
                    <span>Agentic AI Status</span>
                  </CardTitle>
                  <CardDescription>Real-time autonomous system monitoring</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Active Agents</span>
                    <Badge variant="outline">{mockAgenticMetrics.activeAgents}</Badge>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Memory Utilization</span>
                      <span>{mockAgenticMetrics.memoryUtilization}%</span>
                    </div>
                    <Progress value={mockAgenticMetrics.memoryUtilization} className="h-2" />
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Governance Compliance</span>
                      <span>{mockAgenticMetrics.governanceCompliance}%</span>
                    </div>
                    <Progress value={mockAgenticMetrics.governanceCompliance} className="h-2" />
                  </div>
                  <div className="grid grid-cols-2 gap-4 pt-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">{mockAgenticMetrics.decisionsToday}</div>
                      <div className="text-xs text-muted-foreground">Decisions Today</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-orange-600">{mockAgenticMetrics.interventionsRequired}</div>
                      <div className="text-xs text-muted-foreground">Interventions</div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Recent Autonomous Decisions */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Workflow className="w-5 h-5 text-purple-600" />
                    <span>Recent Decisions</span>
                  </CardTitle>
                  <CardDescription>Latest autonomous decisions and outcomes</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {mockReasoningDecisions.slice(0, 3).map((decision) => (
                      <div key={decision.id} className="flex items-start space-x-3 p-3 bg-slate-50 dark:bg-slate-800 rounded-lg">
                        <div className="flex-shrink-0">
                          {decision.outcome === 'approved' ? (
                            <CheckCircle className="w-5 h-5 text-green-600" />
                          ) : decision.outcome === 'pending_review' ? (
                            <Clock className="w-5 h-5 text-orange-600" />
                          ) : (
                            <XCircle className="w-5 h-5 text-red-600" />
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium truncate">{decision.decision}</p>
                          <p className="text-xs text-muted-foreground">
                            Confidence: {decision.confidence}% • {new Date(decision.timestamp).toLocaleTimeString()}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="memory" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {Object.entries(mockMemoryLayers).map(([layerName, data]) => (
                <Card key={layerName}>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base capitalize flex items-center justify-between">
                      {layerName} Memory
                      <Badge variant={data.status === 'optimal' ? 'default' : data.status === 'healthy' ? 'secondary' : 'destructive'}>
                        {data.status}
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {layerName === 'episodic' && (
                      <>
                        <div className="flex justify-between text-sm">
                          <span>Total Events</span>
                          <span className="font-medium">{data.totalEvents}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span>Recent Events</span>
                          <span className="font-medium">{data.recentEvents}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span>Retention</span>
                          <span className="font-medium">{data.retention}</span>
                        </div>
                      </>
                    )}
                    {layerName === 'semantic' && (
                      <>
                        <div className="flex justify-between text-sm">
                          <span>Concepts</span>
                          <span className="font-medium">{data.concepts}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span>Relationships</span>
                          <span className="font-medium">{data.relationships}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span>Accuracy</span>
                          <span className="font-medium">{data.accuracy}%</span>
                        </div>
                      </>
                    )}
                    {layerName === 'procedural' && (
                      <>
                        <div className="flex justify-between text-sm">
                          <span>Workflows</span>
                          <span className="font-medium">{data.workflows}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span>Automations</span>
                          <span className="font-medium">{data.automations}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span>Success Rate</span>
                          <span className="font-medium">{data.successRate}%</span>
                        </div>
                      </>
                    )}
                    {layerName === 'working' && (
                      <>
                        <div className="flex justify-between text-sm">
                          <span>Active Contexts</span>
                          <span className="font-medium">{data.activeContexts}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span>Capacity</span>
                          <span className="font-medium">{data.capacity}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span>Response Time</span>
                          <span className="font-medium">{data.responseTime}</span>
                        </div>
                      </>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="reasoning" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Brain className="w-5 h-5 text-purple-600" />
                  <span>Reasoning Engine Decisions</span>
                </CardTitle>
                <CardDescription>Detailed view of autonomous decision-making process</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {mockReasoningDecisions.map((decision) => (
                    <div key={decision.id} className="border rounded-lg p-4 space-y-3">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4 className="font-medium">{decision.decision}</h4>
                          <p className="text-sm text-muted-foreground">
                            {new Date(decision.timestamp).toLocaleString()}
                          </p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge variant={decision.outcome === 'approved' ? 'default' : decision.outcome === 'pending_review' ? 'secondary' : 'destructive'}>
                            {decision.outcome.replace('_', ' ')}
                          </Badge>
                          <Badge variant="outline">
                            {decision.confidence}% confidence
                          </Badge>
                        </div>
                      </div>
                      <div className="space-y-2">
                        <h5 className="text-sm font-medium">Decision Factors:</h5>
                        <div className="flex flex-wrap gap-2">
                          {decision.factors.map((factor, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {factor}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      <div className="bg-slate-50 dark:bg-slate-800 p-3 rounded">
                        <p className="text-sm"><strong>Impact:</strong> {decision.impact}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="risk" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <AlertTriangle className="w-5 h-5 text-orange-600" />
                  <span>Sprint Risk Forecasting</span>
                </CardTitle>
                <CardDescription>AI-powered risk prediction and mitigation recommendations</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {mockRiskForecasts.map((forecast) => (
                    <div key={forecast.id} className="border rounded-lg p-4 space-y-3">
                      <div className="flex items-start justify-between">
                        <div>
                          <h4 className="font-medium">{forecast.sprint}</h4>
                          <p className="text-sm text-muted-foreground">{forecast.impact}</p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge variant={
                            forecast.riskLevel === 'high' ? 'destructive' : 
                            forecast.riskLevel === 'medium' ? 'secondary' : 
                            'outline'
                          }>
                            {forecast.riskLevel} risk
                          </Badge>
                          <Badge variant="outline">
                            {forecast.probability}% probability
                          </Badge>
                        </div>
                      </div>
                      <div className="space-y-2">
                        <h5 className="text-sm font-medium">Risk Factors:</h5>
                        <div className="flex flex-wrap gap-2">
                          {forecast.factors.map((factor, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {factor}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      <div className="bg-blue-50 dark:bg-blue-950/20 p-3 rounded border border-blue-200 dark:border-blue-800">
                        <p className="text-sm"><strong>Recommendation:</strong> {forecast.recommendation}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="governance" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Shield className="w-5 h-5 text-green-600" />
                  <span>Governance Framework</span>
                </CardTitle>
                <CardDescription>Autonomous decision governance and compliance monitoring</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {mockGovernanceRules.map((rule) => (
                    <div key={rule.id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <h4 className="font-medium">{rule.name}</h4>
                        <div className="flex items-center space-x-2">
                          <Badge variant={rule.status === 'active' ? 'default' : 'secondary'}>
                            {rule.status}
                          </Badge>
                          <Badge variant="outline">
                            {rule.compliance}% compliance
                          </Badge>
                        </div>
                      </div>
                      <div className="grid grid-cols-3 gap-4 text-sm">
                        <div className="text-center">
                          <div className="text-lg font-bold text-blue-600">{rule.triggers}</div>
                          <div className="text-muted-foreground">Triggers</div>
                        </div>
                        <div className="text-center">
                          <div className="text-lg font-bold text-green-600">{rule.triggers - rule.violations}</div>
                          <div className="text-muted-foreground">Compliant</div>
                        </div>
                        <div className="text-center">
                          <div className="text-lg font-bold text-red-600">{rule.violations}</div>
                          <div className="text-muted-foreground">Violations</div>
                        </div>
                      </div>
                      <div className="mt-3">
                        <Progress value={rule.compliance} className="h-2" />
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="analytics" className="space-y-6">
            <TabsTrigger value="velocity" className="flex items-center space-x-2">
              <TrendingUp className="w-4 h-4" />
              <span>Velocity</span>
            </TabsTrigger>
            <TabsTrigger value="defects" className="flex items-center space-x-2">
              <Bug className="w-4 h-4" />
              <span>Defects</span>
            </TabsTrigger>
            <TabsTrigger value="leadtime" className="flex items-center space-x-2">
              <Clock className="w-4 h-4" />
              <span>Lead Time</span>
            </TabsTrigger>
            <TabsTrigger value="trends" className="flex items-center space-x-2">
              <BarChart3 className="w-4 h-4" />
              <span>Trends</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="velocity" className="space-y-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Sprint Velocity Analysis</CardTitle>
                  <CardDescription>
                    Track team velocity and completion rates over time
                  </CardDescription>
                </div>
                <Button variant="outline" size="sm">
                  <Download className="w-4 h-4 mr-2" />
                  Export
                </Button>
              </CardHeader>
              <CardContent>
                <div className="h-80 flex items-center justify-center bg-slate-50 dark:bg-slate-800 rounded-lg">
                  <div className="text-center">
                    <BarChart3 className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
                    <p className="text-muted-foreground">Velocity chart will be displayed here</p>
                    <p className="text-sm text-muted-foreground mt-2">
                      Connect to Jira to see real-time velocity data
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="defects" className="space-y-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Defect Analysis Dashboard</CardTitle>
                  <CardDescription>
                    Analyze defect patterns and quality metrics
                  </CardDescription>
                </div>
                <Button variant="outline" size="sm">
                  <Download className="w-4 h-4 mr-2" />
                  Export
                </Button>
              </CardHeader>
              <CardContent>
                <div className="h-80 flex items-center justify-center bg-slate-50 dark:bg-slate-800 rounded-lg">
                  <div className="text-center">
                    <Bug className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
                    <p className="text-muted-foreground">Defect analysis charts will be displayed here</p>
                    <p className="text-sm text-muted-foreground mt-2">
                      Connect to Jira to see defect patterns and quality metrics
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="leadtime" className="space-y-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Lead Time Analysis</CardTitle>
                  <CardDescription>
                    Monitor lead time and cycle time metrics
                  </CardDescription>
                </div>
                <Button variant="outline" size="sm">
                  <Download className="w-4 h-4 mr-2" />
                  Export
                </Button>
              </CardHeader>
              <CardContent>
                <div className="h-80 flex items-center justify-center bg-slate-50 dark:bg-slate-800 rounded-lg">
                  <div className="text-center">
                    <Clock className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
                    <p className="text-muted-foreground">Lead time charts will be displayed here</p>
                    <p className="text-sm text-muted-foreground mt-2">
                      Connect to Jira to see lead time distribution and trends
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="trends" className="space-y-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Trend Analysis</CardTitle>
                  <CardDescription>
                    Identify trends and patterns in your data
                  </CardDescription>
                </div>
                <Button variant="outline" size="sm">
                  <Download className="w-4 h-4 mr-2" />
                  Export
                </Button>
              </CardHeader>
              <CardContent>
                <div className="h-80 flex items-center justify-center bg-slate-50 dark:bg-slate-800 rounded-lg">
                  <div className="text-center">
                    <TrendingUp className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
                    <p className="text-muted-foreground">Trend analysis charts will be displayed here</p>
                    <p className="text-sm text-muted-foreground mt-2">
                      Connect to Jira to see trend analysis and forecasting
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Connection Status */}
        <Card className="mt-8 border-dashed border-2 border-orange-200 bg-orange-50 dark:bg-orange-950/20 dark:border-orange-800">
          <CardContent className="p-6 text-center">
            <div className="flex items-center justify-center space-x-2 mb-4">
              <div className="w-3 h-3 bg-orange-500 rounded-full animate-pulse"></div>
              <span className="font-medium text-orange-800 dark:text-orange-200">
                Jira Connection Required
              </span>
            </div>
            <p className="text-orange-700 dark:text-orange-300 mb-4">
              Connect to your Jira instance to start analyzing real data and generating insights.
            </p>
            <Button className="bg-orange-600 hover:bg-orange-700">
              <Settings className="w-4 h-4 mr-2" />
              Configure Jira Connection
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default App


            {/* Legacy Analytics for Compatibility */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                  <div>
                    <CardTitle>Sprint Velocity Analysis</CardTitle>
                    <CardDescription>
                      Track team velocity and completion rates over time
                    </CardDescription>
                  </div>
                  <Button variant="outline" size="sm">
                    <Download className="w-4 h-4 mr-2" />
                    Export
                  </Button>
                </CardHeader>
                <CardContent>
                  <div className="h-80 flex items-center justify-center bg-slate-50 dark:bg-slate-800 rounded-lg">
                    <div className="text-center">
                      <BarChart3 className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
                      <p className="text-muted-foreground">Velocity chart will be displayed here</p>
                      <p className="text-sm text-muted-foreground mt-2">
                        Connect to Jira to see real-time velocity data
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                  <div>
                    <CardTitle>Defect Analysis Dashboard</CardTitle>
                    <CardDescription>
                      Analyze defect patterns and quality metrics
                    </CardDescription>
                  </div>
                  <Button variant="outline" size="sm">
                    <Download className="w-4 h-4 mr-2" />
                    Export
                  </Button>
                </CardHeader>
                <CardContent>
                  <div className="h-80 flex items-center justify-center bg-slate-50 dark:bg-slate-800 rounded-lg">
                    <div className="text-center">
                      <Bug className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
                      <p className="text-muted-foreground">Defect analysis charts will be displayed here</p>
                      <p className="text-sm text-muted-foreground mt-2">
                        Connect to Jira to see defect patterns and quality metrics
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

export default App

