from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Div, Field, Fieldset, Layout, Row, Submit, HTML
from django import forms
from django.core.exceptions import ValidationError

from tracker.utils import constants
from tracker.templatetags import tags


class DatePickerInput(forms.DateInput):
    input_type = "date"


class TimePickerInput(forms.TimeInput):
    input_type = "time"


class DateTimePickerInput(forms.DateTimeInput):
    input_type = "datetime-local"


class LadderForm(forms.Form):
    """Ladder creation form"""

    # TODO: Default datetimes do not show up for some reason
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        print(start_date, end_date)
        if start_date and end_date and start_date > end_date:
            raise ValidationError("Start date must be previous to end date.")
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                "Create a new ladder",
                Column(
                    Field(
                        "name",
                        css_class=constants.DEFAULT_FORM_STYLE,
                        autocomplete="off",
                    ),
                    Field("start_date", css_class=constants.DEFAULT_FORM_STYLE),
                    Field("end_date", css_class=constants.DEFAULT_FORM_STYLE),
                    Div(  # TODO: Change this to be is_relative. Makes more sense for absolute to be the default.
                        HTML(  # TODO: Maybe this can be prettified. At least it works.
                            "{% include 'tracker/partials/help_button.html' with help='If this box is ticked, whoever has the highest LPs wins. If not, the player who climbs the most from its starting ELO will win.' %}"
                        ),
                        Field(
                            "is_absolute",
                        ),
                        css_class="inline",
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
    start_date = forms.DateTimeField(label=("Start date"), widget=DateTimePickerInput)
    end_date = forms.DateTimeField(label=("End date"), widget=DateTimePickerInput)
    is_absolute = forms.BooleanField(label=("Absolute ranking"), required=False)
    ignore_unranked = forms.BooleanField(label=("Hide unranked"), required=False)


class PlayerForm(forms.Form):
    """Form to input the name and platform of a single player. Used as a part of LadderForm that gets added dynamically"""

    form_id = ""

    def __init__(self, *args, form_id="", **kwargs):
        super().__init__(*args, **kwargs)
        self.form_id = form_id
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Div(
            Row(
                Field(
                    "player_name",
                    css_class="bg-neutral-800 text-white",
                    autocomplete="off",
                ),
                Field("platform"),
                Field("valid", css_class="hidden"),
                css_class="flex flex-row text-white bg-neutral-800",
            ),
            css_class="flex flex-col",
        )

        self.fields["player_name"].widget = forms.TextInput(
            attrs={
                "hx-post": "/create/htmx/provisional_parse/",
                "hx-trigger": "keyup delay:500ms changed",
                "hx-swap": "innerhtml",
                "form": "ladder_form",
                "hx-target": f"#results-{self.form_id}",
            }
        )

        self.fields["platform"].widget = forms.Select(
            attrs={
                "hx-post": "/create/htmx/provisional_parse/",
                "hx-trigger": "changed",
                "hx-swap": "innerhtml",
                "form": "ladder_form",
                "hx-target": f"#results-{self.form_id}",
            }
        )

    platform = forms.ChoiceField(label="Platform", choices=constants.PLATFORM_CHOICES)
    player_name = forms.CharField(label="Name", max_length=16, min_length=3)
    valid = forms.BooleanField(required=False, label="", show_hidden_initial=True)  # Unused for now
