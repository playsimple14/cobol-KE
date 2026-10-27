       IDENTIFICATION DIVISION.
       PROGRAM-ID. LNPROC01.
       AUTHOR. FINANCIAL-SYSTEMS-TEAM.
      *================================================================*
      * PURPOSE: COMPUTE LOAN INTEREST AND RISK ADJUSTMENTS            *
      *================================================================*

       ENVIRONMENT DIVISION.
       CONFIGURATION SECTION.

       DATA DIVISION.
       WORKING-STORAGE SECTION.
      *--- INPUT TRANSACTION RECORD ---*
       01  WS-LOAN-RECORD.
           05  WS-CUST-ID             PIC X(8).
           05  WS-CREDIT-SCORE        PIC 9(3).
               88  CREDIT-EXCELLENT   VALUES 750 THRU 850.
               88  CREDIT-GOOD        VALUES 650 THRU 749.
               88  CREDIT-FAIR        VALUES 580 THRU 649.
               88  CREDIT-POOR        VALUES 300 THRU 579.
           05  WS-LOAN-AMOUNT         PIC 9(7)V99.
           05  WS-LOAN-TERM-MONTHS    PIC 9(3).
           05  WS-COLLATERAL-TYPE     PIC X(4).
               88  COLLATERAL-PROPERTY VALUE 'PROP'.
               88  COLLATERAL-VEHICLE  VALUE 'VEHI'.
               88  COLLATERAL-UNSEC    VALUE 'NONE'.

      *--- WORKING CALCULATION FIELDS ---*
       01  WS-CALC-VARS.
           05  WS-BASE-INTEREST-RATE  PIC 9(2)V99 VALUE 05.50.
           05  WS-RISK-PREMIUM        PIC 9(2)V99 VALUE 00.00.
           05  WS-FINAL-INTEREST-RATE PIC 9(2)V99.
           05  WS-MONTHLY-INTEREST    PIC 9(7)V99.
           05  WS-TOTAL-INTEREST      PIC 9(8)V99.
           05  WS-STATUS-FLAG         PIC X(1).
               88  LOAN-APPROVED      VALUE 'A'.
               88  LOAN-REJECTED      VALUE 'R'.
               88  LOAN-MANUAL-REVIEW VALUE 'M'.

       PROCEDURE DIVISION.
       0000-MAIN-PROCESS.
           PERFORM 1000-EVAL-CUSTOMER-TIER.
           IF LOAN-REJECTED
               DISPLAY 'LOAN REJECTED FOR ID: ' WS-CUST-ID
           ELSE
               PERFORM 2000-CALC-INTEREST
               PERFORM 3000-APPLY-RISK-PENALTY
               PERFORM 4000-UPDATE-RECORD
           END-IF.
           STOP RUN.

       1000-EVAL-CUSTOMER-TIER.
           IF CREDIT-POOR
               SET LOAN-REJECTED TO TRUE
               MOVE 00.00 TO WS-FINAL-INTEREST-RATE
           ELSE
               IF CREDIT-EXCELLENT
                   SET LOAN-APPROVED TO TRUE
                   MOVE 00.00 TO WS-RISK-PREMIUM
               ELSE
                   IF CREDIT-GOOD
                       SET LOAN-APPROVED TO TRUE
                       MOVE 01.25 TO WS-RISK-PREMIUM
                   ELSE
                       SET LOAN-MANUAL-REVIEW TO TRUE
                       MOVE 02.50 TO WS-RISK-PREMIUM
                   END-IF
               END-IF
           END-IF.

       2000-CALC-INTEREST.
           COMPUTE WS-FINAL-INTEREST-RATE =
               WS-BASE-INTEREST-RATE + WS-RISK-PREMIUM.
           COMPUTE WS-MONTHLY-INTEREST ROUNDED =
               (WS-LOAN-AMOUNT * (WS-FINAL-INTEREST-RATE / 100)) / 12.
           COMPUTE WS-TOTAL-INTEREST ROUNDED =
               WS-MONTHLY-INTEREST * WS-LOAN-TERM-MONTHS.

       3000-APPLY-RISK-PENALTY.
           IF COLLATERAL-UNSEC AND NOT CREDIT-EXCELLENT
               COMPUTE WS-TOTAL-INTEREST =
                   WS-TOTAL-INTEREST + (WS-LOAN-AMOUNT * 0.015)
           END-IF.

       4000-UPDATE-RECORD.
           DISPLAY 'PROCESSED LOAN FOR: ' WS-CUST-ID.
           DISPLAY 'FINAL RATE: ' WS-FINAL-INTEREST-RATE.
           DISPLAY 'TOTAL INTEREST: ' WS-TOTAL-INTEREST.
