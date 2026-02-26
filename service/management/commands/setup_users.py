"""
Management command to create default users for the platform.
Usage: python manage.py setup_users
"""

from django.core.management.base import BaseCommand

from accounts.models import User


class Command(BaseCommand):
    help = 'Create default admin, librarian, and blind user accounts'

    def handle(self, *args, **options):
        users = [
            {
                'username': 'admin',
                'password': 'Admin@12345',
                'email': 'admin@taibah.edu.sa',
                'role': User.Role.LIBRARIAN,
                'full_name_ar': 'مدير النظام',
                'is_staff': True,
                'is_superuser': True,
            },
            {
                'username': 'librarian',
                'password': 'Lib@12345',
                'email': 'librarian@taibah.edu.sa',
                'role': User.Role.LIBRARIAN,
                'full_name_ar': 'أخصائي المكتبة',
                'is_staff': False,
                'is_superuser': False,
            },
            {
                'username': 'blind_user',
                'password': 'User@12345',
                'email': 'user@taibah.edu.sa',
                'role': User.Role.BLIND,
                'full_name_ar': 'مستفيد',
                'is_staff': False,
                'is_superuser': False,
            },
        ]

        for u in users:
            user, created = User.objects.get_or_create(
                username=u['username'],
                defaults={
                    'email': u['email'],
                    'role': u['role'],
                    'full_name_ar': u['full_name_ar'],
                    'is_staff': u['is_staff'],
                    'is_superuser': u['is_superuser'],
                }
            )
            if created:
                user.set_password(u['password'])
                user.save()
                self.stdout.write(self.style.SUCCESS(
                    f"  Created: {u['username']} / {u['password']}  ({u['role']})"
                ))
            else:
                # Update password for existing user
                user.set_password(u['password'])
                user.role = u['role']
                user.is_staff = u['is_staff']
                user.is_superuser = u['is_superuser']
                user.save()
                self.stdout.write(self.style.WARNING(
                    f"  Updated: {u['username']} / {u['password']}  ({u['role']})"
                ))

        self.stdout.write(self.style.SUCCESS('\nLogin credentials:'))
        self.stdout.write('  admin     / Admin@12345   (Admin + Librarian)')
        self.stdout.write('  librarian / Lib@12345     (Librarian)')
        self.stdout.write('  blind_user / User@12345   (Blind User / Beneficiary)')
