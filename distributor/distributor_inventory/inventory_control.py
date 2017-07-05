from functools import wraps
from django.shortcuts import redirect

def user_passes_test_custom(test_func, redirect_namespace):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            return redirect(redirect_namespace)
        return _wrapped_view
    return decorator

def tenant_has_inventory(user):
    return (user.tenant.maintain_inventory)

