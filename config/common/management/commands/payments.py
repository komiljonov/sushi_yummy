import random
from django.core.management.base import BaseCommand
from bot.models import User
from data.payment.models import (
    Payment,
)  # Assuming `Payment` and `User` are in `bot` app
from data.cart.models import Cart  # Assuming `Cart` is in `cart` app


class Command(BaseCommand):
    help = "Create test data for Payment model"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count", type=int, help="Number of test payments to create"
        )

    def handle(self, *args, **kwargs):
        count = kwargs["count"]
        if not count:
            count = int(input("Enter the number of test payments to create: "))

        providers = ["CLICK", "PAYME", "CASH"]
        statuses = ["SUCCESSFUL", "CANCELLED"]

        users = list(User.objects.all())
        carts = list(Cart.objects.all())

        if not users:
            self.stdout.write(
                self.style.ERROR("No users available to assign payments.")
            )
            return

        if not carts:
            self.stdout.write(self.style.ERROR("No carts available to assign orders."))
            return

        for _ in range(count):
            user = random.choice(users)
            cart = random.choice(carts)
            provider = random.choice(providers)
            status = random.choice(statuses)
            amount = random.randint(10000, 1000000)

            payment = Payment.objects.create(
                user=user,
                provider=provider,
                amount=amount,
                status=status,
                # order=cart,
                data={
                    "transaction_id": random.randint(1000, 9999),
                    "description": f"Test payment with provider {provider}",
                },
            )

            self.stdout.write(
                self.style.SUCCESS(f"Successfully created Payment: {payment.id}")
            )

        self.stdout.write(self.style.SUCCESS(f"Created {count} test payments."))
