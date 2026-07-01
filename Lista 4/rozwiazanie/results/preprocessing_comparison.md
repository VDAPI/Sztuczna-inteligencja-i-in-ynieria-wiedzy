| model        | preprocessing   |   f1_macro_cv |   f1_macro_std |   accuracy_cv |   f1_weighted_cv |
|:-------------|:----------------|--------------:|---------------:|--------------:|-----------------:|
| DecisionTree | feature_select  |        0.5062 |         0.0982 |        0.6436 |           0.6401 |
| DecisionTree | baseline        |        0.4829 |         0.0477 |        0.6257 |           0.6297 |
| DecisionTree | pca             |        0.4056 |         0.0304 |        0.5869 |           0.5837 |
| GaussianNB   | baseline        |        0.5191 |         0.035  |        0.6497 |           0.6574 |
| GaussianNB   | feature_select  |        0.4949 |         0.0842 |        0.6676 |           0.6544 |
| GaussianNB   | pca             |        0.4699 |         0.0337 |        0.7065 |           0.6757 |