from typing import Coroutine


def update_fields(obj: object, data_dict: dict, data_to_obj_fields: dict = None):
    """Function that uses setattr to mass update fields in an object. i.e instead of calling things like
    player.name = ...
    player.lp = ...
    ...
    You can call this function to do it with one line (only having to create the dicts before)

    Args:
        obj (object): The object that will be updated. It is usually a Django ORM object.
        data_dict (dict): The dictionary with the data to update. It's keys must be field names, and it's values will be the values that will be set.
        data_to_obj_fields (dict, Optional): Optional parameter for when the names of the fields are different between the dict and the object.
                                            Maps the keys (data_dict keys) to values (obj field names)
                                            Defaults to a dict that has the keys of data_dict mapped to itself (as in, both objects have the same fields.)

    Raises:
        KeyError: Throws an error if the field wasn't found.
    """

    if data_to_obj_fields is None:
        data_to_obj_fields = dict([tuple([x, x]) for x in data_dict.keys()])

    for field in data_to_obj_fields.keys():
        if field in data_dict.keys() and hasattr(obj, data_to_obj_fields[field]):
            setattr(obj, data_to_obj_fields[field], data_dict[field])
        else:
            print("Couldn't find dict field {0} or object field {1}", field, data_to_obj_fields[field])
            raise KeyError


async def async_wrapper(func: Coroutine, *args, **kwargs):
    """Function that wraps and awaits an awaitable function.
    Mostly used so I can do asyncio.run() of things like asyncio.gather() in sync functions.

    Args:
        func (Coroutine): The async function to await.

    Returns:
        _type_: Whatever that function returns.
    """
    return await func(*args, **kwargs)
