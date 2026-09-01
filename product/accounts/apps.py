from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'product.accounts'
    label = 'accounts'

    def ready(self):
        import product.accounts.signals  # noqa
