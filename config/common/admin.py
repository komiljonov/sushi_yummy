from django.contrib import admin
from django.apps import apps

try:
    models = apps.get_models()

    for model in models:
        try:
            if hasattr(model, "Admin"):
                modelAdmin = getattr(model, "Admin")

                @admin.register(model)
                class ModelAdmin(modelAdmin):
                    model = model
                    list_filter = (model.CustomFilter,)

            else:
                if not hasattr(model, "CustomFilter"):
                    admin.site.register(model)
                else:

                    @admin.register(model)
                    class ModelAdmin(admin.ModelAdmin):
                        model = model
                        list_filter = (model.CustomFilter,)

        except admin.sites.AlreadyRegistered as e:
            pass
except Exception as e:
    print(e)
