from django import forms
from .models import Picture, TongueFeature, Tagged_Data, Single_Physique
from django.forms import modelformset_factory




class PictureForm(forms.ModelForm):
    class Meta:
        model = Picture
        fields = ["path"]
        labels = {
            "path": "图片",
        }

    def __init__(self, *args, **kwargs):
        super(PictureForm, self).__init__(*args, **kwargs)
        self.fields["path"].widget.attrs.update({"multiple": "multiple"})


class TaggedDataForm(forms.ModelForm):
    tongue_color = forms.ModelChoiceField(
        queryset=TongueFeature.objects.filter(feature_type="TC"), label="舌色"
    )
    moss_color = forms.ModelChoiceField(
        queryset=TongueFeature.objects.filter(feature_type="MC"), label="苔色"
    )
    moss_quality = forms.ModelChoiceField(
        queryset=TongueFeature.objects.filter(feature_type="MQ"), label="苔质"
    )
    tongue_shape = forms.ModelMultipleChoiceField(
        queryset=TongueFeature.objects.filter(feature_type="TS"),
        label="舌形",
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    body_fluid = forms.ModelChoiceField(
        queryset=TongueFeature.objects.filter(feature_type="BF"), label="津液"
    )
    sublingual_collaterals = forms.ModelChoiceField(
        queryset=TongueFeature.objects.filter(feature_type="SC"), label="舌下络脉"
    )
    single_physique = forms.ModelMultipleChoiceField(
        queryset=Single_Physique.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="体质",
    )

    class Meta:
        model = Tagged_Data
        fields = [
            "tongue_color",
            "moss_color",
            "moss_quality",
            "tongue_shape",
            "body_fluid",
            "sublingual_collaterals",
            "single_physique",
        ]

    def clean(self):
        cleaned_data = super().clean()

        # 平和体质与其他体质互斥
        selected_physiques = cleaned_data.get("single_physique")
        if selected_physiques:
            physiques_ids = [p.id for p in selected_physiques]
            if 1 in physiques_ids and len(physiques_ids) > 1:
                raise forms.ValidationError("平和体质不能与其他体质同时选择")

        return cleaned_data

    def clean_single_physique(self):
        # 获取选择的体质数据
        single_physique_data = self.cleaned_data.get("single_physique")

        # 根据选择的体质数量来判断physique_type
        if len(single_physique_data) == 0:
            raise forms.ValidationError("您必须选择至少一个体质.")
        elif len(single_physique_data) > 6:
            raise forms.ValidationError("选择的体质数量过多.")

        return single_physique_data


# 用于多个图片上传的formset
PictureFormSet = modelformset_factory(Picture, form=PictureForm, extra=1)
