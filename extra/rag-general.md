```mermaid
flowchart LR
    %% Retrieval subgraph
    subgraph Retrieval [Retrieval Phase]
        direction TB
        Q[User Query]
        Emb[Embed Query]
        VS[Vector Search]
        Docs[Top-k Documents]
    end

    %% Generation subgraph
    subgraph Generation [Generation Phase]
        direction TB
        Combine[Combine Query + Documents]
        LLM[LLM Completion]
        Ans[Final Answer]
    end

    %% Flow
    Q --> Emb --> VS --> Docs --> Combine --> LLM --> Ans

    %% Styling
    style Retrieval fill:#FFF3E0,stroke:#FB8C00,stroke-width:2px
    style Generation fill:#E8F5E9,stroke:#43A047,stroke-width:2px
    style Q fill:#E3F2FD,stroke:#2196F3
    style Ans fill:#D1C4E9,stroke:#512DA8
