from kraken_schema_org.class_kraken_schema_org import Schema_org




s = Schema_org()

def normalize_type(record_type):

    return s.normalize_record_type(record_type)


def normalize_key(key):

    return s.normalize_key(key)


def get_keys(record_type):

    return s.get_keys(record_type)


def get_datatype(record_type, key):

    return s.get_datatype(record_type, key)


