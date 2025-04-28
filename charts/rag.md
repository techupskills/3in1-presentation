```mermaid
flowchart TD
    %% Subgraphs
    subgraph user [User Interaction]
        A[User inputs query]
    end

    subgraph rag [RAG Search]
        B[Search ChromaDB - RAG]
        C{City found in RAG}
        D[Extract city from RAG]
        E[Fallback detect via LLM]
    end

    subgraph facts [Fact Gathering]
        F[Retrieve Office Facts]
        G[Retrieve City Facts]
    end

    subgraph dist [Distance Calculation]
        H[Calculate distance from Raleigh NC]
    end

    subgraph output [Final Output]
        I[Format final answer]
        J[Print RAG query and snippets]
        K[Display final answer]
    end

    %% Flow connections (all outside subgraphs)
    A --> B
    B --> C
    C -- Yes --> D
    C -- No  --> E
    D --> F
    E --> F
    F --> G
    G --> H
    H --> I
    I --> J
    J --> K

    %% Styling
    style user  fill:#E3F2FD,stroke:#2196F3,stroke-width:2px
    style rag   fill:#FFF3E0,stroke:#FB8C00,stroke-width:2px
    style facts fill:#E8F5E9,stroke:#43A047,stroke-width:2px
    style dist  fill:#E1F5FE,stroke:#0288D1,stroke-width:2px
    style output fill:#F3E5F5,stroke:#8E24AA,stroke-width:2px
