## Webtrends

Provides web, social and mobile analytics.

## Webtrends and python automation

It is possible to collect, analyze, group and sort data from Webtrends directly through python

## Requirements

* SQLAlchemy >= 0.5

`pip install SQLAlchemy`

* PyODBC >= 2.0

`Download for your Python version at https://code.google.com/p/pyodbc/` 

* Webtrends Windows ODBC driver

`Download for your WebTrends version at http://webtrends.com/support/software-center. You need "Client Components"`

* Install sqlawebtrends

`pip install sqlawebtrends`

## Configuration

* `C:\Windows\SysWOW64\odbcad32.exe`

* System DNS -> Add -> WebTrends ODBC Driver. Fill the blanks. Ok -> Finish
