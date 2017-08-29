from .. import dict_utils


def computed_address_field(field):
    """Gets Contact address from Company is address_same_as_company."""
    def get_field(contact):
        if contact.address_same_as_company:
            company = contact.company
            if company.has_valid_trading_address():
                return getattr(company, f'trading_{field}')

            return getattr(company, f'registered_{field}')

        return getattr(contact, field)

    def get_id_name_field(contact):
        id_name_field = get_field(contact)
        if id_name_field is None:
            return None
        return dict_utils.id_name_dict(id_name_field)

    if field == 'address_country':
        return get_id_name_field

    return get_field
