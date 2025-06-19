"""
JUNO Phase 2: Test Data Generation Infrastructure
Comprehensive synthetic data generation for enterprise-scale testing
"""

import random
import json
import csv
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import pytest
np = pytest.importorskip("numpy")
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TeamSize(Enum):
    SMALL = "small"      # 3-5 members
    MEDIUM = "medium"    # 6-9 members
    LARGE = "large"      # 10-15 members


class SprintStatus(Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TicketStatus(Enum):
    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    TESTING = "testing"
    DONE = "done"
    BLOCKED = "blocked"


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class TeamMember:
    user_id: str
    name: str
    role: str
    seniority_level: str  # junior, mid, senior, lead
    skills: List[str]
    capacity: float  # 0.0 to 1.0
    join_date: datetime


@dataclass
class Team:
    team_id: str
    name: str
    department: str
    project: str
    size: TeamSize
    members: List[TeamMember]
    created_date: datetime
    tech_stack: List[str]
    methodology: str  # scrum, kanban, hybrid


@dataclass
class Sprint:
    sprint_id: str
    team_id: str
    name: str
    start_date: datetime
    end_date: datetime
    status: SprintStatus
    planned_velocity: int
    actual_velocity: int
    planned_story_points: int
    completed_story_points: int
    success_rate: float
    risk_factors: Dict[str, float]
    retrospective_notes: str


@dataclass
class Ticket:
    ticket_id: str
    team_id: str
    sprint_id: Optional[str]
    title: str
    description: str
    status: TicketStatus
    priority: Priority
    story_points: int
    assignee_id: str
    reporter_id: str
    created_date: datetime
    updated_date: datetime
    resolved_date: Optional[datetime]
    labels: List[str]
    components: List[str]
    time_spent: int  # hours
    estimated_time: int  # hours


class TestDataGenerator:
    """Comprehensive test data generator for JUNO Phase 2 testing"""
    
    def __init__(self, seed: int = 42):
        """Initialize test data generator with reproducible seed"""
        random.seed(seed)
        np.random.seed(seed)
        
        # Configuration parameters based on test strategy
        self.config = {
            "teams": {
                "total_teams": 50,
                "departments": ["Engineering", "Product", "Data", "Platform", "Security"],
                "projects": ["Core Platform", "Mobile App", "Analytics", "Infrastructure", 
                           "Security", "AI/ML", "Customer Portal", "Admin Tools", "API Gateway",
                           "Data Pipeline", "Monitoring", "DevOps", "Frontend", "Backend", "QA"],
                "methodologies": ["scrum", "kanban", "hybrid"],
                "tech_stacks": {
                    "frontend": ["React", "Vue", "Angular", "TypeScript", "JavaScript"],
                    "backend": ["Python", "Java", "Node.js", "Go", "C#"],
                    "database": ["PostgreSQL", "MySQL", "MongoDB", "Redis"],
                    "cloud": ["AWS", "Azure", "GCP", "Kubernetes", "Docker"],
                    "tools": ["Jira", "Confluence", "Git", "Jenkins", "Terraform"]
                }
            },
            "users": {
                "total_users": 200,
                "roles": ["Developer", "Senior Developer", "Tech Lead", "Product Manager", 
                         "QA Engineer", "DevOps Engineer", "Data Scientist", "Designer"],
                "seniority_levels": ["junior", "mid", "senior", "lead"],
                "capacity_range": (0.6, 1.0)
            },
            "sprints": {
                "total_sprints": 50000,  # Training dataset
                "validation_sprints": 12500,  # Validation dataset
                "test_sprints": 5000,  # Test dataset
                "active_sprints": 500,  # Current active sprints
                "duration_days": [7, 14, 21, 28],
                "velocity_range": (20, 60),
                "success_rate_mean": 0.83,
                "seasonal_factors": {
                    1: 0.95, 2: 0.98, 3: 1.02,  # Q1
                    4: 1.05, 5: 1.08, 6: 1.03,  # Q2
                    7: 0.90, 8: 0.85, 9: 0.95,  # Q3
                    10: 0.88, 11: 0.82, 12: 0.75  # Q4
                }
            },
            "tickets": {
                "total_tickets": 25000,
                "tickets_per_sprint": (15, 45),
                "story_points_range": (1, 13),  # Fibonacci sequence
                "priority_distribution": {
                    Priority.LOW: 0.3,
                    Priority.MEDIUM: 0.5,
                    Priority.HIGH: 0.15,
                    Priority.CRITICAL: 0.05
                },
                "status_distribution": {
                    TicketStatus.DONE: 0.70,
                    TicketStatus.IN_PROGRESS: 0.15,
                    TicketStatus.TODO: 0.08,
                    TicketStatus.TESTING: 0.04,
                    TicketStatus.BLOCKED: 0.02,
                    TicketStatus.BACKLOG: 0.01
                }
            }
        }
        
        # Initialize data containers
        self.teams: List[Team] = []
        self.users: List[TeamMember] = []
        self.sprints: List[Sprint] = []
        self.tickets: List[Ticket] = []
        
        # Name generators
        self.first_names = [
            "Alex", "Jordan", "Taylor", "Casey", "Morgan", "Riley", "Avery", "Quinn",
            "Blake", "Cameron", "Drew", "Emery", "Finley", "Harper", "Hayden", "Jamie",
            "Kendall", "Logan", "Parker", "Peyton", "Reese", "River", "Rowan", "Sage",
            "Sam", "Skylar", "Sydney", "Tanner", "Teagan", "Tyler"
        ]
        
        self.last_names = [
            "Anderson", "Brown", "Chen", "Davis", "Garcia", "Johnson", "Jones", "Lee",
            "Martinez", "Miller", "Moore", "Rodriguez", "Smith", "Taylor", "Thomas",
            "Thompson", "White", "Williams", "Wilson", "Young", "Clark", "Lewis",
            "Walker", "Hall", "Allen", "King", "Wright", "Lopez", "Hill", "Green"
        ]
        
        self.project_adjectives = [
            "Advanced", "Agile", "Cloud", "Digital", "Enterprise", "Future", "Global",
            "Intelligent", "Modern", "Next-Gen", "Optimized", "Scalable", "Smart",
            "Strategic", "Unified", "Innovative", "Robust", "Secure", "Efficient"
        ]
        
    def generate_user_id(self) -> str:
        """Generate unique user ID"""
        return f"user_{uuid.uuid4().hex[:8]}"
    
    def generate_team_id(self) -> str:
        """Generate unique team ID"""
        return f"team_{uuid.uuid4().hex[:8]}"
    
    def generate_sprint_id(self, team_id: str, sprint_number: int) -> str:
        """Generate sprint ID based on team and sprint number"""
        return f"{team_id}_sprint_{sprint_number:03d}"
    
    def generate_ticket_id(self) -> str:
        """Generate unique ticket ID"""
        return f"JUNO-{random.randint(1000, 99999)}"
    
    def generate_name(self) -> str:
        """Generate realistic name"""
        first = random.choice(self.first_names)
        last = random.choice(self.last_names)
        return f"{first} {last}"
    
    def generate_team_members(self, team_size: TeamSize) -> List[TeamMember]:
        """Generate team members based on team size"""
        size_ranges = {
            TeamSize.SMALL: (3, 5),
            TeamSize.MEDIUM: (6, 9),
            TeamSize.LARGE: (10, 15)
        }
        
        min_size, max_size = size_ranges[team_size]
        actual_size = random.randint(min_size, max_size)
        
        members = []
        roles = self.config["users"]["roles"]
        seniority_levels = self.config["users"]["seniority_levels"]
        
        # Ensure at least one tech lead for medium/large teams
        if team_size in [TeamSize.MEDIUM, TeamSize.LARGE]:
            lead_member = TeamMember(
                user_id=self.generate_user_id(),
                name=self.generate_name(),
                role="Tech Lead",
                seniority_level="lead",
                skills=self.generate_skills(),
                capacity=random.uniform(0.8, 1.0),
                join_date=datetime.now() - timedelta(days=random.randint(365, 1825))
            )
            members.append(lead_member)
            actual_size -= 1
        
        # Generate remaining team members
        for _ in range(actual_size):
            member = TeamMember(
                user_id=self.generate_user_id(),
                name=self.generate_name(),
                role=random.choice(roles),
                seniority_level=random.choice(seniority_levels),
                skills=self.generate_skills(),
                capacity=random.uniform(*self.config["users"]["capacity_range"]),
                join_date=datetime.now() - timedelta(days=random.randint(30, 1825))
            )
            members.append(member)
        
        return members
    
    def generate_skills(self) -> List[str]:
        """Generate realistic skill set"""
        all_skills = []
        for category in self.config["teams"]["tech_stacks"].values():
            all_skills.extend(category)
        
        # Each person has 3-8 skills
        num_skills = random.randint(3, 8)
        return random.sample(all_skills, min(num_skills, len(all_skills)))
    
    def generate_tech_stack(self) -> List[str]:
        """Generate realistic tech stack for team"""
        tech_stacks = self.config["teams"]["tech_stacks"]
        stack = []
        
        # Each team has technologies from multiple categories
        for category, technologies in tech_stacks.items():
            if category in ["frontend", "backend"]:
                # Primary technologies
                stack.extend(random.sample(technologies, random.randint(1, 2)))
            else:
                # Supporting technologies
                stack.extend(random.sample(technologies, random.randint(1, 3)))
        
        return stack
    
    def generate_teams(self) -> List[Team]:
        """Generate realistic team data"""
        logger.info("Generating team data...")
        
        teams = []
        departments = self.config["teams"]["departments"]
        projects = self.config["teams"]["projects"]
        methodologies = self.config["teams"]["methodologies"]
        
        for i in range(self.config["teams"]["total_teams"]):
            team_size = random.choice(list(TeamSize))
            
            team = Team(
                team_id=self.generate_team_id(),
                name=f"{random.choice(self.project_adjectives)} {random.choice(projects)} Team",
                department=random.choice(departments),
                project=random.choice(projects),
                size=team_size,
                members=self.generate_team_members(team_size),
                created_date=datetime.now() - timedelta(days=random.randint(30, 730)),
                tech_stack=self.generate_tech_stack(),
                methodology=random.choice(methodologies)
            )
            
            teams.append(team)
            
            # Add team members to global user list
            self.users.extend(team.members)
        
        self.teams = teams
        logger.info(f"Generated {len(teams)} teams with {len(self.users)} total users")
        return teams
    
    def calculate_sprint_success_factors(self, team: Team, sprint_date: datetime) -> Tuple[float, Dict[str, float]]:
        """Calculate realistic sprint success rate and risk factors"""
        base_success_rate = self.config["sprints"]["success_rate_mean"]
        
        # Seasonal adjustment
        month = sprint_date.month
        seasonal_factor = self.config["sprints"]["seasonal_factors"][month]
        
        # Team size factor (medium teams tend to be most successful)
        size_factors = {
            TeamSize.SMALL: 0.95,
            TeamSize.MEDIUM: 1.05,
            TeamSize.LARGE: 0.90
        }
        size_factor = size_factors[team.size]
        
        # Team maturity factor (older teams are more successful)
        team_age_days = (sprint_date - team.created_date).days
        maturity_factor = min(1.2, 0.8 + (team_age_days / 365) * 0.1)
        
        # Calculate final success rate
        success_rate = base_success_rate * seasonal_factor * size_factor * maturity_factor
        success_rate = max(0.3, min(0.98, success_rate))  # Clamp between 30% and 98%
        
        # Generate risk factors
        risk_factors = {
            "velocity_risk": random.uniform(0.1, 0.4),
            "scope_risk": random.uniform(0.05, 0.3),
            "capacity_risk": random.uniform(0.1, 0.35),
            "dependency_risk": random.uniform(0.05, 0.25),
            "technical_debt_risk": random.uniform(0.1, 0.4),
            "external_risk": random.uniform(0.0, 0.2)
        }
        
        return success_rate, risk_factors
    
    def generate_sprints(self) -> List[Sprint]:
        """Generate comprehensive sprint data for training, validation, and testing"""
        logger.info("Generating sprint data...")
        
        if not self.teams:
            raise ValueError("Teams must be generated before sprints")
        
        sprints = []
        total_sprints = (self.config["sprints"]["total_sprints"] + 
                        self.config["sprints"]["validation_sprints"] + 
                        self.config["sprints"]["test_sprints"])
        
        # Generate historical sprints (past 3 years)
        start_date = datetime.now() - timedelta(days=3*365)
        current_date = start_date
        
        sprint_counter = 0
        while sprint_counter < total_sprints and current_date < datetime.now():
            for team in self.teams:
                if sprint_counter >= total_sprints:
                    break
                
                # Sprint duration
                duration = random.choice(self.config["sprints"]["duration_days"])
                sprint_start = current_date
                sprint_end = sprint_start + timedelta(days=duration)
                
                # Skip if sprint would be in the future
                if sprint_start > datetime.now():
                    continue
                
                # Calculate success factors
                success_rate, risk_factors = self.calculate_sprint_success_factors(team, sprint_start)
                
                # Generate velocity data
                base_velocity = random.randint(*self.config["sprints"]["velocity_range"])
                planned_velocity = base_velocity
                
                # Actual velocity based on success rate and risk factors
                velocity_variance = 1.0 - sum(risk_factors.values()) / len(risk_factors)
                actual_velocity = int(planned_velocity * velocity_variance * random.uniform(0.8, 1.2))
                actual_velocity = max(0, actual_velocity)
                
                # Story points
                planned_story_points = planned_velocity
                completed_story_points = int(planned_story_points * success_rate * random.uniform(0.9, 1.1))
                completed_story_points = max(0, min(completed_story_points, planned_story_points))
                
                # Determine sprint status
                if sprint_end < datetime.now() - timedelta(days=7):
                    status = SprintStatus.COMPLETED
                elif sprint_start <= datetime.now() <= sprint_end:
                    status = SprintStatus.ACTIVE
                else:
                    status = SprintStatus.PLANNED
                
                sprint = Sprint(
                    sprint_id=self.generate_sprint_id(team.team_id, sprint_counter % 100),
                    team_id=team.team_id,
                    name=f"Sprint {(sprint_counter % 100) + 1}",
                    start_date=sprint_start,
                    end_date=sprint_end,
                    status=status,
                    planned_velocity=planned_velocity,
                    actual_velocity=actual_velocity,
                    planned_story_points=planned_story_points,
                    completed_story_points=completed_story_points,
                    success_rate=success_rate,
                    risk_factors=risk_factors,
                    retrospective_notes=self.generate_retrospective_notes(success_rate, risk_factors)
                )
                
                sprints.append(sprint)
                sprint_counter += 1
            
            # Move to next sprint cycle (average 2 weeks)
            current_date += timedelta(days=14)
        
        self.sprints = sprints
        logger.info(f"Generated {len(sprints)} sprints")
        return sprints
    
    def generate_retrospective_notes(self, success_rate: float, risk_factors: Dict[str, float]) -> str:
        """Generate realistic retrospective notes based on sprint performance"""
        notes = []
        
        if success_rate > 0.9:
            notes.append("Excellent sprint execution with all goals met.")
        elif success_rate > 0.8:
            notes.append("Good sprint with most objectives achieved.")
        elif success_rate > 0.6:
            notes.append("Mixed results with some challenges encountered.")
        else:
            notes.append("Challenging sprint with significant obstacles.")
        
        # Add specific risk factor notes
        if risk_factors.get("velocity_risk", 0) > 0.3:
            notes.append("Team velocity was lower than expected.")
        
        if risk_factors.get("scope_risk", 0) > 0.25:
            notes.append("Scope changes impacted sprint planning.")
        
        if risk_factors.get("dependency_risk", 0) > 0.2:
            notes.append("External dependencies caused delays.")
        
        if risk_factors.get("technical_debt_risk", 0) > 0.3:
            notes.append("Technical debt slowed development progress.")
        
        return " ".join(notes)
    
    def generate_tickets(self) -> List[Ticket]:
        """Generate realistic ticket data for sprints"""
        logger.info("Generating ticket data...")
        
        if not self.sprints:
            raise ValueError("Sprints must be generated before tickets")
        
        tickets = []
        ticket_types = [
            "Feature", "Bug", "Task", "Story", "Epic", "Improvement", 
            "Sub-task", "Technical Debt", "Research", "Documentation"
        ]
        
        components = [
            "Frontend", "Backend", "Database", "API", "UI/UX", "Infrastructure",
            "Security", "Performance", "Testing", "Documentation", "DevOps"
        ]
        
        for sprint in self.sprints:
            # Number of tickets per sprint
            min_tickets, max_tickets = self.config["tickets"]["tickets_per_sprint"]
            num_tickets = random.randint(min_tickets, max_tickets)
            
            # Get team members for assignment
            team = next((t for t in self.teams if t.team_id == sprint.team_id), None)
            if not team:
                continue
            
            team_members = team.members
            
            for i in range(num_tickets):
                # Ticket timing within sprint
                created_offset = random.randint(0, max(1, (sprint.end_date - sprint.start_date).days - 1))
                created_date = sprint.start_date + timedelta(days=created_offset)
                
                # Story points (Fibonacci sequence)
                story_points = random.choice([1, 2, 3, 5, 8, 13])
                
                # Priority based on distribution
                priority_choices = list(self.config["tickets"]["priority_distribution"].keys())
                priority_weights = list(self.config["tickets"]["priority_distribution"].values())
                priority = np.random.choice(priority_choices, p=priority_weights)
                
                # Status based on distribution and sprint status
                if sprint.status == SprintStatus.COMPLETED:
                    # Completed sprints have mostly done tickets
                    status_choices = [TicketStatus.DONE, TicketStatus.DONE, TicketStatus.DONE, TicketStatus.BLOCKED]
                    status = random.choice(status_choices)
                elif sprint.status == SprintStatus.ACTIVE:
                    # Active sprints have mixed status
                    status_choices = list(self.config["tickets"]["status_distribution"].keys())
                    status_weights = list(self.config["tickets"]["status_distribution"].values())
                    status = np.random.choice(status_choices, p=status_weights)
                else:
                    # Planned sprints have mostly todo/backlog tickets
                    status = random.choice([TicketStatus.TODO, TicketStatus.BACKLOG])
                
                # Assignee and reporter
                assignee = random.choice(team_members)
                reporter = random.choice(team_members)
                
                # Timing calculations
                updated_date = created_date + timedelta(hours=random.randint(1, 168))  # 1 hour to 1 week
                
                resolved_date = None
                if status == TicketStatus.DONE:
                    resolved_date = updated_date + timedelta(hours=random.randint(1, 72))
                
                # Time estimates
                estimated_time = story_points * random.randint(4, 8)  # 4-8 hours per story point
                time_spent = estimated_time if status == TicketStatus.DONE else random.randint(0, estimated_time)
                
                # Generate ticket title and description
                ticket_type = random.choice(ticket_types)
                component = random.choice(components)
                
                ticket = Ticket(
                    ticket_id=self.generate_ticket_id(),
                    team_id=sprint.team_id,
                    sprint_id=sprint.sprint_id,
                    title=f"{ticket_type}: {component} {random.choice(['Enhancement', 'Fix', 'Implementation', 'Optimization'])}",
                    description=f"Implement {component.lower()} {ticket_type.lower()} to improve system functionality and user experience.",
                    status=status,
                    priority=priority,
                    story_points=story_points,
                    assignee_id=assignee.user_id,
                    reporter_id=reporter.user_id,
                    created_date=created_date,
                    updated_date=updated_date,
                    resolved_date=resolved_date,
                    labels=[component.lower(), ticket_type.lower()],
                    components=[component],
                    time_spent=time_spent,
                    estimated_time=estimated_time
                )
                
                tickets.append(ticket)
        
        self.tickets = tickets
        logger.info(f"Generated {len(tickets)} tickets")
        return tickets
    
    def export_to_json(self, output_dir: str = "test_data") -> Dict[str, str]:
        """Export all generated data to JSON files"""
        logger.info("Exporting data to JSON files...")
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        files_created = {}
        
        # Export teams
        teams_file = output_path / "teams.json"
        with open(teams_file, 'w') as f:
            teams_data = []
            for team in self.teams:
                team_dict = asdict(team)
                # Convert datetime objects to strings
                team_dict['created_date'] = team_dict['created_date'].isoformat()
                # Convert enum to string
                team_dict['size'] = team_dict['size'].value
                for member in team_dict['members']:
                    member['join_date'] = member['join_date'].isoformat()
                teams_data.append(team_dict)
            json.dump(teams_data, f, indent=2)
        files_created['teams'] = str(teams_file)
        
        # Export users
        users_file = output_path / "users.json"
        with open(users_file, 'w') as f:
            users_data = [asdict(user) for user in self.users]
            for user in users_data:
                user['join_date'] = user['join_date'].isoformat()
            json.dump(users_data, f, indent=2)
        files_created['users'] = str(users_file)
        
        # Export sprints
        sprints_file = output_path / "sprints.json"
        with open(sprints_file, 'w') as f:
            sprints_data = [asdict(sprint) for sprint in self.sprints]
            for sprint in sprints_data:
                sprint['start_date'] = sprint['start_date'].isoformat()
                sprint['end_date'] = sprint['end_date'].isoformat()
                sprint['status'] = sprint['status'].value
            json.dump(sprints_data, f, indent=2)
        files_created['sprints'] = str(sprints_file)
        
        # Export tickets
        tickets_file = output_path / "tickets.json"
        with open(tickets_file, 'w') as f:
            tickets_data = [asdict(ticket) for ticket in self.tickets]
            for ticket in tickets_data:
                ticket['status'] = ticket['status'].value
                ticket['priority'] = ticket['priority'].value
                ticket['created_date'] = ticket['created_date'].isoformat()
                ticket['updated_date'] = ticket['updated_date'].isoformat()
                if ticket['resolved_date']:
                    ticket['resolved_date'] = ticket['resolved_date'].isoformat()
            json.dump(tickets_data, f, indent=2)
        files_created['tickets'] = str(tickets_file)
        
        logger.info(f"Exported data to {len(files_created)} JSON files in {output_dir}")
        return files_created
    
    def export_to_csv(self, output_dir: str = "test_data") -> Dict[str, str]:
        """Export all generated data to CSV files"""
        logger.info("Exporting data to CSV files...")
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        files_created = {}
        
        # Export teams to CSV
        teams_file = output_path / "teams.csv"
        with open(teams_file, 'w', newline='') as f:
            if self.teams:
                writer = csv.DictWriter(f, fieldnames=[
                    'team_id', 'name', 'department', 'project', 'size', 
                    'member_count', 'created_date', 'methodology'
                ])
                writer.writeheader()
                for team in self.teams:
                    writer.writerow({
                        'team_id': team.team_id,
                        'name': team.name,
                        'department': team.department,
                        'project': team.project,
                        'size': team.size.value,
                        'member_count': len(team.members),
                        'created_date': team.created_date.isoformat(),
                        'methodology': team.methodology
                    })
        files_created['teams'] = str(teams_file)
        
        # Export sprints to CSV
        sprints_file = output_path / "sprints.csv"
        with open(sprints_file, 'w', newline='') as f:
            if self.sprints:
                writer = csv.DictWriter(f, fieldnames=[
                    'sprint_id', 'team_id', 'name', 'start_date', 'end_date', 'status',
                    'planned_velocity', 'actual_velocity', 'planned_story_points', 
                    'completed_story_points', 'success_rate'
                ])
                writer.writeheader()
                for sprint in self.sprints:
                    writer.writerow({
                        'sprint_id': sprint.sprint_id,
                        'team_id': sprint.team_id,
                        'name': sprint.name,
                        'start_date': sprint.start_date.isoformat(),
                        'end_date': sprint.end_date.isoformat(),
                        'status': sprint.status.value,
                        'planned_velocity': sprint.planned_velocity,
                        'actual_velocity': sprint.actual_velocity,
                        'planned_story_points': sprint.planned_story_points,
                        'completed_story_points': sprint.completed_story_points,
                        'success_rate': sprint.success_rate
                    })
        files_created['sprints'] = str(sprints_file)
        
        # Export tickets to CSV
        tickets_file = output_path / "tickets.csv"
        with open(tickets_file, 'w', newline='') as f:
            if self.tickets:
                writer = csv.DictWriter(f, fieldnames=[
                    'ticket_id', 'team_id', 'sprint_id', 'title', 'status', 'priority',
                    'story_points', 'assignee_id', 'created_date', 'resolved_date',
                    'time_spent', 'estimated_time'
                ])
                writer.writeheader()
                for ticket in self.tickets:
                    writer.writerow({
                        'ticket_id': ticket.ticket_id,
                        'team_id': ticket.team_id,
                        'sprint_id': ticket.sprint_id,
                        'title': ticket.title,
                        'status': ticket.status.value,
                        'priority': ticket.priority.value,
                        'story_points': ticket.story_points,
                        'assignee_id': ticket.assignee_id,
                        'created_date': ticket.created_date.isoformat(),
                        'resolved_date': ticket.resolved_date.isoformat() if ticket.resolved_date else '',
                        'time_spent': ticket.time_spent,
                        'estimated_time': ticket.estimated_time
                    })
        files_created['tickets'] = str(tickets_file)
        
        logger.info(f"Exported data to {len(files_created)} CSV files in {output_dir}")
        return files_created
    
    def export_to_database(self, db_path: str = "test_data/juno_test_data.db") -> str:
        """Export all generated data to SQLite database"""
        logger.info("Exporting data to SQLite database...")
        
        # Ensure directory exists
        Path(db_path).parent.mkdir(exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teams (
                team_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                project TEXT NOT NULL,
                size TEXT NOT NULL,
                member_count INTEGER NOT NULL,
                created_date TEXT NOT NULL,
                methodology TEXT NOT NULL,
                tech_stack TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                seniority_level TEXT NOT NULL,
                skills TEXT NOT NULL,
                capacity REAL NOT NULL,
                join_date TEXT NOT NULL,
                team_id TEXT,
                FOREIGN KEY (team_id) REFERENCES teams (team_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sprints (
                sprint_id TEXT PRIMARY KEY,
                team_id TEXT NOT NULL,
                name TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                status TEXT NOT NULL,
                planned_velocity INTEGER NOT NULL,
                actual_velocity INTEGER NOT NULL,
                planned_story_points INTEGER NOT NULL,
                completed_story_points INTEGER NOT NULL,
                success_rate REAL NOT NULL,
                risk_factors TEXT NOT NULL,
                retrospective_notes TEXT,
                FOREIGN KEY (team_id) REFERENCES teams (team_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                ticket_id TEXT PRIMARY KEY,
                team_id TEXT NOT NULL,
                sprint_id TEXT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL,
                priority TEXT NOT NULL,
                story_points INTEGER NOT NULL,
                assignee_id TEXT NOT NULL,
                reporter_id TEXT NOT NULL,
                created_date TEXT NOT NULL,
                updated_date TEXT NOT NULL,
                resolved_date TEXT,
                labels TEXT,
                components TEXT,
                time_spent INTEGER NOT NULL,
                estimated_time INTEGER NOT NULL,
                FOREIGN KEY (team_id) REFERENCES teams (team_id),
                FOREIGN KEY (sprint_id) REFERENCES sprints (sprint_id),
                FOREIGN KEY (assignee_id) REFERENCES users (user_id),
                FOREIGN KEY (reporter_id) REFERENCES users (user_id)
            )
        ''')
        
        # Insert teams
        for team in self.teams:
            cursor.execute('''
                INSERT OR REPLACE INTO teams 
                (team_id, name, department, project, size, member_count, created_date, methodology, tech_stack)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                team.team_id, team.name, team.department, team.project, team.size.value,
                len(team.members), team.created_date.isoformat(), team.methodology,
                json.dumps(team.tech_stack)
            ))
            
            # Insert team members
            for member in team.members:
                cursor.execute('''
                    INSERT OR REPLACE INTO users 
                    (user_id, name, role, seniority_level, skills, capacity, join_date, team_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    member.user_id, member.name, member.role, member.seniority_level,
                    json.dumps(member.skills), member.capacity, member.join_date.isoformat(),
                    team.team_id
                ))
        
        # Insert sprints
        for sprint in self.sprints:
            cursor.execute('''
                INSERT OR REPLACE INTO sprints 
                (sprint_id, team_id, name, start_date, end_date, status, planned_velocity,
                 actual_velocity, planned_story_points, completed_story_points, success_rate,
                 risk_factors, retrospective_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                sprint.sprint_id, sprint.team_id, sprint.name, sprint.start_date.isoformat(),
                sprint.end_date.isoformat(), sprint.status.value, sprint.planned_velocity,
                sprint.actual_velocity, sprint.planned_story_points, sprint.completed_story_points,
                sprint.success_rate, json.dumps(sprint.risk_factors), sprint.retrospective_notes
            ))
        
        # Insert tickets
        for ticket in self.tickets:
            cursor.execute('''
                INSERT OR REPLACE INTO tickets 
                (ticket_id, team_id, sprint_id, title, description, status, priority,
                 story_points, assignee_id, reporter_id, created_date, updated_date,
                 resolved_date, labels, components, time_spent, estimated_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                ticket.ticket_id, ticket.team_id, ticket.sprint_id, ticket.title,
                ticket.description, ticket.status.value, ticket.priority.value,
                ticket.story_points, ticket.assignee_id, ticket.reporter_id,
                ticket.created_date.isoformat(), ticket.updated_date.isoformat(),
                ticket.resolved_date.isoformat() if ticket.resolved_date else None,
                json.dumps(ticket.labels), json.dumps(ticket.components),
                ticket.time_spent, ticket.estimated_time
            ))
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sprints_team_id ON sprints (team_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sprints_start_date ON sprints (start_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tickets_team_id ON tickets (team_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tickets_sprint_id ON tickets (sprint_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets (status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tickets_created_date ON tickets (created_date)')
        
        conn.commit()
        conn.close()
        
        logger.info(f"Exported data to SQLite database: {db_path}")
        return db_path
    
    def generate_all_data(self) -> Dict[str, Any]:
        """Generate all test data and return summary statistics"""
        logger.info("Starting comprehensive test data generation...")
        
        start_time = datetime.now()
        
        # Generate data in dependency order
        teams = self.generate_teams()
        sprints = self.generate_sprints()
        tickets = self.generate_tickets()
        
        generation_time = (datetime.now() - start_time).total_seconds()
        
        # Calculate statistics
        stats = {
            "generation_time_seconds": generation_time,
            "teams": {
                "total": len(teams),
                "by_size": {size.value: len([t for t in teams if t.size == size]) for size in TeamSize},
                "by_department": {dept: len([t for t in teams if t.department == dept]) 
                               for dept in self.config["teams"]["departments"]}
            },
            "users": {
                "total": len(self.users),
                "by_role": {},
                "by_seniority": {}
            },
            "sprints": {
                "total": len(sprints),
                "by_status": {status.value: len([s for s in sprints if s.status == status]) for status in SprintStatus},
                "avg_success_rate": sum(s.success_rate for s in sprints) / len(sprints) if sprints else 0,
                "avg_velocity": sum(s.actual_velocity for s in sprints) / len(sprints) if sprints else 0
            },
            "tickets": {
                "total": len(tickets),
                "by_status": {status.value: len([t for t in tickets if t.status == status]) for status in TicketStatus},
                "by_priority": {priority.value: len([t for t in tickets if t.priority == priority]) for priority in Priority},
                "avg_story_points": sum(t.story_points for t in tickets) / len(tickets) if tickets else 0
            }
        }
        
        # Calculate user statistics
        for user in self.users:
            role = user.role
            seniority = user.seniority_level
            stats["users"]["by_role"][role] = stats["users"]["by_role"].get(role, 0) + 1
            stats["users"]["by_seniority"][seniority] = stats["users"]["by_seniority"].get(seniority, 0) + 1
        
        logger.info(f"Data generation completed in {generation_time:.2f} seconds")
        logger.info(f"Generated: {stats['teams']['total']} teams, {stats['users']['total']} users, "
                   f"{stats['sprints']['total']} sprints, {stats['tickets']['total']} tickets")
        
        return stats


def main():
    """Main function to generate comprehensive test data"""
    logger.info("JUNO Phase 2 Test Data Generation Starting...")
    
    # Initialize generator
    generator = TestDataGenerator(seed=42)  # Reproducible results
    
    # Generate all data
    stats = generator.generate_all_data()
    
    # Export to multiple formats
    json_files = generator.export_to_json("test_data")
    csv_files = generator.export_to_csv("test_data")
    db_file = generator.export_to_database("test_data/juno_test_data.db")
    
    # Print summary
    print("\n" + "="*60)
    print("JUNO Phase 2 Test Data Generation Complete")
    print("="*60)
    print(f"Generation Time: {stats['generation_time_seconds']:.2f} seconds")
    print(f"Teams Generated: {stats['teams']['total']}")
    print(f"Users Generated: {stats['users']['total']}")
    print(f"Sprints Generated: {stats['sprints']['total']}")
    print(f"Tickets Generated: {stats['tickets']['total']}")
    print(f"Average Sprint Success Rate: {stats['sprints']['avg_success_rate']:.1%}")
    print(f"Average Sprint Velocity: {stats['sprints']['avg_velocity']:.1f}")
    print(f"Average Story Points per Ticket: {stats['tickets']['avg_story_points']:.1f}")
    
    print("\nFiles Created:")
    for file_type, file_path in json_files.items():
        print(f"  JSON {file_type}: {file_path}")
    for file_type, file_path in csv_files.items():
        print(f"  CSV {file_type}: {file_path}")
    print(f"  Database: {db_file}")
    
    print("\nTest data generation completed successfully!")
    print("Data is ready for JUNO Phase 2 testing and validation.")


if __name__ == "__main__":
    main()

