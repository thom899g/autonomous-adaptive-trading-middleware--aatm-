"""
Autonomous Adaptive Trading Middleware Core
Facilitates communication between trading modules with pub/sub pattern
"""
import asyncio
from typing import Dict, Any, List, Optional, Callable, Set
from dataclasses import dataclass
from enum import Enum
import json
from loguru import logger
import firebase_admin
from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from config import get_config, TradingMode

class MessageType(Enum):
    """Types of messages that can be sent through middleware"""
    MARKET_DATA = "market_data"
    TRADING_SIGNAL = "trading_signal"
    ORDER_EXECUTION = "order_execution"
    RISK_ALERT = "risk_alert"
    STRATEGY_UPDATE = "strategy_update"
    PERFORMANCE_METRIC = "performance_metric"

@dataclass
class MiddlewareMessage:
    """Standardized message format for inter-module communication"""
    message_id: str
    message_type: MessageType
    sender: str
    recipient: Optional[str] = None  # None for broadcast
    payload: Dict[str, Any] = None
    timestamp: float = None
    priority: int = 1  # 1=low, 5=high
    
    def __post_init__(self):
        if self.timestamp is None:
            import time
            self.timestamp = time.time()
        if self.payload is None