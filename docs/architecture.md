# Architecture

```mermaid
flowchart LR
    A[Synthetic data generator] --> B[Fault events CSV]
    A --> C[Problem records CSV]
    B --> D[Streamlit application]
    C --> D
    D --> E[Overview dashboard]
    D --> F[Fault explorer]
    D --> G[Session-based problem board]
    D --> H[Method and limitations]
```

## Design decisions
- CSV files keep the starter version transparent and easy to inspect.
- Streamlit session state allows a user to demonstrate updates without requiring a cloud database.
- Updates are intentionally temporary; persistence can be added later using a hosted database.
- The app uses a fixed synthetic demo period so the analysis remains coherent after deployment.
