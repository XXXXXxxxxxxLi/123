import os
import subprocess
from django.http import FileResponse
from django.shortcuts import render
from .forms import ChapterForm
from jinja2 import Environment, FileSystemLoader

# 配置常量：模板目录
TEMPLATES_DIR = "latex_app/templates"

# 章节内容定义
CHAPTERS_CONTENT = {
    "A": "这是章节A的具体内容。",
    "B": "这是章节B的具体内容。",
    "C": "这是章节C的具体内容。",
}


class LatexRenderer:
    def __init__(self, env, chapter_content):
        self.env = env
        self.chapter_content = chapter_content

    def render_latex_template(self, chapter):
        template = self.env.get_template(f"chapter{chapter}.tex")
        return template.render(content=self.chapter_content.get(chapter, ""))

    def compile_latex_to_pdf(self, latex_code):
        with open("temp.tex", "w") as f:
            f.write(latex_code)
        subprocess.run(
            ["xelatex", "-interaction", "nonstopmode", "-shell-escape", "temp.tex"]
        )
        # 删除临时文件
        for ext in ["aux", "log", "out", "tex"]:
            try:
                os.remove(f"temp.{ext}")
            except FileNotFoundError:
                pass
        with open("temp.pdf", "rb") as pdf:
            return FileResponse(pdf)


# 初始化Jinja环境
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
renderer = LatexRenderer(env, CHAPTERS_CONTENT)


# 主视图函数
def select_chapters(request):
    form = ChapterForm(request.POST or None)

    if form.is_valid():
        selected_chapters = form.cleaned_data["chapters"]
        order = form.cleaned_data.get("order", selected_chapters)
        latex_code = "".join(
            renderer.render_latex_template(chapter) for chapter in order
        )
        main_template = env.get_template("main_template.tex")
        final_latex_code = main_template.render(chapters=[latex_code])
        return renderer.compile_latex_to_pdf(final_latex_code)

    return render(request, "latex_app/select_chapters.html", {"form": form})
