from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin


def role_required(*roles):
    """
    Décorateur pour les FBV.
    Usage : @role_required('ENSEIGNANT')
            @role_required('DIRECTION', 'SCOLARITE')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if not request.user.actif:
                return redirect('accounts:login')
            user_groups = request.user.groups.values_list('name', flat=True)
            if any(r in user_groups for r in roles):
                return view_func(request, *args, **kwargs)
            return redirect('accounts:acces_refuse')
        return wrapper
    return decorator


class RoleRequiredMixin(LoginRequiredMixin):
    """
    Mixin pour les CBV.
    Usage : class MaVue(RoleRequiredMixin, ListView):
                roles_requis = ['ENSEIGNANT']
    """
    roles_requis = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.actif:
            return redirect('accounts:login')
        user_groups = request.user.groups.values_list('name', flat=True)
        if not any(r in user_groups for r in self.roles_requis):
            return redirect('accounts:acces_refuse')
        return super().dispatch(request, *args, **kwargs)
