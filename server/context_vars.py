import contextvars

# Define the context variable for the correlation ID globally
correlation_id = contextvars.ContextVar('correlation_id', default='')
