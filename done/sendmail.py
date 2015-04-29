import win32com.client as win32
outlook = win32.Dispatch('outlook.application')
mail = outlook.CreateItem(0)
mail.To = 'vkolesni@gmail.com'
mail.Subject = 'Swedbank monitoring'
mail.body = message
mail.send
