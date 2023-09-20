from django.shortcuts import redirect
from django.urls import reverse

class RedirectAuthenticatedUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.path == redirect('login'):
            # If the user is logged in and tries to access the login page, redirect them to the login page.
            return redirect('login')

        response = self.get_response(request)
        return response
