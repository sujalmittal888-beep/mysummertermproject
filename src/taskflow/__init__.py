"""TaskFlow: Language-to-Task Flow Graph Generator for industrial robot operations.

Scope: NL instruction -> JSON task schema -> validation -> NetworkX DAG ->
graph validation -> visualization -> export. The pipeline terminates after
export generation. No execution engine, robot control, or ROS integration
exists in this codebase by design.
"""
__version__ = "1.0.0"
