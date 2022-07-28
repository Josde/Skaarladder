from socket import fromshare
from django import forms 
from django.utils.translation import gettext as _ # Localization
from tracker.utils.constants import tierChoices, rankChoices, platformChoices
from django.utils import timezone
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Field, Row, Column, Div
from .models import Challenge, Player
class DatePickerInput(forms.DateInput):
    input_type = 'date'

class TimePickerInput(forms.TimeInput):
    input_type = 'time'

class DateTimePickerInput(forms.DateTimeInput):
    input_type = 'datetime-local'
class ChallengeForm(forms.Form): 
    # TODO: Default datetimes
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
                Fieldset('Create a new challenge',
                    Column(
                        Field('name', css_class="bg-neutral-900 text-white p-4", autocomplete='off'),
                        Field('start_date', css_class="bg-neutral-900 text-white p-4"),
                        Field('end_date', css_class="bg-neutral-900 text-white p-4"),
                        Submit('Submit', 'Submit', css_class="px-4 py-2 m-4 font-bold text-white bg-blue-500 rounded"),
                        css_class="m-4",
                    ),
                css_class="flex flex-col text-white"
                ),  
        )

    name = forms.CharField(label=_('ChallengeName'), max_length=50, empty_value="Challenge name")
    start_date = forms.DateTimeField(label=_('StartDate'), widget=DateTimePickerInput, initial=timezone.now())
    end_date = forms.DateTimeField(label=_('EndDate'), widget=DateTimePickerInput)
   

class PlayerForm(forms.Form):

    def __init__(self, form_id="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Div(
                Row(
                    Field('player_name', css_class="bg-neutral-900 text-white", autocomplete='off'),
                    Field('platform'),
                    css_class="flex flex-row text-white bg-neutral-900"
                ),
                css_class='flex flex-col',
        )

        self.fields['player_name'].widget = forms.TextInput(attrs={'hx-post': '/create/htmx/provisional_parse/',
                                                                            'hx-trigger': 'keyup delay:500ms changed',
                                                                            'hx-swap':"innerhtml",
                                                                            'form': "challenge_form",
                                                                            'hx-target': '#results-{0}'.format(form_id)})
        
        self.fields['platform'].widget = forms.Select(attrs={'hx-post': '/create/htmx/provisional_parse/',
                                                                            'hx-trigger': 'onchange',
                                                                            'hx-swap':"innerhtml",
                                                                            'form': "challenge_form",
                                                                            'hx-target': '#results-{0}'.format(form_id)})
        
    platform = forms.ChoiceField(label=_('platform'), choices=platformChoices)
    player_name = forms.CharField(label=_('PlayerName'), max_length=30)
    

    
    