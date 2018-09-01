
###What is Preprp
Preprep is a library for performing preprocessing of machine learning efficiently and quickly. Cache the calculations  in the past, when calculating the next time, calculate only the part where the source code was changed.

###Install
```
pip install preprep
```

##How To Use
```python
#prepare preprocessing function

def func1(df):
    return df * 2

def func2(df):
    return df * 3

#init preprep instance
p = Preprep()
p = p.add(func1)
p = p.add(func2)
df = p.fit_gene(df)
```
