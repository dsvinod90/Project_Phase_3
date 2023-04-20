-- Referential integrity constraints
ALTER TABLE album_artist
  DROP CONSTRAINT fk_album_artist_album,
  DROP CONSTRAINT fk_album_artist_artist,
  ADD CONSTRAINT fk_album_artist_album
    FOREIGN KEY (album_id)
    REFERENCES album (id)
    ON DELETE CASCADE,
  ADD CONSTRAINT fk_album_artist_artist
    FOREIGN KEY (artist_id)
    REFERENCES artist (id)
    ON DELETE CASCADE;

ALTER TABLE track_artist
  DROP CONSTRAINT fk_track_artist_artist,
  DROP CONSTRAINT fk_track_artist_track,
  ADD CONSTRAINT fk_track_artist_artist
    FOREIGN KEY (artist_id)
    REFERENCES artist (id)
    ON DELETE CASCADE,
  ADD CONSTRAINT fk_track_artist_track
    FOREIGN KEY (track_id)
    REFERENCES track (id)
    ON DELETE CASCADE;

ALTER TABLE track_playlist
  DROP CONSTRAINT fk_track_playlist_playlist,
  DROP CONSTRAINT fk_track_playlist_track,
  ADD CONSTRAINT fk_track_playlist_playlist
    FOREIGN KEY (playlist_id)
    REFERENCES playlist (playlist_id)
    ON DELETE CASCADE,
  ADD CONSTRAINT fk_track_playlist_track
    FOREIGN KEY (track_id)
    REFERENCES track (id)
    ON DELETE CASCADE;

ALTER TABLE track
  DROP CONSTRAINT fk_track_album,
  ADD CONSTRAINT fk_track_album
    FOREIGN KEY (album_id)
    REFERENCES album (id)
    ON DELETE CASCADE;