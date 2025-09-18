from django.core.management.base import BaseCommand
from orders.models import WeightBasedShippingFee

class Command(BaseCommand):
    help = '全国一律の重量別送料を登録します（ふくのこめ便）'

    def handle(self, *args, **kwargs):
        data = [
            (2, 800),
            (5, 1000),
            (10, 1300),
            (20, 1800),
            (30, 2300),
        ]
        for max_weight, fee in data:
            WeightBasedShippingFee.objects.update_or_create(
                max_weight=max_weight,
                defaults={'fee': fee, 'tax_rate': 0.1}
            )
        self.stdout.write(self.style.SUCCESS('全国一律・重量別送料を登録しました'))
