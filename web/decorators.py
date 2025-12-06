from functools import wraps
from typing import Iterable
from django.core.exceptions import PermissionDenied


def role_required(roles: Iterable[str]):
  roles_set = set(roles)

  def decorator(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
      if not request.user.is_authenticated:
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.get_full_path())
      if request.user.role not in roles_set and not request.user.is_superuser:
        raise PermissionDenied("Insufficient role")
      return view_func(request, *args, **kwargs)

    return _wrapped_view

  return decorator
