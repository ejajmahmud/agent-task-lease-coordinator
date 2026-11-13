"""Distributed lease and lock coordinator with monotonic fencing tokens."""
import time
from typing import Dict, Optional, Tuple, Any

class LeaseInfo:
    def __init__(self, resource: str, owner_id: str, fence_token: int, expires_at: float):
        self.resource = resource
        self.owner_id = owner_id
        self.fence_token = fence_token
        self.expires_at = expires_at

class LeaseCoordinator:
    """Manages high-reliability resource leases with fence tokens and TTL expiration."""

    def __init__(self):
        self.leases: Dict[str, LeaseInfo] = {}
        self.current_fence_token = 1000

    def acquire(self, resource: str, owner_id: str, ttl_seconds: float = 5.0) -> Tuple[bool, Optional[int]]:
        now = time.time()
        current_lease = self.leases.get(resource)

        if current_lease and now < current_lease.expires_at:
            if current_lease.owner_id == owner_id:
                # Renew
                current_lease.expires_at = now + ttl_seconds
                return True, current_lease.fence_token
            return False, None

        self.current_fence_token += 1
        new_lease = LeaseInfo(resource, owner_id, self.current_fence_token, now + ttl_seconds)
        self.leases[resource] = new_lease
        return True, self.current_fence_token

    def renew_heartbeat(self, resource: str, owner_id: str, fence_token: int, ttl_seconds: float = 5.0) -> bool:
        now = time.time()
        lease = self.leases.get(resource)
        if not lease or lease.owner_id != owner_id or lease.fence_token != fence_token:
            return False
        if now >= lease.expires_at:
            return False
        lease.expires_at = now + ttl_seconds
        return True

    def release(self, resource: str, owner_id: str, fence_token: int) -> bool:
        lease = self.leases.get(resource)
        if not lease or lease.owner_id != owner_id or lease.fence_token != fence_token:
            return False
        del self.leases[resource]
        return True

    def is_valid(self, resource: str, fence_token: int) -> bool:
        now = time.time()
        lease = self.leases.get(resource)
        return bool(lease and lease.fence_token == fence_token and now < lease.expires_at)
