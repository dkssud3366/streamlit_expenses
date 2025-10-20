import streamlit as st
from utils import connect_redis
from utils.tools import formated_amount
import pandas as pd
from streamlit_extras.floating_button import floating_button
from redis.exceptions import ResponseError, ConnectionError
from redis.commands.search.query import Query,NumericFilter
import time

rds = connect_redis()
print(">>>>>>>>>>>>>>>>>>>>>>>")
# 从 redis 回传支出表数据
def get_exp_data(expense=None,income=None,start_date=None,end_date=None):
    # search_content = f"@type:{{{expense|income}}}"
    # query = Query(search_content) \
    #     .add_filter(NumericFilter("date", start_date, end_date)) \
    #     .paging(0,5000) \
    #     .sort_by("date", asc=False)
    # result = rds.ft("idx:expenses").search(query)
    pipe = rds.pipeline()
    keys_ = rds.keys("expenses:*")
    for i in keys_:
        pipe.hgetall(i)
    data = pipe.execute()
    return data    


_type = ['电费','宽带','买菜','话费','超市','房租','管理费','过路费','国民保险','加油','汽车保险','买菜','工资','私活','其他']

def insert_expenses_callback():
    if "submit_error" in st.session_state:
        del st.session_state.submit_error

    if not st.session_state.description.strip():
        st.session_state.submit_error = "标题不能留空"
        return 
    
    if not st.session_state.price:
        st.session_state.submit_error = "总金额不能为空"
        return 
    price = formated_amount(st.session_state.price)
    if not isinstance(price,int):
        st.session_state.submit_error = "金额格式不正确"
        return 
    
    id = rds.incr("id_expenses")
    data = {
        "id":id,
        "date":st.session_state.date.strftime("%Y-%m-%d"),
        "type": st.session_state.type,
        "description":st.session_state.description,
        "category": st.session_state.category,
        "cost":st.session_state.cost or 0,
        "price":st.session_state.price,
    }
    try:
        rds.hset(f"expenses:{id}", mapping=data)
        st.session_state.submit_success = True  # 标记表单已完成
        # st.rerun()  # ✅ 只在这里刷新一次
    except ConnectionError as e:
        rds.rpush("error","expenses.py line:32 create_expenses error")
        st.session_state.submit_error = "数据库连接错误"
    
# @st.fragment    
@st.dialog("填写表单", width="medium")        
def insert_expenses_form():    
    with st.form("form",border=False,enter_to_submit=False,clear_on_submit=True):
        main_box = st.container(horizontal=False,horizontal_alignment="distribute")
        with main_box:
            row1 = st.container(horizontal=True) 
            row1.selectbox("种类",options=['支出','收入'], key="type")
            row1.date_input("日期",key="date")

            row2 = st.container(horizontal=True)  
            row2.selectbox("类型",options=_type,key="category")

            row3 = st.container(horizontal=True)  
            row3.text_input("成本",key="cost",placeholder="可留空")
            row3.text_input("总金额",key="price")

            st.text_input("描述",key="description")

        # st.text_area("detail")
        button_box = st.container(horizontal=True, horizontal_alignment="center")   
        button_box.form_submit_button("save",type="primary", on_click=insert_expenses_callback)
        if "submit_success" in st.session_state:
            del st.session_state.submit_success
            st.toast(" ✅ 添加成功")
            st.rerun()
        if "submit_error" in st.session_state:
           st.error(st.session_state.submit_error)  
           del st.session_state.submit_error


def delete_expense_callback(id):
    key = f"expenses:{id}"
    try:
       rds.delete(key)
       st.session_state.delete_sucdess = True
       st.switch_page("sidebar/show_exp.py")
    except ConnectionError as e:
    #    st.toast(f"❌ 删除异常: {e}")
       st.session_state.delete_error = False  

@st.dialog("删除", width="small") 
def confirm_delete(id):
    # st.write(f"确定要删除这条记录吗？")
    col1, col2 = st.columns(2)
    if col1.button("确认删除", type="primary", use_container_width=True):
       delete_expense_callback(id) 
    if col2.button("取消", use_container_width=True):
       st.switch_page("sidebar/show_exp.py") 

@st.fragment
def for_loop_exp_data(i):
    # time.sleep(0.3)
    id = i['id']
    main = st.container(border=True)
    sub_box = main.container(border=False,horizontal=True)
    sub_box.write(i['date'])
    sub_box.write(i['type'])
    sub_box.write(i['category'])
    sub_box.write(i['price'])
    sub_box.write(i['cost'])
    main.write(i['description'])
    with st.container(horizontal=True):  
        if st.button("delete",type="primary", use_container_width=True,key=f"delete_{id}"):
            confirm_delete(id) 
            if "submit_success" in st.session_state:
               print("delete call back")
               del st.session_state.submit_success 
               st.rerun()
                
        st.button("edit",use_container_width=True,key=f"edit_{id}")    


header = st.container()
header.subheader("Here is a sticky header")

@st.fragment
def filter_setting():
    st.warning(f"支出 : , 进账 : ")
    with st.container(horizontal=True,vertical_alignment="center"):
       select_type = st.selectbox("类型选择", options=['全部'] + _type)
       datetime = st.selectbox("范围", options=['当月','昨天','前天','上月','全年','去年'])
       with st.container(horizontal=True,horizontal_alignment="distribute",vertical_alignment="center"):
           expense = st.checkbox("支出",value=True)
           income = st.checkbox("收入")
           if st.button("search"):
              st.rerun()   

with header.expander("过滤设置"):
     filter_setting()

result = get_exp_data()  

for i in result:
    for_loop_exp_data(i)

@st.fragment
def insert_exp_button(): 
    if floating_button(":material/chat: 新增"):
       insert_expenses_form()
      
insert_exp_button()
   
