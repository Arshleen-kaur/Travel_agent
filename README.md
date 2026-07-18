# Travel_agent
                          ┌───────────────┐
                          │     START     │
                          └───────┬───────┘
                                  │
                                  ▼
                 ┌─────────────────────────┐
                 │ Guardrails              │
                 │ • Detect gibberish      │
                 │ • Validate input        │
                 └───────────┬─────────────┘
                             │
                      Valid Input?
                      ┌───┴────┐
                    No│        │Yes
                      ▼        ▼
                 Error/End  Extract Preferences
                             │
                             │
                             ▼
                  ┌────────────────────────┐
                  │ Ask Hotel Information  │
                  │ • Hotel name           │
                  │ • Address/Location     │
                  └───────────┬────────────┘
                              │
                              ▼
                  ┌────────────────────────┐
                  │ Research Agent         │
                  │ • Hotel location       │
                  │ • Nearby attractions   │
                  │ • Restaurants          │
                  │ • Travel times         │
                  └───────────┬────────────┘
                              │
                              ▼
                  ┌────────────────────────┐
                  │ Itinerary Planner      │
                  │ • Start from hotel     │
                  │ • Cluster attractions  │
                  │ • Minimize travel      │
                  │ • Budget optimization  │
                  └───────────┬────────────┘
                              │
                              ▼
                  ┌────────────────────────┐
                  │ Critic Agent           │
                  │ • Logical route?       │
                  │ • Budget OK?           │
                  │ • Timing feasible?     │
                  └───────────┬────────────┘
                              │
                    Approved? │
                     ┌────┴─────┐
                   No│          │Yes
                     ▼          ▼
          Itinerary Planner    END
                ▲
                └───────────────────────