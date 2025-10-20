


def formated_amount(val:str|int):
    if isinstance(val,int):
       return f"{val:,}"
    if isinstance(val,str):
       if "," in val:
          val = val.replace(",", "")
       try:
          val = int(val)
       except Exception as e:
          return val   
       return val



        
