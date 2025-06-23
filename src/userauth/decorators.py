from django.shortcuts import redirect

def user_not_authenticated(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')  # or any other page
        return view_func(request, *args, **kwargs)
    return wrapper