```mermaid
flowchart TD
    %% Subgraphs grouping each phase
    subgraph User_Input [User Input]
        A[Prompt user for location or “exit”]
    end

    subgraph LLM_Call [LLM Interaction]
        B[Build system and user messages]
        C[Call local LLM for 3 facts]
        D[Receive LLM completion]
    end

    subgraph Output [Display Output]
        E[Print the 3 facts to the console]
    end

    %% Flow Connections
    A --> B
    B --> C
    C --> D
    D --> E
    E --> A

    %% Styling
    style User_Input fill:#E3F2FD,stroke:#2196F3,stroke-width:2px
    style LLM_Call   fill:#E8F5E9,stroke:#43A047,stroke-width:2px
    style Output     fill:#F3E5F5,stroke:#8E24AA,stroke-width:2px
