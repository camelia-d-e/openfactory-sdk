CREATE TABLE time_series_frequencyX WITH (KAFKA_TOPIC='time_series_fx')
AS
SELECT
    ID,
    COLLECT_LIST(VALUE) AS value_list,
    COLLECT_LIST(TIMESTAMPTOSTRING(ROWTIME, 'yyyy-MM-dd''T''HH:mm:ss[.nnnnnnn]', 'Canada/Eastern')) AS timestamps
FROM assets_stream
WINDOW HOPPING (SIZE 20 SECONDS, ADVANCE BY 10 SECONDS)
WHERE ASSET_UUID = 'WTVB01' AND TYPE IN ('Events', 'Condition', 'Samples') AND VALUE != 'UNAVAILABLE' AND id = 'hx'
GROUP BY ID
EMIT CHANGES;

CREATE STREAM spectrogram_stream_fx (key VARCHAR, spectrogram_data ARRAY<ARRAY<DOUBLE>>) WITH (KAFKA_TOPIC='spectrogram_stream_fx', VALUE_FORMAT='JSON', PARTITIONS=1);