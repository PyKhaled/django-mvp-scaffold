import factory
from faker import Faker
from django.contrib.auth.models import User


fake = Faker()

class UserFactory(factory.django.DjangoModelFactory):
    username = factory.LazyAttribute(lambda _: fake.user_name())
    first_name = factory.LazyAttribute(lambda _: fake.first_name())
    last_name = factory.LazyAttribute(lambda _: fake.last_name())
    email = factory.LazyAttribute(lambda _: fake.email())
    is_active = True
    is_staff = False
    is_superuser = False

    class Meta:
        model = User

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.pop("password", "demo-password")
        user = model_class(*args, **kwargs)
        user._skip_welcome_email = True
        user.set_password(password)
        user.save()
        return user
