       IDENTIFICATION DIVISION.
       PROGRAM-ID. ABH003.
       AUTHOR. TCSABH.
       ENVIRONMENT DIVISION.
       SPECIAL-NAMES.
           CONSOLE IS CRT.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WA-POS.
           05 WA-ROW     PIC 9(02) VALUE ZEROS.
           05 WA-COL     PIC 9(02) VALUE ZEROS.
       01  WA-DATE.
           05 WA-DD      PIC 9(02) VALUE ZEROS.
           88 WA-VAL-DD VALUES ARE 1 THRU 31.
           05 WA-MM      PIC 9(02) VALUE ZEROS.
           88 WA-VAL-MM  VALUES ARE 1 THRU 12.
           88 WA-30-MM   VALUES ARE 04 06 09 11.
           05 WA-YY      PIC 9(04) VALUE ZEROS.
           05 WA-YY-RE REDEFINES WA-YY.
              10 WA-YY-CC  PIC 9(02).
              10 WA-YY-YY  PIC 9(02).
       01  WA-D          PIC 9(04) VALUE ZEROS.
       01  WA-R          PIC 9(04) VALUE ZEROS.
       01  WA-ERR        PIC X(01) VALUE SPACES.
       LINKAGE SECTION.
       01  LS-DATE       PIC 9(08).
       01  LS-ERR        PIC X(01).
       PROCEDURE DIVISION USING LS-DATE LS-ERR.
       0000-BEGIN.
           MOVE SPACES TO WA-ERR.
           MOVE LS-DATE  TO WA-DATE.
       0000-VAL-DD.
           IF NOT WA-VAL-DD
                  MOVE "*" TO WA-ERR
                  GO TO 0000-DATE-EXIT.
       0000-VAL-MON.
           IF NOT WA-VAL-MM
                  MOVE "*" TO WA-ERR
                  GO TO 0000-DATE-EXIT.
       0000-VAL-MON-DAY.
           IF WA-30-MM 
              IF WA-DD > 30
                  MOVE "*" TO WA-ERR
                  GO TO 0000-DATE-EXIT.
       0000-VAL-LEAP.
           IF WA-MM = 2
              PERFORM 1000-LEAP THRU 1000-EXIT.
       0000-DATE-EXIT.
           MOVE WA-ERR TO LS-ERR.
           EXIT PROGRAM.
       1000-LEAP.
           IF WA-YY-YY = ZEROS
              DIVIDE WA-YY BY 400 GIVING WA-D REMAINDER WA-R
           ELSE
              DIVIDE WA-YY BY 4   GIVING WA-D REMAINDER WA-R.
           IF WA-R = ZEROS AND WA-DD > 29
              MOVE "*" TO WA-ERR
           ELSE
           IF WA-R NOT = ZEROS AND WA-DD > 28
              MOVE "*" TO WA-ERR.
       1000-EXIT.
           EXIT.
