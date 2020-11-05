import os
import json
from datetime import datetime, timedelta
from os import sys, path



from core.postgres_client import PostgresClient



def query_get_request_data(request):
    """get site_id by site_name from postgres"""
    query = """
        SELECT request_id, request, last_updated, risk, total_voting, classification, link
        FROM reports
        WHERE request LIKE '{request}'
        """.format(request=request)
    return query



def query_counter_requests(data):
    query_string = """
    INSERT INTO requests (
        request_id, date, number_of_requests
        )
    VALUES (
    '{request_id}'::integer,
    NOW(),
    '{number_of_requests}'::integer,
    )
    ON CONFLICT (request_id, date)
    DO UPDATE
    SET number_of_requests = requests.number_of_requests+1
    RETURNING *;
    """
    return query_string.format(**data)



def query_insert_new_request(data):
    query_string = """
    INSERT INTO reports (
        request, last_updated, risk, total_voting, classification, link
        )
    VALUES (
    '{request}'::text,
    NOW(),
    '{risk}'::text,
    '{total_voting}'::jsonb,
    '{classification}'::jsonb,
    '{link}'::text
    )
    ON CONFLICT DO NOTHING
    RETURNING *;
    """
    return query_string.format(**data)


def query_update_request(data):
    query_string = """
        UPDATE reports AS t
        SET last_updated=c.last_updated,
            risk=c.risk,
            total_voting=c.total_voting,
            classification=c.classification
        FROM (
            SELECT a.request_id,
                   a.last_updated,
                   a.risk,
                   a.total_voting,
                   a.classification
            FROM(
                    VALUES('{request_id}'::integer,
                            NOW(),
                            '{risk}'::text,
                            '{total_voting}'::jsonb,
                            '{classification}'::jsonb
                            )
                ) AS a(request_id, last_updated, risk, total_voting, classification)
                INNER JOIN reports b
                        ON (a.request_id=b.request_id)
            ) AS c(request_id, last_updated, risk, total_voting, classification)
        WHERE c.request_id=t.request_id
        RETURNING *;
    """
    return query_string.format(**data)


class PG:
    def __init__(self):
        self.pg_client = PostgresClient(
            dsn="postgres://docker:docker@localhost:5400/sites_checker_service"
            )
        self.queries = {
            "query_get_request_data": query_get_request_data,
            "query_insert_new_request": query_insert_new_request,
            "query_update_request": query_update_request,
            "query_counter_requests": query_counter_requests,
        }

    def from_postges_get_request(self, request):
        """from_postges_get_request"""
        result = tuple(self.pg_client.select(
            self.queries['query_get_request_data'](request)))

        return dict(result[0]) if result and len(result) > 0 else None


    def counter_of_request(self, data):
        result = tuple(self.pg_client.insert(
            self.queries['query_counter_requests'](data)))

        return dict(result[0])

    def postges_request(self, query_function, data):
        query = query_function(data)
        result = tuple(self.pg_client.insert(query))
        return dict(result[0])
