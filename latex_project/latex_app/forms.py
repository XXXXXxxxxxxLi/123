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
    order = forms.CharField(
        max_length=50, required=False, help_text="使用逗号分隔章节标识，如：A,C,B 或 B,C,A"
    )

    def clean_order(self):
        data = [
            chapter.strip().upper() for chapter in self.cleaned_data["order"].split(",")
        ]
        valid_choices = [choice[0] for choice in CHAPTER_CHOICES]

        for char in data:
            if char not in valid_choices:
                raise forms.ValidationError(f"无效的章节标识：{char}")

        return data
