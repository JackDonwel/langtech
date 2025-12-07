from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings

class Command(BaseCommand):
    help = 'Setup password reset system'
    
    def handle(self, *args, **options):
        self.stdout.write('Setting up password reset system...')
        
        # Update site domain for password reset emails
        try:
            site = Site.objects.get_current()
            if site.domain == 'example.com':
                site.domain = '127.0.0.1:8000' if settings.DEBUG else 'yourdomain.com'
                site.name = 'Langtech'
                site.save()
                self.stdout.write(self.style.SUCCESS('✓ Site domain updated'))
        except:
            pass
        
        self.stdout.write(self.style.SUCCESS('\n✓ Password reset system is ready!'))
        self.stdout.write('\nTo test:')
        self.stdout.write('1. Go to: /accounts/password-reset/')
        self.stdout.write('2. Enter your email')
        self.stdout.write('3. Check console for reset link')
        self.stdout.write('4. Follow link to reset password')