import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
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
  Sparkles
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

const mockRecentQueries = [
  "How many tickets are assigned to John Doe?",
  "Show me the status distribution for project DEMO",
  "List all bugs from last month",
  "What's the velocity trend for the last 3 sprints?"
]

function App() {
  const [selectedProject, setSelectedProject] = useState('DEMO')
  const [query, setQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [queryResults, setQueryResults] = useState(null)

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
                  Jira AI Analytics
                </h1>
              </div>
              <Badge variant="secondary" className="hidden sm:inline-flex">
                <Sparkles className="w-3 h-3 mr-1" />
                AI-Powered
              </Badge>
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

        {/* Key Metrics Overview */}
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
                  <p className="text-sm font-medium text-muted-foreground">Avg Velocity</p>
                  <p className="text-2xl font-bold">{mockMetrics.avgVelocity}</p>
                </div>
                <Zap className="w-8 h-8 text-green-600" />
              </div>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Defect Rate</p>
                  <p className="text-2xl font-bold">{mockMetrics.defectRate}%</p>
                </div>
                <Bug className="w-8 h-8 text-red-600" />
              </div>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Avg Lead Time</p>
                  <p className="text-2xl font-bold">{mockMetrics.avgLeadTime}d</p>
                </div>
                <Clock className="w-8 h-8 text-purple-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Analytics Dashboard */}
        <Tabs defaultValue="velocity" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
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

