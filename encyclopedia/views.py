from django.shortcuts import render,redirect
from django.core.files.storage import default_storage
import markdown2
from . import util
import random
from django.db.models import Q
import re
from django.core.files.base import ContentFile


def convert_markdown_to_html(markdown_text):
    html = markdown2.markdown(markdown_text)
    return html

def convert_markdown_to_html(markdown_text):
    # Convert headings
    markdown_text = re.sub(r'^(#{1,6})\s*(.*?)$', r'<h\1>\2</h\1>', markdown_text, flags=re.M)
    # Convert bold text
    markdown_text = re.sub(r'__(.*?)__', r'<strong>\1</strong>', markdown_text)
    # Convert unordered lists
    markdown_text = re.sub(r'^\s*(-\s.*?)$', r'<li>\1</li>', markdown_text, flags=re.M)
    # Join list items
    markdown_text = re.sub(r'<li>(.*?)</li>\s*(?=<li>)', r'<ul><li>\1</li>', markdown_text)
    markdown_text = re.sub(r'</li>\s*</ul>', r'</li></ul>', markdown_text)
    # Convert links
    markdown_text = re.sub(r'$ (.*?) $$ (.*?) $', r'<a href="\2">\1</a>', markdown_text)
    # Convert paragraphs
    markdown_text = re.sub(r'^(.*?)$', r'<p>\1</p>', markdown_text, flags=re.M)

    return markdown_text

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def get_entry(request,entry):
    entry_content = util.get_entry(entry)
    
    # 如果条目存在，将其转换为 HTML
    if entry_content:
        entry_html = convert_markdown_to_html(entry_content)
        return render(request, 'encyclopedia/get_entry.html', {
            'entry_title': entry.replace('_', ' ').title(),
            'entry_content': entry_html,
        })
    else:
        # 如果条目不存在，返回 404 错误
        return render(request, 'encyclopedia/404.html', status=404)

def search(request):
    query = request.GET.get('q', '').strip()
    if query:
        entry_content = util.get_entry(query)
    
        # 如果条目存在，将其转换为 HTML
        if entry_content:
            return redirect('get_entry  ', entry=query)
        else:
            # 如果条目不存在，返回 404 错误
            return render(request, 'encyclopedia/404.html', status=404)
    else:
        # If the query is empty, redirect to the index page
        return redirect('index')
    
def random_page(request):
    # 获取所有条目的列表
    entries = util.list_entries()
    # 如果列表不为空，随机选择一个条目
    if entries:
        random_entry = random.choice(entries)
        # 确保随机选择的条目存在
        if util.get_entry(random_entry):
            return redirect('get_entry', entry=random_entry)
    # 如果没有条目或者随机选择的条目不存在，重定向到首页
    return redirect('index')



def new_page(request):
    if request.method == 'POST':
        title = request.POST.get('title').strip()
        content = request.POST.get('content')
        # Check if an entry with the same title already exists
        if util.get_entry(title):
            return render(request, 'encyclopedia/new_page.html', {
                'error': f'An entry with the title "{title}" already exists.',
                'title': title,
                'content': content,
            })
        # Save the new entry
        util.save_entry(title, content)
        # Redirect to the new entry's page
        return redirect('get_entry', entry=title)
    else:
        # Display the new page form
        return render(request, 'encyclopedia/new_page.html')

def edit_page(request, entry):
    if request.method == 'POST':
        # Get the updated content from the form
        content = request.POST.get('content')
        # Save the updated entry
        util.save_entry(entry, content)
        # Redirect to the updated entry's page
        return redirect('get_entry', entry=entry)
    else:
        # Retrieve the existing entry content
        content = util.get_entry(entry)
        # Display the edit page form
        return render(request, 'encyclopedia/edit_page.html', {
            'entry': entry,
            'content': content,
        })