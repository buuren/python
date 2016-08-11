import win32com.client as win32
outlook = win32.Dispatch('outlook.application')
mail = outlook.CreateItem(0)
mail.To = 'asda@gmail.com'
mail.Subject = ' monitoring'
mail.body = message
mail.send
