def format_record(record: list):

    return '''("{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}",
    "{}","{}",cast("{}" as datetime),"{}","{}","{}","{}","{}")'''.format(*record)

def create_statement(data: list) -> str:
    query = """
    REPLACE INTO `parser/travelata_raw`(
        title, href, location, distances, 
        rating, reviews, less_places, 
        num_stars, orders_count, criteria,
        price, oil_tax, attributes, created_dttm,
        website, link, offer_hash, key, bucket)
    VALUES
    {}
    """.format(',\n'.join(map(format_record, data)))

    return query

def create_queries(data):

    queries = []
    for i in range(len(data) // 10 + 1):
        sub_data = data[i * 10: (i + 1) * 10]
        if len(sub_data) > 0:
            queries.append(
                create_statement(data[i * 10: (i + 1) * 10])
            )
    return queries