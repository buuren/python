def addNumbers1(num):
	total = 0
	i = 1
	while i <= num:
		print i
		total = total + i
		i = i + 1
	return total

def addNumbers(start, end):
	total = 0
	while start <= end:	
		total = total + start
		start = start  + 1
	return total

def countPages(num):
	total = 0
	i = 1
	while i <= num:
		page_no = str(i)
		total += page_no.count('1')
		i = i + 1
	return total 
	
countPages(200)


Private Sub Application_Startup()
' Set workbook = excelApplication.Open("\\ubuntu64\sys$\contactEstel.txt.csv")

Dim MyString, MyNumber
Open "\\ubuntu64\sys$\contactEstel.txt.csv" For Input As #1 ' Open file for input.
Do While Not EOF(1) ' Loop until end of file.
Input #1, MyString, MyNumber ' Read data into two variables.
Debug.Print MyString, MyNumber ' Print data to the Immediate window.
Loop
Close #1 ' Close file.
End Sub


' Set workbook = excelApplication.Open("\\ubuntu64\sys$\contactEstel.txt.csv")
        Dim myFileName As String
    Dim myLine As String
    Dim FileNum As Long
    Dim MyWord As String
    Dim sFile As String
    Dim sArray() As String
    Dim Index As Long
    ReDim sArray(1)
        
    myFileName = "\\ubuntu64\sys$\contactEstel.txt.csv"
    FileNum = FreeFile
    Close FileNum
    Open myFileName For Input As FileNum
    Do While Not EOF(FileNum)
        Line Input #FileNum, myLine
        newstring = Split(myLine, ";")
        '=============================
        ofullname = newstring(0)
        ojobtitle = newstring(1)
        oCompanyName = newstring(2)
        oBusinessPhone = newstring(6)
        oBusinessFax = newstring(7)
        oMobilePhone = newstring(9)
        oEmail = newstring(10)
        '=============================
        'Debug.Print ofullname
        
        Do While Not EOF(FileNum)
        Index = Index + 1
        ReDim Preserve sArray(Index)
        Line Input #FileNum, sArray(Index)

        Debug.Print Index
        Loop
        
  Loop

