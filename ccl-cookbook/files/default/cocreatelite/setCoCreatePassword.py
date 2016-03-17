#!/usr/bin/env python
import django
import sys
from django.contrib.auth.models import User

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.stderr.write('Enter a password to be set')
        sys.exit(1)
    django.setup()
    user = User.objects.get(username='cocreate')
    user.set_password(sys.argv[1])
    user.save()
