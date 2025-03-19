from django import forms
from .models import RecommendationInput

class RecommendationForm(forms.ModelForm):
    age = forms.IntegerField(
        required=True,
        error_messages={'required': '나이를 입력해주세요!'}
    )

    transport = forms.ChoiceField(
        choices=RecommendationInput.TRANSPORT_CHOICES,
        widget=forms.RadioSelect(),
        required=True,
        error_messages={'required': '주 이용 교통수단을 선택해주세요!'}
    )

    facility = forms.ChoiceField(
        choices=RecommendationInput.FACILITY_CHOICES,
        widget=forms.RadioSelect(),
        required=True,
        error_messages={'required': '주 이용 편의시설을 선택해주세요!'}
    )

    property_type = forms.ChoiceField(
        choices=RecommendationInput.PROPERTY_TYPE_CHOICES,
        widget=forms.RadioSelect(),
        required=True,
        error_messages={'required': '희망 매물 형태를 선택해주세요!'}
    )

    class Meta:
        model = RecommendationInput
        fields = ['age', 'transport', 'facility', 'property_type']