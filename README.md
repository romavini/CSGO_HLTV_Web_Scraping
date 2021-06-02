# CS:GO BestOf3 [HLTV.org](https://www.hltv.org/)
[![Selenium](https://img.shields.io/badge/lib-Selenium-darkgreen)](https://www.selenium.dev/documentation/en/selenium_installation/installing_selenium_libraries/) [![Pandas](https://img.shields.io/badge/lib-Pandas-white)](https://pandas.pydata.org/) [![NumPy](https://img.shields.io/badge/lib-NumPy-darkblue)](https://numpy.org/)

### 🗡 Python Web Scraping Project 🔫

[Kaggle Dataset](https://www.kaggle.com/viniciusromanosilva/csgo-hltv)

### How to Run 🏁
**1. Create a virtual environment**

**2. Install de Dependences**
```
$ pip install -r requirements.txt
```
**3. Run**
```
$ python csgo_hltv\main.py
```
![example](images/example.gif)

### How to Read the Results 📖
```python
>>> from csgo_hltv.helpers import read_datacs
>>> df = read_datacs()
```

### Test 🚧
```
$ pytest csgo_hltv\
```
