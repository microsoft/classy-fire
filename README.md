# 🤵🔥 Classy-Fire 🔥🤵
Classy-fire is a pretrained multiclass text classification approach that leverages Azure OpenAI's LLM APIs using clever parameter tuning and prompting for classification.

## Why?
* Tired of having to beg your LLM to pick from a set of options / actions?
* Tired of working hard on cleaning and parsing its responses to trigger a flow?
* Struggling to strip unhelpful prefixes (such as "Sure! " or "I am just a language model!")?
* Having to wait on retries in cases of unexpected outputs?
* Getting random responses on the same query?
* Need a "quick and dirty" text classifier? Don't have enough training data?


# Start here

## Installation
```
pip install classy-fire
```
## Usage example

```python
from classy_fire import LLMClassifier

classifier = LLMClassifier(["Banana", "Watermelon", "Apple", "Grape"])

result = classifier("Has an elongated shape")
print(result)
>>> ('Banana', 0)
```

## Prerequisites
make sure you have OPENAI_API_BASE, OPENAI_API_VERSION, OPENAI_API_TYPE and OPENAI_API_KEY environment variables populated beforehand and a deployment of gpt-3.5-turbo named gpt-35-turbo-0301 (or pass deployment_name and model_name parameters to the LLMClassifier constructor).

# Continue here

## LLMClassifier optional parameters
LLMClassifier can be initialized with added parameters that can help instruct and ground it to the classification task at hand.
* task_description = "Ability to provide additional context on the classification options and overall context on inputs"
* few_shot_examples = "Ability to provide instances of inputs and corresponding expected output values as a string"

## The premise behind classy-fire
In Classy-fire, we instruct the LLM to provide the most likely classification for an input string to a set of predetermined classes (also strings).
Formally, given a string instance $x_i$ and a set of $k$ classes provided as strings, $C=(C_1, ..., C_k)$, classy-fire determines 

$argmax_j Pr[x_i \in C_j | C, \Theta]$

Where $\Theta$ is the parameters (knowledge of the world) of the language model.

* Classy-fire does this efficiently by mapping class strings to single tokens and providing a strong prior probability for these tokens. We instruct the model to generate a single token response, which allows for optimized inference runtime.
* Classy-fire does this deterministically and with less sensitivity to confabulation (hallucination) by setting the model temperature to 0, thereby guaranteeing the returned response is the argmax of the model posterior probability.

## Quality of results
We ran a preliminary experiment to classify a sample of 100 tweets from the [tweet_eval dataset](https://huggingface.co/datasets/tweet_eval/viewer/emotion/train).
The results [appear to beat the SOTA](https://huggingface.co/spaces/autoevaluate/leaderboards?dataset=tweet_eval&only_verified=0&task=-any-&config=emotion&split=test&metric=f1).
             
|              | precision | recall | f1-score | support |
|--------------|-----------|--------|----------|---------|
| anger        | 0.97      | 0.81   | 0.88     | 42      |
| joy          | 0.74      | 0.92   | 0.82     | 25      |
| optimism     | 1.00      | 0.25   | 0.40     | 8       |
| sadness      | 0.75      | 1.00   | 0.86     | 21      |
|              |           |        |          |         |
| accuracy     |           |        | 0.83     | 96      |
| macro avg    | 0.87      | 0.74   | 0.74     | 96      |
| weighted avg | 0.87      | 0.83   | 0.82     | 96      |

See evaluate.ipynb for the details behind this experiment.

* We encourage the community to benchmark and explore this method against larger or more standardized datasets.
* We have not evaluated alternative prompting strategies or the impact of adding few shot examples, there may be flexibility in the achievable quality.


# Other stuff

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
 
<!-- BEGIN MICROSOFT SECURITY.MD V0.0.5 BLOCK -->

## Security

Microsoft takes the security of our software products and services seriously, which includes all source code repositories managed through our GitHub organizations, which include [Microsoft](https://github.com/Microsoft), [Azure](https://github.com/Azure), [DotNet](https://github.com/dotnet), [AspNet](https://github.com/aspnet), [Xamarin](https://github.com/xamarin), and [our GitHub organizations](https://opensource.microsoft.com/).

If you believe you have found a security vulnerability in any Microsoft-owned repository that meets [Microsoft's definition of a security vulnerability](https://docs.microsoft.com/en-us/previous-versions/tn-archive/cc751383(v=technet.10)), please report it to us as described below.

## Reporting Security Issues

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them to the Microsoft Security Response Center (MSRC) at [https://msrc.microsoft.com/create-report](https://msrc.microsoft.com/create-report).

If you prefer to submit without logging in, send email to [secure@microsoft.com](mailto:secure@microsoft.com).  If possible, encrypt your message with our PGP key; please download it from the [Microsoft Security Response Center PGP Key page](https://www.microsoft.com/en-us/msrc/pgp-key-msrc).

You should receive a response within 24 hours. If for some reason you do not, please follow up via email to ensure we received your original message. Additional information can be found at [microsoft.com/msrc](https://www.microsoft.com/msrc).

Please include the requested information listed below (as much as you can provide) to help us better understand the nature and scope of the possible issue:

  * Type of issue (e.g. buffer overflow, SQL injection, cross-site scripting, etc.)
  * Full paths of source file(s) related to the manifestation of the issue
  * The location of the affected source code (tag/branch/commit or direct URL)
  * Any special configuration required to reproduce the issue
  * Step-by-step instructions to reproduce the issue
  * Proof-of-concept or exploit code (if possible)
  * Impact of the issue, including how an attacker might exploit the issue

This information will help us triage your report more quickly.

If you are reporting for a bug bounty, more complete reports can contribute to a higher bounty award. Please visit our [Microsoft Bug Bounty Program](https://microsoft.com/msrc/bounty) page for more details about our active programs.

## Preferred Languages

We prefer all communications to be in English.

## Policy

Microsoft follows the principle of [Coordinated Vulnerability Disclosure](https://www.microsoft.com/en-us/msrc/cvd).

<!-- END MICROSOFT SECURITY.MD BLOCK -->
