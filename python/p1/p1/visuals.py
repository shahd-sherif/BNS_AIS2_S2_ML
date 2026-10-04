import warnings
import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import ShuffleSplit, train_test_split, validation_curve
from sklearn.tree import DecisionTreeRegressor

warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")

def ModelComplexity(X, y):
    cv = ShuffleSplit(n_splits=10, test_size=0.2, random_state=0)
    max_depth = np.arange(1, 11)

    train_scores, test_scores = validation_curve(
        DecisionTreeRegressor(), X, y,
        param_name="max_depth",
        param_range=max_depth,
        cv=cv,
        scoring="r2"
    )

    train_mean = np.mean(train_scores, axis=1)
    train_std = np.std(train_scores, axis=1)
    test_mean = np.mean(test_scores, axis=1)
    test_std = np.std(test_scores, axis=1)

    plt.figure(figsize=(7, 5))
    plt.title('Decision Tree Regressor Complexity Performance')
    plt.plot(max_depth, train_mean, 'o-', color='r', label='Training Score')
    plt.plot(max_depth, test_mean, 'o-', color='g', label='Validation Score')
    plt.fill_between(max_depth, train_mean - train_std, train_mean + train_std, alpha=0.15, color='r')
    plt.fill_between(max_depth, test_mean - test_std, test_mean + test_std, alpha=0.15, color='g')

    plt.legend(loc='lower right')
    plt.xlabel('Maximum Depth')
    plt.ylabel('Score')
    plt.ylim([-0.05, 1.05])
    plt.show()

def PredictTrials(X, y, fitter, data):
    prices = []

    for k in range(10):
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=k
        )
        reg = fitter(X_train, y_train)
        pred = reg.predict([data[0]])[0]
        prices.append(pred)
        print('Trial {}: ${:,.2f}'.format(k + 1, pred))

    print('\nRange in prices: ${:,.2f}'.format(max(prices) - min(prices)))