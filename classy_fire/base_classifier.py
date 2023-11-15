# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from abc import ABC, abstractmethod
import os
import tiktoken
from typing import Any, Callable, Dict
from openai import OpenAI, AzureOpenAI

class BaseClassifier(ABC):
    """
    A generic LLM based classifier that can be used to classify a string into a set of classes.
    Usage example:
        classifier = LLMClassifier(["Grapes", "Bananas", "Stars"], gpt_api_config)
        classifier("Is yellow")
        > "Bananas"
        classifier("Is round")
        > "Grapes"
        classifier("Shines")
        > "Stars"
    """

    MAX_TOKEN_PRIOR: int = 10

    system_prompt_base: str = (
        "You are an AI assistant. Select for the following human input the most related item from "
        "the following set of <options> and leveraging information given in <context>. Respond with the number corresponding to the selected option.\n"
        "<context>\n{context_string}\n</context>\n"
        "<options>\n{options_string}\n</options>\n"
        "{few_shot_prompt_segment}\n###\n"
    )
    user_prompt_base: str = "<Input>\n{user_prompt}\n</Input>\nResponse: "

    def __init__(
        self,
        class_names: list[str],
        task_description: str = "",
        few_shot_examples: str = "",
        deployment_name: str = "gpt-35-turbo-0301",
        model_name: str = "gpt-3.5-turbo",
    ) -> None:
        """
        param class_names: A list of class names to classify to.
        param task_description: A description of the task to be performed by the classifier.
        param few_shot_examples: A string containing a few shot examples of how to use the classifier.
        param deployment_name: The name of the deployment to use for the classifier.
        param model_name: The name of the model to use for the classifier.
        """
        self.class_names = class_names
        tokenizer = tiktoken.encoding_for_model(model_name)
        class_id_tokens = [tokenizer.encode(str(i)) for i in range(len(class_names))]
        assert all(
            len(token_list) == 1 for token_list in class_id_tokens
        ), f"A class id number did not map to a single token, maybe too many classes in list: {len(class_names)}"
        self.system_message = {
            "role": "system", 
            "content": self.system_prompt_base.format(
                context_string=task_description,
                options_string="\n".join(
                    [
                        f"{i}. {cls}"
                        for i, cls in enumerate(class_names)
                    ]
                ),
                few_shot_prompt_segment=BaseClassifier._construct_few_shot_prompt_segment(few_shot_examples),
            )
        }
        self._logit_bias = {
            token_list[0]: BaseClassifier.MAX_TOKEN_PRIOR
            for token_list in class_id_tokens
        }
        self._deplyment_name = deployment_name
        self._model_name = model_name
        self._llm_chat: Callable[[list[Dict[str, str]]], Any] = self._establish_llm_parameters()
        if os.environ["OPENAI_API_TYPE"] == "azure":
            self.client = AzureOpenAI(api_key = os.environ["OPENAI_API_KEY"],
                                      api_version = os.environ["OPENAI_API_VERSION"],
                                      azure_endpoint = os.environ["OPENAI_API_BASE"])
        else:
            self.client = OpenAI(api_key = os.environ["OPENAI_API_KEY"])

    @staticmethod
    def _construct_few_shot_prompt_segment(few_shot_examples: str) -> str:
        if len(few_shot_examples) > 0:
            return f"Here are some examples of how to respond:\n{few_shot_examples}\n"
        else:
            return ""

    @abstractmethod
    def _establish_llm_parameters(self) -> Callable[[list[Dict[str, str]]], Any]:
        pass

    @abstractmethod
    def __call__(self, input_string: str, **kwargs) -> Any:
        pass
