\copy lab.Article FROM '~/dev/db/creator/created/articles.csv' DELIMITER ',' CSV HEADER;
\copy lab.Owner FROM '~/dev/db/creator/created/owners.csv' DELIMITER ',' CSV HEADER;
\copy lab.Car FROM '~/dev/db/creator/created/cars.csv' DELIMITER ',' CSV HEADER;
\copy lab.Camera FROM '~/dev/db/creator/created/cameras.csv' DELIMITER ',' CSV HEADER;
\copy lab.Fine FROM '~/dev/db/creator/created/fines.csv' DELIMITER ',' CSV HEADER;
