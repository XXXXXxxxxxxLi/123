import os
import subprocess
from django.http import FileResponse
from django.shortcuts import render
from .forms import ChapterForm
from jinja2 import Environment, FileSystemLoader

# 配置常量：模板目录
TEMPLATES_DIR = "app/templates"

# 章节内容定义
CHAPTERS_CONTENT = {
    "A": "这是章节A的具体内容。",
    "B": "这是章节B的具体内容。",
    "C": "这是章节C的具体内容。",
}


class LatexRenderer:
    def __init__(self, chapter_templates: dict, main_template):
        self.env = env
        self.chapter_templates = chapter_templates
        self.main_template = main_template

    def render_chapter(self, chapter, content):
        template = self.chapter_templates[chapter]
        return template.render(content=content)

    def compile(self, latex_code: str):
        base_name = "temp"
        tex_file = f"{base_name}.tex"
        with open(tex_file, "w") as f:
            f.write(latex_code)
        try:
            compile_command = [
                "xelatex",
                "-no-pdf",
                "-interaction",
                "nonstopmode",
                "-shell-escape",
                tex_file,
            ]
            # 需要编译 2 次
            subprocess.run(compile_command)
            compile_command.pop(compile_command.index("-no-pdf"))
            subprocess.run(compile_command)
        except Exception as e:
            return None
        # 删除临时文件
        for ext in ["aux", "log", "out", "tex"]:
            if os.path.exists(f"{base_name}.{ext}"):
                os.remove(f"{base_name}.{ext}")
        return f"{base_name}.pdf"

    def __call__(self, chapter_order, chapter_contents):
        tex_chapter_contents = "\n".join(
            self.render_chapter(chapter, content)
            for chapter, content in zip(chapter_order, chapter_contents)
        )
        pdf_file = self.compile(
            self.main_template.render(chapters=[tex_chapter_contents])
        )
        return pdf_file


# 初始化 Jinja 环境
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
chapter_templates = {
    c: env.get_template(f"chapter{c}.tex") for c in CHAPTERS_CONTENT.keys()
}
main_template = env.get_template("main_template.tex")
tex_renderer = LatexRenderer(chapter_templates, main_template)


# 主视图函数
def select_chapters(request):
    form = ChapterForm(request.POST or None)
    if form.is_valid():
        chapter_order = form.cleaned_data["order"]
        chapter_contents = {c: CHAPTERS_CONTENT[c] for c in chapter_order}
        pdf_file = tex_renderer(chapter_order, chapter_contents)
        if pdf_file:
            f = open(pdf_file, "rb")
            response = FileResponse(f)
            response["Content-Type"] = "application/pdf"
            response["Content-Disposition"] = f'attachment; filename="{pdf_file}"'
            return response
        else:
            return None
    else:
        return render(request, "select_chapters.html", {"form": form})
