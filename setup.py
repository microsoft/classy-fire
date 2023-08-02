from setuptools import setup, find_packages
import codecs
import os

#here = os.path.abspath(os.path.dirname(__file__))

#with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
#    long_description = "\\n" + fh.read()
long_description = "See github for details"

setup(
    name="classy_fire",
    version='{{VERSION_PLACEHOLDER}}',
    author="Shay Ben-Elazar",
    author_email="shbenela@microsoft.com",
    description="Classy-fire is multiclass text classification approach leveraging OpenAI LLM model APIs optimally using clever parameter tuning and prompting",
    url = "https://github.com/microsoft/classy-fire",
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['tiktoken, langchain, openai'],
    keywords=['pypi', 'cicd', 'python'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows"
    ]
)