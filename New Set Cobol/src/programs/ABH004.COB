       IDENTIFICATION DIVISION.
       PROGRAM-ID. ABH004.
       AUTHOR. TCSABH.
       ENVIRONMENT DIVISION.
       SPECIAL-NAMES.
           CONSOLE IS CRT.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WA-DATE        PIC 9(08) VALUE ZEROS.
       01 FILLER REDEFINES WA-DATE.
          05 WA-DD       PIC 9(02).
          05 WA-MM       PIC 9(02).
          05 WA-YY       PIC 9(04).
          05 FILLER REDEFINES WA-YY.
             10 WA-YY-CC PIC 9(02).
             10 WA-YY-YY PIC 9(02).
       01 WA-LC          PIC 9(02) VALUE ZEROS.
       01 WA-R           PIC 9(02) VALUE ZEROS.
       01 WA-Q           PIC 9(02) VALUE ZEROS.
       01 WA-R-100       PIC 9(02) VALUE ZEROS.
       01 WA-R-400       PIC 9(02) VALUE ZEROS.
       01 WA-TOTAL       PIC 9(06) VALUE ZEROS.
       01 WA-TEMP        PIC 9(06) VALUE ZEROS.
       01 WA-I           PIC 9(04) VALUE ZEROS.
       01 WA-DAY-YR      PIC 9(06) VALUE ZEROS.
       01 WA-DAY-MM      PIC 9(06) VALUE ZEROS.
       01 WA-MON         PIC X(24) VALUE
          "312831303130313130313031".
       01 FILLER REDEFINES WA-MON.
          05 WA-M-ARR OCCURS 12 TIMES PIC 9(02).
           
       LINKAGE SECTION.
       01 LS-DATE        PIC 9(08).
       01 LS-TOTAL       PIC 9(06).
       
       PROCEDURE DIVISION USING LS-DATE LS-TOTAL.
       0000-BEGIN.
           MOVE LS-DATE TO WA-DATE.
           PERFORM 0000-CNT-LP VARYING WA-I FROM 1901 BY 1 UNTIL
                       WA-I = WA-YY.
           
           PERFORM 0000-CNT-MM VARYING WA-I FROM 1 BY 1 UNTIL 
                       WA-I = WA-MM.
           
           COMPUTE WA-TEMP = WA-YY - 1900 - WA-LC.
           
           COMPUTE WA-TOTAL = (WA-TEMP * 365) + (WA-LC * 366)
                                + WA-DAY-MM + WA-DD.
                           
           IF WA-YY-YY = ZEROS
              DIVIDE WA-YY BY 400 GIVING WA-Q REMAINDER WA-R
           ELSE
              DIVIDE WA-YY BY 4   GIVING WA-Q REMAINDER WA-R.
           IF (WA-R = 0 AND WA-MM > 2)
              ADD 1 TO WA-TOTAL.

           MOVE WA-TOTAL TO LS-TOTAL.

           EXIT PROGRAM.

       0000-CNT-LP.
           DIVIDE WA-I BY 100 GIVING WA-Q REMAINDER WA-R-100.
           DIVIDE WA-I BY 400 GIVING WA-Q REMAINDER WA-R-400.
           DIVIDE WA-I BY 4   GIVING WA-Q REMAINDER WA-R.
           IF(WA-R-100 NOT = 0 AND WA-R = 0) OR (WA-R-400 = 0)
              ADD 1 TO WA-LC.

       0000-CNT-MM.
           COMPUTE WA-DAY-MM = WA-DAY-MM + WA-M-ARR(WA-I).



           
