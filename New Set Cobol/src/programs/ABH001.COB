       IDENTIFICATION DIVISION.
       PROGRAM-ID. ABH001.
       AUTHOR. TCSABH.
       ENVIRONMENT DIVISION.
       SPECIAL-NAMES.
           CONSOLE IS CRT.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WA-NAME        PIC X(50) VALUE SPACES.
       01 WA-CH          PIC X(01) VALUE SPACES.
       LINKAGE SECTION.
       01 LS-NAME     PIC X(50).
       01 LS-CH       PIC X(01).
       01 LS-CH-NAME  PIC X(50).
       PROCEDURE DIVISION USING LS-NAME LS-CH LS-CH-NAME.
       0000-BEGIN.
           
           MOVE LS-NAME TO WA-NAME.
           MOVE LS-CH TO WA-CH.
           IF(WA-CH = "l" OR = "L")
              INSPECT WA-NAME CONVERTING 
                  "ABCDEFGHIJKLMNOPQRSTUVWXYZ" TO
                  "abcdefghijklmnopqrstuvwxyz"
           
           ELSE IF(WA-CH = "u" OR "U")
              INSPECT WA-NAME CONVERTING
                  "abcdefghijklmnopqrstuvwxyz" TO
                  "ABCDEFGHIJKLMNOPQRSTUVWXYZ".
            
           MOVE WA-NAME TO LS-CH-NAME.
           EXIT PROGRAM.
