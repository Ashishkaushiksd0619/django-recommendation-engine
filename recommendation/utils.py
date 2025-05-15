import scipy.sparse as sp
from django.utils import timezone
from django.db import OperationalError
from .models import Food, Order, NewAndSpecial, UserProfile, Promotion
from implicit.als import AlternatingLeastSquares

# ----------------------
# MATRIX FACTORIZATION SETUP
# ----------------------
try:
    data = {}
    for uid, fid in Order.objects.values_list('user_id', 'food_id'):
        data[(uid, fid)] = data.get((uid, fid), 0) + 1

    _users = sorted({u for u, _ in data})
    _items = sorted({i for _, i in data})
    u_index = {u: idx for idx, u in enumerate(_users)}
    i_index = {i: idx for idx, i in enumerate(_items)}

    rows, cols, vals = [], [], []
    for (u, f), count in data.items():
        rows.append(u_index[u])
        cols.append(i_index[f])
        vals.append(count)

    _ui_matrix = sp.csr_matrix((vals, (rows, cols)), shape=(len(_users), len(_items)))
    _als_model = AlternatingLeastSquares(factors=50, regularization=0.01, iterations=15)
    # implicit expects item-user matrix
    _als_model.fit(_ui_matrix.T)
except OperationalError:
    _als_model = None
    _ui_matrix = None
    _users = []
    _items = []

# ----------------------
# PUBLIC API FUNCTIONS
# ----------------------

def get_cf_recommendations(user, n=5):
    """ALS collaborative filtering with fallback to popular items."""
    # IDs the user has already ordered
    ordered_ids = set(Order.objects.filter(user=user).values_list('food_id', flat=True))

    def _popular_fallback(count):
        extras = Food.objects.exclude(pk__in=ordered_ids).order_by('-num_orders')[:count]
        return [{'title': f.title, 'score': 0.0, 'price': float(f.price)} for f in extras]

    if _als_model is None or _ui_matrix is None:
        return _popular_fallback(n)

    try:
        uid = _users.index(user.id)
    except ValueError:
        return []

    user_items = _ui_matrix[uid]
    # request extra for filtering
    raw_recs = _als_model.recommend(uid, user_items, N=n * 2)
    # normalize to list of (idx, score)
    if isinstance(raw_recs, tuple) and len(raw_recs) == 2:
        ids, scores = raw_recs
        recs = list(zip(ids.tolist(), scores.tolist()))
    else:
        recs = raw_recs

    results = []
    added = set()
    for idx, score in recs:
        item_idx = int(idx)
        if item_idx < 0 or item_idx >= len(_items):
            continue
        fid = _items[item_idx]
        if fid in ordered_ids or fid in added:
            continue
        food = Food.objects.filter(pk=fid).first()
        if food:
            results.append({'title': food.title, 'score': float(score), 'price': float(food.price)})
            added.add(fid)
        if len(results) >= n:
            break

    # supplement if needed
    if len(results) < n:
        results += _popular_fallback(n - len(results))

    return results


def get_new_and_specials(user):
    """Return specials for the user's home canteen."""
    profile = UserProfile.objects.get(user=user)
    specials = NewAndSpecial.objects.filter(
        food__canteen=profile.home_canteen,
        is_special=True
    )
    return [{'title': s.food.title, 'price': float(s.food.price)} for s in specials]


def get_promotions(user):
    """Return active local and national promotions for the user."""
    profile = UserProfile.objects.get(user=user)
    now = timezone.now().date()
    local = Promotion.objects.filter(
        canteen=profile.home_canteen,
        valid_from__lte=now,
        valid_to__gte=now,
        level='local'
    )
    national = Promotion.objects.filter(
        chain=profile.home_canteen.chain,
        valid_from__lte=now,
        valid_to__gte=now,
        level='national'
    )
    return [
        {'code': p.code, 'discount_percent': p.discount_percent, 'level': p.level}
        for p in list(local) + list(national)
    ]

# alias
get_personalised = get_cf_recommendations
