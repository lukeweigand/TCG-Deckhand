# TCG Deckhand - Design Document

## Project Overview

**TCG Deckhand** is an AI-powered, private sandbox application for competitive TCG players. Its core purpose is to provide a dedicated, secure environment for refining decks and practicing against an AI opponent without revealing strategies. The product is managed by Luke Weigand.

## Refined Problem Statement

The competitive TCG ecosystem is plagued by inefficiencies and a lack of professional-grade tools. High-stakes players face a "preparation paradox" due to public simulators that expose their strategies and fail to provide the data needed for rigorous playtesting. This results in player burnout, strategic erosion, and frustration. Simultaneously, tournament organizers struggle with time-consuming manual deck checks, judges lack immediate access to analytical tools for complex rulings, and brands have no objective data for player endorsements.

**How might we** create a platform that provides a private, secure, and professional-grade environment for all stakeholders—from competitive players and tournament organizers to judges and brand representatives—to improve, manage, and grow the TCG community?

## Target Audience

The TCG Deckhand serves a diverse yet interconnected set of users, each with unique needs and motivations.

### Tournament Organizer (Tina)

Tina is a dedicated tournament organizer who manages large-scale TCG events. Her primary pain points revolve around logistics and ensuring a fair, timely, and engaging experience for all participants. Tina's biggest headache is the **inefficient deck-checking process**. Currently, judges manually verify decklists against physical decks, which is a tedious and error-prone process that causes significant delays, especially in the early rounds of a tournament. Tina envisions a future where TCG Deckhand could be a required pre-tournament tool, allowing players to submit their decks for automated verification before the event, freeing up judges and ensuring the tournament runs smoothly and on schedule.

### TCG Brand Endorsement Representative (Barry)

Barry works for a major TCG brand and is responsible for talent scouting and managing player endorsements. He is constantly looking for new and promising players to represent the brand. Barry's challenge is the **lack of reliable, quantifiable data on a player's strategic skill**. While he can track tournament wins, he has no way to see how a player performs in practice, what their win rate is with specific decks, or how they adapt to different matchups. The private, AI-powered environment of TCG Deckhand would be a game-changer for Barry. It could provide him with detailed analytics and a player's strategic data, giving him a more objective basis for making endorsement decisions and justifying brand investments in specific players, card creation, and playing platforms.

### Competitive Player (Carson)

Carson is a highly competitive player aiming to win a major tournament with a large prize pool. His life revolves around refining their skills and preparing for their next event. His main frustration is the **"preparation paradox"** that makes practicing seem impossible. He spends countless hours on public simulators, but the environment is often hostile, and their experimental strategies are exposed to potential opponents. He also finds it difficult to get a sufficient number of games against specific matchups to gather reliable data. TCG Deckhand solves this by providing him with a private, secure, and data-rich sandbox where he can tirelessly practice against an AI, fine-tuning his deck and strategy without revealing their hand. The "Best Move" suggestion feature is particularly valuable as it helps him identify and correct misplays.

### Judge (Judy)

Judy is a long-time TCG player and a certified judge. She volunteers her time to ensure the integrity of tournaments. Judy's biggest challenge is **resolving disputes and handling complex rules interactions** during a match between players. She often has to make rulings on the spot, and while she is knowledgeable, a wrong call could unfairly impact a player's game or even a tournament's outcome. The core game engine of TCG Deckhand could be a powerful tool for judges. By allowing players to recreate complex game states within the application, a judge could use the game to quickly analyze the board state and a rules interaction, making more accurate and confident rulings.

## Design Goals & Success Metrics

- **Improve Player Preparation:** Achieve a 20% increase in the number of games played by a competitive player per week compared to traditional methods
- **Enhance Tournament Efficiency:** Reduce the average time for deck checks at sanctioned events by at least 50% for players who use the application
- **Provide Strategic Insights:** The "Best Move" suggestion feature should be rated as "useful" or "highly useful" by over 75% of user testers
- **Generate Actionable Analytics:** Create a dashboard that successfully provides brand representatives and content creators with data on win rates, strategic tendencies, and play patterns

## Guiding Design Principles

- **User-Centrism:** The design will be centered on the specific needs of its diverse user base. It will prioritize features that enhance strategic preparation for players while also providing logistical benefits for organizers, analytical tools for brands, and decision support for judges and players
- **Simplicity:** The UI will be clean and focused, avoiding unnecessary complexity. The core gameplay loop, data input, and analytical tools will be intuitive and easy to navigate for all users
- **Honesty:** The application's purpose is to provide objective, real-time strategic analysis. The design will be transparent about its win-probability metrics and "Best Move" suggestions, serving as a professional training and analytical environment
- **Integrity:** The platform will prioritize security and privacy, ensuring a player's deck lists and strategic data remain confidential and are not exposed to competitors

## Competitive Visual Analysis

The main competitors are existing online simulators.

- A separate user interface for tournament organizers to manage events
