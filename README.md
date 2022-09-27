# blueink-client-python-examples
This repo should provide some practical examples for getting started with the 
[BlueInk Python module](https://github.com/blueinkhq/blueink-client-python); in particular interacting with the Client,
using the BundleHelper and PersonHelper to build Bundles and Persons respectfully.

Currently, these examples are built and tested to blueink-client-python v0.9.3

## Usage
### Requisite Python Packages
Install ```blueink-client-python``` from PyPI:
```shell
pip3 install blueink-client-python 
```
The PyPI page can be found [here](https://pypi.org/project/blueink-client-python/).

You will need to set these environment variables before you can run ``main.py``:
 * ```PYTHONUNBUFFERED=1;```
 * ```BLUEINK_PRIVATE_API_KEY=[YOUR API KEY]```

Usage is through a CLI menu. Default values for prompts are suggested in [brackets]. Pressing enter will use the default
value. Otherwise enter a selection. 
## Features
The example ran through executing ```main.py``` contains two major examples, one for interacting with Bundle endpoints,
one for interacting with Person endpoints.

The beginning prompt looks something like this and from there you can enter into either example script.
```
BlueInk Python Client Examples
1) Bundle Example
2) Person Example
To pick, enter a number of a selection above, from 1 to 2
Your Selection [1]: 
```

### Bundle Example
This example will walk through creating a Bundle (through the ```BundleHelper``` class) and either printing out a preview or sending it off to BlueInk to be
created.

```
Main Menu
1) Setup a Bundle
2) Add a Document
3) Add a Signer
4) Add a Field
5) Rolling Summary
6) Print Bundle JSON
7) Send Bundle
8) List all Bundles
9) List Bundles, filtered
To pick, enter a number of a selection above, from 1 to 9
Your Selection [1]: 
```

Options (8) and (9) are to demonstrate listing of Bundles. Option (8) allows for either regular list call or using the
paginated option. Option 9 will demonstrate filtering by user-selected status.

### Person Example
This example demonstrates basic CRUD operations on a Person, through the ```PersonHelper``` class as well as simple
listing.

```
Main Menu
1) Create a Person
2) List Persons
3) Update a person
4) Delete a Person
To pick, enter a number of a selection above, from 1 to 4
Your Selection [1]: ```