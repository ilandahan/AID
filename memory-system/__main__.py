"""
AID Memory System - CLI Entry Point

Allows running the sub-agent as a module:
    python -m memory_system --analyze
    python -m memory_system --dashboard
    python -m memory_system --status
"""

from .subagent import main

if __name__ == "__main__":
    main()
