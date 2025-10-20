import streamlit as st
from utils import connect_redis
import pandas as pd
from streamlit_extras.floating_button import floating_button
from redis.exceptions import ResponseError, ConnectionError

rds = connect_redis()

# 从 redis 回传支出数据
def get_exp_data():
    pipe = rds.pipeline()
    keys_ = rds.keys("expenses:*")
    for i in keys_:
        pipe.hgetall(i)
    data = pipe.execute()
    return data    
# def dataframe_data():
#     df = pd.DataFrame(get_expenses())
#     df.rename(columns={
#         "date":"日期",
#         "type":"种类",
#         "description":"描述",
#         "category":"类型",
#         "cost":"成本",
#         "price":"金额",
#     }, inplace=True)
#     return df

_type = ['电费','宽带','买菜','话费','超市','房租','管理费','过路费','国民保险','加油','汽车保险','买菜','工资','私活','其他']

def insert_expenses_callback():
    if "submit_error" in st.session_state:
        del st.session_state.submit_error

    if not st.session_state.description:
        st.session_state.submit_error = "标题不能留空"
        return False
    
    if not st.session_state.price:
        st.session_state.submit_error = "总金额不能为空"
        return False
    
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
        st.toast(f"✅ 添加成功")
    except ConnectionError as e:
        rds.rpush("error","expenses.py line:32 create_expenses error")
        st.session_state.submit_error = "数据库连接错误"
        return False
    
@st.dialog("填写表单", width="medium")        
def insert_expenses_form():    
    with st.form("form",border=False):
        main_box = st.container(horizontal=False,horizontal_alignment="distribute")
        with main_box:
            row1 = st.container(horizontal=True) 
            row1.date_input("日期",key="date")
            row1.selectbox("种类",options=['支出','收入'], key="type")
            row2 = st.container(horizontal=True)  
            row2.selectbox("类型",options=_type,key="category")
            row3 = st.container(horizontal=True)  
            row3.text_input("成本",key="cost",placeholder="可留空")
            row3.text_input("总金额",key="price")
            st.text_input("描述",key="description")
        # st.text_area("detail")
        button_box = st.container(horizontal=True, horizontal_alignment="center")   
        save = button_box.form_submit_button("save", on_click=insert_expenses_callback)
        if button_box.form_submit_button("cancel"):
            st.switch_page("sidebar/show_exp.py")
        if "submit_error" in st.session_state:
           st.error(st.session_state.submit_error)  
        elif save:
           st.rerun() 


def delete_expense_callback(id):
    key = f"expenses:{id}"
    try:
       rds.delete(key)
       st.toast(f"✅ 已删除 {key}")
    except ConnectionError as e:
       st.toast(f"❌ 删除异常: {e}")
       return False  
    st.rerun()

def for_loop_exp_data():    
    for i in result:
        id = i['id']
        main = st.container(border=True)
        sub_box = main.container(border=False,horizontal=True)
        sub_box.write(i['date'])
        sub_box.write(i['type'])
        sub_box.write(i['category'])
        sub_box.write(i['price'])
        sub_box.write(i['cost'])
        main.write(i['description'])
        with main.container(horizontal=True):
            del_response = st.button("delete",type="primary", use_container_width=True,key=f"delete_{id}", on_click=delete_expense_callback,args=(id,))
            st.button("edit",use_container_width=True,key=f"edit_{id}")

header = st.container()
header.subheader("Here is a sticky header")
header.write("""<div class='fixed-header'/>""", unsafe_allow_html=True)

st.markdown(
    """
<style>
    div[data-testid="stVerticalBlock"] div:has(div.fixed-header) {
        position: sticky;
        top: 2.875rem;
        background-color: white;
        z-index: 999;
    }
    .fixed-header {
        border-bottom: 1px solid black;
    }
</style>
    """,
    unsafe_allow_html=True)    

with header.expander("过滤设置"):
    st.checkbox("启用排序1")

result = get_exp_data()
    
if result:
   for_loop_exp_data() 
else:
   st.write("还没有数据")    

if floating_button(":material/chat: 新增"):
   insert_expenses_form() 
   
