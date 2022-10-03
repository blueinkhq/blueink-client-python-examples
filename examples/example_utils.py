from abc import ABC, abstractmethod
from typing import List
from munch import Munch


class BaseExample(ABC):
    @abstractmethod
    def start(self):
        """ Start example script
        """
        raise RuntimeError("Unimplemented 'start' method on example")

    @abstractmethod
    def main_router(self):
        """Main Menu of the example
        :return:
        """
        raise RuntimeError("Unimplemented 'main_router' method on example")


def interactive_text_input(prompt: str, default: str = None, allow_blank=True) -> str:
    value = input(f"{prompt} [{default}]: ")

    if not value or value == "":
        value = default

    if not allow_blank and (value is None or value == ""):
        print("** Blank value is NOT allowed **")
        return interactive_text_input(prompt, default, allow_blank)

    return value


def interactive_yes_no_input(prompt: str, default: str = "n") -> bool:
    value = input(f"{prompt} [{default}]: ")

    if not value or value == "":
        value = default

    if value.lower() == "y":
        return True
    else:
        return False


def input_choices(header: str, end_prompt: str, choices, default: int):
    # Choices can either be a straight list or dict. If a dict,
    # displayed by key but returns value. If a list, returns whatever
    # list element is chosen
    print(header)
    if type(choices) == dict or type(choices) == Munch:
        ordered_keys = list(choices.keys())
        answers = list([choices[key] for key in ordered_keys])
        for i, key in enumerate(ordered_keys):
            print(f"{i + 1}) {answers[i]}")
    else:
        answers = choices
        for i, choice in enumerate(answers):
            print(f"{i + 1}) {choice}")

    print(f"To pick, enter a number of a selection above, from 1 to {len(choices)}")

    try:
        value = int(interactive_text_input(end_prompt, default))
    except ValueError:
        print(f"** Invalid Selection, must be a number. Try again **")
        return input_choices(header, end_prompt, choices, default)

    if value < 1 or value > (len(choices) + 1):
        print(f"** Invalid Selection. Try again **")
        return input_choices(header, end_prompt, choices, default)

    return list(answers)[int(value - 1)]


def interactive_list_entry(init_message: str, additional_msg: str, default: str) -> \
    List[str]:
    items = []
    first_item = interactive_text_input(init_message,
                                        default=default,
                                        allow_blank=False)

    items.append(first_item)
    while interactive_yes_no_input(additional_msg, "n"):
        additional_item = interactive_text_input(init_message,
                                                 default=default,
                                                 allow_blank=False)
        items.append(additional_item)

    return items


def interactive_dict_entry(init_message: str, additional_msg: str, default: str) -> \
    dict:
    map = {}

    first_key = interactive_text_input(init_message,
                                       default=default,
                                       allow_blank=False)

    first_value = interactive_text_input(f"'{first_key}' value",
                                         default=None,
                                         allow_blank=False)

    map[first_key] = first_value
    while interactive_yes_no_input(additional_msg, "n"):
        add_key = interactive_text_input(init_message,
                                         default=default,
                                         allow_blank=False)

        add_val = interactive_text_input("Value",
                                         default=None,
                                         allow_blank=False)

        map[add_key] = add_val

    return map
