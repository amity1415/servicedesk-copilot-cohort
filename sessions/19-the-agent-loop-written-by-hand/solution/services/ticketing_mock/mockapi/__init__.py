"""Mock of the company ticketing system (HelpHub), provided by the trainer.

It behaves like an external enterprise system: it validates input, returns
structured errors, supports idempotent creates and can be told to misbehave
(errors, rate limits, slow responses) so the agent's error handling can be tested.
"""

__version__ = "1.0.0"
