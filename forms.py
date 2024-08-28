from django import forms
from .models import Major
from django.contrib.auth.models import User

class PreferenceForm(forms.Form):
    preferred_major = forms.ModelChoiceField(
        queryset=Major.objects.all(),
        label='Major'
    )
    
    admission = forms.ChoiceField(
        label='Admission',
        choices=[
            ('January', 'January'), ('February', 'February'), ('March', 'March'), ('April', 'April'),
            ('May', 'May'), ('June', 'June'), ('July', 'July'), ('August', 'August'),
            ('September', 'September'), ('October', 'October'), ('November', 'November'), ('December', 'December')
        ]
    )
    
    accommodation = forms.ChoiceField(
        label='Accommodation',
        choices=[('Yes', 'Yes'), ('No','No')]
    )
    
    qualification = forms.ChoiceField(
        label='Qualification', 
        choices=[('PreU', 'PreU'), ('Undergraduate','Undergraduate'), ('Postgraduate', 'Postgraduate')]
    )
    
    institution_type = forms.ChoiceField(
        label='Institution Type', 
        choices=[('Public', 'Public'), ('Private', 'Private')]
    )


VALID_INVITATION_CODES = ['admin2023']  # Replace with your actual codes

class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    is_admin = forms.BooleanField(required=False)
    invitation_code = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'is_admin', 'invitation_code')

    def clean(self):
        cleaned_data = super().clean()
        is_admin = cleaned_data.get("is_admin")
        invitation_code = cleaned_data.get("invitation_code")

        if is_admin and invitation_code not in VALID_INVITATION_CODES:
            self.add_error('invitation_code', 'Invalid invitation code for admin registration')