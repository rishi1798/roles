from rest_auth.models import Role


def create_default_roles():
    perm_config = [("Admin", 1),("Teacher", 2),("Student", 3)]
    for name, level in perm_config:
        role, created = Role.objects.update_or_create(name=name, level=level)
        print(role, created)
