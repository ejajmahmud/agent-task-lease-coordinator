"""Unit tests for agent-task-lease-coordinator."""
import unittest
import time
from agent_task_lease_coordinator.coordinator import LeaseCoordinator

class TestLeaseCoordinator(unittest.TestCase):
    def setUp(self):
        self.coord = LeaseCoordinator()

    def test_acquire_and_release(self):
        ok, token = self.coord.acquire("res1", "ownerA", ttl_seconds=2.0)
        self.assertTrue(ok)
        self.assertIsNotNone(token)
        self.assertTrue(self.coord.is_valid("res1", token))
        self.assertTrue(self.coord.release("res1", "ownerA", token))
        self.assertFalse(self.coord.is_valid("res1", token))

    def test_prevent_concurrent_steal(self):
        ok1, tok1 = self.coord.acquire("res2", "ownerA", ttl_seconds=10.0)
        ok2, tok2 = self.coord.acquire("res2", "ownerB", ttl_seconds=10.0)
        self.assertTrue(ok1)
        self.assertFalse(ok2)
        self.assertIsNone(tok2)

    def test_automatic_expiration(self):
        ok, token = self.coord.acquire("res3", "ownerA", ttl_seconds=0.05)
        self.assertTrue(ok)
        time.sleep(0.08)
        self.assertFalse(self.coord.is_valid("res3", token))
        # Now ownerB can acquire
        ok2, tok2 = self.coord.acquire("res3", "ownerB", ttl_seconds=2.0)
        self.assertTrue(ok2)
        self.assertGreater(tok2, token)

if __name__ == "__main__":
    unittest.main()
