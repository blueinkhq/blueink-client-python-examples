import copy
from pprint import pprint
from random import choice as random_choice
from typing import List

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


class PersonExampleModel:
    def __init__(self, client: Client):
        """ Examples of using PersonHelper and some simple calls to retrieve/update/list Persons using the Client.
        """
        self._client = client

    def setup_person_helper(self, name: str, phones: List[str], emails: List[str], metadata=None):
        """ One-liner example of setting up PersonHelper
        """
        if metadata:
            return PersonHelper(name=name, metadata=metadata, phones=phones, emails=emails)
        else:
            return PersonHelper(name=name, phones=phones, emails=emails)

    def call_create_person(self, helper: PersonHelper):
        """Example network call to create a person via PersonHelper
        """
        try:
            response = self._client.persons.create_from_person_helper(helper)
            print(response.data)
        except HTTPError as e:
            print(f"Failed to create person, HTTP {e.errno}: {e.response.content}")
        print("Example Concluded. To create a new Person, start the example script again.")
        exit()

    def call_list_persons(self, show_metadata: bool, print_people_data=True):
        """Example call to list out Person data.

        Returns:
             collection of persons
        """
        resp = self._client.persons.list()
        if resp.status == 200:
            print(f"Total Persons: {len(resp.data)}")
        else:
            print(f"Response error: HTTP {resp.status}")
            return []

        if print_people_data:
            for person in resp.data:
                print(f"  - Person {person.id}: {person.name}")
                if show_metadata:
                    print(f"     meta:")
                    pprint(person.metadata)

        return resp.data

    def call_delete_person(self, person_id: str) -> bool:
        """Example call to delete a person by ID number
        """
        try:
            first_del_res = self._client.persons.delete(person_id)
            print(f"Successfully deleted person: {person_id}")
            return True
        except HTTPError as e:
            print(f"Failed to delete person with ID == {person_id}, "
                  f" HTTP {e.errno}: {e.response.content}")
            return False

    def call_update_person(self, person_id, data):
        """Example call to update a Person
        """
        try:
            response = self._client.persons.update(person_id=person_id,
                                                   data=data,
                                                   partial=True)
            print(f"Successfully updated person with id {person_id}")

            print(response.data)

        except HTTPError as e:
            print(f"Failed to update person with ID {person_id}, "
                  f" HTTP {e.errno}: {e.response.content}")


class ClientPersonExample(BaseExample, PersonExampleModel):
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
        """ CLI UI Controller for Person Example.

        For network calls / interactions with the PersonHelper, see above PersonExampleModel
        """
        BaseExample.__init__(self)
        PersonExampleModel.__init__(self, client)

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
            self.call_create_person(person_helper)
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
        metadata = None
        if add_metadata:
            metadata = interactive_dict_entry("Metadata Key",
                                              "Add more Metadata?",
                                              "key")
        ph = self.setup_person_helper(name, phones, emails, metadata=metadata)

        self.person_menu(ph)

    def list_persons(self):
        show_metadata = interactive_yes_no_input("Show Metadata?")
        self.call_list_persons(show_metadata)
        self.main_router()

    def delete_person(self):
        persons = self.call_list_persons(False, False)
        if len(persons) == 0:
            print("No Persons found. Returning to main menu")
            self.main_router()

        people_by_id = {}
        for person in persons:
            people_by_id[person.id] = (person.id, person.name)

        first_delete = input_choices("Delete Person",
                                     "Which Person",
                                     people_by_id,
                                     default=1)
        first_id = first_delete[0]
        first_name = first_delete[1]
        print(f"Attempting to delete '{first_name}' by ID '{first_id}'")

        if self.call_delete_person(first_id):
            people_by_id.pop(first_id)

        while interactive_yes_no_input("Delete more Persons", "n"):
            another_delete = input_choices("Delete Person",
                                           "Which Person",
                                           people_by_id,
                                           default=1)

            another_id = another_delete[0]
            if self.call_delete_person(another_id):
                people_by_id.pop(first_id)

        self.main_router()

    def update_person(self):
        persons = self.call_list_persons(False, False)
        if len(persons) == 0:
            print("No Persons found. Returning to main menu")
            self.main_router()

        person_name_by_id = {}
        person_data_by_id = {}
        for person in persons:
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

        self.call_update_person(update_id, new_data)
        self.main_router()

    def print_person(self, person_helper: PersonHelper):
        if person_helper is None:
            print("** Person not yet configured. Please build a person**")
            self.main_router()

        pprint(person_helper.as_dict())
        self.person_menu(person_helper)
