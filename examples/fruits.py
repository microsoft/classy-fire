import os
import sys

# Get the current script's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the path to the repository root directory (two levels up from the script)
repository_root = os.path.abspath(os.path.join(current_dir, ".."))

# Add the repository root directory to the Python path
sys.path.insert(0, repository_root)  # Insert at the beginning of sys.path

from classy_fire.llm_classifier import LLMClassifier  # noqa: E402

llm_classifier = LLMClassifier(["Banana", "Watermelon", "Apple", "Grape"])

result = llm_classifier("Has an elongated shape")
print(result)
# Output:
# >>> ('Banana', 0)
# tuple of class name and class ids of the argmax class

from classy_fire.mcmc_classifier import MCMCClassifier  # noqa: E402

mcmc_classifier = MCMCClassifier(["Banana", "Watermelon", "Apple", "Grape"])

result = mcmc_classifier("Has an oval or spherical shape")
print(result)
# Output:
# >>> [('Banana', 0, 0.0), ('Watermelon', 1, 0.02), ('Apple', 2, 0.81), ('Grape', 3, 0.17)]
# list of tuples of class names, class ids, and their probabilities
