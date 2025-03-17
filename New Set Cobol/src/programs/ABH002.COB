       IDENTIFICATION DIVISION.
       PROGRAM-ID. ABH002.
       AUTHOR. TCSABH.
       ENVIRONMENT DIVISION.
       SPECIAL-NAMES.
           CONSOLE IS CRT.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WA-NAME        PIC X(50) VALUE SPACES.
       01 WA-CH-NAME     PIC X(50) VALUE SPACES.
       01 WA-CH          PIC X(01) VALUE SPACES.
       88 WA-VAL-CH VALUES "u" "U" "L" "l".
       PROCEDURE DIVISION.
       0000-BEGIN.
           DISPLAY SPACES.
           DISPLAY "ENTER NAME :- " AT 0505.
           ACCEPT WA-NAME AT 0520. 
           DISPLAY "ENTER CHOICE :- " AT 0705.
       0000-CH.    
           ACCEPT WA-CH   AT 0725.
           
             CALL "ABH001" USING WA-NAME WA-CH WA-CH-NAME.
             CANCEL "ABH001".
          
           DISPLAY WA-CH-NAME AT 1510.
           STOP RUN.
           
