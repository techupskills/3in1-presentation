```mermaid
flowchart TD
    %% Main user input
    A([User inputs query]) --> B[Search ChromaDB (RAG)]

    %% RAG Search Block
    subgraph RAG Search
        B --> C{City found in RAG snippets?}
        C -- Yes --> D[Extract city name from RAG]
        C -- No --> E[Fallback: Detect city with LLM]
    end

    %% Data Retrieval
    subgraph Fact Gathering
        D --> F[Retrieve Office Facts from RAG]
        E --> F
        F --> G[Retrieve City Facts using LLM]
    end

    %% Distance Calculation
    G --> H[Calculate Distance from Raleigh, NC]

    %% Final Output
    subgraph Final Output
        H --> I[Format and Structure Final Answer]
        I --> J[Print RAG Query & Retrieved Snippets]
        J --> K[Display Final Answer to User]
    end

    %% Styling
    style A fill:#E3F2FD,stroke:#2196F3,stroke-width:2px
    style B,C,D,E fill:#FFF3E0,stroke:#FB8C00,stroke-width:2px
    style F,G fill:#E8F5E9,stroke:#43A047,stroke-width:2px
    style H fill:#E1F5FE,stroke:#0288D1,stroke-width:2px
    style I,J,K fill:#F3E5F5,stroke:#8E24AA,stroke-width:2px
