-- Return the Top 10 books that have the most number of 5 stars reviews in recent 2 years.

(
    SELECT Title, YEAR(Date) AS Year 
    FROM Review NATURAL JOIN Book 
    WHERE StarRating=5 AND YEAR(Date)=2021 
    GROUP BY ISBN, YEAR(Date) 
    ORDER BY COUNT( * ) DESC LIMIT 10
)
UNION ALL
(
    SELECT Title, YEAR(Date) AS Year 
    FROM Review NATURAL JOIN Book 
    WHERE StarRating=5 AND YEAR(Date)=2020 
    GROUP BY ISBN, YEAR(Date) 
    ORDER BY COUNT( * ) DESC LIMIT 10
) LIMIT 15;

-- Return the Top 10 Users who have the most number of reviews in recent 2 years.
 
(
    SELECT Name, YEAR(Date)
    FROM Review NATURAL JOIN User
    WHERE YEAR(Date)=2021
    GROUP BY Review.UserID, YEAR(Date)
    ORDER BY COUNT(*) DESC LIMIT 10
)
UNION ALL
(
    SELECT Name, YEAR(Date)
    FROM Review NATURAL JOIN User
    WHERE YEAR(Date)=2020
    GROUP BY Review.UserID, YEAR(Date)
    ORDER BY COUNT(*) DESC LIMIT 10
) LIMIT 15;
