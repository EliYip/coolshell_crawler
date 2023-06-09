import os
from datetime import datetime
from bs4 import BeautifulSoup
import html2text


def main() -> None:
    html_directory = os.path.join(os.getcwd(), 'articles')
    output_directory = os.path.join(os.getcwd(), 'markdowns')

    if not os.path.exists(output_directory):
        os.mkdir(output_directory)

    for html_file in os.listdir(html_directory):
        if html_file.endswith('.html'):
            html_file_path = os.path.join(html_directory, html_file)
            print(f'正在处理文件：{html_file_path}')
            extract_content(html_file_path, output_directory)
            print(f'处理完成：{html_file_path}')


def remove_elements_by_text(soup, text_list, level=1):
    for text in text_list:
        element = soup.find(lambda tag: tag.text.strip() == text)
        if element:
            for _ in range(level):
                if element.parent:
                    element = element.parent
            element.decompose()


def remove_element(soup, tag, attr_dict):
    element = soup.find(tag, attrs=attr_dict)
    if element:
        element.decompose()


def extract_content(html_file, output_directory):
    # 获取文件名
    filename = os.path.splitext(os.path.basename(html_file))[0]

    # 打开并解析HTML文件
    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # 根据文件名寻找文章内容
    article = soup.find('article', {'id': filename})

    entry_meta_tag = article.find('div', {'class': 'entry-meta'})
    if entry_meta_tag is not None:
        time_tag = entry_meta_tag.find('time', {'class': 'entry-date'})
        if time_tag is not None:
            # 使用strip()方法删除字符串两端的空格
            time_info = time_tag.text.strip()
        # 删除该元素
        entry_meta_tag.decompose()
    # 将时间信息转化为日期对象
    date = datetime.strptime(time_info, '%Y年%m月%d日')
    # 将日期对象格式化为你想要的格式
    formatted_date = date.strftime('%Y-%m-%d')

    # 删除指定的元素
    elements_to_remove = [
        {'class': 'entry-meta'},
        {'class': 'related_post_title'},
        {'id': 'related_posts'},
        {'class': 'post-navigation'},
        {'class': 'post-comments'},
        {'id': 'secondary'},
        {'class': 'row site-info'},
        {'class': 'post-ratings-loading'},
        {'class': 'entry-footer'},
        {'class': 'post-ratings'},
        {'class': 'screen-reader-text'},
    ]

    for element in elements_to_remove:
        tag = article.find('div', element) or article.find(
            'h3', element) or article.find('footer', element)
        if tag is not None:
            tag.decompose()

    remove_element(article, 'ul', {'class': 'related_post wp_rp'})
    remove_element(article, 'span', {'class': 'screen-reader-text'})

    # 删除特定文本的元素
    text_list = [
        "关注CoolShell微信公众账号和微信小程序",
        "转载本站文章请注明作者和出处",
    ]
    remove_elements_by_text(article, text_list)

    text_list = ["酷壳404页面"]
    remove_elements_by_text(article, text_list, level=3)

    # 将HTML内容转换为Markdown
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.body_width = 0  # 设置一个更大的宽度限制
    markdown_content = h.handle(str(article))

    time_info_to_add = '\n> ' + time_info
    markdown_lines = markdown_content.split('\n')
    markdown_lines.insert(1, time_info_to_add)
    markdown_content = '\n'.join(markdown_lines)

    markdown_lines = markdown_content.split('\n')

    if len(markdown_lines) >= 2:
        markdown_content = '\n'.join(markdown_lines[:-2])

    markdown_content += "\n---\n"

    # 将Markdown内容写入新的.md文件
    output_file_path = os.path.join(
        output_directory, f'{formatted_date}-{filename}.md')
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(markdown_content)


if __name__ == '__main__':
    main()
