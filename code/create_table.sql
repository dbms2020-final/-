CREATE TABLE users (
    user_id VARCHAR PRIMARY KEY,
    name VARCHAR,
    password VARCHAR
);

CREATE TABLE book (
    book_id VARCHAR PRIMARY KEY,
    name VARCHAR,
    state BOOLEAN
);

CREATE TABLE CD (
    CD_id VARCHAR PRIMARY KEY,
    name VARCHAR,
    state BOOLEAN
);

CREATE TABLE library (
    library_id VARCHAR PRIMARY KEY,
    name VARCHAR,
    address VARCHAR,
    open_time TIME,
    close_time TIME
);

CREATE TABLE room (
    library_id VARCHAR,
    room_id VARCHAR,
    state BOOLEAN
);

CREATE TABLE item_placed (
    library_id VARCHAR,
    item_type VARCHAR,
    item_id VARCHAR,
    floor INTEGER,
    coordinate POINT
);

CREATE TABLE book_borrow (
    bood_id VARCHAR,
    user_id VARCHAR,
    lend_date DATE,
    estimated_return DATE,
    state BOOLEAN,
    exact_return DATE
);

CREATE TABLE CD_borrow (
    CD_id VARCHAR,
    user_id VARCHAR,
    lend_date DATE,
    estimated_return DATE,
    state BOOLEAN,
    exact_return DATE
);

CREATE TABLE room_borrow (
    library_id VARCHAR,
    room_id VARCHAR,
    user_id VARCHAR,
    start_time TIME,
    end_time TIME
);
