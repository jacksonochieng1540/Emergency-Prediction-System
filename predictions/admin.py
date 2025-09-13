from django.contrib import admin

# Register your models here.
from. models import EmergencyType,SeverityLevel,EmergencyPrediction,PredictionFeedback


#admin.site.register(EmergencyType)
# admin.site.register(SeverityLevel)
# admin.site.register(EmergencyPrediction)
admin.site.register(PredictionFeedback)