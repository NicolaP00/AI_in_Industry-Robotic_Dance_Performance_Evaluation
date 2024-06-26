import numpy as np
import pandas as pd
import sys
from sklearn.model_selection import GridSearchCV, KFold
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
import warnings
import os
from pathlib import Path
from ANOVA import *

def smape(y_true, y_pred):
    return 100/len(y_true) * np.sum(np.abs(y_pred - y_true) / (np.abs(y_true) + np.abs(y_pred)))

if __name__ == "__main__":

    if(len(sys.argv)<4):
        print("ERROR! Usage: python scriptName.py fileCSV targetN modelloML\n")
              
        sys.exit(1)
    nome_script, pathCSV, targId, mlModel = sys.argv

    targetId = int(targId)

    if not sys.warnoptions:
        warnings.simplefilter("ignore")
        os.environ["PYTHONWARNINGS"] = "ignore"

    back = ['Artistic', 'Scientific']
    pos = 1
    ds = 'S'
    if (pathCSV == 'datasetArtisticBackground.csv'):
        pos = 0
        ds = 'A'


    dataset = pd.read_csv(pathCSV, sep=';')

    index_target= dataset.iloc[:,-7:]
    list_ind_t = index_target.columns.values.tolist()
    targetN = list_ind_t[targetId]

    X = dataset[['timeDuration', 'nMovements', 'movementsDifficulty', 'AItechnique', 'robotSpeech', 'acrobaticMovements', 'movementsRepetition', 'musicGenre', 'movementsTransitionsDuration', 'humanMovements', 'balance', 'speed', 'bodyPartsCombination', 'musicBPM', 'sameStartEndPositionPlace', 'headMovement', 'armsMovement', 'handsMovement', 'legsMovement', 'feetMovement']]
    y = dataset[targetN]

    categorical_features = ['AItechnique', 'musicGenre']

    categorical_transformer = Pipeline(steps=[
                                          ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
                                          ('onehot', OneHotEncoder(handle_unknown='ignore'))])

    numeric_features = ['timeDuration', 'nMovements', 'movementsDifficulty', 'robotSpeech', 'acrobaticMovements', 'movementsRepetition', 'movementsTransitionsDuration', 'humanMovements', 'balance', 'speed', 'bodyPartsCombination', 'musicBPM', 'sameStartEndPositionPlace', 'headMovement', 'armsMovement', 'handsMovement', 'legsMovement', 'feetMovement']
    numeric_transformer = Pipeline(steps=[
                                      ('imputer', SimpleImputer(strategy='median')),
                                      ('scaler', StandardScaler())])

    preprocessor = ColumnTransformer(
                                 transformers=[
                                               ('num', numeric_transformer, numeric_features),
                                               ('cat', categorical_transformer, categorical_features)])
    
    ############# ML MODELS ###############

    model_reg = ['lr',
                'dt',
                'rf',
                'gbr']

    param_lr = [{'fit_intercept':[True,False], 'normalize':[True,False], 'copy_X':[True, False]}]

    param_dt = [{'max_depth': [5,10,20]}]

    param_rf = [{'bootstrap': [True, False],
                 'max_depth': [10, 20],
                 'max_features': ['auto', 'sqrt'],
                 'min_samples_leaf': [1, 2, 4],
                 'min_samples_split': [2],}]

    param_gbr = [{'learning_rate': [0.01,0.03],
                'subsample'    : [0.5, 0.2],
                'n_estimators' : [100,200],
                'max_depth'    : [4,8]}]

    models_regression = {
        'lr': {'name': 'Linear Regression',
               'estimator': LinearRegression(),
               'param': param_lr,
              },
        'dt': {'name': 'Decision Tree',
               'estimator': DecisionTreeRegressor(random_state=42),
               'param': param_dt,
              },
        'rf': {'name': 'Random Forest',
               'estimator': RandomForestRegressor(random_state=42),
               'param': param_rf,
              },

        'gbr': {'name': 'Gradient Boosting Regressor',
                'estimator': GradientBoostingRegressor(random_state=42),
                'param': param_gbr
                },
    }

    k = 10
    kf = KFold(n_splits=k, random_state=None)
    mod_grid = GridSearchCV(models_regression[mlModel]['estimator'], models_regression[mlModel]['param'], cv=5, return_train_score = False, scoring='neg_mean_squared_error', n_jobs = 8)

    for train_index , test_index in kf.split(X):
        data_train , data_test = X.iloc[train_index,:],X.iloc[test_index,:]
        target_train , target_test = y[train_index] , y[test_index]

        model = Pipeline(steps=[('preprocessor', preprocessor),
                ('regressor', mod_grid)])


        _ = model.fit(data_train, target_train)

    
    ######### PREPROCESSING ###########
    
    feature_cat_names = model['preprocessor'].transformers_[1][1]['onehot'].get_feature_names(categorical_features)
    
    l= feature_cat_names.tolist()
    ltot = numeric_features + l
    

    lf = ['t', 'n', 'md', 'rs', 'am', 'mr', 'mtd', 'h', 'b', 's', 'bc', 'bpm', 'pp', 'hm', 'arm', 'hdm', 'lm', 'fm', 'AIc', 'AIp', 'AIs', 'mEl', 'mFol', 'mInd', 'mPop', 'mRap', 'mRock']

    ####################### ANOVA & LASSO #############################

    X = preprocessor.fit_transform(X)

    feature_cat_names = model['preprocessor'].transformers_[1][1]['onehot'].get_feature_names(categorical_features)
    l= feature_cat_names.tolist()
    ltot = numeric_features + l

    X = pd.DataFrame(X, columns=ltot)
    #print(X.median())

    if not Path.cwd().joinpath("Anova_results").exists():
        Path.cwd().joinpath("Anova_results").mkdir(parents=True)

    Anova_results = Anova_Decomposition(mod_grid.best_estimator_, X, y, lf)
    #f_statistic, p_values = f_regression(X, y)
    original_stdout = sys.stdout
    with open(f'Anova_results/{targetId}_{mlModel}_{ds}.txt', 'w') as f:
        sys.stdout = f
        print('\n--------------------- Anova Lasso Results:-------------------------')
        for i in Anova_results:
            print(i)
            
        
    sys.stdout = original_stdout
