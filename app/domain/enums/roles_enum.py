from enum import Enum

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    TEAM_LEADER = "TEAM_LEADER"
    AGENT = "AGENT"
    CUSTOMER = "CUSTOMER"