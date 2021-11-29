DELIMITER //
DROP PROCEDURE IF EXISTS CalculateLibraryFeeAndScores //
CREATE PROCEDURE CalculateLibraryFeeAndScores(IN currentUser INT, OUT total_late_fee REAL, OUT score REAL)
BEGIN
    DECLARE due_date DATE;
    DECLARE curr_date DATE default CURDATE();
    DECLARE return_date DATE;
    DECLARE late_fee REAL;
    DECLARE is_buyable BOOL;
    
    DECLARE fee REAL default 0;
    DECLARE checked_out_books REAL;
    DECLARE returned_books REAL;

    DECLARE bb_cur CURSOR FOR SELECT DueDate, LateFee, Buyable, ReturnDate FROM BorrowedBook NATURAL JOIN LibraryBook WHERE UserID = currentUser;

    OPEN bb_cur;
    BEGIN
        DECLARE exit_flag BOOLEAN DEFAULT FALSE;
        DECLARE CONTINUE HANDLER FOR NOT FOUND SET exit_flag = TRUE;

        cloop: LOOP
            FETCH bb_cur INTO due_date, late_fee, is_buyable, return_date;
            
            IF exit_flag THEN LEAVE cloop;
            END IF;

            IF return_date is NULL AND NOT is_buyable AND curr_date > due_date THEN
				SET fee = fee + DATEDIFF(curr_date, due_date) * late_fee;
            END IF;
            
        END LOOP cloop;
    END;
	
    CLOSE bb_cur;
    
    SELECT SUM(t.cnt) FROM (
        SELECT COUNT(*) cnt FROM BorrowedBook WHERE UserID = currentUser GROUP BY YEAR(DueDate) order by YEAR(DueDate) DESC LIMIT 3) as t
	INTO checked_out_books;

    SELECT SUM(t.cnt) FROM (
        SELECT COUNT(*) cnt FROM BorrowedBook WHERE UserID = currentUser and ReturnDate <= DueDate GROUP BY YEAR(DueDate) order by YEAR(DueDate) DESC LIMIT 3) as t
	INTO returned_books;

    SELECT fee INTO total_late_fee;
    SELECT returned_books / checked_out_books INTO score;
END //
DELIMITER ;


DELIMITER //
DROP TRIGGER IF EXISTS CheckoutTrigger //
CREATE TRIGGER CheckoutTrigger
BEFORE INSERT ON BorrowedBook
FOR EACH ROW
BEGIN
	CALL CalculateLibraryFeeAndScores(new.UserID, @late_fee, @score);
    IF @late_fee > 10.00 OR @score < 0.2 THEN
		SET new.DueDate = DATE_ADD(CURDATE(), INTERVAL 7 DAY);
    END IF;
END //
DELIMITER ;