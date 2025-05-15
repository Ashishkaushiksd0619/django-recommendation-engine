from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from recommendation.models import (
    Chain, Canteen, Food, Promotion,
    UserProfile, CartItem, ViewingHistory,
    Order, NewAndSpecial
)
import importlib
import recommendation.utils as utils

class UtilsTestCase(TestCase):
    def setUp(self):
        date_today = timezone.now().date()
        # Create chain and canteen
        self.chain = Chain.objects.create(name='TestChain')
        self.canteen = Canteen.objects.create(name='TestCanteen', chain=self.chain)
        # Create food items
        self.food1 = Food.objects.create(
            title='Pizza', canteen=self.canteen,
            price=10.00, num_orders=5,
            category='Fast Food', avg_rating=4.5, num_rating=10,
            tags='cheese, tomato'
        )
        self.food2 = Food.objects.create(
            title='Burger', canteen=self.canteen,
            price=8.00, num_orders=3,
            category='Fast Food', avg_rating=4.0, num_rating=5,
            tags='potato, lettuce'
        )
        self.food3 = Food.objects.create(
            title='Salad', canteen=self.canteen,
            price=6.00, num_orders=2,
            category='Healthy', avg_rating=5.0, num_rating=2,
            tags='lettuce, tomato'
        )
        # Create promotions
        self.promo_local = Promotion.objects.create(
            code='LOCAL10', discount_percent=10.0,
            canteen=self.canteen, chain=self.chain,
            level='local', valid_from=date_today,
            valid_to=date_today
        )
        self.promo_national = Promotion.objects.create(
            code='NAT20', discount_percent=20.0,
            canteen=None, chain=self.chain,
            level='national', valid_from=date_today,
            valid_to=date_today
        )
        # Create user and profile
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='pass'
        )
        UserProfile.objects.create(
            user=self.user, home_canteen=self.canteen
        )
        # Create order to train CF model
        Order.objects.create(user=self.user, food=self.food3)
        # Create new special
        NewAndSpecial.objects.create(food=self.food2, is_special=True)
        # Reload utils to train ALS model
        importlib.reload(utils)

    def test_get_cf_recommendations(self):
        # Request 2 recommendations
        recs = utils.get_cf_recommendations(self.user, n=2)
        self.assertIsInstance(recs, list)
        self.assertEqual(len(recs), 2)
        # Ensure the ordered item isn't recommended again
        titles = [r['title'] for r in recs]
        self.assertNotIn(self.food3.title, titles)

    def test_get_personalised_alias(self):
        # get_personalised is alias to CF
        cf_recs = utils.get_cf_recommendations(self.user, n=3)
        personal_recs = utils.get_personalised(self.user, n=3)
        self.assertEqual(cf_recs, personal_recs)

    def test_get_new_and_specials(self):
        specials = utils.get_new_and_specials(self.user)
        self.assertEqual(len(specials), 1)
        self.assertEqual(specials[0]['title'], 'Burger')

    def test_get_promotions(self):
        promos = utils.get_promotions(self.user)
        codes = {p['code'] for p in promos}
        self.assertSetEqual(codes, {'LOCAL10', 'NAT20'})
