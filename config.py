"""
AATM Configuration Management
Centralized configuration with environment variable support and type validation
"""
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json
from loguru import logger

class TradingMode(Enum):
    BACKTEST = "backtest"
    PAPER = "paper"
    LIVE = "live"

class EvolutionStrategy(Enum):
    NEAT = "neat"
    GA = "genetic_algorithm"
    CMA_ES = "cma_es"

@dataclass
class DatabaseConfig:
    """Firebase configuration"""
    project_id: str
    credentials_path: str = "credentials/firebase-service-account.json"
    collection_prefix: str = "aatm"
    
    def __post_init__(self):
        if not os.path.exists(self.credentials_path):
            logger.warning(f"Firebase credentials not found at {self.credentials_path}")
            
@dataclass
class NeuroevolutionConfig:
    """Neuroevolution algorithm configuration"""
    strategy: EvolutionStrategy = EvolutionStrategy.GA
    population_size: int = 100
    generations: int = 50
    mutation_rate: float = 0.1
    crossover_rate: float = 0.7
    elite_size: int = 5
    
@dataclass
class TradingConfig:
    """Trading module configuration"""
    mode: TradingMode = TradingMode.PAPER
    max_position_size: float = 0.1  # 10% of portfolio
    stop_loss_pct: float = 0.02  # 2% stop loss
    take_profit_pct: float = 0.05  # 5% take profit
    max_open_positions: int = 5
    
@dataclass
class RiskConfig:
    """Risk management configuration"""
    max_daily_loss: float = 0.02  # 2% maximum daily loss
    max_drawdown: float = 0.1  # 10% maximum drawdown
    var_confidence: float = 0.95  # 95% VaR confidence
    correlation_threshold: float = 0.7
    
class Config:
    """Main configuration singleton"""
    _instance: Optional['Config'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """Load configuration from environment and defaults"""
        # Database
        self.db = DatabaseConfig(
            project_id=os.getenv("FIREBASE_PROJECT_ID", "aatm-trading"),
            credentials_path=os.getenv("FIREBASE_CREDENTIALS_PATH", 
                                      "credentials/firebase-service-account.json")
        )
        
        # Neuroevolution
        self.neuro = NeuroevolutionConfig(
            strategy=EvolutionStrategy(
                os.getenv("EVOLUTION_STRATEGY", "genetic_algorithm")
            ),
            population_size=int(os.getenv("POPULATION_SIZE", "100")),
            generations=int(os.getenv("GENERATIONS", "50"))
        )
        
        # Trading
        self.trading = TradingConfig(
            mode=TradingMode(os.getenv("TRADING_MODE", "paper")),
            max_position_size=float(os.getenv("MAX_POSITION_SIZE", "0.1"))
        )
        
        # Risk
        self.risk = RiskConfig(
            max_daily_loss=float(os.getenv("MAX_DAILY_LOSS", "0.02"))
        )
        
        logger.info("Configuration loaded successfully")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for logging"""
        return {
            "database": {
                "project_id": self.db.project_id,
                "collection_prefix": self.db.collection_prefix
            },
            "neuroevolution": {
                "strategy": self.neuro.strategy.value,
                "population_size": self.neuro.population_size
            },
            "trading": {
                "mode": self.trading.mode.value,
                "max_position_size": self.trading.max_position_size
            }
        }

def get_config() -> Config:
    """Get configuration singleton instance"""
    return Config()