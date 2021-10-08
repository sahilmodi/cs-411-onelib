CREATE TABLE Book (
    ISBN INT PRIMARY KEY, 
    Title VARCHAR(255) NOT NULL,
    Author VARCHAR(255) NOT NULL,
    ImageURL VARCHAR(4096), 
    Publisher VARCHAR(255)
);

CREATE TABLE Library (
    LibraryID INT PRIMARY KEY, 
    LibraryName VARCHAR(255),
    Zipcode INT NOT NULL,
    Address VARCHAR(4096)
);

CREATE TABLE User (
    UserID INT PRIMARY KEY, 
    Name VARCHAR(255),
    Age INT, 
    Zipcode INT NOT NULL, 
    PaymentNumber INT,
    Password VARCHAR(255) NOT NULL
);

CREATE TABLE LibraryBook (
    LibraryID INT,
    ISBN INT,
    Quantity INT NOT NULL,
    LateFee REAL,
    Price REAL,
    Buyable BOOL,
    TimeLimitDays REAL,
    FOREIGN KEY (LibraryID) REFERENCES Library(LibraryID) ON DELETE CASCADE,
    FOREIGN KEY (ISBN) REFERENCES Book(ISBN) ON DELETE CASCADE,
    PRIMARY KEY (LibraryID, ISBN)
);

CREATE TABLE Review (
    UserID INT, 
    ISBN INT,
    Time TIME,
	Text VARCHAR(4096),
	StarRating INT,
    FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE,
    FOREIGN KEY (ISBN) REFERENCES Book(ISBN) ON DELETE CASCADE,
    PRIMARY KEY (UserID, ISBN)
);
