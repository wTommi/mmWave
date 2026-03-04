# KKT_Library

this module is based on different library (C# library, WIFIconnection) API implementation of python interface.

```Integration``` is wrapper modules for different libs.
    
* ```wrapper.py``` is wrapper interface.
* ```CSharpWrapper.py``` is wrapper for C# library API.
* ```WifiWrapper.py``` is wrapper for wifi connection API.

```KsocLib.py``` is design as adapator pattern for extension different connection API.


```KKTLib.py``` is the module to do backward compatibility for old version of KKT_Module.

* design as a singleton pattern for only one instance of ```Lib``` class.


## Installation

It requires python version 3.8 above and 3.11 below. We recommend to create venv in python version *``3.8.9``*

### Install from gitlab with pip

```bash
pip install git+http://10.10.68.133/KKT_Python_Module/Library.git[branch_name]   
```

### How to develop as submodule of other project with dev mode.

1. Add this project to your main git project in local machine.

    ```bash
    git submodule add http://10.10.68.133/KKT_Python_Module/Library.git
    ```
2. Install this module in dev mode.

    ```bash
    pip install -e Library
    ```

It will be easy to develop and debug this module in your main project.  


## About C# dll can't found in exe file

If you want to use this module in exe file, you need to copy the C# dll files to the same directory of exe file.

```python
import KKT_Library as library

library.setupDLL() # copy package of dll files (KSOC_Libs) to exe directory.
```

## Example

please refer to [``examples``](Library\examples) folder.


## 命名規則

資料夾名稱 : 單字開頭大寫並以底線分割，縮寫皆大寫，ex. <code>KSOC_Libs/</code>

Module名稱 : 單字開頭大寫不以底線分割，ex.<code>LibWrapper.py </code>

class名稱 : 單字開頭大寫不以底線分割，ex.<code>class KSOCIntegration()</code>

function名稱 : 以動詞+名詞的形式如果有備註以底線分割，動詞開頭小寫其餘大寫，ex.<code>def receiveAllData_list()</code>

global變數 : 單字皆大寫並以底線分割，ex.<code>GLOBAL_VAR</code>

class屬性 : 單字小寫並以底線分割，ex.<code>self.class_var</code>


## KKTLib.py

此模組中的類別<code>"Lib"</code>為**單例模式**的實作，只要進入程式後第一次實例化類別<code>"Lib"</code>就可以在有 import 此類別的模組中
在其靜態屬性<code>"ksoclib"</code>中使用 Libaray 的函數。

此模組一部分是為了 PyQT/PySide 設計( 如果有使用 QT 的 UI 需在 QApplication 的 loop 中實例化，不然在使用QFileDialog類別的時候會有檔案選單打不開的bug)，
一部分是為了分離KKT_Module模組間的相依性。






