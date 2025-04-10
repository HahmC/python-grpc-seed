from contextlib import contextmanager
from context_vars import correlation_id

@contextmanager
def set_correlation_id(correlation_id_var):
    """
    Set the correlation_id for the context

    :param correlation_id_var: correlation_id to set
    :return:
    """
    token = correlation_id.set(correlation_id_var)
    try:
        yield
    finally:
        correlation_id.reset(token)
