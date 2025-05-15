from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .utils import get_personalised, get_new_and_specials, get_promotions

@login_required
def contextual_view(request):
    user = request.user
    recs = get_personalised(user, n=5)
    specials = get_new_and_specials(user)
    promos = get_promotions(user)
    return JsonResponse({
        'recommendations': recs,
        'specials': specials,
        'promotions': promos
    })
