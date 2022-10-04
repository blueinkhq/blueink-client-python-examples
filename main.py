from munch import Munch

from examples.example_utils import input_choices
from examples.person_example import ClientPersonExample
from blueink import Client
from examples.bundle_example import ClientBundleExample

MAIN_CHOICES = Munch(
    bdl="Bundle Example",
    prs="Person Example"
)

client = Client()
main_choice = input_choices("BlueInk Python Client Examples",
                            "Your Selection",
                            MAIN_CHOICES,
                            1)

if main_choice == MAIN_CHOICES.bdl:
    example = ClientBundleExample(client)
elif main_choice == MAIN_CHOICES.prs:
    example = ClientPersonExample(client)

example.start()
