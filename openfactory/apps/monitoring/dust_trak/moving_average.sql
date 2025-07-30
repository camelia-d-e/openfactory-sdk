CREATE TABLE pm1_concentration_moving_average AS
SELECT
    ID,
    AVG(CAST(VALUE AS DOUBLE)) AS average_value,
    TIMESTAMPTOSTRING(WINDOWEND, 'yyyy-MM-dd''T''HH:mm:ss[.nnnnnnn]', 'Canada/Eastern') AS TIMESTAMP
FROM device_stream_dusttrak
WINDOW HOPPING (SIZE 10 SECONDS, ADVANCE BY 5 SECONDS)
WHERE id = 'pm1_concentration'
GROUP BY id
EMIT CHANGES;

CREATE TABLE pm2_5_concentration_moving_average AS
SELECT
    ID,
    AVG(CAST(VALUE AS DOUBLE)) AS average_value,
    TIMESTAMPTOSTRING(WINDOWEND, 'yyyy-MM-dd''T''HH:mm:ss[.nnnnnnn]', 'Canada/Eastern') AS TIMESTAMP
FROM device_stream_dusttrak
WINDOW HOPPING (SIZE 10 SECONDS, ADVANCE BY 5 SECONDS)
WHERE id = 'pm2_5_concentration'
GROUP BY id
EMIT CHANGES;

CREATE TABLE pm4_concentration_moving_average AS
SELECT
    ID,
    AVG(CAST(VALUE AS DOUBLE)) AS average_value,
    TIMESTAMPTOSTRING(WINDOWEND, 'yyyy-MM-dd''T''HH:mm:ss[.nnnnnnn]', 'Canada/Eastern') AS TIMESTAMP
FROM device_stream_dusttrak
WINDOW HOPPING (SIZE 10 SECONDS, ADVANCE BY 5 SECONDS)
WHERE id = 'pm4_concentration'
GROUP BY id
EMIT CHANGES;

CREATE TABLE pm10_concentration_moving_average AS
SELECT
    ID,
    AVG(CAST(VALUE AS DOUBLE)) AS average_value,
    TIMESTAMPTOSTRING(WINDOWEND, 'yyyy-MM-dd''T''HH:mm:ss[.nnnnnnn]', 'Canada/Eastern') AS TIMESTAMP
FROM device_stream_dusttrak
WINDOW HOPPING (SIZE 10 SECONDS, ADVANCE BY 5 SECONDS)
WHERE id = 'pm10_concentration'
GROUP BY id
EMIT CHANGES;