from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'product.accounts'
    label = 'accounts'

    def ready(self):
        from django.contrib.auth import get_user_model
        from simple_history import register

        register(get_user_model(), app=self.name, excluded_fields=["password", "last_login"])
        import product.accounts.signals  # noqa
