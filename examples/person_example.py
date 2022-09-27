import copy
from pprint import pprint
from random import choice as random_choice

from munch import Munch
from requests import HTTPError

from examples.example_utils import (
    interactive_text_input, interactive_yes_no_input, input_choices,
    interactive_list_entry, interactive_dict_entry, BaseExample
)
from blueink import Client
from blueink.person_helper import PersonHelper

FNAMES = ["HOMER", "MARGE", "LISA", "BART", "MOE", "FRED", "GORDON", "BARNEY", "ELI"]
LNAMES = ["SIMPSON", "FLANDERS", "FREEMAN", "CALHOUN", "VANCE"]


class ClientPersonExample(BaseExample):
    MAIN_CHOICES = Munch(
        crt="Create a Person",
        lst="List Persons",
        upd="Update a person",
        dlt="Delete a Person",
    )
    TERMINAL_CHOICES = Munch(
        prt="Print Person Data",
        snd="Send Person to Server",
        ext="Exit to Main Menu",
    )

    def __init__(self, client: Client):
        self.client = client

    def start(self):
        print("BlueInk API Client Example: Person Helper")
        print("(C) BlueInk 2022")
        print("\n")
        self.main_router()

    def main_router(self):
        choice = input_choices(
            header="\nMain Menu",
            end_prompt="Your Selection",
            choices=self.MAIN_CHOICES.values(),
            default=1
        )
        print("Your choice: `" + choice + "`")

        if choice == self.MAIN_CHOICES.crt:
            self.create_person()
        elif choice == self.MAIN_CHOICES.lst:
            self.list_persons()
        elif choice == self.MAIN_CHOICES.dlt:
            self.delete_person()
        elif choice == self.MAIN_CHOICES.upd:
            self.update_person()

    def person_menu(self, person_helper: PersonHelper):
        choice = input_choices(
            header="\nPerson Menu",
            end_prompt="Your Selection",
            choices=self.TERMINAL_CHOICES.values(),
            default=1
        )
        print("Your choice: `" + choice + "`")

        if choice == self.TERMINAL_CHOICES.prt:
            self.print_person(person_helper)
        elif choice == self.TERMINAL_CHOICES.snd:
            self._create_person(person_helper)
        elif choice == self.TERMINAL_CHOICES.ext:
            self.main_router()

    def create_person(self):
        fname = interactive_text_input("First Name", random_choice(FNAMES),
                                       allow_blank=False)
        lname = interactive_text_input("Last Name", random_choice(LNAMES),
                                       allow_blank=False)
        name = f"{fname} {lname}"

        phones = interactive_list_entry("Add Phone Number (format xxx xxx xxxx)",
                                        "Add another phone number?",
                                        "505 555 5555")

        if interactive_yes_no_input("Add emails", "n"):
            emails = interactive_list_entry("Add email address",
                                            "Add another email address?",
                                            "jeff.gordon@nascar.com")
        else:
            emails = []

        add_metadata = interactive_yes_no_input("Add metadata?")
        if add_metadata:
            md = interactive_dict_entry("Metadata Key",
                                        "Add more Metadata?",
                                        "key")
            ph = PersonHelper(name=name, metadata=md, phones=phones, emails=emails)
        else:
            ph = PersonHelper(name=name, phones=phones, emails=emails)

        self.person_menu(ph)

    def list_persons(self):
        show_metadata = interactive_yes_no_input("Show Metadata?")

        resp = self.client.persons.list()
        print(f"Response Code: {resp.status}")
        if resp.status == 200:
            print(f"Total Persons: {len(resp.data)}")
        else:
            print(f"Response error: HTTP {resp.status}")
            self.main_router()

        for person in resp.data:
            print(f"  - Person {person.id}: {person.name}")
            if show_metadata:
                print(f"     meta:")
                pprint(person.metadata)
        self.main_router()

    def delete_person(self):
        list_resp = self.client.persons.list()
        print(f"Fetch List Response Code: {list_resp.status}")
        if list_resp.status == 200:
            print(f"Total Persons: {len(list_resp.data)}")
        else:
            print(f"Response error: HTTP {list_resp.status}")
            self.main_router()

        people_by_id = {}
        for person in list_resp.data:
            people_by_id[person.id] = (person.id, person.name)

        first_delete = input_choices("Delete Person",
                                     "Which Person",
                                     people_by_id,
                                     default=1)
        first_id = first_delete[0]
        first_name = first_delete[1]
        print(f"Attempting to delete '{first_name}' by ID '{first_id}'")

        try:
            first_del_res = self.client.persons.delete(first_id)
            print(f"Successfully deleted person '{first_name}': {first_del_res.data}")
            people_by_id.pop(first_id)
        except HTTPError as e:
            print(f"Failed to delete person with ID {first_id} ({first_name}), "
                  f" HTTP {e.errno}: {e.response.content}")

        while interactive_yes_no_input("Delete more Persons", "n"):
            another_delete = input_choices("Delete Person",
                                         "Which Person",
                                         people_by_id,
                                         default=1)

            another_id = another_delete[0]
            another_name = another_delete[1]
            try:
                another_del_res = self.client.persons.delete(another_id)
                print(f"Successfully deleted person '{another_name}': {another_del_res.data}")
                people_by_id.pop(another_id)
            except HTTPError as e:
                print(f"Failed to delete person with ID {another_id} ({another_name}), "
                      f" HTTP {e.errno}: {e.response.content}")

        self.main_router()

    def update_person(self):
        list_resp = self.client.persons.list()
        print(f"Fetch List Response Code: {list_resp.status}")
        if list_resp.status == 200:
            print(f"Total Persons: {len(list_resp.data)}")
        else:
            print(f"Response error: HTTP {list_resp.status}")
            self.main_router()

        person_name_by_id = {}
        person_data_by_id = {}
        for person in list_resp.data:
            person_name_by_id[person.id] = (person.id, person.name)
            person_data_by_id[person.id] = person

        choice = input_choices("Update Person",
                                     "Which Person",
                                     person_name_by_id,
                                     default=1)
        update_id = choice[0]
        update_name = choice[0]
        data = copy.deepcopy(person_data_by_id[update_id])
        print(f"Updating {update_id} ({update_name})")

        new_data = {}
        for key in data.keys():
            value = data[key]

            # ignore more complex fields within the returned data; this is to illustrate
            # updating in general.
            if type(value) not in [int, str, float] or key == "id":
                continue

            print(f"Original value for key '{key}': {value}")
            change = interactive_yes_no_input(f"Change value of '{key}'")
            if change:
                correct_type = False

                while not correct_type:
                    new_val = interactive_text_input(f"New value ({type(value)}",
                                                     default=value,
                                                     allow_blank=False)

                    try:
                        if type(value) == int:
                            new_val = int(new_val)
                        elif type(value) == str:
                            new_val = str(new_val)
                        elif type(value) == float:
                            new_val = float(new_val)

                        correct_type = True
                        new_data[key] = new_val
                    except TypeError:
                        print(f"Incorrect type. Must be {type(value)}")
            else:
                any_further_changes = interactive_yes_no_input("Any further changes?", "y")
                if not any_further_changes:
                    break

        self._update_person(update_id, data=new_data)



    def print_person(self, person_helper: PersonHelper):
        if person_helper is None:
            print("** Person not yet configured. Please build a person**")
            self.main_router()

        pprint(person_helper.as_dict())
        self.person_menu(person_helper)

    def _update_person(self, person_id, data):
        try:
            response = self.client.persons.update(person_id=person_id,
                                                  data=data,
                                                  partial=True)
            print(f"Successfully updated person with id {person_id}")

            see_data = interactive_yes_no_input(
                "Would you like to see the returned data?")
            if see_data:
                print(response.data)

        except HTTPError as e:
            print(f"Failed to update person with ID {person_id}, "
                  f" HTTP {e.errno}: {e.response.content}")

        self.main_router()

    def _create_person(self, person_helper: PersonHelper):
        if person_helper is None:
            print("** Person not yet configured. Please build a person**")
            self.main_router()

        try:
            response = self.client.persons.create_from_person_helper(person_helper)
            see_data = interactive_yes_no_input("Would you like to see the returned data?")
            if see_data:
                print(response.data)

            print(
                "Example Concluded. To create a new Person, start the example script again.")
            exit()
        except HTTPError as e:
            print(f"Failed to create person, HTTP {e.errno}: {e.response.content}")
            print("Returning to main menu")
            self.main_router()


