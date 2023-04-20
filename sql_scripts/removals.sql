-- Remove uris and null values from tables
DELETE FROM album
WHERE name ~ '[^[\x00-\x7F]]';

DELETE FROM playlist
WHERE name ~ '[^[\x00-\x7F]]';

DELETE FROM track
WHERE name ~ '[^[\x00-\x7F]]';

DELETE FROM artist
WHERE name ~ '[^[\x00-\x7F]]';

ALTER TABLE album 
    DROP COLUMN IF EXISTS album_uri;

DELETE FROM album 
WHERE name IS NULL;

DELETE FROM playlist
WHERE name IS NULL;

ALTER TABLE track
    DROP COLUMN IF EXISTS album_uri,
    DROP COLUMN IF EXISTS track_uri;

DELETE FROM track
WHERE name IS NULL;

ALTER TABLE artist
    DROP COLUMN IF EXISTS artist_uri;

DELETE FROM artist
WHERE name IS NULL;