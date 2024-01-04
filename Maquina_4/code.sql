CREATE TABLE User(
    username VARCHAR(50),
    password VARCHAR(50),
    email VARCHAR(50),
    admin INTEGER,
    PRIMARY KEY(username)
);

INSERT INTO User VALUES ('admin', 'ashfewbfvwhefew', 'admin@dspwpcv2.local', 1)
