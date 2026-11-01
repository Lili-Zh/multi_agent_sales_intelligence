
from contextvars import ContextVar

current_run_id = ContextVar("current_run_id", default=None)


def set_run_id(run_id: str):
    return current_run_id.set(run_id)


def get_run_id():
    return current_run_id.get()


def reset_run_id(token):
    current_run_id.reset(token)
