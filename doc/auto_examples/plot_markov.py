"""
================================================
Blahng regularization in Multi-layer Perceptron
================================================

A comparison of different values for regularization parameter 'alpha' on
synthetic datasets. The plot shows that different alphas yield different
decision functions.


Alpha is a parameter for regularization term, aka penalty term, that combats
overfitting by constraining the size of the weights. Increasing alpha may fix
high variance (a sign of overfitting) by encouraging smaller weights, resulting
in a decision boundary plot that appears with lesser curvatures.  Similarly,
decreasing alpha may fix high bias (a sign of underfitting) by encouraging
larger weights, potentially resulting in a more complicated decision boundary.
"""

print(__doc__)

