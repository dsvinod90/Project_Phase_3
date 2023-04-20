-- Create table L1 containing frequent itemsets of size 1
DROP TABLE IF EXISTS L1;
DROP TABLE IF EXISTS L2;
DROP TABLE IF EXISTS L3;
DROP TABLE IF EXISTS L4;
DROP TABLE IF EXISTS L5;

SELECT
	artist_id as artist_1,
	count(1)
INTO L1
FROM
	album_artist
GROUP BY
	artist_id
HAVING
	count(1) >= 5;