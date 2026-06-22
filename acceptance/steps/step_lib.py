"""Shared step-handler registry utilities for acceptance step modules."""
import re


def make_registry():
    """Return a (STEP_HANDLERS dict, step decorator, run_step fn) triple."""
    handlers = {}

    def step(pattern):
        def decorator(fn):
            handlers[pattern] = fn
            return fn
        return decorator

    def run_step(keyword: str, text: str, params: dict) -> None:
        for pattern, handler in handlers.items():
            m = re.fullmatch(pattern, text)
            if m:
                handler(m, params)
                return
        raise NotImplementedError(f"No step handler for: {keyword} {text!r}")

    return handlers, step, run_step
