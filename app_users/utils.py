# accounts/utils.py
from django.db.models import Q

def search_users(queryset, search_term):
    if search_term:
        return queryset.filter(
            Q(first_name__icontains=search_term) |
            Q(last_name__icontains=search_term) |
            Q(telephone__icontains=search_term)
        )
    return queryset
