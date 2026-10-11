from plans.apps import PlansConfig


class ScaffoldPlansConfig(PlansConfig):
    # Match upstream migrations instead of inheriting the project's BigAutoField.
    default_auto_field = "django.db.models.AutoField"
