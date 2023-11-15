import numpy as np
import openai
from classy_fire.base_classifier import BaseClassifier
from typing import Any, Callable, Dict


class MCMCClassifier(BaseClassifier):
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

    def _establish_llm_parameters(self) -> Callable[[list[Dict[str, str]]], Any]:
        def _llm_chat(messages: list[Dict[str, str]]):
            return self.client.chat.completions.create(
                messages=messages,
                model = self._deplyment_name,
                temperature=1,
                n=100,
                max_tokens=1,
                logit_bias = self._logit_bias
                )
        return _llm_chat

    def __call__(self, input_string: str, **kwargs) -> Any:
        """
        The function takes a string and returns a tuple containing the classified class name (string) and corresponding class id (int).
        param input_string: The string to classify.
        """
        response = self._llm_chat(
            [
                self.system_message,
                {
                    "role": "user",
                    "content": self.user_prompt_base.format(user_prompt=input_string)
                },
            ]
        )
        results = [res.message.content for res in response.choices]
        distribution = np.histogram(results, bins=range(len(self.class_names)+1), density=True)[0]
        result_list = list(zip(self.class_names, range(len(self.class_names)+1), distribution.tolist()))
        return result_list
