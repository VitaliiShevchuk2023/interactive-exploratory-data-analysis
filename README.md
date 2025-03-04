
# Створення веб-додатка для дослідницького аналізу даних за допомогою Python та Streamlit

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://blank-app-template.streamlit.app/)


## Вступ

Сьогодні ми розглянемо, як підняти ваші навички програмування на Python на новий рівень, створивши інтерактивний веб-додаток для аналізу даних. Не хвилюйтеся, якщо це здається складним — процес набагато простіший, ніж ви думаєте!

Для цього ми використаємо **Streamlit** — потужний Python-фреймворк, ідеальний для швидкого прототипування веб-додатків. Він пропонує зручні віджети для взаємодії користувачів з даними та перетворює складні аналітичні процеси на прості та зрозумілі операції.

## Що вміє наш додаток?

Веб-додаток, який ми створимо, дозволить користувачам:
- Завантажувати файли Excel/CSV
- Визначати ключові характеристики даних (розміри, описи полів, статистику, кількість значень)
- Створювати візуалізації з інтерфейсом у стилі Tableau
- Розгортати додаток за допомогою Streamlit Community Cloud та отримувати власну URL-адресу для поширення

## Частина 1: Налаштування середовища

Спочатку необхідно встановити Streamlit та інші потрібні бібліотеки:

```python
# Імпортування необхідних бібліотек
import streamlit as st
import openpyxl
import pygwalker as pyg
import pandas as pd

# Налаштування веб-сторінки
st.set_page_config(page_title='Додаток для дослідницького аналізу даних', page_icon=None, layout="wide")
```

## Частина 2: Завантаження файлів

Створимо інтерфейс для завантаження файлів:

```python
# Створення розділу в бічній панелі
st.sidebar.write("****A) Завантаження файлу****")

# Вибір типу файлу
ft = st.sidebar.selectbox("*Який тип файлу?*", ["Excel", "csv"])

# Створення динамічного варіанту завантаження
uploaded_file = st.sidebar.file_uploader("*Завантажте файл тут*")

if uploaded_file is not None:
    file_path = uploaded_file

    if ft == 'Excel':
        try:
            # Вибір аркуша в Excel-файлі
            sh = st.sidebar.selectbox("*Який аркуш треба прочитати?*", pd.ExcelFile(file_path).sheet_names)
            # Вибір рядка з назвами стовпців
            h = st.sidebar.number_input("*У якому рядку містяться назви стовпців?*", 0, 100)
        except:
            st.info("Файл не розпізнається як Excel")
            sys.exit()
    
    elif ft == 'csv':
        try:
            # Для csv не потрібні sh та h
            sh = None
            h = None
        except:
            st.info("Файл не розпізнається як csv")
            sys.exit()

    # Функція кешування для завантаження даних
    @st.cache_data(experimental_allow_widgets=True)
    def load_data(file_path, ft, sh, h):
        
        if ft == 'Excel':
            try:
                # Читання Excel-файлу
                data = pd.read_excel(file_path, header=h, sheet_name=sh, engine='openpyxl')
            except:
                st.info("Файл не розпізнається як Excel")
                sys.exit()
    
        elif ft == 'csv':
            try:
                # Читання csv-файлу
                data = pd.read_csv(file_path)
            except:
                st.info("Файл не розпізнається як csv")
                sys.exit()
        
        return data

    data = load_data(file_path, ft, sh, h)
```

## Частина 3: Дослідження даних

Після завантаження файлу, ми можемо відобразити його попередній перегляд:

```python
## 1. Огляд даних
    st.write('### 1. Попередній перегляд набору даних')

    try:
        # Відображення датафрейму в Streamlit
        st.dataframe(data, use_container_width=True)
    except:
        st.info("Файл не було правильно прочитано. Переконайтеся, що вхідні параметри визначено правильно.")
        sys.exit()
```

## Частина 4: Аналіз характеристик даних

Створимо інтерактивний вибір різних характеристик даних:

```python
## 2. Розуміння даних
    st.write('### 2. Загальний огляд')

    # Створення радіокнопок у бічній панелі
    selected = st.sidebar.radio("**B) Що ви хочете дізнатися про дані?**", 
                               ["Розміри даних",
                                "Описи полів",
                                "Статистика", 
                                "Кількість значень полів"])

    # Відображення типів полів
    if selected == 'Описи полів':
        fd = data.dtypes.reset_index().rename(columns={'index':'Назва поля', 0:'Тип поля'}).sort_values(by='Тип поля', ascending=False).reset_index(drop=True)
        st.dataframe(fd, use_container_width=True)

    # Відображення статистики
    elif selected == 'Статистика':
        ss = pd.DataFrame(data.describe(include='all').round(2).fillna(''))
        st.dataframe(ss, use_container_width=True)

    # Відображення кількості значень у полях
    elif selected == 'Кількість значень полів':
        # Створення радіокнопки в бічній панелі для цього вибору
        sub_selected = st.sidebar.radio("*Яке поле потрібно дослідити?*", data.select_dtypes('object').columns)
        vc = data[sub_selected].value_counts().reset_index().rename(columns={'count':'Кількість'}).reset_index(drop=True)
        st.dataframe(vc, use_container_width=True)

    # Відображення розмірів датафрейму
    else:
        st.write('###### Дані мають розміри:', data.shape)
```

## Частина 5: Візуалізація даних за допомогою PyGWalker

Додамо можливість візуалізації даних:

```python
## 3. Візуалізація

    # Вибір необхідності візуалізації
    vis_select = st.sidebar.checkbox("**C) Потрібна візуалізація для цього набору даних?**")

    if vis_select:
        st.write('### 3. Візуальний аналіз')

        # Створення панелі PyGWalker
        walker = pyg.walk(data, return_html=True)
        st.components.v1.html(walker, width=1100, height=800)  # Налаштуйте ширину та висоту за потреби
```

## Частина 6: Розгортання додатка

Для публікації додатка ми можемо використати Streamlit Community Cloud:

1. Створіть репозиторій GitHub з вашим Python-скриптом та файлом requirements.txt
2. Створіть файл requirements.txt за допомогою команди "pipreqs" в терміналі
3. З'єднайте ваш акаунт GitHub з Streamlit Community Cloud
4. Налаштуйте розгортання, вказавши репозиторій та інші параметри
5. Виберіть унікальну URL-адресу для вашого додатка

## Висновок

Вітаємо! Ви створили ваш власний веб-додаток для аналізу даних з інтерактивними можливостями завантаження файлів, дослідження даних та створення візуалізацій. Streamlit - потужний інструмент, який дозволяє швидко перетворювати код Python на інтерактивні веб-додатки без глибоких знань веб-розробки.

## Додаткові ресурси

- Офіційна документація Streamlit
- Документація PyGWalker для створення візуалізацій
- Платформа Streamlit Community Cloud для розгортання додатків
- How to Build An Interactive Exploratory Data Analysis Application Using Python and Streamlit, https://medium.com/@nivanthab/how-to-build-an-interactive-exploratory-data-analysis-application-using-python-and-streamlit-4b569acee935
- How to explore data in Python with PyGWalker and Streamlit, https://www.youtube.com/watch?v=rprn79wfB9E
- PyGWalker for Exploratory Data Analysis In Jupyter Notebooks, https://www.youtube.com/watch?v=3WjWeH3HIMo
- Quick intro to PyGWalker, turn your dataframe into an interactive UI for data visualization, https://www.youtube.com/watch?v=m9xszlY8Z8A
- A Tableau Alternative in Python for Data Analysis (in Streamlit & Jupyter) | PyGWalker Tutorial, https://www.youtube.com/watch?v=Ynt7Etci1KU
- Create Tableau like Interactive Dashboards in Python for Free!, https://www.youtube.com/watch?v=6qymrlkkUG4




