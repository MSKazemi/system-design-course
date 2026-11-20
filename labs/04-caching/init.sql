-- Lumen product catalog: 100,000 rows. get_product() adds a fixed 20 ms delay to stand in for an
-- "expensive" query (joins, aggregation, a remote call). The delay is a labelled lab assumption.
CREATE TABLE products (
    id      integer PRIMARY KEY,
    name    text    NOT NULL,
    price   numeric(10, 2) NOT NULL,
    payload text    NOT NULL
);

INSERT INTO products (id, name, price, payload)
SELECT g, 'product-' || g, (g % 500) + 0.99, repeat(md5(g::text), 6)
FROM generate_series(1, 100000) AS g;

CREATE FUNCTION get_product(p_id integer)
RETURNS TABLE (id integer, name text, price numeric, payload text)
LANGUAGE sql AS $$
    SELECT pg_sleep(0.020);
    SELECT id, name, price, payload FROM products WHERE id = p_id;
$$;
