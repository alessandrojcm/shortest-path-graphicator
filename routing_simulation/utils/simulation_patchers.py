from functools import wraps


# Calls pre and post before an after resource acquisition
def patch_resource(resource, pre=None, post=None):
    def get_wrapper(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if pre:
                pre(resource)

            ret = func(*args, **kwargs)

            if post:
                post(resource)
            return ret

        return wrapper

    for name in ['put', 'get', 'request', 'release']:
        if hasattr(resource, name):
            setattr(resource, name, get_wrapper(getattr(resource, name)))


# Registers a callback for the resource items
def items_spy(callback, resource):
    callback(resource.items)
