# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
    
import os
import tiktoken
from typing import Tuple
from langchain.chat_models import AzureChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

class LLMClassifier:
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
    MAX_TOKEN_PRIOR: int = 100

    system_prompt_base: str = (
        "You are an AI assistant. Select for the following human input the most related item from "
        "the following set of <options> and leveraging information given in <context>. Respond with the number corresponding to the selected option.\n"
        "<context>\n{context_string}\n</context>\n"
        "<options>\n{options_string}\n</options>\n"
        "\nHere are some examples of how to respond:\n{few_shot_examples}\n\n###\n"
    )
    user_prompt_base: str = (
        "<Input>\n{user_prompt}\n</Input>\nResponse: "
    )

    def __init__(self, 
                 class_names: list[str], 
                 task_description: str = "",
                 few_shot_examples: str = "", 
                 deployment_name: str = "gpt-35-turbo-0301", 
                 model_name: str = "gpt-3.5-turbo") -> None:
        self.class_names = class_names
        tokenizer = tiktoken.encoding_for_model(model_name)
        class_id_tokens = [tokenizer.encode(str(i)) for i in range(len(class_names))]
        assert all(len(token_list) == 1 for token_list in class_id_tokens), \
            f"A class id number did not map to a single token, maybe too many classes in list: {len(class_names)}"
        self.system_message = SystemMessage(
            content=self.system_prompt_base.format(
                context_string = task_description,
                options_string="\n".join([f"{i}. {cls}" for i, cls in zip(range(len(class_names)), class_names)]),
                few_shot_examples=few_shot_examples
        ))
        self._logit_bias = {token_list[0]: LLMClassifier.MAX_TOKEN_PRIOR for token_list in class_id_tokens}
        self._llm_chat = AzureChatOpenAI(deployment_name=deployment_name,
                                         openai_api_base=os.environ.get("OPENAI_API_BASE"),
                                         openai_api_version=os.environ.get("OPENAI_API_VERSION"),
                                         openai_api_key=os.environ.get("OPENAI_API_KEY"),
                                         temperature=0,
                                         max_tokens=1,
                                         model_kwargs={"logit_bias": self._logit_bias})

    def __call__(self, input_string: str) -> Tuple[str, int]:
        """
        The function takes a string and classifies it to a class name and class id.
        """
        response = self._llm_chat([self.system_message, HumanMessage(content=self.user_prompt_base.format(user_prompt=input_string))])
        predicted_class_id = int(response.content)

        return self.class_names[predicted_class_id], predicted_class_id
