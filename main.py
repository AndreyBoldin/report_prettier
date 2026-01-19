import base64
import streamlit as st
import re
import markdown
from datetime import datetime
from io import BytesIO
from weasyprint import HTML
import tempfile
import os

# icon star
st.set_page_config(page_title="Report_Prettier", page_icon="🌟", layout="wide")
st.markdown("""
    <style>
    .block-container {
        padding-top: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
        padding-bottom: 2rem;
    }
    .stMarkdown p {
        color: #333333;
        font-family: 'Helvetica', 'Arial', sans-serif;
        text-align: justify;
        text-align-last: left;
    }
    
    img {
            display: block !important;
            margin-left: auto !important;
            margin-right: auto !important;
            
        }
    
    .stMarkdown li {
        color: #333333;
        font-family: 'Helvetica', 'Arial', sans-serif;
    }
    
    .stMardown table nth-child(even) {
        background-color: #f2f2f2;
    }
    
    
    /* Стили для футера в предпросмотре */
    .footer-container {
        position: relative;
        margin-top: 50px;
        padding-top: 20px;
        border-top: 2px solid #297fb9;
        page-break-after: always;
    }
    
    .footer-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .footer-logo {
        display: flex;
        align-items: center;
    }
    
    .footer-logo img {
        height: 50px;
        margin-right: 10px;
    }
    
    .footer-logo-text {
        font-size: 16px;
        font-weight: bold;
        color: #297fb9;
        font-family: 'Helvetica', 'Arial', sans-serif;
    }
    
    .footer-info {
        text-align: right;
        font-family: 'Helvetica', 'Arial', sans-serif;
        color: #666;
    }
    
    .footer-date {
        font-size: 14px;
        margin-bottom: 5px;
    }
    
    .footer-page {
        font-size: 14px;
        font-style: italic;
    }
    
    /* Стиль для обрыва страницы */
    .page-break {
        page-break-after: always;
        height: 0;
        margin: 0;
        padding: 0;
    }
    </style>
    """, unsafe_allow_html=True)

legend= """<p style="color: #333333; font-weight: bold;">Легенда (мини-словарь):</p>
    
                                <table class="legend-table">
                                    <thead>
                                        <tr>
                                            <th>Термин</th>
                                            <th>Описание</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td><strong>z-score</strong></td>
                                            <td>
                                                <span class="math-notation">|z| &lt; 1</span> — в коридоре; 
                                                <span class="math-notation">1 ≤ |z| &lt; 2</span> — смещение; 
                                                <span class="math-notation">|z| ≥ 2</span> — выраженное ограничение 
                                                <em>(для навигации в динамике)</em>
                                            </td>
                                        </tr>
                                        
                                        <tr>
                                            <td><strong>Паттерн<br>(EM/IS/AA и т.д.)</strong></td>
                                            <td>
                                                Это устойчивое сочетание метаболитов/соотношений, образующее метаболический профиль и получающее статус: 
                                                <span class="highlight">лимитирующий</span> / 
                                                <span class="highlight">потенциально лимитирующий</span> / 
                                                <span class="highlight">контекстный</span>
                                            </td>
                                        </tr>
                                        
                                        <tr>
                                            <td><strong>Лимитирующий</strong></td>
                                            <td>Чаще всего ограничивает переносимость нагрузок/восстановление в текущий момент</td>
                                        </tr>
                                        
                                        <tr>
                                            <td><strong>Функциональные режимы (FR)</strong></td>
                                            <td>
                                                Это интегральные «сценарии работы» ключевых регуляторно-метаболических паттернов 
                                                (детокси-редокс, адаптация/стресс, энергетика, восстановление, иммунно-воспалительный и др.). 
                                                FR показывает какой контур сейчас реально задаёт переносимость нагрузки и восстановление, 
                                                чаще через регуляторные механизмы, а не «организму поломку».
                                            </td>
                                        </tr>
                                        
                                        <tr>
                                            <td><strong>FR "активен"</strong></td>
                                            <td>Когда присутствуют его паттерны-драйверы</td>
                                        </tr>
                                        
                                        <tr>
                                            <td><strong>FR "ведущий/лимитирующий"</strong></td>
                                            <td>Когда в ядре есть лимитирующий паттерн и именно он определяет управляемость траектории</td>
                                        </tr>
                                        
                                        <tr>
                                            <td><strong>Каждый активный FR читается как связка</strong></td>
                                            <td>
                                                <strong>(1)</strong> Что означает функционально → 
                                                <strong>(2)</strong> Какими паттернами сформирован → 
                                                <strong>(3)</strong> Что уместно клинически проверить → 
                                                <strong>(4)</strong> Навигационный рычаг наблюдения на 2–6 недель.
                                            </td>
                                        </tr>
                                        
                                        <tr>
                                            <td><strong>Управляемость траектории</strong><br>(высокая/сохранённая/ограниченная/напряжённая)</td>
                                            <td>Насколько предсказуемо профиль отвечает на изменение режима за 4–6 недель (цель — двигать к 0)</td>
                                        </tr>
                                        
                                        <tr>
                                            <td><strong>Цель динамики</strong></td>
                                            <td>
                                                Вести ключевые маркеры и соотношения к <span class="math-notation">z=0</span> 
                                                и подтверждать выводы клиническими данными; 
                                                <em style="color:#d84040 !important">отчёт не является диагнозом</em>
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>"""
                        

if 'editor_content' not in st.session_state: 
    st.session_state.editor_content = "# Пример Markdown\n\n## **0. Общая информация**\n\n## **1. Основные данные**\n\n## **2. Результаты анализа**\n\n### **Подзаголовок**\n\n### Это заголовок уровня 3\n\nВозможности Markdown:\n1. **Жирный** и *курсивный* текст\n2. Нумерованные списки\n3. Маркированные пункты\n   - Элемент А\n   - Элемент Б\n\n### Пример HTML:\n<button style='background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: p#333333nter;'>Нажми меня!</button>\n\n### Пример таблицы:\n| Столбец 1 | Столбец 2 | Столбец 3 |\n|-----------|-----------|-----------|\n| Строка 1, Колонка 1 | Строка 1, Колонка 2 | Строка 1, Колонка 3 |\n| Строка 2, Колонка 1 | Строка 2, Колонка 2 | Строка 2, Колонка 3 |\n\n> Это блок цитаты.\n\n---"

# Преобразуйте картинку в Base64
def image_path_to_base64(image_path):
    # уменьшить размер картинки и преобразовать в Base64
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return f"data:image/png;base64,{encoded_string}"

# Получите Base64 строку
logo_base64 = image_path_to_base64("logo.jpg")

if "header" not in st.session_state:
    st.session_state.header = "ОТЧЕТ МЕТАБОСКАН - ТОЛЬКО ДЛЯ ВРАЧА"
    
if "legend" not in st.session_state:
    st.session_state.legend = ""

if "show_legend" not in st.session_state:
    st.session_state.show_legend = False

with st.sidebar:
    st.write("**Изменения заголовка:**")
    st.caption("Ввести в поле ниже")
    # Используем session_state напрямую и обновляем его
    new_header = st.text_input(
        "Заголовок", 
        value=st.session_state.header, 
        label_visibility="collapsed"
    )
    
    # Radio add legend that session state = legend, if no than == ""
    legend_option = st.radio(
        "Добавить легенду?",
        ["Без легенды", "С легендой"],
        index=1 if st.session_state.show_legend else 0,
        horizontal=True,
        label_visibility="collapsed"
    )
    # Обновляем session_state в зависимости от выбора
    if legend_option == "С легендой":
        st.session_state.show_legend = True
        st.session_state.legend = legend
    else:
        st.session_state.show_legend = False
        st.session_state.legend = ""
        
    # Обновляем session_state при изменении
    if new_header != st.session_state.header:
        st.session_state.header = new_header
        
    st.write("**Справочник:**")
    st.write("Картинка:")
    st.code("![любое_название](data:image/...)", language="markdown")
    st.caption("Можно получить через онлайн конвертер: https://www.base64-image.de/")

    st.write("Перенос страницы:")
    st.code("""<div style="page-break-after: always"></div>""", language="html")
    st.write("Перенос строки:")
    st.code("""<br>""", language="html")
    st.write("Математические формулы:")
    st.code("""log<sub>n</sub>10 = 2; E = mc<sup>2</sup>""", language="html")
    st.write("Синий заголовок ##:")
    st.code("""## **Текст заголовка**""", language="markdown")
    
    st.write("Голубой заголовок ###:")
    st.code("""### **Текст заголовка**""", language="markdown")
    
    st.write("Таблица")
    st.code("""| Столбец 1 | Столбец 2 | Столбец 3 |
|-----------|-----------|-----------|
| Строка 1, Колонка 1 | Строка 1, Колонка 2 | Строка 1, Колонка 3 |
| Строка 2, Колонка 1 | Строка 2, Колонка 2 | Строка 2, Колонка 3 |""", language="markdown")
    

col1, col2 = st.columns([1, 1.414]) 

with col1:
    with st.container():
        html_content = """
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h3>Редактор</h3>
            <div></div>
        </div>
        """
        st.markdown(html_content, unsafe_allow_html=True)
        

    editor_content = st.text_area("Текст для редактирования:", value=st.session_state.editor_content, height=450, key="editor", label_visibility="collapsed")

with col2:
    st.subheader("Предпросмотр")
    
    preview_container = st.container(border=True)
    word_count = len(editor_content.split())
    char_count = len(editor_content)
    st.caption(f"📊 Статистика: {word_count} слов, {char_count} символов")
    
    with preview_container:
        try:
            def fix_trailing_spaces(text):
                """
                Удаляет пробелы перед точкой в конце строк
                """
                fixed_text = re.sub(r'\s*\.(\n|$)', r'.\1', text)
                return fixed_text

            # Process the content to wrap ## **text** patterns with blue background
            def highlight_h2_h3(text):
                pattern_h3 = r'(^|\n)###\s+\*\*(.+?)\*\*'
                pattern_h2 = r'(^|\n)##\s+\*\*(.+?)\*\*'
                
                def replace_match_h2(match):
                    full_match = match.group(2).strip()
                    return f'<div style = "background-color: #297fb9; padding: 1px 10px; border-radius: 3px; margin: 10px 0;"><span style = "font-size: 16px;font-family: Helvetica, Arial, sans-serif; font-weight: bold; color: white;">{full_match}</span></div>'
                
                def replace_match_h3(match):
                    full_match = match.group(2).strip()
                    return f'<div style = "background-color: #deeaf6; padding: 1px 10px; border-radius: 3px; margin: 10px 0;"><span style = "font-size: 14px; font-family: Helvetica, Arial, sans-serif; font-weight: bold; color: #193654;">{full_match}</span></div>'
                
                processed_text = re.sub(pattern_h3, replace_match_h3, text)
                processed_text = re.sub(pattern_h2, replace_match_h2, processed_text)
                return processed_text
            

            def markdown_to_html_with_styles(text):
                """
                Преобразует Markdown в HTML с сохранением специальных стилей
                """
                # Сначала заменяем специальные заголовки с фоном
                processed_text = highlight_h2_h3(fix_trailing_spaces(text))
                
                # Разделяем текст на блоки: стилизованные заголовки и остальное
                lines = processed_text.split('\n')
                processed_blocks = []
                current_block = []
                
                for line in lines:
                    # Проверяем, является ли строка стилизованным заголовком
                    if '<div style=' in line and ('background-color: #297fb9' in line or 'background-color: #deeaf6' in line):
                        # Если есть накопленный блок, обрабатываем его
                        if current_block:
                            processed_blocks.append('\n'.join(current_block))
                            current_block = []
                        # Стилизованный заголовок добавляем как отдельный блок
                        processed_blocks.append(line)
                    else:
                        current_block.append(line)
                
                # Добавляем последний блок, если он есть
                if current_block:
                    processed_blocks.append('\n'.join(current_block))
                
                # Обрабатываем каждый блок
                result_blocks = []
                extensions = [
                    'markdown.extensions.extra',
                    'markdown.extensions.tables',
                    'markdown.extensions.nl2br',
                    'markdown.extensions.sane_lists',
                    'markdown.extensions.toc',
                ]
                
                for block in processed_blocks:
                    # Если блок - это стилизованный заголовок, оставляем как есть
                    if block.strip().startswith('<div style='):
                        result_blocks.append(block)
                    else:
                        # Преобразуем Markdown блок целиком
                        html_block = markdown.markdown(block, extensions=extensions)
                        result_blocks.append(html_block)
                
                # Объединяем все блоки
                full_html = '\n'.join(result_blocks)
                
                return full_html
            # Преобразуем контент для предпросмотра
            processed_content = markdown_to_html_with_styles(editor_content)
            
            # Apply the processed content
            st.markdown(processed_content, unsafe_allow_html=True)
            
            # Добавляем футер с логотипом и информацией
            month_names = {
                1: "января", 2: "февраля", 3: "марта", 4: "апреля",
                5: "мая", 6: "июня", 7: "июля", 8: "августа",
                9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
            }

            now = datetime.now()
            current_date = f"{now.day} {month_names[now.month]} {now.year}"
            
            
            # Кнопка скачать файлы
            st.markdown("---")
            col_filename, col_button = st.columns([2, 1])
            
            with col_filename:
                file_name = st.text_input("Название файла:", value="Метабоскан_отчет", label_visibility="collapsed")
            
            with col_button:
                col_html, col_pdf = st.columns(2)
                
                with col_html:
                    if st.button("📥 HTML", use_container_width=True):
                     
                        html_doc = f"""
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <meta charset="UTF-8">
                            <meta name="viewport" content="width=device-width, initial-scale=1.0">
                            <title>Report</title>
                            <style>
                                body {{
                                    font-family: 'Helvetica', 'Arial', sans-serif;
                                    color: #333333;
                                    line-height: 1.6;
                                    margin: 40px auto 15px auto;
                                    max-width: 800px;
                                    padding: 20px;
                                    background-color: #ffffff;
                                }}
                                .h2-styled {{
                                    background-color: #297fb9 !important;
                                    padding: 8px 12px !important;
                                    border-radius: 3px !important;
                                    margin: 20px 0 10px 0 !important;
                                    color: white !important;
                                    font-size: 18px !important;
                                    font-weight: bold !important;
                                    font-family: 'Helvetica', 'Arial', sans-serif !important;
                                }}
                                .h3-styled {{
                                    background-color: #deeaf6 !important;
                                    padding: 6px 10px !important;
                                    border-radius: 3px !important;
                                    margin: 15px 0 8px 0 !important;
                                    color: #193654 !important;
                                    font-size: 16px !important;
                                    font-weight: bold !important;
                                    font-family: 'Helvetica', 'Arial', sans-serif !important;
                                }}
                                p {{
                                    text-align: justify !important;
                                    text-align-last: left !important;
                                    margin-bottom: 10px !important;
                                    font-family: 'Helvetica', 'Arial', sans-serif !important;
                                    color: #333333 !important;
                                }}
                                table {{
                                    border-collapse: collapse !important;
                                    width: 100% !important;
                                    margin: 15px 0 !important;
                                    font-family: 'Helvetica', 'Arial', sans-serif !important;
                                }}
                                th, td {{
                                    border: 1px solid #ddd !important;
                                    padding: 6px !important;
                                    text-align: left !important;
                                }}
                                th {{
                                    background-color: #f2f2f2 !important;
                                    font-weight: bold !important;
                                }}
                                strong, b {{
                                    font-weight: bold !important;
                                }}
                                
                                .page-break {{
                                    page-break-after: always;
                                    height: 0;
                                    margin: 0;
                                    padding: 0;
                                }}
                            </style>
                        </head>
                        <body>
                            <div class="content">
                                {processed_content}
                            </div>
                        </body>
                        </html>
                        """
                        
                        # Кодируем для скачивания
                        b64 = base64.b64encode(html_doc.encode()).decode()
                        href = f'data:text/html;base64,{b64}'
                        
                        st.markdown(f'''
                            <a href="{href}" download="{file_name}.html" style="
                                display: inline-block;
                                background-color: #4CAF50;
                                color: white;
                                padding: 10px 20px;
                                text-decoration: none;
                                border-radius: 4px;
                                font-weight: bold;
                                text-align: center;">
                                Скачать
                            </a>
                        ''', unsafe_allow_html=True)
                
                with col_pdf:
                    if st.button("📄 PDF", use_container_width=True):
                        
                            
                        # Функция для создания PDF с header и footer
                        def create_pdf_with_header_footer(content, legend):
                            # Создаем временный HTML файл
                            temp_html = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8')
                            
                            # Полный HTML с header, footer и контентом
                            full_html_content = f"""
                            <!DOCTYPE html>
                            <html>
                            <head>
                                <meta charset="UTF-8">
                                <title>Метабоскан отчет</title>
                                <style>
                                    @page {{
                                        size: A4;
                                        margin: 2.3cm 1cm 2cm 1.5cm;
                                        
                                        @top-left {{
                                            /* Логотип как фон с маленьким размером */
                                            background-image: url("{logo_base64}");
                                            background-repeat: no-repeat;
                                            background-size: 160px 47px; /* width height - маленький размер */
                                            background-position: left center;
                                            width: 160px; /* Ширина области */
                                            height: 80px; /* Высота области */
                                            
                                            content: ""; /* Пустое содержимое, только фон */
                                        }}
                                        
                                        @top-right {{
                                            /* Заголовок справа */
                                            content: "{st.session_state.header}";
                                            font-family: 'Helvetica', 'Arial', sans-serif;
                                            font-size: 10pt;
                                            font-weight: bold;
                                            color: #297fb9;
                                            padding: 0px 20px 0px 40px;
                                            border-radius: 2px;
                                            height: 80px;
                                            vertical-align: middle !important; /* Выравнивание по вертикали */
                                            display: inline-block !important;
                                            
                                        }}
                                        
                                        
                                        @bottom-right {{
                                            content: "{current_date}";
                                            font-family: 'Helvetica', 'Arial', sans-serif;
                                            font-size: 9pt;
                                            font-weight: bold;
                                            color: #666;
                                        }}
                                        
                                        @bottom-center {{
                                            content: "Страница " counter(page) " из " counter(pages);
                                            font-family: 'Helvetica', 'Arial', sans-serif;
                                            font-size: 9pt;
                                            color: #666;
                                        }}
                                        
                                    }}
                                    
                                    body {{
                                        font-family: 'Helvetica', 'Arial', sans-serif;
                                        color: #333333;
                                        line-height: 1.5;
                                        margin: 0;
                                        
                                        padding: 0;
                                    }}
                                    
                                    
                                    
                                    
                                    
                                    /* Логотип в верхнем левом углу */
                                    .logo-container {{
                                        position: fixed;
                                        top: 0px;
                                        left: 0px;
                                        width: 160px;
                                        height: auto;
                                        z-index: 10;
                                    }}
                                    
                                    .logo-container img {{
                                        width: 100%;
                                        height: auto;
                                        max-width: 100%;
                                        max-height: 150px;
                                        object-fit: contain;
                                    }}
                                    
                                    .h2-styled {{
                                        background-color: #297fb9 !important;
                                        padding: 8px 12px !important;
                                        border-radius: 5px !important;
                                        margin: 20px 0 10px 0 !important;
                                        color: white !important;
                                        font-size: 18px !important;
                                        font-weight: bold !important;
                                        font-family: 'Helvetica', 'Arial', sans-serif !important;
                                        page-break-after: av#333333d;
                                    }}
                                    
                                    .h3-styled {{
                                        background-color: #deeaf6 !important;
                                        padding: 6px 10px !important;
                                        border-radius: 5px !important;
                                        margin: 15px 0 8px 0 !important;
                                        color: #193654 !important;
                                        font-size: 16px !important;
                                        font-weight: bold !important;
                                        font-family: 'Helvetica', 'Arial', sans-serif !important;
                                        page-break-after: av#333333d;
                                    }}
                                    
                                    p {{
                                        text-align: justify !important;
                                        text-align-last: left !important;
                                        margin: 0px !important;
                                        font-family: 'Helvetica', 'Arial', sans-serif !important;
                                        color: #333333 !important;
                                        font-size: 11pt;
                                    }}
                                    
                                    li {{
                                        font-family: 'Helvetica', 'Arial', sans-serif !important;
                                        color: #333333 !important;
                                        margin-bottom: 5px !important;
                                        font-size: 11pt;
                                    }}
                                    
                                    ul, ol {{
                                        margin-bottom: 15px !important;
                                        margin-left: 20px !important;
                                    }}
                                    
                                    
                                    table {{
                                        border-collapse: collapse !important;
                                        width: 100% !important;
                                        margin: 15px 0 !important;
                                        font-family: 'Helvetica', 'Arial', sans-serif !important;
                                        font-size: 10pt;
                                        page-break-inside: av#333333d;
                                    }}
                                    
                                    table tr:nth-child(even) {{
                                        background-color: #f2f2f2 !important;
                                    }}
                                    
                                    th, td {{
                                        border: 1px solid #ddd !important;
                                        padding: 8px !important;
                                        text-align: left !important;
                                    }}
                                    
                                    th {{
                                        background-color: #f2f2f2 !important;
                                        font-weight: bold !important;
                                    }}
                                    
                                    img {{
                                        display: block !important;
                                        margin-left: auto !important;
                                        margin-right: auto !important;
                                        
                                    }}
                                    
                                    strong, b {{
                                        font-weight: bold !important;
                                    }}
                                    
                                    em, i {{
                                        font-style: italic !important;
                                    }}
                                    
                                    hr {{
                                        border: none !important;
                                        border-top: 1px solid #ddd !important;
                                        margin: 20px 0 !important;
                                    }}
                                    
                                    .page-break {{
                                        page-break-after: always;
                                    }}
                                    
                                    .header-space {{
                                        height: 60px;
                                    }}
                                    
                                    .footer-space {{
                                        height: 30px;
                                    }}
                                    
                                    .av#333333d-page-break {{
                                        page-break-inside: av#333333d;
                                    }}
                                    .title-container {{
                                        position: fixed;
                                        top: 0px;
                                        right: 0px;
                                        z-index: 10;
                                        text-align: right;
                                        width: auto;
                                    }}

                                    .title-styled {{
                                        font-family: 'Helvetica', 'Arial', sans-serif !important;
                                        color: white !important;
                                        font-size: 15px !important;
                                        font-weight: bold !important;
                                        padding: 6px 12px 6px 40px!important;
                                        text-align: right !important;
                                        display: inline-block !important;
                                        background-color: #297fb9 !important;
                                        white-space: nowrap; /* Предотвращает перенос текста */
                                    }}
                                    
                                    .legend-table {{
                                        width: 100%;
                                        border-collapse: collapse;
                                        margin-top: 15px;
                                        font-size: 14px;
                                    }}
                                    
                                    .legend-table th {{
                                        background-color: #f5f5f5;
                                        color: black;
                                        font-weight: bold;
                                        text-align: left;
                                        padding: 8px 20px;
                                        border: 1px solid #dadada !important;
                                        font-size: 13px;
                                    }}
                                    
                                    .legend-table td {{
                                        padding: 10px 15px;
                                        border: 1px solid #dadada !important;
                                        vertical-align: top;
                                        line-height: 1.4;
                                        color: #333333;
                                    }}
                                    .math-notation {{
                                        font-style: bold;
                                        font-family: 'Times New Roman', serif;
                                    }}
                                    
                                    
                                    
                                    .section-title {{
                                        color: #0066cc;
                                        font-weight: bold;
                                        margin-top: 15px;
                                        margin-bottom: 5px;
                                    }}
                                    
                                    .note {{
                                        font-size: 12px;
                                        color: #666;
                                        font-style: italic;
                                        margin-top: 15px;
                                        padding: 10px;
                                        background-color: #f9f9f9;
                                        border-left: 4px solid #ffa500;
                                    }}
                                </style>
                            </head>
                            <body>
                                
                                {legend}
                                <div class="content">
                                    {content}
                                </div>
                                
                            </body>
                            </html>
                            """
                            
                            temp_html.write(full_html_content)
                            temp_html.close()
                            
                            try:
                                # Конвертируем HTML в PDF с помощью WeasyPrint
                                pdf_file = BytesIO()
                                HTML(filename=temp_html.name).write_pdf(pdf_file)
                                
                                # Удаляем временный файл
                                os.unlink(temp_html.name)
                                
                                return pdf_file.getvalue()
                            
                            except Exception as e:
                                st.error(f"Ошибка при создании PDF: {str(e)}")

                    
                        # Создаем PDF
                        pdf_bytes = create_pdf_with_header_footer(processed_content, legend=st.session_state.legend)
                        
                        # Кодируем для скачивания
                        b64_pdf = base64.b64encode(pdf_bytes).decode()
                        href_pdf = f'data:application/pdf;base64,{b64_pdf}'
                        
                        st.markdown(f'''
                            <a href="{href_pdf}" download="{file_name}.pdf" style="
                                display: inline-block;
                                background-color: #dc3545;
                                color: white;
                                padding: 10px 20px;
                                text-decoration: none;
                                border-radius: 4px;
                                font-weight: bold;
                                text-align: center;">
                                Скачать
                            </a>
                        ''', unsafe_allow_html=True)
                    
        except Exception as e:
            st.error(f"Ошибка отображения: {str(e)}")
            st.markdown(editor_content, unsafe_allow_html=True)