"""CLI for agent-task-lease-coordinator."""
import sys
import argparse
from .coordinator import LeaseCoordinator

def main():
    parser = argparse.ArgumentParser(description="Agent Task Lease Coordinator CLI")
    parser.add_argument("--demo", action="store_true", help="Run distributed lease acquisition and renewal demo")
    args = parser.parse_args()

    if args.demo:
        coord = LeaseCoordinator()
        ok, token = coord.acquire("finetune_job_8", "agent_node_1", ttl_seconds=2.0)
        print(f"[+] Lease acquired: ok={ok}, fence_token={token}")
        renewed = coord.renew_heartbeat("finetune_job_8", "agent_node_1", token, ttl_seconds=5.0)
        print(f"[+] Heartbeat renewed: {renewed}")
        released = coord.release("finetune_job_8", "agent_node_1", token)
        print(f"[+] Lease cleanly released: {released}")
    else:
        parser.print_help()
    sys.exit(0)

if __name__ == "__main__":
    main()
