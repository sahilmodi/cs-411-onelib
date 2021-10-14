CREATE TABLE Book (
    ISBN VARCHAR(13) PRIMARY KEY, 
    Title VARCHAR(256) NOT NULL,
    Author VARCHAR(256) NOT NULL,
    ImageURL VARCHAR(4096), 
    Publisher VARCHAR(256)
);

CREATE TABLE Library (
    LibraryID INT PRIMARY KEY, 
    Name VARCHAR(256),
    Zipcode VARCHAR(5) NOT NULL,
    Address VARCHAR(1024)
);

CREATE TABLE User (
    UserID INT PRIMARY KEY, 
    Name VARCHAR(256),
    Age INT, 
    Zipcode VARCHAR(5) NOT NULL, 
    PaymentNumber INT,
    Password VARCHAR(64) NOT NULL
);

CREATE TABLE LibraryBook (
    LibraryID INT,
    ISBN VARCHAR(13),
    Quantity INT NOT NULL,
    Buyable BOOL,
    LateFee REAL,
    Price REAL,
    TimeLimitDays REAL,
    FOREIGN KEY (LibraryID) REFERENCES Library(LibraryID) ON DELETE CASCADE,
    FOREIGN KEY (ISBN) REFERENCES Book(ISBN) ON DELETE CASCADE,
    PRIMARY KEY (LibraryID, ISBN)
);

CREATE TABLE Review (
    ISBN VARCHAR(13),
    UserID INT, 
    Date Date,
	StarRating INT,
	Text VARCHAR(4096),
    FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE,
    FOREIGN KEY (ISBN) REFERENCES Book(ISBN) ON DELETE CASCADE,
    PRIMARY KEY (UserID, ISBN)
);
