from .es import index_property, remove_property


def handle_property_created(payload):
    index_property(payload)


def handle_property_updated(payload):
    index_property(payload)


def handle_property_deleted(payload):
    remove_property(payload["propertyId"])


HANDLERS = {
    "PropertyCreated": handle_property_created,
    "PropertyUpdated": handle_property_updated,
    "PropertyDeleted": handle_property_deleted,
}
