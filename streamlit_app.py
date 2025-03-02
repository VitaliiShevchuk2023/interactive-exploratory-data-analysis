
# Імпортування необхідних бібліотек
import streamlit as st
import openpyxl
import pygwalker as pyg
import pandas as pd

# Налаштування веб-сторінки
st.set_page_config(page_title='Додаток для дослідницького аналізу даних', page_icon=None, layout="wide")


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

## 1. Огляд даних
    st.write('### 1. Попередній перегляд набору даних')

    try:
        # Відображення датафрейму в Streamlit
        st.dataframe(data, use_container_width=True)
    except:
        st.info("Файл не було правильно прочитано. Переконайтеся, що вхідні параметри визначено правильно.")
        sys.exit()

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


## 3. Візуалізація

    # Вибір необхідності візуалізації
    vis_select = st.sidebar.checkbox("**C) Потрібна візуалізація для цього набору даних?**")

    if vis_select:
        st.write('### 3. Візуальний аналіз')

        # Створення панелі PyGWalker
        walker = pyg.walk(data, return_html=True)
        st.components.v1.html(walker, width=1100, height=800)  # Налаштуйте ширину та висоту за потреби

