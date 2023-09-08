import os
import sys

# Get the current script's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the path to the repository root directory (two levels up from the script)
repository_root = os.path.abspath(os.path.join(current_dir, ".."))

# Add the repository root directory to the Python path
sys.path.insert(0, repository_root)  # Insert at the beginning of sys.path

from classy_fire import LLMClassifier  # noqa: E402

classifier = LLMClassifier(["Banana", "Watermelon", "Apple", "Grape"])

result = classifier("Has an elongated shape")
print(result)
