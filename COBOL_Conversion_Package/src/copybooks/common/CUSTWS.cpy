01  WS-WORK-AREAS.
           05 CUST-FILE-STATUS         PIC X(2)  VALUE SPACES.
           05 END-OF-FILE-SW           PIC X     VALUE 'N'.
              88 END-OF-FILE                     VALUE 'Y'.
           
       01  WS-CURRENT-DATE.
           05 WS-CURRENT-YEAR          PIC 9(4).
           05 WS-CURRENT-MONTH         PIC 9(2).
           05 WS-CURRENT-DAY           PIC 9(2).