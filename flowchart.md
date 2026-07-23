# Ticker Calendar Service Flow

```mermaid
flowchart TD
    A[Start app / run_server.py] --> B[init_db]
    B --> C{Command?}

    C -->|serve| D[run_server]
    C -->|run-rule| E[run_scheduled_check]
    C -->|list| F[list_scheduled_jobs]
    C -->|doctor| G[run_doctor]

    D --> H[build_scheduler]
    H --> I[add scheduled jobs]
    I --> J[APScheduler triggers]
    J --> E

    E --> K[start_run / lock]
    K --> L[evaluate_rule]
    L --> M[evaluate_earnings_today]
    L --> N[evaluate_earnings_next_week]
    L --> O[evaluate_earnings_tomorrow]
    L --> P[evaluate_earnings_day_morning_matrix]
    L --> Q[evaluate_popular_weekday]
    L --> R[evaluate_popular_friday]
    L --> S[evaluate_thursday_shakeout]
    L --> T[evaluate_eod_reversal]
    L --> U[evaluate_gap_fill_trade]
    L --> V[evaluate_iv_crush]
    L --> W[evaluate_monday_gap_fill]
    L --> X[evaluate_tuesday_high_low]
    L --> Y[evaluate_wednesday_midweek]
    L --> Z[evaluate_friday_gamma_squeeze]

    M --> AA[get_source_earnings_on]
    N --> AB[get_source_earnings_between]
    O --> AC[get_source_earnings_on for tomorrow]
    P --> AA
    Q --> AD[get_symbols]
    R --> AD
    S --> AD
    T --> AD
    U --> AD
    V --> AD
    W --> AD
    X --> AD
    Y --> AD
    Z --> AD

    K --> AE[_maybe_add]
    AE --> AF[alerts_db.record]
    AF --> AG[format_alert_message]
    AG --> AH[send_ntfy]
    AH --> AI[finish_run / write_heartbeat]

    subgraph Desktop UI
        AJ[main.py]
        AK[CalendarApp]
        AL[AlertMonitor]
        AM[evaluate_all]
    end

    AJ --> AK
    AK --> AL
    AL --> AM
    AM --> L
    AL --> AF
    AL --> AH