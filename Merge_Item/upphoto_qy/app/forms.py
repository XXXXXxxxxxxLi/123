from django import forms
from .models import WhirMedicine
from .models import Picture, TongueFeature, Tagged_Data, Physique
from django.forms import modelformset_factory


class UploadImagesForm(forms.Form):
    brand = forms.CharField(label="请输入企业名称：", max_length=255)
    xlsx_file = forms.FileField(
        label="请选择一个xlsx文件：",
        required=True,
        widget=forms.ClearableFileInput(attrs={"accept": ".xlsx"}),
    )
    images = forms.FileField(label="请选择一些图片：", required=True)

    def __init__(self, *args, **kwargs):
        super(UploadImagesForm, self).__init__(*args, **kwargs)
        self.fields["images"].widget.attrs.update(
            {"accept": "image/*", "multiple": "multiple"}
        )


class ImageUploadForm(forms.Form):
    images = forms.ImageField(required=False)

    def __init__(self, *args, **kwargs):
        super(ImageUploadForm, self).__init__(*args, **kwargs)
        self.fields["images"].widget.attrs.update({"multiple": "multiple"})


class MedicineUpdateForm(forms.ModelForm):
    class Meta:
        model = WhirMedicine
        fields = ["name", "img", "effect", "indication", "symptom"]


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
    tongue_types = ["TC", "MC", "MQ", "TS", "BF", "SC"]
    features = TongueFeature.objects.filter(feature_type__in=tongue_types)

    tongue_color = forms.ModelChoiceField(
        queryset=features.filter(feature_type="TC"), label="舌色"
    )
    moss_color = forms.ModelChoiceField(
        queryset=features.filter(feature_type="MC"), label="苔色"
    )
    moss_quality = forms.ModelChoiceField(
        queryset=features.filter(feature_type="MQ"), label="苔质"
    )
    tongue_shape = forms.ModelMultipleChoiceField(
        queryset=features.filter(feature_type="TS"),
        label="舌形",
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    body_fluid = forms.ModelChoiceField(
        queryset=features.filter(feature_type="BF"), label="津液"
    )
    sublingual_collaterals = forms.ModelChoiceField(
        queryset=features.filter(feature_type="SC"), label="舌下络脉"
    )
    physique = forms.ModelMultipleChoiceField(
        queryset=Physique.objects.filter(physique_type="SINGLE"),
        label="体质",
        widget=forms.CheckboxSelectMultiple,
        required=True,
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
            "physique",
        ]

    def clean(self):
        cleaned_data = super().clean()

        # 舌形的检查
        selected_tongue_shapes = cleaned_data.get("tongue_shape")
        if selected_tongue_shapes:
            tongue_shapes_ids = [ts.id for ts in selected_tongue_shapes]

            # 胖和瘦互斥
            if 20 in tongue_shapes_ids and 21 in tongue_shapes_ids:
                raise forms.ValidationError("舌形中，胖和瘦互斥")

            # 老和嫩互斥
            if 22 in tongue_shapes_ids and 23 in tongue_shapes_ids:
                raise forms.ValidationError("舌形中，老和嫩互斥")

        # 体质的检查
        selected_physiques = cleaned_data.get("physique")
        if selected_physiques:
            physiques_ids = [p.id for p in selected_physiques]

            # 阳虚和实热互斥
            if 5 in physiques_ids and 9 in physiques_ids:
                raise forms.ValidationError("体质中，阳虚和实热互斥")

            # 阴虚和痰湿互斥
            if 6 in physiques_ids and 7 in physiques_ids:
                raise forms.ValidationError("体质中，阴虚和痰湿互斥")

            # 气虚和气郁互斥
            if 3 in physiques_ids and 2 in physiques_ids:
                raise forms.ValidationError("体质中，气虚和气郁互斥")

            # 阳虚和阴虚互斥
            if 5 in physiques_ids and 6 in physiques_ids:
                raise forms.ValidationError("体质中，阳虚和阴虚互斥")

            # 平和体质与其他体质互斥
            if 1 in physiques_ids and len(physiques_ids) > 1:
                raise forms.ValidationError("平和体质不能与其他体质同时选择")

        return cleaned_data

    def clean_physique(self):
        # 获取选择的体质数据
        physique_data = self.cleaned_data.get("physique")

        # 根据选择的体质数量来判断physique_type
        if len(physique_data) == 0:
            raise forms.ValidationError("您必须选择至少一个体质.")
        elif len(physique_data) > 6:
            raise forms.ValidationError("选择的体质数量过多.")

        return physique_data


# 用于多个图片上传的formset
PictureFormSet = modelformset_factory(Picture, form=PictureForm, extra=1)

from django import forms

# 定义章节选项
CHAPTER_CHOICES = [
    ("A", "章节 A"),
    ("B", "章节 B"),
    ("C", "章节 C"),
]


class ChapterForm(forms.Form):
    chapters = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=CHAPTER_CHOICES,
    )
    # 用户可选地为章节指定顺序
    order_sep = ";"
    order = forms.CharField(max_length=64, required=False, help_text="如：A;C;B 或 B;C;A")

    def clean_order(self):
        # 将输入的章节顺序转为大写，确保与CHAPTER_CHOICES中的键匹配
        data = self.cleaned_data["order"].upper().split(self.order_sep)
        for char in data:
            # 如果输入的章节标识不在预定义的选项中，抛出验证错误
            if char not in dict(CHAPTER_CHOICES):
                raise forms.ValidationError(f"无效的章节标识：{char}")

        return data
