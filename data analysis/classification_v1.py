import pandas as pd
import numpy as np
from sklearn.preprocessing import Imputer
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.cross_validation import KFold
from sklearn.preprocessing import MinMaxScaler
from sklearn.cross_validation import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.grid_search import GridSearchCV

df = pd.read_csv('Upwork_ds.csv')
df = df.sort('y', ascending = True).reset_index(drop=True)
##print df.info()
##y                  869 non-null int64
##X1                 869 non-null int64
##X2_min             869 non-null int64
##X2_max             869 non-null int64
##X2_distribution    869 non-null float64
##X3                 614 non-null float64
##X4                 869 non-null int64
##X5                 869 non-null int64
##print df.describe()
##                y           X1      X2_min      X2_max  X2_distribution  \
##count  869.000000   869.000000  869.000000  869.000000       869.000000   
##mean     1.579977    26.823936    1.336018   10.219793         3.635999   
##std      1.025983    97.269105    0.569868    3.882939         0.635410   
##min      1.000000     0.000000    1.000000    4.000000         1.768576   
##25%      1.000000     1.000000    1.000000    7.000000         3.195838   
##50%      1.000000     3.000000    1.000000    9.000000         3.569346   
##75%      2.000000     8.000000    2.000000   14.000000         3.984174   
##max      4.000000  1135.000000    4.000000   28.000000         7.763919   
##
##               X3          X4          X5  
##count  614.000000  869.000000  869.000000  
##mean     0.434853    1.316456    0.981588  
##std      0.496142    1.385397    0.134513  
##min      0.000000    1.000000    0.000000  
##25%      0.000000    1.000000    1.000000  
##50%      0.000000    1.000000    1.000000  
##75%      1.000000    1.000000    1.000000  
##max      1.000000   23.000000    1.000000  

y_unique = np.unique(df['y'])
columns = ['y', 'X1', 'X2_min', 'X2_max', 'X2_distribution', 'X3', 'X4', 'X5']
df1 = pd.DataFrame(columns=columns)

for val in y_unique:
    df_ = df.query('y=='+str(val)+'')
    df_.fillna(df["X3"].median(), inplace=True)    
    df1 = pd.concat([df1, df_], ignore_index=True)

##print df1.info()
##y                  869 non-null float64
##X1                 869 non-null float64
##X2_min             869 non-null float64
##X2_max             869 non-null float64
##X2_distribution    869 non-null float64
##X3                 869 non-null float64
##X4                 869 non-null float64
##X5                 869 non-null float64

#print df1.describe()
##count  869.000000   869.000000  869.000000  869.000000       869.000000   
##mean     1.579977    26.823936    1.336018   10.219793         3.635999   
##std      1.025983    97.269105    0.569868    3.882939         0.635410   
##min      1.000000     0.000000    1.000000    4.000000         1.768576   
##25%      1.000000     1.000000    1.000000    7.000000         3.195838   
##50%      1.000000     3.000000    1.000000    9.000000         3.569346   
##75%      2.000000     8.000000    2.000000   14.000000         3.984174   
##max      4.000000  1135.000000    4.000000   28.000000         7.763919   
##
##               X3          X4          X5  
##count  869.000000  869.000000  869.000000  
##mean     0.307250    1.316456    0.981588  
##std      0.461619    1.385397    0.134513  
##min      0.000000    1.000000    0.000000  
##25%      0.000000    1.000000    1.000000  
##50%      0.000000    1.000000    1.000000  
##75%      1.000000    1.000000    1.000000  
##max      1.000000   23.000000    1.000000 

y = df1.pop('y')
X = df1

mnb = MultinomialNB()
nb_params = {
    'alpha': np.logspace(-3, 3, 3),
}
svc = SVC(C=1.0)
svc_params = {'kernel':('linear', 'rbf', 'poly','sigmoid'), 'C':np.logspace(-6, 10, 10)}
rfc = RandomForestClassifier(n_estimators=100)
rfc_params = { 
    'n_estimators': range(100, 1000, 100),
    'max_features': ['auto', 'sqrt', 'log2'],
    'max_depth' : range(1, 10, 2),
    'min_samples_split' : range(1, 5, 1),
    'min_samples_leaf' : range(1, 5),
    'max_leaf_nodes' : range(5, 12)
}
min_max_scaler = MinMaxScaler()

##kf = KFold(len(y), n_folds=2, shuffle=True, random_state=42)
##for train_index, test_index in kf:
##    print("TRAIN:", train_index, "TEST:", test_index)
##    X_train, X_test = X[train_index], X[test_index]
##    y_train, y_test = y[train_index], y[test_index]
##    X_train_minmax = min_max_scaler.fit_transform(X_train)

X_min_max = min_max_scaler.fit_transform(X)
X_train,X_test,y_train,y_test = train_test_split(X_min_max,y,test_size=0.4)

for clf, name, param in [(mnb, 'MultinomialNB', nb_params),
              (svc, 'Support Vector Classification', svc_params),
              (rfc, 'Random Forest Classifier'), rfc_params]:
    print name, '\n'
    gs = GridSearchCV(clf, param, cv=5, n_jobs=-1)
    gs.fit(X_train, y_train)
    print gs.best_params_
##    y_pred = clf.predict(X_test)
##    print name, '\n', confusion_matrix(y_test, y_pred), '\n'
