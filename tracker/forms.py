from django import forms
from django.utils.translation import gettext as _  # Localization
from tracker.utils.constants import platformChoices
from django.utils import timezone
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Field, Row, Column, Div
from tracker.utils import constants
from django.core.exceptions import ValidationError


class DatePickerInput(forms.DateInput):
    input_type = "date"


class TimePickerInput(forms.TimeInput):
    input_type = "time"


class DateTimePickerInput(forms.DateTimeInput):
    input_type = "datetime-local"


class ChallengeForm(forms.Form):
    # TODO: Default datetimes
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        print(start_date, end_date)
        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError("Start date must be previous to end date.")
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                "Create a new challenge",
                Column(
                    Field(
                        "name",
                        css_class=constants.default_form_style,
                        autocomplete="off",
                    ),
                    Field("start_date", css_class=constants.default_form_style),
                    Field("end_date", css_class=constants.default_form_style),
                    Field(
                        "is_absolute",
                    ),
                    Field("ignore_unranked"),
                    Submit(
                        "Submit",
                        "Submit",
                        css_class="px-4 py-2 m-4 font-bold text-white bg-blue-500 rounded",
                    ),
                    css_class="m-4",
                ),
                css_class="flex flex-col text-white place-content-end items-end",
            ),
        )

    name = forms.CharField(label=("Ladder name"), max_length=16, empty_value="Ladder name")
    start_date = forms.DateTimeField(label=("Start date"), widget=DateTimePickerInput, initial=timezone.now())
    end_date = forms.DateTimeField(label=("End date"), widget=DateTimePickerInput)
    is_absolute = forms.BooleanField(label=("Absolute ranking"), required=False)
    ignore_unranked = forms.BooleanField(label=("Hide unranked"), required=False)


class PlayerForm(forms.Form):
    form_id = ""

    def __init__(self, form_id="", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_id = form_id
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Div(
            Row(
                Field(
                    "player_name",
                    css_class="bg-neutral-900 text-white",
                    autocomplete="off",
                ),
                Field("platform"),
                Field("is_valid", css_class="hidden"),
                css_class="flex flex-row text-white bg-neutral-900",
            ),
            css_class="flex flex-col",
        )

        self.fields["player_name"].widget = forms.TextInput(
            attrs={
                "hx-post": "/create/htmx/provisional_parse/",
                "hx-trigger": "keyup delay:500ms changed",
                "hx-swap": "innerhtml",
                "form": "challenge_form",
                "hx-target": "#results-{0}".format(self.form_id),
            }
        )

        self.fields["platform"].widget = forms.Select(
            attrs={
                "hx-post": "/create/htmx/provisional_parse/",
                "hx-trigger": "changed",
                "hx-swap": "innerhtml",
                "form": "challenge_form",
                "hx-target": "#results-{0}".format(self.form_id),
            }
        )

    platform = forms.ChoiceField(label="Platform", choices=platformChoices)
    player_name = forms.CharField(label="Name", max_length=16, min_length=3)
    is_valid = forms.BooleanField(required=False, label="", show_hidden_initial=True)
