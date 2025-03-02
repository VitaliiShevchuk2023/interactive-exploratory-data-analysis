#=======================================================================
## 0.1 Імпорт бібліотек, дані

#Імпортуємо необхідні пакети
import streamlit as st
import openpyxl
import pygwalker as pyg
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as dt
import sys
import os
from PIL import Image

#Отримуємо шлях до зображень
cwd_dir = os.path.dirname(__file__)
rel_path = './images'
images_path = os.path.join(cwd_dir,rel_path)
logo = Image.open(images_path + '/Browser Icon Reverse.png')

#Налаштування сторінки Streamlit
st.set_page_config(page_title = 'Додаток для розвідувального аналізу даних',page_icon = logo,layout = "wide")

#Створюємо контейнер з колонками для заголовка сторінки, конкретного заголовка та логотипу
with st.container():
    col1, col2, padding = st.columns([10,1,1])

    #Встановлюємо заголовок та підзаголовок сторінки
    with col1:
        st.markdown("### Додаток для розвідувального аналізу даних")
        
    #Встановлюємо логотип
    with col2:
        niv_logo = Image.open(images_path + '/Social Logo.png')
        st.image(niv_logo, width=200, output_format='auto')

st.sidebar.write("****А) Завантаження файлу****")

#Запит користувача для вибору типу файлу
ft = st.sidebar.selectbox("*Який тип файлу?*",["Excel", "csv"])

#Створюємо динамічну опцію завантаження файлу в бічній панелі
uploaded_file = st.sidebar.file_uploader("*Завантажте файл тут*")

if uploaded_file is not None:
    file_path = uploaded_file

    if ft == 'Excel':
        try:
            #Запит користувача для вибору імені аркуша в завантаженому Excel
            sh = st.sidebar.selectbox("*Який аркуш у файлі слід прочитати?*",pd.ExcelFile(file_path).sheet_names)
            #Запит користувача для визначення рядка з назвами стовпців, якщо вони не в рядку заголовка в завантаженому Excel
            h = st.sidebar.number_input("*У якому рядку містяться назви стовпців?*",0,100)
        except:
            st.info("Файл не розпізнано як Excel файл")
            sys.exit()
    
    elif ft == 'csv':
        try:
            #Для csv не потрібно sh та h, встановлюємо їх як None
            sh = None
            h = None
        except:
            st.info("Файл не розпізнано як csv файл.")
            sys.exit()

    #Функція кешування для завантаження даних
    @st.cache_data(experimental_allow_widgets=True)
    def load_data(file_path,ft,sh,h):
        
        if ft == 'Excel':
            try:
                #Читаємо Excel файл
                data = pd.read_excel(file_path,header=h,sheet_name=sh,engine='openpyxl')
            except:
                st.info("Файл не розпізнано як Excel файл.")
                sys.exit()
    
        elif ft == 'csv':
            try:
                #Читаємо csv файл
                data = pd.read_csv(file_path)
            except:
                st.info("Файл не розпізнано як csv файл.")
                sys.exit()
        
        return data

    data = load_data(file_path,ft,sh,h)
#=======================================================================
## 0.2 Попередня обробка наборів даних

    #Заміна підкреслень у назвах стовпців на пробіли
    data.columns = data.columns.str.replace('_',' ') 

    data = data.reset_index()

    #Перетворення назв стовпців на заголовний регістр
    data.columns = data.columns.str.title()

    #Горизонтальний роздільник
    st.sidebar.divider()
#=====================================================================================================
## 1. Огляд даних
    st.write( '### 1. Попередній перегляд набору даних ')

    try:
      #Перегляд таблиці даних у streamlit
      st.dataframe(data, use_container_width=True,hide_index=True)

    except:
      st.info("Файл не був правильно прочитаний. Переконайтеся, що вхідні параметри визначені правильно.")
      sys.exit()

    #Горизонтальний роздільник
    st.divider()
#=====================================================================================================
## 2. Розуміння даних
    st.write( '### 2. Загальний огляд ')

    #Створення радіо-кнопки та бічної панелі одночасно
    selected = st.sidebar.radio( "**Б) Що ви хочете знати про дані?**", 
                                ["Розміри даних",
                                 "Опис полів",
                                "Статистичні показники", 
                                "Підрахунок значень полів"])

    #Показ типів полів
    if selected == 'Опис полів':
        fd = data.dtypes.reset_index().rename(columns={'index':'Назва поля',0:'Тип поля'}).sort_values(by='Тип поля',ascending=False).reset_index(drop=True)
        st.dataframe(fd, use_container_width=True,hide_index=True)

    #Показ статистичних показників
    elif selected == 'Статистичні показники':
        ss = pd.DataFrame(data.describe(include='all').round(2).fillna(''))
        #Додавання кількості нульових значень до статистичних показників
        nc = pd.DataFrame(data.isnull().sum()).rename(columns={0: 'кількість_null'}).T
        ss = pd.concat([nc,ss]).copy()
        st.dataframe(ss, use_container_width=True)

    #Показ кількості значень об'єктних полів
    elif selected == 'Підрахунок значень полів':
        # створення радіо-кнопки та бічної панелі одночасно, якщо вибрана ця основна опція
        sub_selected = st.sidebar.radio( "*Яке поле слід дослідити?*",data.select_dtypes('object').columns)
        vc = data[sub_selected].value_counts().reset_index().rename(columns={'count':'Кількість'}).reset_index(drop=True)
        st.dataframe(vc, use_container_width=True,hide_index=True)

    #Показ розмірів таблиці даних
    else:
        st.write('###### Дані мають розміри:',data.shape)

    #Горизонтальний роздільник
    st.divider()

    #Горизонтальний роздільник у бічній панелі
    st.sidebar.divider()
#=====================================================================================================
## 3. Візуалізація

    #Вибір, чи потрібна візуалізація
    vis_select = st.sidebar.checkbox("**В) Чи потрібна візуалізація для цього набору даних (приховайте бічну панель для повного огляду панелі інструментів)?**")

    if vis_select:

        st.write( '### 3. Візуальні дані ')

        try:
            #Створення панелі PyGWalker та відображення HTML-рядка в Streamlit
            walker_html = pyg.walk(data).to_html()
            st.components.v1.html(walker_html, height=1000)
            
        except Exception as e:
            st.error(f"Сталася помилка: {e}")
            
else:
    st.info("Будь ласка, завантажте файл, щоб продовжити.")

#Горизонтальний роздільник
st.divider()

