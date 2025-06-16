"""
JUNO Phase 4: Reinforcement Learning Optimizer
Production-grade RL system for continuous optimization
"""

import asyncio
import numpy as np
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import random
import pickle
from collections import deque

logger = logging.getLogger(__name__)

@dataclass
class State:
    """Represents the current state of the system"""
    timestamp: datetime
    metrics: Dict[str, float]
    resource_utilization: Dict[str, float]
    active_tasks: int
    queue_length: int
    error_rate: float
    response_time_ms: float

@dataclass
class Action:
    """Represents an action that can be taken"""
    action_type: str
    parameters: Dict[str, Any]
    expected_impact: float
    confidence: float

@dataclass
class Experience:
    """Represents a learning experience (state, action, reward, next_state)"""
    state: State
    action: Action
    reward: float
    next_state: State
    done: bool

class QLearningAgent:
    """
    Q-Learning agent for system optimization
    """
    
    def __init__(self, state_size: int, action_size: int, learning_rate: float = 0.1):
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.discount_factor = 0.95
        self.epsilon = 1.0  # Exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        
        # Q-table (simplified - in production would use neural networks)
        self.q_table = np.random.uniform(low=-1, high=1, size=(1000, action_size))
        self.state_mapping = {}  # Map states to indices
        self.next_state_index = 0
        
        # Experience replay
        self.memory = deque(maxlen=10000)
        self.batch_size = 32
        
        # Metrics
        self.total_rewards = 0
        self.episode_count = 0
        self.optimization_history = []
    
    def _state_to_index(self, state: State) -> int:
        """Convert state to index for Q-table lookup"""
        # Simplified state representation
        state_key = (
            round(state.resource_utilization.get('cpu', 0) / 10) * 10,
            round(state.resource_utilization.get('memory', 0) / 10) * 10,
            min(state.active_tasks // 10, 9),
            min(state.queue_length // 5, 9),
            round(state.error_rate * 100)
        )
        
        if state_key not in self.state_mapping:
            if self.next_state_index < len(self.q_table):
                self.state_mapping[state_key] = self.next_state_index
                self.next_state_index += 1
            else:
                # Use random index if table is full
                return random.randint(0, len(self.q_table) - 1)
        
        return self.state_mapping[state_key]
    
    def choose_action(self, state: State) -> int:
        """Choose action using epsilon-greedy policy"""
        if np.random.random() <= self.epsilon:
            return random.randrange(self.action_size)
        
        state_index = self._state_to_index(state)
        return np.argmax(self.q_table[state_index])
    
    def remember(self, experience: Experience):
        """Store experience in replay memory"""
        self.memory.append(experience)
    
    def learn(self):
        """Learn from experiences using Q-learning"""
        if len(self.memory) < self.batch_size:
            return
        
        # Sample batch from memory
        batch = random.sample(self.memory, self.batch_size)
        
        for experience in batch:
            state_index = self._state_to_index(experience.state)
            next_state_index = self._state_to_index(experience.next_state)
            
            target = experience.reward
            if not experience.done:
                target += self.discount_factor * np.amax(self.q_table[next_state_index])
            
            action_index = self._action_to_index(experience.action)
            
            # Q-learning update
            self.q_table[state_index][action_index] += self.learning_rate * (
                target - self.q_table[state_index][action_index]
            )
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def _action_to_index(self, action: Action) -> int:
        """Convert action to index"""
        action_types = [
            "scale_up", "scale_down", "optimize_memory", "adjust_timeout",
            "rebalance_load", "cache_optimization", "no_action"
        ]
        return action_types.index(action.action_type) if action.action_type in action_types else 6

class ReinforcementLearningOptimizer:
    """
    Production-grade RL optimizer for JUNO Phase 4
    Continuously optimizes system performance using reinforcement learning
    """
    
    def __init__(self):
        self.agent = QLearningAgent(state_size=10, action_size=7)
        self.current_state: Optional[State] = None
        self.last_action: Optional[Action] = None
        
        # Configuration
        self.optimization_interval = 60  # seconds
        self.evaluation_window = 300    # 5 minutes
        self.min_improvement_threshold = 0.05  # 5%
        
        # Available actions
        self.available_actions = [
            {"type": "scale_up", "description": "Increase resource allocation"},
            {"type": "scale_down", "description": "Decrease resource allocation"},
            {"type": "optimize_memory", "description": "Optimize memory usage"},
            {"type": "adjust_timeout", "description": "Adjust timeout settings"},
            {"type": "rebalance_load", "description": "Rebalance workload distribution"},
            {"type": "cache_optimization", "description": "Optimize caching strategy"},
            {"type": "no_action", "description": "No optimization needed"}
        ]
        
        # Metrics
        self.metrics = {
            "optimizations_performed": 0,
            "successful_optimizations": 0,
            "avg_improvement_percentage": 0.0,
            "total_reward": 0.0,
            "learning_episodes": 0,
            "current_epsilon": 1.0
        }
        
        self.running = False
        self.optimization_history = []
    
    async def start(self):
        """Start the RL optimizer"""
        self.running = True
        logger.info("Starting RL optimizer")
        
        # Start optimization loop
        asyncio.create_task(self._optimization_loop())
        asyncio.create_task(self._learning_loop())
    
    async def stop(self):
        """Stop the RL optimizer"""
        self.running = False
        logger.info("RL optimizer stopped")
    
    async def _optimization_loop(self):
        """Main optimization loop"""
        while self.running:
            try:
                # Get current system state
                current_state = await self._get_system_state()
                
                # Choose and execute action
                action = await self._choose_optimization_action(current_state)
                
                if action.action_type != "no_action":
                    # Execute optimization
                    success = await self._execute_optimization(action)
                    
                    # Evaluate results
                    await asyncio.sleep(30)  # Wait for changes to take effect
                    new_state = await self._get_system_state()
                    reward = self._calculate_reward(current_state, new_state, action)
                    
                    # Store experience
                    experience = Experience(
                        state=self.current_state or current_state,
                        action=self.last_action or action,
                        reward=reward,
                        next_state=new_state,
                        done=False
                    )
                    self.agent.remember(experience)
                    
                    # Update metrics
                    self.metrics["optimizations_performed"] += 1
                    if reward > 0:
                        self.metrics["successful_optimizations"] += 1
                    
                    self.metrics["total_reward"] += reward
                    
                    logger.info(f"Optimization completed: {action.action_type} "
                              f"(reward: {reward:.2f})")
                
                self.current_state = current_state
                self.last_action = action
                
                await asyncio.sleep(self.optimization_interval)
                
            except Exception as e:
                logger.error(f"Error in optimization loop: {e}")
                await asyncio.sleep(30)
    
    async def _learning_loop(self):
        """Background learning loop"""
        while self.running:
            try:
                # Perform learning
                self.agent.learn()
                
                # Update metrics
                self.metrics["learning_episodes"] = self.agent.episode_count
                self.metrics["current_epsilon"] = self.agent.epsilon
                
                await asyncio.sleep(10)  # Learn every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in learning loop: {e}")
                await asyncio.sleep(5)
    
    async def _get_system_state(self) -> State:
        """Get current system state"""
        try:
            # In production, this would collect real metrics
            # For demo, we'll simulate realistic values
            
            base_cpu = 45.0 + random.uniform(-10, 10)
            base_memory = 60.0 + random.uniform(-15, 15)
            base_tasks = 25 + random.randint(-5, 10)
            base_queue = 8 + random.randint(-3, 7)
            base_error_rate = 0.02 + random.uniform(-0.01, 0.02)
            base_response_time = 150 + random.uniform(-30, 50)
            
            state = State(
                timestamp=datetime.now(),
                metrics={
                    "throughput": 1000 + random.uniform(-100, 200),
                    "latency_p95": 200 + random.uniform(-50, 100),
                    "success_rate": 0.98 + random.uniform(-0.02, 0.02)
                },
                resource_utilization={
                    "cpu": max(0, min(100, base_cpu)),
                    "memory": max(0, min(100, base_memory)),
                    "disk": 30 + random.uniform(-10, 20),
                    "network": 25 + random.uniform(-10, 15)
                },
                active_tasks=max(0, base_tasks),
                queue_length=max(0, base_queue),
                error_rate=max(0, min(1, base_error_rate)),
                response_time_ms=max(50, base_response_time)
            )
            
            return state
            
        except Exception as e:
            logger.error(f"Error getting system state: {e}")
            return State(
                timestamp=datetime.now(),
                metrics={},
                resource_utilization={},
                active_tasks=0,
                queue_length=0,
                error_rate=0.0,
                response_time_ms=100.0
            )
    
    async def _choose_optimization_action(self, state: State) -> Action:
        """Choose optimization action based on current state"""
        try:
            action_index = self.agent.choose_action(state)
            action_config = self.available_actions[action_index]
            
            # Generate action parameters based on state
            parameters = self._generate_action_parameters(action_config["type"], state)
            
            action = Action(
                action_type=action_config["type"],
                parameters=parameters,
                expected_impact=self._estimate_impact(action_config["type"], state),
                confidence=1.0 - self.agent.epsilon  # Higher confidence as we learn
            )
            
            logger.debug(f"Chosen action: {action.action_type} "
                        f"(confidence: {action.confidence:.2f})")
            
            return action
            
        except Exception as e:
            logger.error(f"Error choosing optimization action: {e}")
            return Action(
                action_type="no_action",
                parameters={},
                expected_impact=0.0,
                confidence=0.0
            )
    
    def _generate_action_parameters(self, action_type: str, state: State) -> Dict[str, Any]:
        """Generate parameters for the chosen action"""
        if action_type == "scale_up":
            return {
                "cpu_increase": min(20, 100 - state.resource_utilization.get("cpu", 0)),
                "memory_increase": min(15, 100 - state.resource_utilization.get("memory", 0))
            }
        elif action_type == "scale_down":
            return {
                "cpu_decrease": min(10, state.resource_utilization.get("cpu", 0) - 20),
                "memory_decrease": min(10, state.resource_utilization.get("memory", 0) - 30)
            }
        elif action_type == "optimize_memory":
            return {
                "garbage_collection": True,
                "cache_cleanup": True,
                "memory_pool_resize": True
            }
        elif action_type == "adjust_timeout":
            current_timeout = 5000  # Default timeout
            if state.response_time_ms > 200:
                return {"timeout_ms": current_timeout + 2000}
            else:
                return {"timeout_ms": max(1000, current_timeout - 1000)}
        elif action_type == "rebalance_load":
            return {
                "redistribute_tasks": True,
                "update_weights": True,
                "target_utilization": 70
            }
        elif action_type == "cache_optimization":
            return {
                "cache_size_mb": 512 if state.resource_utilization.get("memory", 0) < 70 else 256,
                "eviction_policy": "lru",
                "prefetch_enabled": state.active_tasks > 20
            }
        else:
            return {}
    
    def _estimate_impact(self, action_type: str, state: State) -> float:
        """Estimate the expected impact of an action"""
        cpu_util = state.resource_utilization.get("cpu", 0)
        memory_util = state.resource_utilization.get("memory", 0)
        
        if action_type == "scale_up" and (cpu_util > 80 or memory_util > 85):
            return 0.3  # High impact if resources are constrained
        elif action_type == "scale_down" and cpu_util < 30 and memory_util < 40:
            return 0.2  # Medium impact if over-provisioned
        elif action_type == "optimize_memory" and memory_util > 75:
            return 0.25
        elif action_type == "adjust_timeout" and state.response_time_ms > 300:
            return 0.15
        elif action_type == "rebalance_load" and state.queue_length > 10:
            return 0.2
        elif action_type == "cache_optimization":
            return 0.1
        else:
            return 0.05
    
    async def _execute_optimization(self, action: Action) -> bool:
        """Execute the chosen optimization action"""
        try:
            logger.info(f"Executing optimization: {action.action_type}")
            
            # Simulate optimization execution
            await asyncio.sleep(2)
            
            # Simulate success/failure (90% success rate)
            success = random.random() > 0.1
            
            if success:
                logger.info(f"Optimization {action.action_type} executed successfully")
            else:
                logger.warning(f"Optimization {action.action_type} failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Error executing optimization {action.action_type}: {e}")
            return False
    
    def _calculate_reward(self, old_state: State, new_state: State, action: Action) -> float:
        """Calculate reward based on state improvement"""
        try:
            reward = 0.0
            
            # Performance improvement
            old_response_time = old_state.response_time_ms
            new_response_time = new_state.response_time_ms
            if new_response_time < old_response_time:
                reward += (old_response_time - new_response_time) / old_response_time * 0.5
            
            # Error rate improvement
            old_error_rate = old_state.error_rate
            new_error_rate = new_state.error_rate
            if new_error_rate < old_error_rate:
                reward += (old_error_rate - new_error_rate) * 10
            
            # Resource efficiency
            old_cpu = old_state.resource_utilization.get("cpu", 0)
            new_cpu = new_state.resource_utilization.get("cpu", 0)
            
            # Reward for moving towards optimal CPU utilization (60-80%)
            old_cpu_score = 1.0 - abs(old_cpu - 70) / 70
            new_cpu_score = 1.0 - abs(new_cpu - 70) / 70
            reward += (new_cpu_score - old_cpu_score) * 0.3
            
            # Queue length improvement
            old_queue = old_state.queue_length
            new_queue = new_state.queue_length
            if new_queue < old_queue:
                reward += (old_queue - new_queue) / max(old_queue, 1) * 0.2
            
            # Penalty for no improvement
            if reward <= 0:
                reward = -0.1
            
            # Bonus for significant improvement
            if reward > 0.3:
                reward += 0.1
            
            return reward
            
        except Exception as e:
            logger.error(f"Error calculating reward: {e}")
            return -0.1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get RL optimizer metrics"""
        avg_improvement = 0.0
        if self.metrics["optimizations_performed"] > 0:
            avg_improvement = (self.metrics["total_reward"] / 
                             self.metrics["optimizations_performed"]) * 100
        
        return {
            **self.metrics,
            "avg_improvement_percentage": round(avg_improvement, 2),
            "success_rate": (self.metrics["successful_optimizations"] / 
                           max(self.metrics["optimizations_performed"], 1)) * 100,
            "exploration_rate": round(self.agent.epsilon, 3),
            "q_table_size": len(self.agent.state_mapping)
        }
    
    def get_optimization_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get optimization history"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            opt for opt in self.optimization_history 
            if opt["timestamp"] >= cutoff_time
        ]
    
    async def save_model(self, filepath: str):
        """Save the trained model"""
        try:
            model_data = {
                "q_table": self.agent.q_table.tolist(),
                "state_mapping": self.agent.state_mapping,
                "metrics": self.metrics,
                "timestamp": datetime.now().isoformat()
            }
            
            with open(filepath, "wb") as f:
                pickle.dump(model_data, f)
            
            logger.info(f"Model saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    async def load_model(self, filepath: str):
        """Load a trained model"""
        try:
            with open(filepath, "rb") as f:
                model_data = pickle.load(f)
            
            self.agent.q_table = np.array(model_data["q_table"])
            self.agent.state_mapping = model_data["state_mapping"]
            self.agent.next_state_index = len(self.agent.state_mapping)
            
            logger.info(f"Model loaded from {filepath}")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")

# Example usage
async def main():
    """Example usage of RL optimizer"""
    
    optimizer = ReinforcementLearningOptimizer()
    await optimizer.start()
    
    # Let it run for a while
    await asyncio.sleep(300)  # 5 minutes
    
    # Print metrics
    metrics = optimizer.get_metrics()
    print(f"RL Optimizer metrics: {json.dumps(metrics, indent=2)}")
    
    # Save model
    await optimizer.save_model("rl_model.pkl")
    
    await optimizer.stop()

if __name__ == "__main__":
    asyncio.run(main())

