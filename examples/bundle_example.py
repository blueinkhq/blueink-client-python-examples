from pprint import pprint

from munch import Munch
from random import choice as random_choice
from random import randint

from requests import HTTPError

from examples.example_utils import interactive_text_input, interactive_yes_no_input, \
    input_choices, BaseExample
from blueink import Client, BundleHelper
from blueink.endpoints import BUNDLES as BUNDLE_ENDPOINTS
from blueink.constants import BUNDLE_STATUS

FNAMES = ["HOMER", "MARGE", "LISA", "BART", "MOE", "FRED", "GORDON", "BARNEY", "ELI"]
LNAMES = ["SIMPSON", "FLANDERS", "FREEMAN", "CALHOUN", "VANCE"]


class BundleExampleModel:
    def __init__(self, client: Client):
        """ Examples of using BundleHelper and some simple calls to list Bundles using the Client.
        """
        self._client = client

    def call_list_bundles(self):
        """Demonstration of listing of bundles. Non-paginated.
        """
        resp = self._client.bundles.list()

        if resp.status == 200:
            print(f"Total Bundles: {len(resp.data)}")
        else:
            print(f"Response Code: {resp.status}: {resp.data}")

        for bundle in resp.data:
            print(f"  - Bundle {bundle.id}: {bundle.label};"
                  f" status: {bundle.status}")

    def call_list_bundles_paginated(self):
        """Demonstration of using paginated calls to list Bundles.
        """
        print(f"A paginated call to '{BUNDLE_ENDPOINTS.LIST}', 5 per page...")
        iterator = self._client.bundles.paged_list(per_page=5)

        for resp in iterator:
            print(f"Page {resp.pagination.page_number} of {resp.pagination.total_pages}:")
            for bundle in resp.data:
                print(f"  - Bundle {bundle.id}: {bundle.label};"
                      f" status: {bundle.status}")

            last_page = resp.pagination.page_number == resp.pagination.total_pages
            keep_going = False if last_page else interactive_yes_no_input(
                "Next Page",
                default="y")

            if not keep_going:
                break

    def call_list_bundles_filtered(self, status):
        """Demonstration of listing of Bundles, using a query parameter.
        """
        # Also note, singular status can be queried as well:
        resp = self._client.bundles.list(status=status)
        print(f"Response Code: {resp.status}")

        if resp.status == 200:
            print(f"Total Bundles with status '{status}': {len(resp.data)}")

        for bundle in resp.data:
            print(f"  - Bundle {bundle.id}: {bundle.label};"
                  f" status: {bundle.status}")

    def call_send_bundle(self, helper: BundleHelper):
        """
        """
        try:
            response = self._client.bundles.create_from_bundle_helper(helper)
            print(f"Successfully sent bundle '{response.data['label']}'")
            print(response.data)
        except HTTPError as e:
            print(f"Response Status: {e.errno}: {e.response.content}")

    def helper_setup(self, label: str, email_subject: str, email_message: str) -> BundleHelper:
        helper = BundleHelper(label=label,
                              email_subject=email_subject,
                              email_message=email_message,
                              is_test=True)
        return helper

    def helper_add_signer(self, key, name, email, phone, deliver_via) -> str:
        packet_key = self.bundle_helper.add_signer(key=key,
                                                   name=name,
                                                   email=email,
                                                   phone=phone,
                                                   deliver_via=deliver_via)
        return packet_key

    def helper_add_document_url(self, helper: BundleHelper, url: str):
        return helper.add_document_by_url(url)

    def helper_add_document_filepath(self, helper: BundleHelper, path: str):
        return helper.add_document_by_path(path)

    def helper_add_document_template(self, helper: BundleHelper, template_id: str):
        return helper.add_document_template(template_id)

    def helper_add_field(self, helper: BundleHelper, doc_key, x, y, w, h, p, kind, label, assigned_editors):
        return helper.add_field(doc_key, x, y, w, h, p, kind,
                                label=label,
                                editors=assigned_editors)


class ClientBundleExample(BaseExample, BundleExampleModel):
    MAIN_CHOICES = Munch(
        bdl="Setup a Bundle",
        doc="Add a Document",
        sig="Add a Signer",
        fld="Add a Field",
        sum="Rolling Summary",
        prn="Print Bundle JSON",
        sen="Send Bundle",
        lba="List all Bundles",
        lbf="List Bundles, filtered"
    )
    DOC_CHOICES = Munch(
        file="Add Document by File Path",
        url="Add Document by URL",
        temp="Add Document by Template UUID",
    )
    DELIVERY_CHOICES = Munch(
        em="email",
        ph="phone",
    )
    LIST_CHOICES = Munch(
        reg="Regularly",
        pag="Paginated",
    )

    def __init__(self, client: Client):
        """ CLI UI Controller for Bundle Example.

        For network calls / interactions with the Bundle Helper, see above BundleExampleModel
        """
        BaseExample.__init__(self)
        BundleExampleModel.__init__(self, client)

        self.bundle_helper: BundleHelper = None

        self.doc_keys = set()
        self.signer_keys = set()
        self.field_keys = set()

    def start(self):
        print("BlueInk API Client Example: Bundle Helper")
        print("(C) BlueInk 2022")
        print("\n")
        self.main_router()

    def suggested_main_option(self):
        if not self.bundle_helper:
            return 1

        if len(self.doc_keys) == 0:
            return 2

        if len(self.signer_keys) == 0:
            return 3

        if len(self.field_keys) == 0:
            return 4

        return 6

    def main_router(self):
        choice = input_choices(
            header="\nMain Menu",
            end_prompt="Your Selection",
            choices=self.MAIN_CHOICES.values(),
            default=self.suggested_main_option()
        )
        print("Your choice: `" + choice + "`")

        if choice == self.MAIN_CHOICES.bdl:
            self.setup_bundle_helper()
        elif choice == self.MAIN_CHOICES.doc:
            self.add_document_interactive()
        elif choice == self.MAIN_CHOICES.sig:
            self.add_signer_interactive()
        elif choice == self.MAIN_CHOICES.fld:
            self.add_field_interactive()
        elif choice == self.MAIN_CHOICES.sum:
            self.summary()
        elif choice == self.MAIN_CHOICES.prn:
            self.print_bundle_json()
        elif choice == self.MAIN_CHOICES.sen:
            self.send_bundle()
        elif choice == self.MAIN_CHOICES.lba:
            self.list_all_bundles()
        elif choice == self.MAIN_CHOICES.lbf:
            self.list_filtered_bundles()

    def list_all_bundles(self):
        choice = input_choices("~~List all Bundles~~",
                               "Your Selection",
                               self.LIST_CHOICES.values(),
                               1)
        if choice == self.LIST_CHOICES.reg:
            self.call_list_bundles()
        else:
            self.call_list_bundles_paginated()

        self.main_router()

    def list_filtered_bundles(self):
        print("~~List Bundles, filtered by status~~")
        status = input_choices("Status Codes",
                               "Your Selection",
                               BUNDLE_STATUS,
                               1
                               )

        self.call_list_bundles_filtered(status)

        self.main_router()

    def summary(self):
        print("Documents Added:")
        for key in list(self.doc_keys):
            print(key)
        print("Signers Added:")
        for key in list(self.signer_keys):
            print(key)
        print("Fields Added to all Docs:")
        for key in list(self.field_keys):
            print(key)

        self.main_router()

    def setup_bundle_helper(self):
        if self.bundle_helper is not None:
            print("** Bundle already setup. Please pick another option **")
            self.main_router()

        print("~~Bundle Initial Setup~~")
        label = interactive_text_input("Bundle Label", "Test_Bundle", False)
        email_subject = interactive_text_input("Email Subject", allow_blank=True)
        email_message = interactive_text_input("Email Message", allow_blank=True)

        self.bundle_helper = self.helper_setup(label, email_subject, email_message)

        print("Bundle Configured!")
        self.main_router()

    def add_signer_interactive(self):
        if self.bundle_helper is None:
            print("** Bundle not yet configured. Please pick option 1**")
            self.main_router()

        print("~~Add a Signer~~")
        suggested_key = f"signer-{len(self.signer_keys) + 1}"
        key = interactive_text_input("Signer Key", suggested_key, allow_blank=False)

        fname = interactive_text_input("First Name", random_choice(FNAMES),
                                       allow_blank=False)
        lname = interactive_text_input("Last Name", random_choice(LNAMES),
                                       allow_blank=False)
        name = f"{fname} {lname}"

        deliver_via = input_choices("Select Delivery Method", "Your Selection",
                                    self.DELIVERY_CHOICES.values(), 1)

        require_email = True if deliver_via == self.DELIVERY_CHOICES.em else False
        email = interactive_text_input("Email Address",
                                       f"{fname}.{lname}@example.com",
                                       require_email
                                       )
        require_phone = True if deliver_via == self.DELIVERY_CHOICES.ph else False
        phone = interactive_text_input("Phone Number (format as: xxx xxx xxxx)",
                                       f"505 555 5555",
                                       require_phone
                                       )

        packet_key = self.helper_add_signer(key, name, email, phone, deliver_via)

        self.signer_keys.add(packet_key)

        print("Signer Added!")
        self.main_router()

    def add_document_interactive(self):
        if self.bundle_helper is None:
            print("** Bundle not yet configured. Please pick option 1**")
            self.main_router()

        choice = input_choices(
            header="~~Add a Document~~",
            end_prompt="How would you like to add a document?",
            choices=self.DOC_CHOICES.values(),
            default=2
        )

        if choice == self.DOC_CHOICES.url:
            file_url = interactive_text_input("URL to PDF",
                                              default="https://www.irs.gov/pub/irs-pdf/fw4.pdf",
                                              allow_blank=False)
            doc_key = self.helper_add_document_url(self.bundle_helper, file_url)

        elif choice == self.DOC_CHOICES.file:
            file_path = interactive_text_input("Path to PDF", allow_blank=False)
            doc_key = self.helper_add_document_filepath(self.bundle_helper, file_path)

        elif choice == self.DOC_CHOICES.temp:
            template_uuid = interactive_text_input("Template UUID", allow_blank=False)
            doc_key = self.helper_add_document_template(self.bundle_helper, template_uuid)

        self.doc_keys.add(doc_key)

        print("Document Added!")
        self.main_router()

    def add_field_interactive(self):
        if self.bundle_helper is None:
            print("** Bundle not yet configured. Please pick option 1**")
            self.main_router()

        if len(self.doc_keys) == 0:
            print("** Documents not yet added. Please add one or more documents **")
            self.main_router()

        if len(self.signer_keys) == 0:
            print("** Signers not yet added. Please add one or more Signers **")
            self.main_router()

        print("~~Add a Field~~")
        ordered_doc_keys = list(self.doc_keys)
        doc_key = input_choices("Which Document should this field go onto?",
                                "Your Selection",
                                ordered_doc_keys,
                                1
                                )
        kind = input_choices(
            "Field Type\n(Inexaustive, see documentation for more kinds)",
            "Your Selection",
            ["inp", "ini", "txt", "cbx", "sdt"],
            1
        )
        label = interactive_text_input("Label", "An Input Field", allow_blank=True)
        x = int(interactive_text_input("x loc", randint(0, 100), allow_blank=False))
        y = int(interactive_text_input("y loc", randint(0, 100), allow_blank=False))
        w = int(interactive_text_input("width", randint(0, 100), allow_blank=False))
        h = int(interactive_text_input("height", randint(0, 100), allow_blank=False))
        p = int(interactive_text_input("page", "1", allow_blank=False))

        assigned_editors = set()
        editor_choices = list(self.signer_keys)
        first_editor = input_choices("Assign a Signer to Field",
                                     "Signer choice",
                                     editor_choices,
                                     1
                                     )
        assigned_editors.add(first_editor)
        editor_choices.remove(first_editor)
        while interactive_yes_no_input("Add more signers", "n"):
            additional_editor = input_choices("Assign a Signer to Field",
                                              "Signer choice",
                                              editor_choices,
                                              1
                                              )
            assigned_editors.add(additional_editor)
            editor_choices.remove(additional_editor)

        key = self.helper_add_field(self.bundle_helper, doc_key, x, y, w, h, p, kind,
                                    label=label,
                                    assigned_editors=assigned_editors)
        self.field_keys.add(key)

        print("Field Added!")
        self.main_router()

    def print_bundle_json(self):
        if self.bundle_helper is None:
            print("** Bundle not yet configured. Please pick option 1**")
            self.main_router()

        pprint(self.bundle_helper.as_json())

        self.main_router()

    def send_bundle(self):
        if self.bundle_helper is None:
            print("** Bundle not yet configured. Please pick option 1**")
            self.main_router()

        self.call_send_bundle(self.bundle_helper)

        print("Example Concluded. To create a new bundle, start the example script again.")
        exit()
