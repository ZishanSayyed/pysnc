from .models import School

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0]
        slug = request.headers.get('X-School-Slug')

        if not slug:
            parts = host.split('.')
            if len(parts) > 2:
                slug = parts[0]

        try:
            request.school = School.objects.get(slug=slug, is_active=True)
        except School.DoesNotExist:
            request.school = None

        return self.get_response(request)