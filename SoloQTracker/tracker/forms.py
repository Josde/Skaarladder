from socket import fromshare
from django import forms 
from django.utils.translation import gettext as _ # Localization
from tracker.utils.constants import tierChoices, rankChoices, regionChoices
from django.utils import timezone
class DatePickerInput(forms.DateInput):
    input_type = 'date'

class TimePickerInput(forms.TimeInput):
    input_type = 'time'

class DateTimePickerInput(forms.DateTimeInput):
    input_type = 'datetime-local'
        
class ChallengeForm(forms.Form):
    # TODO: Default datetimes
    name = forms.CharField(label=_('ChallengeName'), max_length=50)
    start_date = forms.DateTimeField(label=_('StartDate'), widget=DateTimePickerInput)
    end_date = forms.DateTimeField(label=_('EndDate'), widget=DateTimePickerInput)
    player = forms.MultiValueField(fields=[forms.CharField(label=_('PlayerName'), max_length=30)])
    region = forms.CharField(label=_('Region'), widget=forms.Select(choices=regionChoices))
    